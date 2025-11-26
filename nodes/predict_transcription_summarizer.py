# External Libraries
import os
import json

# LangGraph / LangChain
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.messages import HumanMessage, SystemMessage

# Models
from models.predict_model import PredictState

# Utilities
from utils.prompts import load_prompt
from utils.logger import log

this_filename = os.path.basename(__file__).replace(".py","")
log_path = None
log_type = None

def load_initial_messages(home_path, games, transcript):
    # Set Messages
    system_prompt = load_prompt(f"{ home_path }predictor/podcast_summarizer_system.txt").format(
        games = games
    )
    initial_prompt = load_prompt(f"{ home_path }predictor/podcast_summarizer_initial.txt").format(
        transcript = transcript
    )
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=initial_prompt)]

    return messages

def call_llm(messages, llm_base_url, llm_model):
    llm = ChatNVIDIA(
        base_url = llm_base_url, 
        api_key = "not-needed",
        model = llm_model,
        max_tokens = 4096
    )

    response = llm.invoke(messages)

    log(log_path, f"Tokens Used: { response.response_metadata["token_usage"]["total_tokens"] }", log_type, this_filename)
    
    return response

def predict_transcription_summarizer_node(state: PredictState):
    global log_path, log_type
    log_path = state["log_path"]
    log_type = state["log_type"]
    podcast_summaries = {}
    tokens = 0
    for transcript in state["transcriptions"]:
        log(log_path, f"Summarizing { transcript["name"] }", log_type, this_filename)
        messages = load_initial_messages(state["home_path"], state["games"], transcript["full_text"])
        response = call_llm(messages, state["llm_base_url"], state["llm_model"])
        log(log_path, response.content, log_type, this_filename)
        summary = json.loads(response.content)
        tokens += int(response.response_metadata["token_usage"]["total_tokens"])
        for s in summary:
            podcast_summaries[s] = summary[s]
    print(f"Total Tokens Used: { tokens }")
    print(podcast_summaries)
    return {
        "podcast_summaries": podcast_summaries,
        "transcription_summary_tokens": tokens
    }