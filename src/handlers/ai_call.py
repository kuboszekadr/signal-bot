from src.agent.agent_20 import invoke
from src.models.signal import *

from src.config import app_config

def ai_call_handler(message: str, envelope: Envelope):
    llm_input = message.message.replace("@bot", "").strip()
    context = ''
    if message.quote is not None:
        context = message.quote.text

    llm_response = invoke(
        msg=llm_input, 
        chat_id=envelope.chat_id(),
        context=context
    )

    msg = (
        f"[{envelope.sourceName}]\n"
        f"{message.message}\n\n"
        f"[{app_config.bot_name}]\n"
        f"{llm_response}\n"
        f"[{app_config.bot_name}]"
    )
    args = ['--message', msg]
    return args