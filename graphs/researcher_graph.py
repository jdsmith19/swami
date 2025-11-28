# External Libraries
# import os

# LangChain + LangGraph Libraries
from langgraph.graph import StateGraph, START, END

# Models
from models.researcher_model import ResearcherState

# Nodes
from nodes.researcher_setup import researcher_setup_node as setup
from nodes.researcher_caller import researcher_caller_node as caller
from nodes.researcher_progressor import researcher_progressor_node as progressor

print("Starting Researcher app...\n")

# INSTANTIATE THE GRAPH PULLING OVER SHARED KEYS FROM OptimizeState
researcher = StateGraph(ResearcherState)
    
def has_cached_analysis(state: ResearcherState):
    if state["expert_analysis"] == []:
        return "not_cached"
    else:
        return "is_cached"

# NODE DEFINITIONS
researcher.add_node("setup", setup)
researcher.add_node("caller", caller)
researcher.add_node("progressor", progressor)

# EDGE DEFINITIONS
researcher.add_edge(START, "setup")
researcher.add_conditional_edges(
    "setup", 
    has_cached_analysis,
    {
        "not_cached": "caller",
        "is_cached": "progressor"
    }
)
researcher.add_edge("caller", "progressor")
researcher.add_edge("progressor", END)

# COMPILE THE GRAPH
researcher_graph = researcher.compile()
researcher_graph.get_graph().draw_mermaid_png(output_file_path="graphs/images/planner_graph.png")