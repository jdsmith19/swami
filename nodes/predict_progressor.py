# Models
from models.predict_model import PredictState

def build_matchups(games, matchups, predictions, expert_analysis):
    for game in games:
        matchups[game] = predictions[game]
    for a in expert_analysis:
        matchups[a["matchup"]]["expert_analysis"] = a
    return matchups

def predictor_progressor_node(state: PredictState):
    matchups = build_matchups(state["games"], state["matchups"], state["predictions"], state["expert_analysis"])
    return {
        "matchups": matchups
    }