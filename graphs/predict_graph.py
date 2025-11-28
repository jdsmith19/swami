# External Libraries
import os

# LangChain + LangGraph Libraries
from langgraph.graph import StateGraph, START, END

# Models
from models.predict_model import PredictState

# Nodes
from nodes.predict_aggregate_loader import predict_aggregate_loader_node as aggregate_loader
from nodes.predict_setup import predict_setup_node as setup
from nodes.predict_predictor import predict_predictor_node as predictor
from nodes.predict_progressor import predictor_progressor_node as progressor
# from nodes.predict_injury_reporter import predict_injury_reporter_node as injury_reporter
# from nodes.predict_transcriber import predict_transcriber_node as transcriber
# from nodes.predict_transcription_summarizer import predict_transcription_summarizer_node as transcription_summarizer
# from nodes.predict_injury_adjuster import predict_injury_adjuster_node as injury_adjuster

# Graphs
from graphs.analyzer_graph import analyzer_graph as analyzer
from graphs.researcher_graph import researcher_graph as researcher

print("Starting Predictor app...\n")

# INSTANTIATE THE GRAPH PULLING OVER SHARED KEYS FROM OptimizeState
predict = StateGraph(PredictState)


# NODE DEFINITIONS
predict.add_node("setup", setup)
predict.add_node("aggregate_loader", aggregate_loader)
predict.add_node("predictor", predictor)
predict.add_node("researcher", researcher)
predict.add_node("analyzer", analyzer)
predict.add_node("progressor", progressor)
#predict.add_node("injury_reporter", injury_reporter)
#predict.add_node("injury_adjuster", injury_adjuster)
#predict.add_node("transcriber", transcriber)
#predict.add_node("transcription_summarizer", transcription_summarizer)

# EDGE DEFINITIONS
# START
predict.add_edge(START, "setup")

# LEVEL 1
predict.add_edge("setup", "aggregate_loader")

# LEVEL 2
predict.add_edge("aggregate_loader", "researcher")
predict.add_edge("aggregate_loader", "predictor")
#predict.add_edge("aggregate_loader", "injury_reporter")
#predict.add_edge("aggregate_loader", "transcriber")

# LEVEL 4
# predict.add_edge("injury_reporter", "injury_adjuster")
# predict.add_edge("transcriber", "transcription_summarizer")

# LEVEL $

# LEVEL 5
predict.add_edge("researcher", "progressor")
predict.add_edge("predictor", "progressor")

# LEVEL 6
predict.add_edge("progressor", "analyzer")

# END
#predict.add_edge("injury_adjuster", END)
#predict.add_edge("transcription_summarizer", END)
#predict.add_edge("injury_reporter", END)
predict.add_edge("analyzer", END)

# COMPILE THE GRAPH
predict_graph = predict.compile()
predict_graph.get_graph(xray=True).draw_mermaid_png(output_file_path="graphs/images/predict_graph.png")