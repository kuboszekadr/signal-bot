from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from pydantic import BaseModel, Field
from typing import List

from src.models.azure_openai import azure_open_ai_config

planner_prompt_str = """
You will be provided with a user request. Based on the user request, prepare the plan, how to respond to the use and which tools you should use to answer it. You are allowed to use multiple tools if needed.

## Available tools:
Here you can find list of tools with general description of their functionality. You can use them to answer the user request.
- summarize_last_x_msgs: Summarizes the last X messages.
- simple_request: direct asnwer to user provided content, should be used as last-resort if no other tool is applicable.
- web_search_tool: searches the web for the user request, you should use it if you think that answering the message requires external information or in case that you are not able to answer the user request directly.
- get_current_date: returns current date in YYYY-MM-DD format, you should use it if user request contains references to current date.
- add_days: performs simple date arithmetic, adding or subtracting days from a given date. If you use this tool, make sure to provide the date for which you are providing the answer.
- openweather: provides weather information for a given location at a given date.

## General instructions:
- User may ask request in multiple languages, so make sure to return your response in the request language.
- If user requests in language different from English first translate the request to English and then prepare the plan but remember that at the end to translate back into request language.
- For web-search you should **always** use original user request since it may contains regional informations that you be missing after translation.
- You are allowed to use multiple tools if needed.
- Prepare the step by step plan, how to respond to the user request.
- If you are not able to answer the user request directly, you should respond with "I don't know how to answer this question" but in request-language.
- Think step by step when preparing the plan.
- **Remember that the order plan matters.**

## User request:
{user_request}

## Expected output:
{plan_format} 

## Results
"""

class Step(BaseModel):
    """
    A single step in the plan.
    """
    tool_name: str
    reason: str
    step_number: int

class Plan(BaseModel):
    """
    Ordered list of steps to be taken to answer the user request.
    """
    steps: List[Step]

plan_parser = PydanticOutputParser(pydantic_object=Plan)

planner_prompt = PromptTemplate(
    input_variables=["user_request"],
    template=planner_prompt_str,
    partial_variables={
        "plan_format": plan_parser.get_format_instructions(),
    },
)

llm = AzureChatOpenAI(**azure_open_ai_config.model_dump())

planner_chain = (
    planner_prompt
    | llm
    | plan_parser
)