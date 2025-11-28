# External Libraries
import uuid
import json
from pathlib import Path
import os

# Models
from models.researcher_model import ResearcherState

# Utilities
from utils.logger import log

# Initialize global variables
this_filename = os.path.basename(__file__).replace(".py","")
log_path = None
log_type = None
db_path = None

def researcher_setup_node(state: ResearcherState):
    global log_path, log_type
    log_path = state["log_path"]
    log_type = state["log_type"]
    
    researcher_agent_id = str(uuid.uuid4())
    season = state["season"]
    season_week = state["week"]
    file_path = f"cache/perplexity/expert_{ season }_week_{ season_week }.json"
    path = Path(file_path)
    expert_analysis = []
    if path.exists:
        try:
            expert_analysis = json.load(file_path)
        except:
            log(log_path, "Cached research file is not valid JSON", log_type, this_filename)
    
    return {
        "researcher_agent_id": researcher_agent_id,
        "expert_analysis": expert_analysis
    }
