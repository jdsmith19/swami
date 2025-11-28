# External Libraries
import os
import uuid

# Data Sources
from data_sources.ResultsDB import ResultsDB

# Models
from models.optimize_model import OptimizeState

# Utilities
from utils.logger import log
from utils.formatting import formatting

# Initialize global variables
this_filename = os.path.basename(__file__).replace(".py","")
log_path = None
log_type = None
db_path = None

def is_best_result(result, best_results):
    is_best = False

    if result["target"] == "point_differential":
        metric = "mean_absolute_error"
    elif result["target"] == "win":
        metric = "test_accuracy"
    

    for best in best_results:        
        if not result["model_name"] == best["model_name"]:
            continue

        if metric == "mean_absolute_error":
            differential = round(result[metric] - best[metric], 3)
            if result[metric] < best[metric]:
                is_best = True
        elif metric == "test_accuracy":
            differential = round(best[metric] - result[metric], 3)
            if result[metric] > best[metric]:
                is_best = True
        if is_best:
            print(f"🥳 Best result for { result["result"]["model_name"] }: { result[metric] } ({ result["target"]})")
            
        log(log_path, f"Result differential for { result["model_name"] }: { differential }", log_type, this_filename)
    
    return is_best

def set_best_result(result, best_results, features_used, db_path):
    rdb = ResultsDB(db_path)
    rdb.save_best_result(result, features_used)
    new_best_results = []
    for best in best_results:
        if not result["model_name"] == best["model_name"]:
            new_best_results.append(best)
            new_best_results[-1]['features_used'] = features_used
        else:
            result['features_used'] = features_used
            new_best_results.append(result)
    return new_best_results

def optimize_progressor(state: OptimizeState) -> OptimizeState:
    global log_path, log_type, db_path
    log_path = state["log_path"]
    log_type = state["log_type"]
    db_path = state["db_path"]

    # Increment the counts
    num_experiments_run = len(state["last_results"])
    state["experiment_count"] += num_experiments_run
    state["experiment_history"].append(state["next_experiments"])

    id = uuid.uuid4()
    
    # Validate best results
    rdb = ResultsDB(state["db_path"])
    for result in state["last_results"]:
        result["result"]["agent_id"] = state["agent_id"]
        rdb.save_result(result["result"], result["features_used"])
        if is_best_result(result["result"], state["best_results"]):
            state["best_results_found"].append(result["result"])
            state["best_results"] = set_best_result(result["result"], state["best_results"], result["features_used"], state["db_path"])


    # Reset some variables
    state["last_results"] = []
    state["next_experiments"] = []

    #formatted = formatting.format_best_results(state["best_results"], state["prediction_models"])
    #log(log_path, formatted, log_type, this_filename)

    lines = []
    lines.append(f"\n{'='*80}")
    lines.append(f"{ state["experiment_count"] } of { state["max_experiments"] } experiments completed.")
    lines.append(f"Best results updated { len(state["best_results_found"]) } times")
    lines.append(f"{ state["total_error_count"] } validation errors identified")
    lines.append(f"Total tokens so far: { state["total_tokens"]}")
    lines.append(f"{'='*80}\n")

    log(log_path, "\n".join(lines), log_type, this_filename)

    
    if state['experiment_count'] < state["max_experiments"]:
        # Set the phase based on the experiment count
        move_to_phase_2 = (state["experiment_count"] >= (state["max_experiments"] * .2) and state["phase"] == 1)
        move_to_phase_3 = (state["experiment_count"] >= (state["max_experiments"] * .4) and state["experiment_count"] < (state["max_experiments"] * .8) and state["phase"] == 2)
        move_to_phase_4 = (state["experiment_count"] >= (state["max_experiments"] * .8) and state["phase"] == 3)
        if (move_to_phase_2 or move_to_phase_3 or move_to_phase_4):
            state["phase"] = progress_to_next_phase(state["phase"], state["best_results"], state["prediction_models"])
    
    state["trimmed_results"] = state["historical_results"][-100:]
    
    return state
    
def progress_to_next_phase(current_phase, best_results, prediction_models):
    log(log_path, f"Phase { current_phase } complete", log_type, this_filename)
    formatted = formatting.format_best_results(best_results, prediction_models)
    log(log_path, formatted, "file", this_filename)
    return current_phase + 1