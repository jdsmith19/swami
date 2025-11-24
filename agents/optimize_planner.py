# External Libraries
import os
import uuid
from typing import TypedDict, List
import time
import json

# Pydantic
from pydantic import BaseModel, Field, field_validator, ValidationError

# LangChain / LangGraph
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool
from langchain_core.tools import StructuredTool

# Models
from models.optimize_model import OptimizeState

# Utilities
from utils.features import get_extended_features
from utils.prompts import load_prompt
from utils.logger import log

# Initialize global variables
this_filename = os.path.basename(__file__).replace(".py","")
log_path = None
log_type = None
db_path = None

max_retries = 5

class Experiment(BaseModel):
    """Single experiment configuration"""

    # ... means field is required
    model: str = Field(..., description = "The name of the ML model to use")
    features: list[str] = Field(..., description = "The features to be used")

    @field_validator('model')
    @classmethod
    def validate_model(cls, v):
        if v not in ['XGBoost', 'LinearRegression', 'RandomForest', 'LogisticRegression', 'KNearest']:
            raise ValueError(f"Invalid model: { v }")
        return v
    
    @field_validator('features')
    @classmethod
    def validate_features(cls, v):
        invalid = False
        bad_features = []
        valid = get_extended_features()
        for feat in v:
            if feat not in valid:
                invalid = True
                bad_features.append(feat)
        if invalid:
            raise ValueError(f"Invalid features: { bad_features }")
        return v
        
class ExperimentPlan(BaseModel):
    """Experiment plan configuration"""
    experiments: List[Experiment] = Field(..., description = "A list of 10 experiments to run using the Experiment dictionary format")

    @field_validator('experiments')
    @classmethod
    def validate_experiment_count(cls, v):
        if not len(v) == 10:
            raise ValueError(f"You should be planning 10 experiments, you planned { len(v) }")
        return v

def validate_data(data: str) -> str:
    """Validates that the data is valid JSON and passes schema."""
    log(log_path, "Validating tool call from LLM", log_type, this_filename)
    try:
        obj = json.loads(data)    
    except json.JSONDecodeError as e:
        return {
            "validated": False,
            "details": f"VALIDATION ERROR: The output is not valid JSON. You must enclose keys in double quotes and ensure all syntax is correct. Error details: { e }"
            
        }
        
    try:
        validated_plan = ExperimentPlan.model_validate(obj)
    except ValidationError as e:
        return {
            "validated": False,
            "details": f"VALIDATION ERROR. Review the following error details carefully and try again by generating corrected JSON. DO NOT call this tool again until you have fixed the JSON. Details: \n{e}"
        }
    
    return {
        "validated": True,
        "data": validated_plan.model_dump_json(indent=2)
    }
    #return f"SUCCESS: The data passed validation. The validated plan is:\n{validated_plan.model_dump_json(indent=2)}. Return the validated JSON (AND ONLY THE VALIDATED JSON) as your response."

def log_output(output):
    result = output["result"]
    lines = []
    for i, message in enumerate(result['messages']):
        lines.append(f"\n*** TURN { i + 1 }***")
        if message.response_metadata.get("reasoning"):
            lines.append("\n*** REASONING ***")
            lines.append(f"{ message.response_metadata['reasoning'] }")
        if message.content:
            #content = json.dumps(json.loads(message.content), indent=2)
            lines.append("\n*** RESPONSE ***")
            lines.append(f"{ message.content }")
        if message.response_metadata.get("tool_calls"):
            lines.append("\n*** TOOL CALLS ***")
            for tool_call in message.response_metadata["tool_calls"]:
                lines.append(f"Calling { tool_call["function"]["name"]}")
        #lines.append(f"\nTOTAL TOKENS: { result.response_metadata['token_usage']['total_tokens']}")
        #lines.append(f"\nTIME TO COMPLETE: {['time_to_complete']}s")
    
    log(log_path, "\n".join(lines), log_type, this_filename)

def did_validate(output):
    for message in output['result']['messages']:
        pass

def optimize_planner(state: OptimizeState) -> OptimizeState:    
    # Initialize global variables
    global log_path, log_type, db_path
    log_path = state["log_path"]
    log_type = state["log_type"]
    db_path = state["db_path"]

    # Start a timer
    start = time.time()
    state["agent_id"] = uuid.uuid4()

    lines = []
    lines.append(f"\n{'='*80}")
    lines.append(f"OPTIMIZE PLANNER AGENT")
    lines.append(f"ID: { state["agent_id"] }")
    lines.append(f"{'='*80}")
    log(log_path, "\n".join(lines), log_type, this_filename)

    
    # Create an ID
    thread_config = {"configurable": {"thread_id": f"{ id }"}}
    
    phase_prompt = load_prompt(f"{ state['home_path'] }optimize/planner/phase_{ state['phase'] }.txt")

    system_prompt = load_prompt(f"{ state['home_path'] }optimize/planner/system.txt").format(
        phase = str(state["phase"]),
        phase_instructions = phase_prompt,
        historical_results = state.get("trimmed_results")
    )
    
    initial_prompt = load_prompt(f"{ state['home_path'] }optimize/planner/initial.txt")
    
    llm = ChatNVIDIA(
        base_url = state["llm_base_url"], 
        api_key = "not-needed",
        model = state["llm_model"],
        max_tokens = 4096,        
    )

    validate_data_tool = StructuredTool.from_function(
        func = validate_data,
        name = "validate_data",
        description = "Validates that the data is valid JSON and passes schema.",
        return_direct = True
    )

    checkpointer = InMemorySaver()

    agent = create_agent(
        model = llm,
        system_prompt = system_prompt,
        checkpointer = checkpointer,
        tools = [validate_data_tool]
    ).with_config({"recursion_limit": 5})

    result = agent.invoke(
        input = HumanMessage(content = initial_prompt),
        config = thread_config
    )
    
    end = time.time()

    output = {
        "id": state["agent_id"],
        "result": result,
        "time_to_complete": round(end - start, 2)
    }

    log_output(output)
    state["planner_results"].append(output)
    state["next_experiments"] = json.loads(result["messages"][-1].content)['experiments']
    
    return state