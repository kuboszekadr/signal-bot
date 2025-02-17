from pydantic import BaseModel

from langchain_community.tools import DuckDuckGoSearchResults
from langchain.tools import tool
from langchain.prompts import PromptTemplate

from langchain_openai import AzureChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import StrOutputParser

from src.models.azure_openai import azure_open_ai_config

from typing import List

class SearchQuery(BaseModel):
    user_message: str
    web_search_queries: List[str]

class SearchResult(BaseModel):
    snippet: str
    title: str
    link: str

search = DuckDuckGoSearchResults(output_format='list', max_results=5)
llm = AzureChatOpenAI(**azure_open_ai_config.model_dump())

web_search_prompt_str = """
You will be feed with user message. You are tasked to:
- read it carefully,
- split user message into subparts if the message contains several keypoints or unrelated parts,
- before generating a list of search queries make sure to think step-by-step how to simplify the user message,
- if user message is straightforward you can use it as a search query,

User message: {user_message}
Expected output format: {expected_output_format}
Web search queries:
"""

web_search_summary_prompt_str = """
You will be feed with following informations:
- user message,
- list of search queries,
- search results.

Your task is to:
- read user message, search queries, read search results,
- based on those informations, generate a summary of the search results,
- if you find multiple unrelated queries make sure to separete summary accordingly each query, but if queries seems similar you can combine them into one summary,
- the summary should only contain the most important informations requested by the user, do not put any additional information if that was not required,
- return the summary in user-message original language,
- you dont have to use all search results if you think that they are irrelevant,
- if you decide to use a link to answer the user message, make sure to include the link in the summary.

User message: {user_message}
Search results: {search_results}

Summary:
"""

web_search_queries_parser = PydanticOutputParser(pydantic_object=SearchQuery)
web_search_queries_prompt = PromptTemplate.from_template(
    web_search_prompt_str,
    partial_variables={'expected_output_format': web_search_queries_parser.get_format_instructions()}
)

web_search_chain = (
    web_search_queries_prompt
    | llm
    | web_search_queries_parser
)

web_search_summary_prompt = PromptTemplate.from_template(
    web_search_summary_prompt_str,
)

summary_chain = (
    web_search_summary_prompt
    | llm
    | StrOutputParser()
)

def web_search(query: str) -> List[SearchResult]:
    """
    Perform a web search using the given query and return the search results.

    Args:
        query (str): The search query string.

    Returns:
        SeachResults: An object containing the search results.
    """
    results = search.invoke(query)
    return [SearchResult.model_validate(x) for x in results]


@tool
def web_search_tool(user_msg: str) -> str:
    """
    Perform a web search using the given query and return the search results.

    Args:
        query (str): The search query string.

    Returns:
        SeachResults: An object containing the search results.
    """

    search_query = web_search_chain.invoke({
        'user_message': user_msg
    })
    web_search_results = []
    for query in search_query.web_search_queries:
        web_search_results.extend(web_search(query))

    search_summary = summary_chain.invoke({
        'user_message': user_msg,
        # 'web_search_queries': search_query.web_search_queries,
        'search_results': web_search_results
    })
    return search_summary