# External Libraries
import json
import os
from pydantic import ValidationError
import sqlite3

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

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def planner_validator_node(state: PlannerState) -> PlannerState:
    """Validates that the data is valid JSON and passes schema."""
    log_path = state["log_path"]
    log_type = state["log_type"]

    validated = False
    messages = state["messages"]

    # if not isinstance(state["messages"][-1], AIMessage):
    #     return {
    #         "validated": False
    #     }
    
    try:
        obj = json.loads(state["last_message"])

    except json.JSONDecodeError as e:
        error_response = f"VALIDATION ERROR: The output is not valid JSON. You must enclose keys in double quotes and ensure all syntax is correct. Error details: { e }"
        messages.append(HumanMessage(content = error_response))
        log(log_path, error_response, "file", this_filename)
        log(log_path, "Failed JSON Decode Validation", log_type, this_filename)
        return {
            "validated": validated,
            "messages": messages,
            "failed_validation_count": state["failed_validation_count"] + 1
        }
        
    try:
        validated_plan = ExperimentPlan.model_validate(obj)
    
    except ValidationError as e:
        error_response = f"VALIDATION ERROR. Review the following error details carefully and try again by generating corrected JSON. DO NOT call this tool again until you have fixed the JSON. Details: \n{e}"
        messages.append(HumanMessage(content = error_response))
        log(log_path, error_response, "file", this_filename)
        log(log_path, "Failed ExperimentPlan validation", log_type, this_filename)
        return {
            "validated": validated,
            "messages": messages,
            "failed_validation_count": state["failed_validation_count"] + 1
        }
    
    conn = sqlite3.connect(state["db_path"])
    conn.row_factory = dict_factory
    cur = conn.cursor()
    rows = cur.execute(f"SELECT * FROM result WHERE agent_id = '{ state["agent_id"] }'")    
    rows = cur.fetchall()
    conn.close()
    if not state["phase"] == 4:
        duplication_errors = []
        for experiment in validated_plan.model_dump()['experiments']:
            for row in rows:
                if row['model_name'] == experiment['model']:
                    if sorted(row['features_used']) == sorted(experiment['features']):
                        duplication_errors.append(row)
        if not duplication_errors == []:
            error_response = f"DUPLICATE EXPERIMENT ERROR: Exact experiments have already been run. Results were: { duplication_errors }"
            messages = state["messages"]
            messages.append(HumanMessage(content = error_response))
            log(log_path, error_response, "file", this_filename)
            log(log_path, "Failed Duplicate Experiment validation", log_type, this_filename)
            return {
                "validated": validated,
                "messages": messages,
                "failed_validatino_count": state["failed_validation_count"] + 1
            }


    validated = True
    return {
        "validated": validated,
        "next_experiments": validated_plan.model_dump()["experiments"],
        "commentary": validated_plan.model_dump()["commentary"],
        "failed_validation_count": 0
    }