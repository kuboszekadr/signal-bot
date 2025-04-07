from pydantic import BaseModel
from typing import Optional, List, Union

class GroupInfo(BaseModel):
    groupId: str
    groupName: str
    revision: int
    type: str

class Quote(BaseModel):
    id: int
    author: str
    authorNumber: str
    authorUuid: str
    text: str
    attachments: List[str]

class Sticker(BaseModel):
    packId: str
    stickerId: int

class DataMessage(BaseModel):
    timestamp: int
    message: str
    expiresInSeconds: int
    viewOnce: bool
    groupInfo: Optional[GroupInfo] = None
    quote: Optional[Quote] = None

    def is_ai_call(self):
        return (
            self
            .message.lower()
            .startswith("@bot")
        )

class EditMessage(BaseModel):
    targetSentTimestamp: int
    dataMessage: DataMessage

class SentMessage(BaseModel):
    destination: Optional[str]
    destinationNumber: Optional[str]
    destinationUuid: Optional[str]
    timestamp: int
    message: Optional[str] = ""
    expiresInSeconds: int
    viewOnce: bool
    groupInfo: Optional[GroupInfo] = None
    sticker: Optional[Sticker] = None
    quote: Optional[Quote] = None

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
    sentMessage: Optional[SentMessage] = None

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
    
    def chat_id(self):
        message = self.get_message()
        if message.groupInfo is not None:
            return message.groupInfo.groupId

        if type(message) == SentMessage:
            return message.destinationUuid

        return self.sourceUuid 


class MessageModel(BaseModel):
    envelope: Envelope
    account: str