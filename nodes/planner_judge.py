# External Libraries
import os

# LangGraph / LangChain
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Models
from models.planner_model import PlannerState

# Utilities
from utils.logger import log
from utils.messages import get_message_from_llm_response
from utils.prompts import load_prompt

this_filename = os.path.basename(__file__).replace(".py","")

def planner_judge_node(state: PlannerState) -> PlannerState:
    log(state["log_path"], "Judging the agent's response", state["log_type"], this_filename)
    llm = ChatNVIDIA(
        base_url = state["llm_base_url"], 
        api_key = "not-needed",
        model = state["llm_model"],
        max_tokens = 4096
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
        trimmed_results = state["trimmed_results"]
    )

    messages = [SystemMessage(content = system_prompt), HumanMessage(content = state["messages"][-1].content)]
    
    response = llm.invoke(
        messages
    )
    
    caller_messages = state["messages"]
    caller_messages.append(HumanMessage(content = response.content))
    log(state["log_path"], f"CONTENT:\n{ response.content }", "file", this_filename)
    log(state["log_path"], f"REASONING:\n{ response.response_metadata.get("reasoning") }", "file", this_filename)

    return {
        "llm_response": response,
        "last_message": response.content,
        "messages": caller_messages,
        "tokens": response.response_metadata["token_usage"]["total_tokens"],
        "reasoning": response.response_metadata.get("reasoning"),
        "judged": True
    }