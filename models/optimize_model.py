# External Libraries
import pandas as pd

# LangGraph / LangChain
from models.agent_state_model import AgentState
from models.planner_model import PlannerState

from data_sources.DataAggregate import DataAggregate

class OptimizeState(AgentState):
    max_experiments: int # Number of experiments for the agent to run
    experiment_count: int # Current number of experiments run
    experiment_history: list[dict] # List of all experiments run by the agent
    phase: int # The current phase of the optimizer
    best_results: dict # The current set of best results from the optimizer
    prediction_models: list[dict] # List of all available models with name and type
    extended_features: list[str] # List of all extended features including both base and windowed features that can be used for predictions
    historical_results: list
    trimmed_results: dict
    last_results: list # Might want to access these from PlannerState
    next_experiments: list[dict] # Might want to access these from PlannerState
    data_aggregates: DataAggregate
    planner_state: PlannerState
    aggregates: pd.DataFrame
    upcoming_games: pd.DataFrame
    prediction_set: pd.DataFrame
