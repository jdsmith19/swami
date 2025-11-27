# External Libraries
import os

# LangGraph / LangChain
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Models
from models.planner_model import PlannerState

# Utilities
from utils.logger import log
from utils.messages import get_message_from_llm_response

this_filename = os.path.basename(__file__).replace(".py","")

def planner_caller_node(state: PlannerState) -> PlannerState:
    llm = ChatNVIDIA(
        base_url = state["llm_base_url"], 
        api_key = "not-needed",
        model = state["llm_model"],
        max_tokens = 4096
    )

    if (len(state["messages"]) - 2 >= 1) and (state["tokens"] > 50000):
        lines = []
        lines.append(f"Token usage is high! ({ state["tokens"] })")
        lines.append(f"Resetting to system and initial prompt.")
        log(state["log_path"], "\n".join(lines), state["log_path"], this_filename)
        state["messages"] = [SystemMessage(content=state["system_prompt"]), HumanMessage(content=state["initial_prompt"])]

    ai_responses = 0
    for message in state["messages"]:
        #print(type(message))
        if isinstance(message, AIMessage):
            ai_responses += 1

    if ai_responses >= 4:
        log(state["log_path"], f"Validation has failed { state["failed_validation_count"] } times.", state["log_type"], this_filename)
        state["messages"] = [SystemMessage(content=state["system_prompt"]), HumanMessage(content=state["initial_prompt"])]
        state["failed_validation_count"] = 0

    response = llm.invoke(
        state["messages"]
    )

    messages = state["messages"]
    #message = get_message_from_llm_response(response)
    messages.append(AIMessage(content=response.content))
    total_tokens = response.response_metadata["token_usage"]["total_tokens"] + state["tokens"]

    return {
        "llm_response": response,
        "last_message": response.content,
        "messages": messages,
        "tokens": response.response_metadata["token_usage"]["total_tokens"],
        "reasoning": response.response_metadata["reasoning"],
        "total_tokens": total_tokens
    }