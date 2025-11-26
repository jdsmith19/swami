# External Libraries
from dotenv import load_dotenv
import os
import datetime
import uuid
import argparse
import sys
from pathlib import Path
import json

# Internal Models
from models.predict_model import PredictState

# Data Sources
from data_sources.ResultsDB import ResultsDB

# Utilities
from utils.logger import log

load_dotenv()
this_filename = os.path.basename(__file__).replace(".py","")

def predict_setup_node(state: PredictState) -> PredictState:
    # Parse Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="verbose printing of logs to stdout (not just logfile)")
    args = parser.parse_args()
        
    # Print logs to console?
    if args.debug:
        log_type = "all"
    else:
        log_type = "file"

    # Generate details for log_file
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    script = sys.argv[0].replace(".py", "")
    agent_id = str(uuid.uuid4())
    log_path = f"logs/{ script }/{ now }_{ agent_id }.txt"

    log(log_path, "Setting up...\n", log_type, this_filename)

    # Set database
    db_path = os.getenv("DB_PATH")

    # Getting Best Results
    rdb = ResultsDB(db_path)
    best_results = rdb.load_best_results()

    home_path = str(Path.home()) + "/Desktop/swami/prompts/"
    
    # LLM Details
    llm_model = os.getenv('LLM_MODEL')
    llm_base_url = os.getenv('LLM_BASE_URL')

    podcasts_raw = os.getenv("PODCASTS", "[]")
    podcasts = json.loads(podcasts_raw)
    
    return {
        "agent_id": agent_id,
        "log_path": log_path,
        "log_type": log_type,
        "db_path": db_path,
        "best_results": best_results,
        "home_path": home_path,
        "llm_model": llm_model,
        "llm_base_url": llm_base_url,
        "podcasts": podcasts
    }