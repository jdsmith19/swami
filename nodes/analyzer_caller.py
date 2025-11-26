# 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
# External Libraries
import os
import sqlite3
import json
import uuid

# LangGraph / LangChain
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain.tools import tool
from langchain.agents import create_agent

# Models
from models.analyzer_model import AnalyzerState

# Utilities
from utils.logger import log
from utils.nfl import teams
from utils.prompts import load_prompt

this_filename = os.path.basename(__file__).replace(".py","")
db_path = None

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

def get_team_lookup_string(matchup):
    teams_list = matchup.split(" @ ")
    lookup_string = ""
    for team in teams_list:
        lookup_string += f"{ team }: { teams.odds_api_team_to_pfr_team(team)}\n"
    return lookup_string

@tool
def run_select_query(sql: str):
    """Runs a READ ONLY SELECT query on the local SQLITE DB and returns rows as JSON"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = dict_factory
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        conn.close()
        rows_for_agent = []
        for row in rows:
            rows_for_agent.append(row)
        return json.dumps({
                "row_count": len(rows_for_agent),
                "rows": rows_for_agent
        }, default=str)
    except sqlite3.OperationalError as e:
        return json.dumps({
            "error": "sqlite_operational_error",
            "message": str(e),
            "sql": sql,
            "hint": "Check column names, table names, or JOIN aliases."
        })


def analyzer_caller_node(state: AnalyzerState) -> AnalyzerState:
    global db_path
    db_path = state["db_path"]
    llm = ChatNVIDIA(
    #llm = ChatOpenAI(
        base_url = state["llm_base_url"], 
        api_key = "not-needed",
        #api_key = "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",
        model = state["llm_model"],
        #model = "gpt-5.1",
        max_tokens = 4096,
        temperature=0.2
    )

    if not state.get("initial_prompt"):
        initial_prompt = load_prompt(f"{ state['home_path'] }predictor/analyzer/initial.txt").format(
            matchup=state["current_matchup"],
            db_lookup_string=get_team_lookup_string(state["games"][state["game_index"]])
        )
    else:
        initial_prompt = state["initial_prompt"]
    
    if not state.get("system_prompt"):
        system_prompt = load_prompt(f"{ state['home_path'] }predictor/analyzer/system.txt").format(
            best_results=state["best_results"]
        )
    else:
        system_prompt = state["system_prompt"]

    agent = create_agent(
        llm,
        tools=[run_select_query],
    )
    
    if state["failure_count"] == 0:
        print(f"Analyzing { state["games"][state["game_index"]] }")

    response = agent.invoke({
        "messages": state["messages"]
    })
    
    messages = []
    for message in response['messages']:
        if message.type == 'system':
            messages.append(SystemMessage(content=message.content))
        elif message.type == 'human':
            messages.append(HumanMessage(content=message.content))
        elif message.type == 'ai':
            if getattr(message, "tool_calls", None) and not message.content:
                messages.append(
                    AIMessage(
                        content="Calling tools with the specified arguments.",
                        tool_calls=message.tool_calls,
                    )
                )
            else:
                messages.append(AIMessage(
                    content=message.content
                    )
                )
        elif message.type == 'tool':
            messages.append(ToolMessage(
                content=message.content,
                tool_call_id=message.tool_call_id
                )
            )
    
    return {
        "messages": messages
    }