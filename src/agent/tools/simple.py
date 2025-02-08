from langchain_openai import AzureChatOpenAI

from langchain.tools import tool

from src.models.azure_openai import azure_open_ai_config

@tool
def simple_request(input: str) -> str:
    """
    Sends a simple request to the service and returns the response content.

    Args:
        input (str): The input string to be sent to the Azure OpenAI service.

    Returns:
        str: The content of the response from the Azure OpenAI service.
    """
    llm = AzureChatOpenAI(**azure_open_ai_config.model_dump())
    response = llm.invoke(input)
    return response.content