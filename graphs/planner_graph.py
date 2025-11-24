# External Libraries
import os

# LangChain + LangGraph Libraries
from langgraph.graph import StateGraph, START, END

# Models
from models.planner_model import PlannerState
from models.optimize_model import OptimizeState

# Nodes
from nodes.planner_setup import planner_setup_node as setup
from nodes.planner_caller import planner_caller_node as caller
from nodes.planner_validator import planner_validator_node as validator
from nodes.planner_progressor import planner_progressor_node as progressor

print("Starting Planner app...\n")

# INSTANTIATE THE GRAPH PULLING OVER SHARED KEYS FROM OptimizeState
planner = StateGraph(PlannerState)

# CONDITIONAL EDGE DEFINITIONS
def response_is_valid(state: PlannerState) -> PlannerState:
    if state["validated"]:
        return "end"
    return "continue"

# NODE DEFINITIONS
planner.add_node("setup", setup)
planner.add_node("caller", caller)
planner.add_node("validator", validator)
planner.add_node("progressor", progressor)

# EDGE DEFINITIONS
planner.add_edge(START, "setup")
planner.add_edge("setup", "caller")
planner.add_edge("caller", "validator")
planner.add_conditional_edges(
    "validator",
    response_is_valid,
    {
        "continue": "caller",
        "end": "progressor"
    }
)
planner.add_edge("progressor", END)

# COMPILE THE GRAPH
planner_graph = planner.compile()
planner_graph.get_graph().draw_mermaid_png(output_file_path="graphs/images/planner_graph.png")