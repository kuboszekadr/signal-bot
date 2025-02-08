import json
import jsonlines
import os

from pydantic import ValidationError
from datetime import datetime as dt

from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from src.models.signal import *
from src.models.azure_openai import azure_open_ai_config
from src.handlers import ReceiveProcess, SendMessage
from src.logger import logger

# simple_request_chain = (
#     {'input': RunnablePassthrough()}
#     | AzureChatOpenAI(**azure_open_ai_config.model_dump())
#     | StrOutputParser()
# )

llm = AzureChatOpenAI(**azure_open_ai_config.model_dump())

def save_envelope(envelope: Envelope):
    file_path = os.path.join(
        './data',
        dt.now().strftime("%Y-%m"),
        f'{dt.now().strftime("%Y-%m-%d")}.jsonl'
    )

    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with jsonlines.open(file_path, 'a') as writer:
        writer.write(envelope.model_dump_json())

def monitor_incoming_msgs():
    receive_process = ReceiveProcess().start_receive_process()
    while True:
        for line in iter(receive_process.stdout.readline, ''):
            logger.info(line)
            try:
                envelope_json = json.loads(line).get('envelope')
                envelope = Envelope(**envelope_json)
            except ValidationError:
                logger.error("Validation error:\t %s", line)
                continue

            message = envelope.get_message()
            if message is None:
                continue

            save_envelope(envelope)
            if not message.is_ai_call():
                continue

            logger.info("AI call:\t %s", message.message)
            receive_process.kill()

            # signal cli limitation - you can only have one process running at a time
            llm_input = message.message.replace("@bot", "").strip()
            llm_response = llm.invoke(llm_input).content

            chat_response = (
                f"[{envelope.sourceName}]\n"
                f"{message.message}\n\n"
                "[AuraBot]\n"
                f"{llm_response}\n"
                "[AuraBot]"
            )
            SendMessage(chat_response).send_message_to_group()
            receive_process = ReceiveProcess().start_receive_process()

monitor_incoming_msgs()