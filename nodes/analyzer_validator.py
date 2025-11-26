# External Libraries
import json
import os

# LangGraph / LangChain
from langchain_core.messages import HumanMessage, SystemMessage

# Models
from models.analyzer_model import AnalyzerState

# Utilities
from utils.logger import log

this_filename = os.path.basename(__file__).replace(".py","")
log_path = None
log_type = None

def analyzer_validator_node(state: AnalyzerState) -> AnalyzerState:
    """Validates that the data is valid JSON and passes schema."""
    log_path = state["log_path"]
    log_type = state["log_type"]
    log(log_path, "Validating response", log_type, this_filename)
    validated = False
    
    last_message = state["messages"][-1].content
    
    #print(last_message)

    try:
        obj = json.loads(last_message)

    except json.JSONDecodeError as e:
        failure_count = state["failure_count"] + 1
        error_response = f"VALIDATION ERROR: The output is not valid JSON. You must enclose keys in double quotes and ensure all syntax is correct. Error details: { e }"
        messages = state["messages"]
        messages.append(HumanMessage(content=error_response))
        log(log_path, "Validation failed", log_type, this_filename)
        #print(state["messages"])
        if failure_count > 1:
            print(f"Failed { failure_count } times. Resetting messages and restarting analysis.\n")
            return{
                "validated": validated,
                "messages": [SystemMessage(content=state["system_prompt"]),HumanMessage(content=state["initial_prompt"])],
                "failure_count": 0
            }
        else:
            return {
                "validated": validated,
                "messages": messages,
                "failure_count": failure_count
            }
    
    log(log_path, "Validation succeeded", log_type, this_filename)
    final_analysis = state.get("final_analysis") or []
    final_analysis.append(obj)
    validated = True
    return {
        "validated": validated,
        "final_analysis": final_analysis,
        "analysis": obj,
        "failure_count": 0
    }