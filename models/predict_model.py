# External Libraries
from typing import Annotated, Sequence

# Models
from models.agent_state_model import AgentState

# LangGraph / LangChain
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

# Data Sources
import pandas as pd

class PredictState(AgentState):
    predict_agent_id: str
    best_results: dict
    aggregates: pd.DataFrame
    upcoming_games: pd.DataFrame
    prediction_set: pd.DataFrame
    predictions: list[dict]
    matchups: dict
    teams: list
    injury_reports: list
    transcriptions: list
    podcast_summaries: list
    week: int
    season: int
    transcription_summary_messages: Annotated[Sequence[BaseMessage], add_messages]
    games: list
    podcasts: dict
    injury_adjustment_tokens: int
    transcription_summary_tokens: int
    final_analysis: list
    game_index: int
    expert_analysis: list[dict]
