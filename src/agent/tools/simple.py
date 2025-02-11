from langchain_core.output_parsers import StrOutputParser
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate

from langchain.tools import tool

from src.models.azure_openai import azure_open_ai_config

from typing import Optional

simple_request_prompt_str = """You are a conversational AI assistant. Please respond to the following user message based on the context provided, based on following guidelines:
- make sure to read the context provided,
- provide a response that is relevant to the context,
- if context is not provided, provide a general response that relates to the user message,
- make sure to provide a coherent response if you were not tasked differently,
- make sure to response in the same language as the user message.

Context: {context}
User message: {user_message}
"""

@tool
def simple_request(input: str, context: Optional[str] = None) -> str:
    """
    Sends a simple request to the service and returns the response content.

    Args:
        input (str): The input string to be sent to the Azure OpenAI service.

    Returns:
        str: The content of the response from the Azure OpenAI service.
    """

    simple_request_prompt = ChatPromptTemplate.from_template(simple_request_prompt_str)
    llm = AzureChatOpenAI(**azure_open_ai_config.model_dump())
    
    context = context if context is not None else ""
    simple_request_chain = (
        {'input': input, 'context': context}
        | simple_request_prompt
        | llm
        | StrOutputParser()
    )
    
    response = simple_request_chain.invoke(input)
    return response.content