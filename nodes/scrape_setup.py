# External Libraries
from dotenv import load_dotenv
import os
import datetime
import uuid
import argparse
import sys

# LangChain + LangGraph Libraries
from langchain.agents import AgentState

# Internal Models
from models.scrape_model import ScrapeState

# Utilities
from utils.logger import log

load_dotenv()
this_filename = os.path.basename(__file__).replace(".py","")

def scrape_setup_node(state: ScrapeState) -> ScrapeState:
    # Parse Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", action="store_true", help="load all historical data, if not set only the current season will be loaded")
    parser.add_argument("--debug", action="store_true", help="verbose printing of logs to stdout (not just logfile)")
    args = parser.parse_args()
    
    # All data or just this season?
    if args.history:
        # Get HISTORY_START from .env and create a list from the range of seasons to load
        seasons = list(range(int(os.getenv('HISTORY_START')), (datetime.date.today().year + 1)))
        state["seasons"] = seasons
        print(state["seasons"])
    else:
        # Get current year from datetime
        state["seasons"] = [datetime.date.today().year]
    
    # Print logs to console?
    if args.debug:
        state["log_type"] = "all"
    else:
        state["log_type"] = "file"

    # Generate log_file name
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    script = sys.argv[0].replace(".py", "")
    state["agent_id"] = uuid.uuid4()
    state["log_path"] = f"logs/{ script }/{ now }_{ state["agent_id"] }.txt"

    log(state["log_path"], "Setting up...\n", state["log_type"], this_filename)

    # Set database
    state["db_path"] = os.getenv("DB_PATH")
    
    return state