# External Libraries
from typing import Annotated, Sequence

# Models
from models.agent_state_model import AgentState

# LangGraph / LangChain
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langchain_nvidia_ai_endpoints import ChatNVIDIA

# Data Sources
from data_sources.DataAggregate import DataAggregate
import pandas as pd

class PredictState(AgentState):
    predict_agent_id: str
    best_results: dict
    aggregates: pd.DataFrame
    upcoming_games: pd.DataFrame
    prediction_set: pd.DataFrame
    predictions: list[dict]