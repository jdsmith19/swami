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
from nodes.predict_injury_reporter import predict_injury_reporter_node as injury_reporter
from nodes.predict_transcriber import predict_transcriber_node as transcriber
from nodes.predict_transcription_summarizer import predict_transcription_summarizer_node as transcription_summarizer

print("Starting Predictor app...\n")

# INSTANTIATE THE GRAPH PULLING OVER SHARED KEYS FROM OptimizeState
predict = StateGraph(PredictState)


# NODE DEFINITIONS
predict.add_node("setup", setup)
predict.add_node("aggregate_loader", aggregate_loader)
predict.add_node("predictor", predictor)
predict.add_node("injury_reporter", injury_reporter)
predict.add_node("transcriber", transcriber)
predict.add_node("transcription_summarizer", transcription_summarizer)

# EDGE DEFINITIONS
# START
predict.add_edge(START, "setup")

# LEVEL 1
predict.add_edge("setup", "aggregate_loader")

# LEVEL 3
predict.add_edge("aggregate_loader", "predictor")
predict.add_edge("aggregate_loader", "injury_reporter")
predict.add_edge("aggregate_loader", "transcriber")

# LEVEL 4
predict.add_edge("transcriber", "transcription_summarizer")

predict.add_edge("transcription_summarizer", END)
predict.add_edge("injury_reporter", END)
predict.add_edge("predictor", END)

# COMPILE THE GRAPH
predict_graph = predict.compile()
predict_graph.get_graph().draw_mermaid_png(output_file_path="graphs/images/predict_graph.png")