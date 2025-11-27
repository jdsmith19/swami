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
from nodes.planner_judge import planner_judge_node as judge

print("Starting Planner app...\n")

# INSTANTIATE THE GRAPH PULLING OVER SHARED KEYS FROM OptimizeState
planner = StateGraph(PlannerState)

# CONDITIONAL EDGE DEFINITIONS

def valid_and_judged(state: PlannerState):
    if (state["validated"] and state["judged"]) or (state["validated"] and state["phase"] == 1):
        return "progress"
    elif state["validated"] and state["phase"] > 1:
        return "judgment_day"
    elif not state["validated"]:
        return "retry"

def response_is_valid(state: PlannerState) -> PlannerState:
    if state["validated"]:
        return True
    return False

def has_been_judged(state: PlannerState):
    if state["judged"]:
        return True
    return "continue"

# NODE DEFINITIONS
planner.add_node("setup", setup)
planner.add_node("caller", caller)
planner.add_node("validator", validator)
planner.add_node("judge", judge)
planner.add_node("progressor", progressor)

# EDGE DEFINITIONS
planner.add_edge(START, "setup")
planner.add_edge("setup", "caller")
planner.add_edge("caller", "validator")
planner.add_conditional_edges(
    "validator",
    valid_and_judged,
    {
        "progress": "progressor",
        "judgment_day": "judge",
        "retry": "caller"
    }
)
planner.add_edge("judge", "caller")
planner.add_edge("progressor", END)

# COMPILE THE GRAPH
planner_graph = planner.compile()
planner_graph.get_graph().draw_mermaid_png(output_file_path="graphs/images/planner_graph.png")