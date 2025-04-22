from src.models.signal import *
from src.models.db import local_session, Chat
from src.handlers.predef.sticker_report import sticker_report

def command_call_handler(message: str, envelope: Envelope):
    chat_id = envelope.chat_id()

    query = sticker_report(chat_id)
    session = local_session()
    result = session.execute(query).fetchall()
    session.close()
    result = [
        {
            'packId': row[0],
            'stickerId': row[1],
            'cnt': row[2]
        }
        for row in result
    ]
    result = sorted(result, key=lambda x: x['cnt'], reverse=True)
    result = result[:10]

    response = f"Top 10 stickers in chat:\n"
    response += "StickerId | Count\n"
    response += "--------- | ------\n"
    
    stickers = []
    for i, row in enumerate(result):
        response += f"{row['stickerId'].ljust(9)} | Count: {row['cnt'].ljust(4)}\n"
        stickers.append(f"{row['packId']}:{row['stickerId']}")
    
    args = [
        ['--message', response],
    ]
    for sticker in stickers:
        args.append(['--sticker', sticker][:3])

    return args