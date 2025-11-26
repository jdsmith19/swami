#External Libraries
import json
import os

# Models
from models.predict_model import PredictState

# LangGraph / LangChain
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.messages import HumanMessage, SystemMessage

# Utilities
from utils.logger import log
from utils.prompts import load_prompt

this_filename = os.path.basename(__file__).replace(".py","")
log_path = None
log_type = None

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

def load_initial_messages(home_path, injury_report):
    # Set Messages
    system_prompt = load_prompt(f"{ home_path }predictor/injury_adjustment_system.txt")
    initial_prompt = load_prompt(f"{ home_path }predictor/injury_adjustment_initial.txt").format(
        injury_report = injury_report
    )
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=initial_prompt)]

    return messages

def predict_injury_adjuster_node(state: PredictState):
    tokens = 0
    adjustment_instructions = []
    for ir in state["injury_reports"]:
        log(log_path, f"Generating adjustment ratios for { ir["team"] }", log_type, this_filename)
        messages = load_initial_messages(state["home_path"], ir)
        response = call_llm(messages, state["llm_base_url"], state["llm_model"])
        tokens += int(response.response_metadata["token_usage"]["total_tokens"])
        print(response)
        log(log_path, response.content, log_type, this_filename)
        instruction = json.loads(response.content)
        adjustment_instructions.append(instruction)
    print(f"Total Tokens Used: { tokens }")
    print(adjustment_instructions)
    
    return {
        "injury_adjustment_instructions": adjustment_instructions,
        "injury_adjustment_tokens": tokens
    }