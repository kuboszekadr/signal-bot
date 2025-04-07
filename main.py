import json
import jsonlines
import os

from pydantic import ValidationError
from datetime import datetime as dt

from src.models.signal import *
from src.models.db import local_session, Chat
from src.handlers import ReceiveProcess, SendMessage
from src.logger import logger

from src.agent.agent import invoke

def save_envelope(envelope: Envelope):
    file_path = os.path.join(
        './data',
        envelope.chat_id(),
        dt.now().strftime("%Y-%m"),
        f'{dt.now().strftime("%Y-%m-%d")}.jsonl'
    )

    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with jsonlines.open(file_path, 'a') as writer:
        writer.write(envelope.model_dump_json())

    message = Chat(
        chat_id=envelope.chat_id(),
        message=envelope.get_message().message,
        envelope=envelope.model_dump()
    )
    session = local_session()
    session.add(message)
    session.commit()

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
            context = ''
            if message.quote is not None:
                context = message.quote.text

            llm_response = invoke(
                msg=llm_input, 
                chat_id=envelope.chat_id(),
                context=context
            ).content

            chat_response = (
                f"[{envelope.sourceName}]\n"
                f"{message.message}\n\n"
                "[AuraBot]\n"
                f"{llm_response}\n"
                "[AuraBot]"
            )

            if message.groupInfo is None:
                args = [envelope.chat_id()]
            else:
                args = ['--group-id', message.groupInfo.groupId]

            SendMessage().send_message(
                msg=chat_response,
                params=args
            )
            receive_process = ReceiveProcess().start_receive_process()

monitor_incoming_msgs()