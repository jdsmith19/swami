# External Libraries
import time
import os
import uuid

# LangGraph / LangChain
from langchain_core.messages import HumanMessage, SystemMessage

# Models
from models.planner_model import PlannerState

# Utilities
from utils.prompts import load_prompt
from utils.logger import log

# Set variables that will need to be accessed
this_filename = os.path.basename(__file__).replace(".py","")
log_path = None
log_type = None
db_path = None

def planner_setup_node(state: PlannerState) -> PlannerState:
    # Start a timer
    state["start"] = time.time()
    state["planner_agent_id"] = str(uuid.uuid4())
    
    global log_path, log_type, db_path
    log_path = state["log_path"]
    log_type = state["log_type"]
    db_path = state["db_path"]
    
    lines = []
    lines.append(f"\n{'='*80}")
    lines.append(f"OPTIMIZE PLANNER AGENT")
    lines.append(f"ID: { state["planner_agent_id"] }")
    lines.append(f"{'='*80}")
    log(log_path, "\n".join(lines), log_type, this_filename)
    #print(state["trimmed_results"])
    
    # Create a Conversation ID
    state["phase_prompt"] = load_prompt(f"{ state['home_path'] }optimize/planner/phase_{ state['phase'] }.txt")
    state["system_prompt"] = load_prompt(f"{ state['home_path'] }optimize/planner/system.txt").format(
        phase = str(state["phase"]),
        phase_instructions = state["phase_prompt"],
        historical_results = {
            "best_results": state["best_results"],
            "previous_experiments": state["trimmed_results"]
        }
    )
    #print(state["system_prompt"])
    state["initial_prompt"] = load_prompt(f"{ state['home_path'] }optimize/planner/initial.txt")
    state["messages"] = [SystemMessage(content=state["system_prompt"]), HumanMessage(content=state["initial_prompt"])]
    state["failed_validation_count"] = 0
    state["skip_validation"] = False
    # DEBUG
    state["confirmed_append"] = False
    return state