# External Libraries
import os

# Models
from models.predict_model import PredictState

# Data Sources
from data_sources.ESPN import NFLDepthChartAnalyzer

# Utilities
from utils.logger import log
from utils.nfl import teams
from utils.matchups import get_injury_reports_by_matchup

this_filename = os.path.basename(__file__).replace(".py","")

def predict_injury_reporter_node(state: PredictState):
    log_path = state["log_path"]
    log_type = state["log_type"]
    log(log_path, "Starting Injury Reporter Node", log_type, this_filename)
    requested_teams = state["teams"]
    injury_reports = []
    matchups = state["matchups"]
    dca = NFLDepthChartAnalyzer()

    for team in requested_teams:
        injury_report = dca.get_injury_summary_for_agent(teams.team_name_to_espn_code(team))
        injury_reports.append(injury_report)
    
    matchups = get_injury_reports_by_matchup(injury_reports, state["matchups"])
    
    return {
        "injury_reports": injury_reports
    }