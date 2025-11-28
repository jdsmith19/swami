# External Libraries
from dotenv import load_dotenv
import os
import datetime
import uuid
import sys
from pathlib import Path
import json

# LangGraph / LangChain
from langchain_core.messages import HumanMessage, SystemMessage

# Internal Models
from models.analyzer_model import AnalyzerState

# Data Sources
from data_sources.ResultsDB import ResultsDB

# Utilities
from utils.logger import log
from utils.prompts import load_prompt
from utils.nfl import teams

load_dotenv()
this_filename = os.path.basename(__file__).replace(".py","")

def get_team_lookup_string(matchup):
    teams_list = matchup.split(" @ ")
    lookup_string = ""
    for team in teams_list:
        lookup_string += f"{ team }: { teams.odds_api_team_to_pfr_team(team)}\n"
    return lookup_string

def analyzer_setup_node(state: AnalyzerState):
    log(state["log_path"], "Setting up Analyzer...\n", state["log_type"], this_filename)
    analyzer_agent_id = str(uuid.uuid4())
    game_index = 0
    tokens = 0
    current_matchup = state["matchups"][state["games"][game_index]]
    current_matchup = json.dumps(current_matchup)
    db_lookup_string = get_team_lookup_string(state["games"][game_index])
    initial_prompt = load_prompt(f"{ state['home_path'] }predictor/analyzer/initial.txt").format(
        matchup=current_matchup,
        db_lookup_string=db_lookup_string
    )
    system_prompt = load_prompt(f"{ state['home_path'] }predictor/analyzer/system.txt").format(
        best_results=state["best_results"]
    )

    return {
        "agent_id": analyzer_agent_id,
        "game_index": game_index,
        "current_matchup": current_matchup,
        "initial_prompt": initial_prompt,
        "system_prompt": system_prompt,
        "games": state["games"],
        "messages": [SystemMessage(content=system_prompt),HumanMessage(content=initial_prompt)],
        "tokens": tokens,
        "failure_count": 0
    }