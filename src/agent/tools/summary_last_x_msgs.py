import os
import glob
import json
import jsonlines


from itertools import groupby
from typing import List, Dict

from langchain_core.tools import tool
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI

from pydantic_settings import BaseSettings

from src.models.signal import Envelope
from src.models.azure_openai import azure_open_ai_config

class ChatConfig(BaseSettings):
    data_path: str

    class Config:
        env_prefix = 'CHAT_'

def load_chat_messages(chat_folder_path: str, n: int) -> List[Dict]:
    """
    Load the latest n chat messages from a specified folder containing JSONL files.
    Args:
        chat_folder_path (str): The path to the folder containing chat message files in JSONL format.
        n (int): The number of latest messages to load.
    Returns:
        List[Dict]: A list of dictionaries representing the latest n chat messages.
    """
    files = glob.glob(chat_folder_path)
    files.sort(key=os.path.getmtime, reverse=True)
    
    messages: List[str] = [''] * n
    count = 0

    # read the latest n messages from the chat
    for file in files:
        with jsonlines.open(file) as reader:
            lines = list(reader)
            for message in reversed(lines):
                if count < n:
                    messages[count] = json.loads(message)
                    count += 1
                else:
                    break
        if count >= n:
            break
    messages = messages
    return messages

def process_chat_messages(chat_messages: List[Dict]) -> List[str]:
    """
    Args:
        chat_messages (List[Dict]): A list of dictionaries where each dictionary represents a chat message.
    Returns:
        List[str]: A list of summarized messages grouped by the source name.
    """
    envelopes_stream = [Envelope(**envelope) for envelope in chat_messages]

    envelopes_stream = sorted(
        envelopes_stream, 
        key=lambda x: x.timestamp, 
        reverse=True
    )

    envelopes_stream_grouped = groupby(
        envelopes_stream, 
        key=lambda x: x.sourceName
    )
    
    envelopes = []
    for _, group in envelopes_stream_grouped:
        messages = [envelope.get_message().message for envelope in group]
        envelopes.append("\n".join(messages))
    
    return envelopes

@tool
def summarize_last_x_msgs(n: int, chat_id: str) -> List[str]:
    """
    Summarizes the last 'n' messages from a chat.

    Args:
        n (int): The number of recent messages to summarize.
        chat_id (str): The chat ID to summarize the messages from.

    Returns:
        List[str]: A list containing the summarized messages.
    """
    llm = AzureChatOpenAI(**azure_open_ai_config.model_dump())
    prompt_template_str = """
You are an AI assistant. Your task is to summarize the messages that comes from the chat. Please follow below requirements:
- make sure to read it carefully before providing an answer,
- make sure to provide a concise summary,
- if in the chat are multiple threads make sure to organize the summary in a logical way, and format your answer using markdown syntax.
- messages may be from different users, you don't have to consider the user who sent the message, just the content of the message,
- make sure to return response in original language.

Messages:
{messages}

Summary:
"""
    n = max(50, n)
    summary_prompt = PromptTemplate(
        template=prompt_template_str,
    )
    output_parser = StrOutputParser()
    summary_chain = (
        summary_prompt
        | llm
        | output_parser
    )

    chat_folder_path = os.path.join(
        ChatConfig().data_path,
        chat_id,
    )
    chat_messages = load_chat_messages(
        chat_folder_path=chat_folder_path,
        n=n)
    summarized_messages = process_chat_messages(chat_messages)

    response = summary_chain.invoke(input={'messages':summarized_messages})
    return response