# External Libraries
import os

# LangChain + LangGraph Libraries
from langgraph.graph import StateGraph, START, END

# Models
from models.optimize_model import OptimizeState

# Nodes
from nodes.optimize_setup import optimize_setup_node as setup
from nodes.optimize_progressor import optimize_progressor as progressor
from nodes.optimize_trainer import optimize_trainer as trainer

# Graphs
from graphs.planner_graph import planner_graph as planner

# Utils
from utils.formatting import formatting
from utils.logger import log

# Data Sources
from data_sources.ResultsDB import ResultsDB

# Set variables that will need to be accessed
this_filename = os.path.basename(__file__).replace(".py","")
log_path = None
log_type = None
db_path = None

print("Starting Optimize app...\n")

# INSTANTIATE THE GRAPH
graph = StateGraph(OptimizeState)

# CONDITIONAL EDGE DEFINITIONS
def is_optimization_complete(state: OptimizeState) -> OptimizeState:
    if state["experiment_count"] >= state["max_experiments"]:
        formatted = formatting.format_best_results(state["best_results"], state['prediction_models'])
        log(state["log_path"], formatted, state["log_type"], this_filename)
        rdb = ResultsDB(state["db_path"])
        rdb.set_agent_completion(state["agent_id"])
        return "end"
    return "continue"

# NODE DEFINITIONS
graph.add_node("setup", setup)
graph.add_node("planner", planner)
graph.add_node("progressor", progressor)
graph.add_node("trainer", trainer)

# EDGE DEFINITIONS
graph.add_edge(START, "setup")
graph.add_edge("setup", "planner")
graph.add_edge("planner", "trainer")
graph.add_edge("trainer", "progressor")
graph.add_conditional_edges(
    "progressor",
    is_optimization_complete,
    {
        "continue": "planner",
        "end": END
    }
)

# COMPILE THE GRAPH
app = graph.compile()