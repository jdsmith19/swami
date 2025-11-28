# Models
from models.researcher_model import ResearcherState


def researcher_progressor_node(state: ResearcherState):
    return {
        "expert_analysis": state["expert_analysis"]
    }