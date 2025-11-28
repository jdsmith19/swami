# External Libraries
import os

# Data Sources
from data_sources.DataAggregate import DataAggregate

# Models
from models.predict_model import PredictState

# Utilities
from utils.logger import log
from utils.matchups import create_matchups, get_unique_teams, get_unique_games

this_filename = os.path.basename(__file__).replace(".py","")

def predict_aggregate_loader_node(state: PredictState):
    aggregates = DataAggregate(state)
    
    lines = []
    lines.append(f"{ len(aggregates.aggregates) } aggregate rows loaded.")
    lines.append(f"{ len(aggregates.upcoming_games) } upcoming game rows loaded.")
    lines.append(f"{ len(aggregates.upcoming_games) } prediction set rows loaded.")
    log(state["log_path"], "\n".join(lines), state["log_type"], this_filename)
    matchups = create_matchups(aggregates.upcoming_games)
    teams = get_unique_teams(aggregates.upcoming_games)
    games = get_unique_games(matchups)
    print(games)
    
    week = aggregates.upcoming_games['season_week_number'].unique()[0]
    season = aggregates.upcoming_games['season'].unique()[0]
    
    return {
        "aggregates": aggregates.aggregates,
        "upcoming_games": aggregates.upcoming_games,
        "prediction_set": aggregates.prediction_set,
        "matchups": matchups,
        "teams": teams,
        "week": week,
        "season": season,
        "games": games
    }