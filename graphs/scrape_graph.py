# LangChain + LangGraph Libraries
from langgraph.graph import StateGraph, START, END

# Models
from models.scrape_model import ScrapeState

# Nodes
from nodes.scrape_setup import scrape_setup_node as setup
from nodes.load_history_from_pfr import load_history_from_pfr as load

print("Starting app...\n")

# INSTANTIATE THE GRAPH
graph = StateGraph(ScrapeState)

# NODE DEFINITIONS
graph.add_node("setup", setup)
graph.add_node("load", load)

# EDGE DEFINITIONS
graph.add_edge(START, "setup")
graph.add_edge("setup", "load")
graph.add_edge("load", END)

# COMPILE THE GRAPH
app = graph.compile()
app.get_graph().draw_mermaid_png(output_file_path="graphs/images/scrape_graph.png")