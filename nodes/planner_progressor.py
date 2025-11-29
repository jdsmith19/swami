# External Libraries
import os
import json
import time

# Models
from models.planner_model import PlannerState

# Utilities
from utils.logger import log

# Set variables that will need to be accessed
this_filename = os.path.basename(__file__).replace(".py","")
log_path = None
log_type = None
db_path = None

def planner_progressor_node(state: PlannerState) -> PlannerState:
    global log_path, log_type
    log_path = state["log_path"]
    log_type = state["log_type"]
    state["judged"] = False
    state["end"] = time.time()
    lines = []
    if state.get("reasoning"):
        lines.append("\n*** REASONING ***")
        for reason in state['reasoning']:
            lines.append(state["reasoning"])
    lines.append("\n*** COMMENTARY ***")
    lines.append(state["commentary"])
    #lines.append(f"\nTokens Used: { state["tokens"] }")
    lines.append(f"{'='*80}")
    log(log_path, "\n".join(lines), "file", this_filename)
    
    lines = []
    lines.append(f"Planner Agent { state["planner_agent_id"] } finished in { round(state["end"] - state["start"], 2) }s")
    lines.append(f"{'='*80}")
    log(log_path, "\n".join(lines), log_type, this_filename)

    return state