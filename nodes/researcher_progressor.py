# Models
from models.researcher_model import ResearcherState


def researcher_progressor_node(state: ResearcherState):
    print(state["expert_analysis"])
    return {}