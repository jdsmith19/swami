# External Libraries
from dotenv import load_dotenv
import os
import datetime
import uuid
import argparse
import sys
from pathlib import Path
import time
import sqlite3

# Data Sources
from data_sources.DataAggregate import DataAggregate
from data_sources.ResultsDB import ResultsDB

# Internal Models
from models.optimize_model import OptimizeState

# Utilities
from utils.logger import log
from utils.features import get_extended_features

load_dotenv()
this_filename = os.path.basename(__file__).replace(".py","")

# Initialize global variables
this_filename = os.path.basename(__file__).replace(".py","")

def optimize_setup_node(state: OptimizeState) -> OptimizeState:
    state["start"] = time.time()
    # Set the agent ID
    state["agent_id"] = str(uuid.uuid4())

    # Set up the DB Path
    state["db_path"] = os.getenv("DB_PATH")

    with open("queries/insert_agent_run.sql") as f:
        template = f.read()
        query = template.format(
            agent_id = f"\"{ state["agent_id"] }\"",
            agent_name = f"\"Optimize Agent\""
        )
        conn = sqlite3.connect(state["db_path"])
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        conn.close()


    # Parse Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action = "store_true", help = "verbose printing of logs to stdout (not just logfile)")
    parser.add_argument("--max_experiments", type = int, default = 500, help = "max number of experiments to run, default is 500")
    args = parser.parse_args()
    
    # Print logs to console?
    if args.debug:
        state["log_type"] = "all"
    else:
        state["log_type"] = "file"
    
    # Create the 

    # Set the max number of experiments, current experiment count, and initialize experiment history in the AgentState
    state["max_experiments"] = args.max_experiments
    state["experiment_count"] = 0
    state["experiment_history"] = []
    state["phase"] = 1

    # Generate log_file name
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    script = sys.argv[0].replace(".py", "")
    state["log_path"] = f"logs/{ script }/{ now }_{ state["agent_id"] }.txt"
    log(state["log_path"], "Setting up...\n", state["log_type"], this_filename)
    
    # Load best current best feature results
    rdb = ResultsDB(state["db_path"])
    state["best_results"] = rdb.load_best_results()
    
    #with open('results/feature_optimization_results.json', 'r') as f:
    #    state["best_results"] = json.load(f)['best_results']

    # Load the list of relevant models
    state["prediction_models"] = [
        {
            "name": "XGBoost",
            "type": "regressor"
        },
        {
            "name": "LinearRegression",
            "type": "regressor"
        },
        {
            "name": "RandomForest",
            "type": "regressor"
        },
        {
            "name": "LogisticRegression",
            "type": "classifier"
        },
        {
            "name": "KNearest",
            "type": "classifier"
        }
    ]

    # Load all of the extendeded features
    state["extended_features"] = get_extended_features()

    # Historical Results
    state["historical_results"] = []
    state["planner_results"] = []
    
    # LLM Details
    state["llm_model"] = os.getenv('LLM_MODEL')
    state["llm_base_url"] = os.getenv('LLM_BASE_URL')

    # System Details
    state["home_path"] = str(Path.home()) + "/Desktop/swami/prompts/"

    # Data Aggregates
    start_time = time.time()
    state["data_aggregates"] = DataAggregate(state)
    end_time = time.time()
    log(state["log_path"], f"Loaded DataAggregates in { end_time - start_time }s.", state["log_type"], this_filename)

    state["aggregates"] = state["data_aggregates"].aggregates
    state["upcoming_games"] = state["data_aggregates"].upcoming_games
    state["prediction_set"] = state["data_aggregates"].prediction_set
    
    state["trimmed_results"] = {
        "best_results": state["best_results"],
        "historical_results": {}
    }
    
    state["total_tokens"] = 0
    
    return state