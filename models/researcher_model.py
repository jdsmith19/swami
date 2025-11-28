# External Libraries
from typing import Annotated, Sequence

# Models
from models.predict_model import PredictState

class ResearcherState(PredictState):
    research_agent_id: str
    expert_analysis: list[dict]