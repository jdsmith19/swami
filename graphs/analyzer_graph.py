# External Libraries
# import os

# LangChain + LangGraph Libraries
from langgraph.graph import StateGraph, START, END

# Models
from models.analyzer_model import AnalyzerState

# Nodes
from nodes.analyzer_setup import analyzer_setup_node as setup
from nodes.analyzer_caller import analyzer_caller_node as caller
from nodes.analyzer_progressor import analyzer_progressor_node as progressor
from nodes.analyzer_validator import analyzer_validator_node as validator

print("Starting Analyzer app...\n")

# INSTANTIATE THE GRAPH PULLING OVER SHARED KEYS FROM OptimizeState
analyzer = StateGraph(AnalyzerState)

# CONDITIONAL EDGE DEFINITIONS
def analyzed_all_games(state: AnalyzerState) -> AnalyzerState:
    if state["game_index"] >= len(state["games"]) - 1:
        print(state["final_analysis"])
        print(f"Tokens Used: { state["tokens"] }")
        return "end"
    print(f"Turn: { state["game_index"] + 1 }")
    return "continue"

def is_validated(state: AnalyzerState) -> AnalyzerState:
    if state["validated"] == True:
        return "end"
    return "continue"
    
# NODE DEFINITIONS
analyzer.add_node("setup", setup)
analyzer.add_node("caller", caller)
analyzer.add_node("validator", validator)
analyzer.add_node("progressor", progressor)

# EDGE DEFINITIONS
analyzer.add_edge(START, "setup")
analyzer.add_edge("setup", "caller")
#analyzer.add_edge('caller', "progressor")
analyzer.add_edge("caller", "validator")
analyzer.add_conditional_edges(
    "progressor",
    analyzed_all_games,
    {
        "continue": "caller",
        "end": END
    }
)
analyzer.add_conditional_edges(
    "validator",
    is_validated,
    {
        "continue": "caller",
        "end": "progressor"
    }
)

# COMPILE THE GRAPH
analyzer_graph = analyzer.compile()
analyzer_graph.get_graph().draw_mermaid_png(output_file_path="graphs/images/planner_graph.png")