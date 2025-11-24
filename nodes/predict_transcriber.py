#External Libraries
import time
import os
import json

# Models
from models.predict_model import PredictState

# Data Sources
from data_sources.BillSimmonsPodcast import BillSimmonsPodcast

# Utilities
from utils.logger import log

this_filename = os.path.basename(__file__).replace(".py","")

def join_chunks(results):
    chunks = []
    for result in results:
        chunks.append(result['text'])
    return " ".join(chunks)

def predict_transcriber_node(state: PredictState):
    log_path = state["log_path"]
    log_type = state["log_type"]

    transcriptions = []
    bsp = BillSimmonsPodcast(week = state["week"], season = state["season"], podcast="guess_the_lines")
    job_id = bsp.transcribe_episode(episode_type = "guess_the_lines")
    episode_name = bsp.current_episode_name
    
    log(log_path, f"Transcribing { episode_name }", log_type, this_filename)

    # Update progress while waiting
    job_completed = False
    while not job_completed:
        data = bsp.check_job_status(job_id)
        status = bsp.job_status
        if status == "completed":
            job_completed = True
        elif status == "failed":
            log(log_path, (data['error']), log_type, this_filename)
            log(log_path, (data['traceback']), log_type, this_filename)
        time.sleep(5)
    result = bsp.check_job_status(job_id)['result']
    
    transcriptions.append({
        "name": episode_name,
        "chunks": result,
        "full_text": join_chunks(result)
    })
    
    return {
        "transcriptions": transcriptions
    }