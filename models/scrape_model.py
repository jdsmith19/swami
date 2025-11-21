# External Libraries
from models.agent_state_model import AgentState

class ScrapeState(AgentState):
    seasons: list[int] # Seasons to be scraped from Pro Football Reference
    db_path: str # Path to the database file