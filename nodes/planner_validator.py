# External Libraries
import json
import os
from pydantic import ValidationError

# LangGraph / LangChain
from langchain_core.messages import HumanMessage, AIMessage

# Models
from models.planner_model import PlannerState
from models.experiments_model import ExperimentPlan

# Utilities
from utils.logger import log

this_filename = os.path.basename(__file__).replace(".py","")
log_path = None
log_type = None

def planner_validator_node(state: PlannerState) -> PlannerState:
    """Validates that the data is valid JSON and passes schema."""
    log_path = state["log_path"]
    log_type = state["log_type"]

    validated = False

    # if not isinstance(state["messages"][-1], AIMessage):
    #     return {
    #         "validated": False
    #     }
    
    try:
        obj = json.loads(state["last_message"])

    except json.JSONDecodeError as e:
        error_response = f"VALIDATION ERROR: The output is not valid JSON. You must enclose keys in double quotes and ensure all syntax is correct. Error details: { e }"
        message = [HumanMessage(content = error_response)]
        log(log_path, error_response, log_type, this_filename)
        return {
            "validated": validated,
            "messages": message,
            "failed_validation_count": state["failed_validation_count"] + 1
        }
        
    try:
        validated_plan = ExperimentPlan.model_validate(obj)
    
    except ValidationError as e:
        error_response = f"VALIDATION ERROR. Review the following error details carefully and try again by generating corrected JSON. DO NOT call this tool again until you have fixed the JSON. Details: \n{e}"
        message = [HumanMessage(content = error_response)]
        log(log_path, error_response, log_type, this_filename)
        return {
            "validated": validated,
            "messages": message,
            "failed_validation_count": state["failed_validation_count"] + 1
        }
    validated = True
    return {
        "validated": validated,
        "next_experiments": validated_plan.model_dump()["experiments"],
        "commentary": validated_plan.model_dump()["commentary"]
    }