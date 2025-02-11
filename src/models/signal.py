import jsonlines

from pydantic import BaseModel
from typing import Optional, List, Union

class GroupInfo(BaseModel):
    groupId: str
    groupName: str
    revision: int
    type: str

class DataMessage(BaseModel):
    timestamp: int
    message: str
    expiresInSeconds: int
    viewOnce: bool
    groupInfo: Optional[GroupInfo] = None

    def is_ai_call(self):
        return (
            self
            .message.lower()
            .startswith("@bot")
        )

class EditMessage(BaseModel):
    targetSentTimestamp: int
    dataMessage: DataMessage

class Quota(BaseModel):
    id: int
    author: str
    authorNumber: str
    authorUuid: str
    text: str
    attachments: List[str]

class SentMessage(BaseModel):
    destination: Optional[str]
    destinationNumber: Optional[str]
    destinationUuid: Optional[str]
    timestamp: int
    message: str
    expiresInSeconds: int
    viewOnce: bool
    groupInfo: Optional[GroupInfo] = None
    quote: Optional[Quota] = None

    def is_ai_call(self):
        return (
            self
            .message.lower()
            .startswith("@bot")
        )

class SyncMessage(BaseModel):
    sentMessage: SentMessage

class ReceiptMessage(BaseModel):
    when: int
    isDelivery: bool
    isRead: bool
    isViewed: bool
    timestamps: List[int]

class Envelope(BaseModel):
    source: str
    sourceNumber: Optional[str]
    sourceUuid: str
    sourceName: str
    sourceDevice: int

    timestamp: int
    serverReceivedTimestamp: int
    serverDeliveredTimestamp: int

    reciptMessage: Optional[ReceiptMessage] = None
    editMessage: Optional[EditMessage] = None
    dataMessage: Optional[DataMessage] = None
    syncMessage: Optional[SyncMessage] = None

    def get_message(self) -> Union[DataMessage, SentMessage, None]:
        """Returns DataMessage object from the envelope"""
        msg = None
        if self.dataMessage is not None:
            msg = self.dataMessage
        elif self.editMessage is not None:
            msg = self.editMessage.dataMessage
        elif self.syncMessage is not None:
            msg = self.syncMessage.sentMessage

        return msg


class MessageModel(BaseModel):
    envelope: Envelope
    account: str