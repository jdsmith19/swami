# External Libraries
from typing import TypedDict

class AgentState(TypedDict):
    agent_id: str # Unique identifier for this agent's run
    log_path: str # Path for log files to be saved to
    log_type: str # "file" saves only to file, "all" also prints to stdout
    db_path: str # Path to the database file
    home_path: str
    llm_base_url: str
    llm_model: str