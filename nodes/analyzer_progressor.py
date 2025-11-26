# External Libraries
import os
import json
import time

# Models
from models.analyzer_model import AnalyzerState

# LangGraph / LangChain
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Utilities
from utils.logger import log
from utils.prompts import load_prompt, get_team_lookup_string

# Set variables that will need to be accessed
this_filename = os.path.basename(__file__).replace(".py","")
log_path = None
log_type = None
db_path = None

def analyzer_progressor_node(state: AnalyzerState) -> AnalyzerState:
    global log_path, log_type
    log_path = state["log_path"]
    log_type = state["log_type"]
    #print(state.get("analysis"))
    lines = []
    lines.append(f"\n{'='*80}")
    lines.append(f"MATCHUP: { state["analysis"]["matchup"] }")
    lines.append(f"PREDICTION: { state["analysis"]["final_prediction"] }")
    lines.append(f"CONFIDENCE: { state["analysis"]["confidence"] }")
    lines.append(f"ANALYSIS: { state["analysis"]["analysis"] }")
    lines.append(f"\n{'='*80 }\n")
    log(state["log_path"], "\n".join(lines), state["log_type"], this_filename)
    game_index = state["game_index"]
    game_index += 1
    if game_index <= len(state["games"]) - 1:
        current_matchup = state["matchups"][state["games"][game_index]]
        initial_prompt = load_prompt(f"{ state['home_path'] }predictor/analyzer/initial.txt").format(
            matchup=current_matchup,
            db_lookup_string=get_team_lookup_string(state["games"][game_index])
        )
        system_prompt = load_prompt(f"{ state['home_path'] }predictor/analyzer/system.txt").format(
            best_results=state["best_results"]
        )
        scratch_messages = [SystemMessage(content=system_prompt), HumanMessage(content=initial_prompt)]
        return {
            "game_index": game_index,
            "current_matchup": current_matchup,
            "initial_prompt": initial_prompt,
            "system_prompt": system_prompt,
            "messages": [SystemMessage(content=system_prompt),HumanMessage(content=initial_prompt)],
            "scratch_messages": scratch_messages
        }
    return {}
