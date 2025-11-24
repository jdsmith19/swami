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

print("Starting Predictor app...\n")

# INSTANTIATE THE GRAPH PULLING OVER SHARED KEYS FROM OptimizeState
predict = StateGraph(PredictState)


# NODE DEFINITIONS
predict.add_node("setup", setup)
predict.add_node("aggregate_loader", aggregate_loader)
predict.add_node("predictor", predictor)

# EDGE DEFINITIONS
predict.add_edge(START, "setup")
predict.add_edge("setup", "aggregate_loader")
predict.add_edge("aggregate_loader", "predictor")
predict.add_edge("predictor", END)

# COMPILE THE GRAPH
predict_graph = predict.compile()