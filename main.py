import json
import jsonlines
import os

from pydantic import ValidationError
from datetime import datetime as dt

from src.config import app_config
from src.handlers.ai_call import ai_call_handler
from src.handlers.command import command_call_handler

from src.models.signal import *
from src.models.db import local_session, Chat

from src.signal_cli_api import ReceiveProcess, SendMessage
from src.logger import logger


def save_envelope(envelope: Envelope):
    file_path = os.path.join(
        app_config.envelopes_path,
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
    session.close()

def dump_stream(line):
    folder_name = dt.now().strftime("%Y-%m-%d")
    file_path = os.path.join(
        app_config.stream_path,
        f'{folder_name}.jsonl'
    )

    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with jsonlines.open(file_path, 'a') as writer:
        writer.write(line)

def monitor_incoming_msgs():
    receive_process = ReceiveProcess().start_receive_process()
    while True:
        for line in iter(receive_process.stdout.readline, ''):
            logger.info(line)
            dump_stream(line)

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
            
            if message.get_handler() == HandlerType.NONE:
                continue

            logger.info("AI call:\t %s", message.message)
            # signal cli limitation - you can only have one process running at a time
            # TODO: maybe this can be fixed by using d-bus?
            receive_process.kill()

            switcher = {
                HandlerType.BOT: ai_call_handler,
                #OSTROŻNIE
                HandlerType.COMMAND: command_call_handler,
            }
            handler = switcher.get(message.get_handler())
            
            msg_args = handler(message, envelope)
            for args in msg_args:
                if message.groupInfo is None:
                    args.insert(0, envelope.chat_id())
                else:
                    #FIXME
                    tmp = ['--group-id', message.groupInfo.groupId]
                    tmp.extend(args)
                    args = tmp

                SendMessage().send_message(
                    params=args
                )
            receive_process = ReceiveProcess().start_receive_process()

monitor_incoming_msgs()