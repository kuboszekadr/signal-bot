from src.logger import logger

from langchain.agents.output_parsers.tools import parse_ai_message_to_tool_action, ToolsAgentOutputParser
from langchain.agents import AgentExecutor
from langchain_openai import AzureChatOpenAI

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers.openai_tools import PydanticToolsParser

from langgraph.graph.state import StateGraph
from langgraph.graph import END 

from src.models.azure_openai import azure_open_ai_config
from src.logger import logger

from .planner import planner_chain, Plan
from .tools import tools

from pydantic import BaseModel
from typing import Optional

class State(BaseModel):
    """
    State of the agent.
    """
    chat_id: str
    user_request: str
    environment_context: dict = {}
    plan: Plan
    current_step: int = 0
    result: str = ""
    context: str = ""

def plan(state: State) -> str:
    """
    Plans the steps to be taken to answer the user request.
    """
    response = planner_chain.invoke({"user_request": state.user_request})
    return response.content

def execute_plan_step(state: State) -> str:
    """
    Executes the current step of the plan.
    """
    step_executor_prompt_str = """
    You will be provided with environment context. Your task is to prepare tool call based on provided environment variables to be used and tool arguments.

    Tool definition: {tool}
    Environment context: {environment_context}
    User request: {user_request}
"""
    step_executor_prompt = PromptTemplate(
        input_variables=["tool", "environment_context", "user_request"],
        template=step_executor_prompt_str,
    )

    llm = AzureChatOpenAI(**azure_open_ai_config.model_dump())
    tool_name = state.plan.steps[state.current_step].tool_name
    tool = tools[tool_name]

    llm_tool_call = llm.bind_tools(
        tools=[tool], 
        tool_choice=tool_name
        )

    tool_call_chain = (
        step_executor_prompt
        | llm_tool_call
        | ToolsAgentOutputParser()
    )

    tool_call = tool_call_chain.invoke({
        "tool": tool,
        "environment_context": state.environment_context,
        "user_request": state.user_request,
    })
    tool_call = tool_call[0]

    if 'chat_id' in tool_call.tool_input.keys():
        tool_call.tool_input['chat_id'] = state.chat_id
    if 'context' in tool_call.tool_input.keys():
        tool_call.tool_input['context'] = state.context

    results = tool.invoke(tool_call.tool_input)
    context = state.environment_context
    context |= {tool_name: results}

    return {
        'current_step': state.current_step + 1,
        'environment_context': context,
        'result': results,
    }


def should_continue(state: State) -> str:
    """
    Determines if the plan should continue.
    """
    return 'continue' if state.current_step < len(state.plan.steps) else 'end'


def print_stream(stream) -> str:
    message = stream["result"]
    logger.warning(message)
    return message

def invoke(msg: str, chat_id: Optional[str] = "", context: Optional[str] = "") -> str:
    plan = planner_chain.invoke({"user_request": msg})
    logger.warning(plan.model_dump_json())

    environment_context = {}
    if context:
        environment_context = {"chat_history": context}

    state = State(
        chat_id=chat_id,
        user_request=msg,
        plan=plan,
        environment_context=environment_context,
    )

    response = agent.invoke(state, stream_mode="values")
    return print_stream(response)


workflow = StateGraph(State)
workflow.add_node("execute_plan", execute_plan_step)
workflow.add_conditional_edges(
    "execute_plan", 
    should_continue, 
    {
        "continue": "execute_plan",
        "end": END
    }
)

workflow.set_entry_point('execute_plan')
agent = workflow.compile()