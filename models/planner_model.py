# External Libraries
from typing import Annotated, Sequence

# Models
from models.agent_state_model import AgentState

# LangGraph / LangChain
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langchain_nvidia_ai_endpoints import ChatNVIDIA

class PlannerState(AgentState):
    planner_agent_id: str
    # annotates the 'messages' list with the 'add_messages' reducer.
    messages: list[BaseMessage]
    last_message: BaseMessage
    llm_response: BaseMessage
    validated: bool
    start: float
    end: float
    next_experiments: list[dict]
    trimmed_results: dict
    best_results: dict
    max_experiments: int
    experiment_count: int
    system_prompt: str
    initial_prompt: str
    phase: int
    failed_validation_count: int
    commentary: str
    tokens: int
    reasoning: str
    skip_validation: bool
    judged: bool
    # DEBUG
    confirmed_append: bool