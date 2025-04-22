from sqlalchemy import func, select, text

from src.models.db import Chat


def sticker_report(chat_id: str, top_n: int = 10):
    """
    This function generates a report of sticker usage in a specific chat.
    It extracts the packId and stickerId from the JSON envelope of the Chat model,
    counts the occurrences of each sticker, and orders the results by count in descending order.
    """

    cte = (
        select(
            func.json_extract(Chat.envelope, '$.dataMessage.sticker.packId').label('packId'),
            func.json_extract(Chat.envelope, '$.dataMessage.sticker.stickerId').label('stickerId')
        )
        .where(
            Chat.chat_id == chat_id,
            func.json_extract(Chat.envelope, '$.dataMessage.sticker').isnot(None)
        )
        .cte('cte')
    )

    query = (
        select(
            cte.c.packId,
            cte.c.stickerId,
            func.count(1).label('cnt')
        )
        .select_from(cte)
        .group_by(
            cte.c.packId,
            cte.c.stickerId
        )
        .order_by(text('cnt DESC')) 
    )
    return query
