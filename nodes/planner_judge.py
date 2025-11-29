# External Libraries
import os
import sqlite3
import json

# LangGraph / LangChain
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.agents import create_agent
from langchain.tools import tool

# Models
from models.planner_model import PlannerState

# Utilities
from utils.logger import log
from utils.prompts import load_prompt
from utils.features import get_extended_features, calculate_feature_effects

this_filename = os.path.basename(__file__).replace(".py","")
db_path = None
agent_id = None

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

def query_database(query, db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    result = cur.execute(query)
    rows = result.fetchall()
    conn.close()
    if not rows:
        rows = "No experiments run yet"
    return rows

@tool
def get_best_experiments(
    n: int
):
    """Returns the best "n" experiment results for each model type."""
    print(f"Agent is requesting { n } best experiments.")
    with open("queries/get_top_n_experiments.sql") as f:
        query = f.read()
    query = query.format(
        agent_id = f"\"{ agent_id }\"",
        n = n
    )
    result = query_database(query, db_path)
    return result

@tool
def get_recent_experiments(
    n: int
):
    """Returns the last "n" experiment results."""
    print(f"Agent is requesting last { n } experiments.")
    with open("queries/get_n_recent_experiments.sql") as f:
        query = f.read()
    query = query.format(
        agent_id = f"\"{ agent_id }\"",
        n = n
    )
    result = query_database(query, db_path)
    return result

@tool
def get_experiments_with_feature(
    feature: str
):
    """Returns last 25 experiments run that DO contain a specific feature."""
    print(f"Agent is requesting experiments with feature: { feature }")
    with open("queries/get_experiments_by_feature.sql") as f:
        query = f.read()
    query = query.format(
        agent_id = f"\"{ agent_id }\"",
        feature = f"\"%{ feature }%\""
    )
    result = query_database(query, db_path)
    return result

@tool
def get_experiments_without_feature(
    feature: str
):
    """Returns last 25 experiments run that DO NOT contain a specific feature."""
    print(f"Agent is requesting experiments without feature: { feature }")
    with open("queries/get_experiments_without_feature.sql") as f:
        query = f.read()
    query = query.format(
        agent_id = f"\"{ agent_id }\"",
        feature = f"\"%{ feature }%\""
    )
    result = query_database(query, db_path)
    return result

@tool 
def get_feature_usage():
    """Returns a dictionary of all features and how many experiments have contained them."""
    print(f"Agent is requesting feature usage data")
    with open("queries/get_feature_usage.sql") as f:
        query = f.read()
    query = query.format(
        agent_id = f"\"{ agent_id }\""
    )
    result = query_database(query, db_path)

    usage = {}
    for feature in get_extended_features():
        usage[feature] = {
            'XGBoost': 0,
            'LinearRegression': 0,
            'RandomForest': 0,
            'LogisticRegression': 0,
            'KNearest': 0
        }
        
    result = query_database(query, db_path)
    
    if isinstance(result, str):
        return result
    
    for item in result:
        for feature in json.loads(item['features_used']):
            usage[feature][item['model_name']] += 1
    
    return usage

@tool
def summarize_feature_effects(feature):
    """
        Returns a dictionary of the effects of including or not including a specific feature.
        Provides the average score for each model type.
    """
    print(f"Agent is requesting feature effect summary for { feature }")
    with open("queries/get_experiments_by_feature.sql") as f:
        query_with = f.read()
    query_with = query_with.format(
        agent_id = f"\"{ agent_id }\"",
        feature = f"\"%{ feature }%\""
    )
    with open("queries/get_experiments_without_feature.sql") as f:
        query_without = f.read()
    query_without = query_without.format(
        agent_id = f"\"{ agent_id }\"",
        feature = f"\"%{ feature }%\""
    )

    result_with = query_database(query_with, db_path)
    result_without = query_database(query_without, db_path)
    if isinstance(result_with, str):
        print("No experiments found")
        return f"No experiments found using { feature }"

    effects = calculate_feature_effects(result_with, result_without)

    return effects

def planner_judge_node(state: PlannerState) -> PlannerState:
    global db_path, agent_id
    db_path = state["db_path"]
    agent_id = state["agent_id"]

    log(state["log_path"], "Judging the agent's response", state["log_type"], this_filename)

    temperature = 0.2

    llm = ChatNVIDIA(
        base_url = state["llm_base_url"], 
        api_key = "not-needed",
        model = state["llm_model"],
        max_tokens = 4096,
        temperature = temperature,
        top_p = 1.0
    )

    phase_judge_instructions = [
        "If these conditions are not met, suggest additional experiments or tweaks to restore broad exploration.",
        "If the planner is not doing fine-grained, hypothesis-driven optimization, you should push them toward more targeted ablations and structured comparisons.",
        "If the planner is only tweaking one model, or ignoring cross-model validation, flag this and recommend comparative experiments."
    ]

    system_prompt = load_prompt(
        f"{ state['home_path'] }optimize/planner/judge_system.txt"
    ).format(
        phase_number = state["phase"],
        phase_prompt = load_prompt(f"{ state['home_path'] }optimize/planner/phase_{ state['phase'] }.txt"),
        phase_judge_instructions = phase_judge_instructions[state["phase"] - 2],
    )

    messages = [SystemMessage(content = system_prompt), HumanMessage(content = state["messages"][-1].content)]
    
    agent = create_agent(
    llm,
    tools=[
            get_best_experiments, 
            get_recent_experiments, 
            get_experiments_with_feature, 
            get_experiments_without_feature,
            get_feature_usage,
            summarize_feature_effects
        ],
    )
    
    response = agent.invoke({
        "messages": messages
    })
    
    caller_messages = state["messages"]
    caller_messages.append(HumanMessage(content = response['messages'][-1].content))
    tokens = 0
    total_tokens = state["total_tokens"]
    content = response['messages'][-1].content
    reasoning = response['messages'][-1].response_metadata.get('reasoning')
    for message in response['messages']:
        if message.response_metadata:
            tokens += message.response_metadata['token_usage']['total_tokens']

    total_tokens += tokens

    log(state["log_path"], f"CONTENT:\n{ response['messages'][-1].content }", "file", this_filename)
    log(state["log_path"], f"REASONING:\n{ reasoning }", "file", this_filename)
    log(state["log_path"], f"Tokens used: { tokens }", state["log_type"], this_filename)

    return {
        "llm_response": response,
        "last_message": content,
        "messages": caller_messages,
        "tokens": tokens,
        "reasoning": reasoning,
        "judged": True,
        "total_tokens": total_tokens
    }