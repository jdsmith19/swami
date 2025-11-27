# LangGraph / LangChain
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage

def get_message_from_llm_response(response):
    if response.type == 'system':
        message = (SystemMessage(content=response.content))
    elif response.type == 'human':
        message = (HumanMessage(content=response.content))
    elif response.type == 'ai':
        if getattr(response, "tool_calls", None) and not response.content:
            message = (
                AIMessage(
                    content="Calling tools with the specified arguments.",
                    tool_calls=message.tool_calls,
                )
            )
        else:
            message = (
                AIMessage(
                    content=response.content
                )
            )
    elif response.type == 'tool':
        message = (
            ToolMessage(
                content=response.content,
                tool_call_id=response.tool_call_id
            )
        )
    print(message)
    return message