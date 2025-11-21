# External Libraries
from typing import TypedDict

class AgentState(TypedDict):
    agent_id: str # Unique identifier for this agent's run
    log_path: str # Path for log files to be saved to
    log_type: str # "file" saves only to file, "all" also prints to stdout