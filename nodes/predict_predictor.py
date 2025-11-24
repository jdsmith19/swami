# External Libraries
from dotenv import load_dotenv
import os
import datetime
import uuid
import argparse
import sys
import json

# Prediction Models
from prediction_models.XGBoost import XGBoost
from prediction_models.LinearRegression import LinearRegression
from prediction_models.RandomForest import RandomForest
from prediction_models.LogisticRegression import LogisticRegression
from prediction_models.KNearest import KNearest

# Internal Models
from models.predict_model import PredictState

# Data Sources
from data_sources.ResultsDB import ResultsDB

# Utilities
from utils.logger import log
from utils.matchups import get_predictions_by_matchup
from utils.formatting import formatting

load_dotenv()
this_filename = os.path.basename(__file__).replace(".py","")

def predict_predictor_node(state: PredictState):
    num_predictions = len(state["prediction_set"])
    log(state["log_path"], f"Making predictions for { num_predictions } games", state["log_type"], this_filename)
    predictions = []
    for best in state["best_results"]:
        if best["model_name"] == 'XGBoost':
            xgb = XGBoost(state["aggregates"], best["target"], best["features_used"], state["prediction_set"])
            xgb.predict_spread(state["prediction_set"])
            predictions.append(xgb.model_output)

        elif best["model_name"] == 'LinearRegression':
            lr = LinearRegression(state["aggregates"], best["target"], best["features_used"], state["prediction_set"])
            lr.predict_spread(state["prediction_set"])
            predictions.append(lr.model_output)

        elif best["model_name"] == 'RandomForest':
            rf = RandomForest(state["aggregates"], best["target"], best["features_used"], state["prediction_set"])
            rf.predict_spread(state["prediction_set"])
            predictions.append(rf.model_output)

        elif best["model_name"] == 'LogisticRegression':
            lg = LogisticRegression(state["aggregates"], best["target"], best["features_used"], state["prediction_set"])
            lg.predict_winner(state["prediction_set"])
            predictions.append(lg.model_output)

        elif best["model_name"] == 'KNearest':
            kn = KNearest(state["aggregates"], best["target"], best["features_used"], state["prediction_set"])
            kn.predict_winner(state["prediction_set"])
            predictions.append(kn.model_output)
    
    matchups = get_predictions_by_matchup(predictions, state["matchups"])
    formatted = formatting.format_predictions(matchups)
    
    log(state["log_path"], formatted, state["log_type"], this_filename)
    
    return {
        "predictions": predictions,
        "matchups": matchups
    }