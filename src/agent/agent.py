from langgraph.prebuilt import create_react_agent
from langchain_community.agent_toolkits.load_tools import load_tools

from langchain_openai import AzureChatOpenAI

from src.models.azure_openai import azure_open_ai_config
from src.logger import logger

from .tools.summary_last_x_msgs import summarize_last_x_msgs
from .tools.simple import simple_request
from .tools.web_search import web_search_tool
from .tools.date import get_current_date, add_days

from typing import Optional

tool_selection_prompt_str = (
    """You will be provided with a user request, chat_id and context. Based on the user request, select the appropriate tool(s) to use.
    
    Available tools:
    - summarize_last_x_msgs: Summarizes the last X messages.
    - simple_request: direct asnwer to user provided content, should be used as last-resort if no other tool is applicable.
    - web_search_tool: searches the web for the user request, you should use it if you think that answering the message requires external information or in case that you are not able to answer the user request directly.
    - get_current_date: returns current date in YYYY-MM-DD format, you should use it if user request contains references to current date.
    - add_days: performs simple date arithmetic, adding or subtracting days from a given date. If you use this tool, make sure to provide the date for which you are providing the answer.
    - openweather: provides weather information for a given location at a given date.
    
    Chat_id: {chat_id}
    Context: {context}

    Please note that user may ask request in multiple languages, so make sure to return your response in the request language.
    """
)

azure_open_ai_config.deployment_name = 'gpt-4o-researcher'  # FIXME
llm = AzureChatOpenAI(**azure_open_ai_config.model_dump())

openweather_tool = load_tools(["openweathermap-api"])
tools = [
    summarize_last_x_msgs,
    simple_request,
    web_search_tool,
    get_current_date,
    add_days
] + openweather_tool

def print_stream(stream) -> str:
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            logger.warning(message)
        else:
            logger.warning(message.content)
    return message

def invoke(msg: str, chat_id: Optional[str] = "", context: Optional[str] = "") -> str:
    """
    Invokes the agent with the provided input and returns the response content. 
    If no chat ID is provided, only LLM will be invoked without a chat ID.

    Args:
        input (str): The input string to be sent to the agent.
        chat_id (str): The chat ID to send the input to.
        context (str): The context of the input.

    Returns:
        str: The content of the response from the agent.
    """

    if chat_id == "":
        return llm.invoke(msg)

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=tool_selection_prompt_str.format(
            chat_id=chat_id,
            context=context
        ),
    )

    inputs = {
        "messages": [("user", msg)],
        "chat_id": chat_id,
        "context": context,
        }

    response = agent.stream(inputs, stream_mode="values")
    return print_stream(response)