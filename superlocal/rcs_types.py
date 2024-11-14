from typing_extensions import Optional, Union, List, Literal, TypedDict, Sequence
from pydantic import BaseModel, Field
from rcs import Card, Action


class SenderMetadata(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None


class MessageMetadata(BaseModel):
    timestamp: str


InboundMessageType = Union[
    Literal["text"],
    Literal["media"],
    Literal["action"],
    Literal["location"],
]


class InboundMessageBase(BaseModel):
    from_: str = Field(..., alias="from")
    to: str
    messageType: InboundMessageType
    metadata: Optional[dict] = None


class InboundTextMessage(InboundMessageBase):
    messageType: Literal["text"]
    text: str


class MediaPayload(BaseModel):
    type: str
    url: str


class InboundMediaMessage(InboundMessageBase):
    messageType: Literal["media"]
    text: Optional[str] = None
    mediaUrls: List[MediaPayload]


class InboundActionMessage(InboundMessageBase):
    messageType: Literal["action"]
    actionTitle: str
    payload: Optional[str] = None
    actionMetadata: Optional[str] = None


class Coordinates(TypedDict):
    lat: float
    lng: float


class InboundLocationMessage(InboundMessageBase):
    messageType: Literal["location"]
    coordinates: Coordinates


InboundMessage = Union[
    InboundTextMessage,
    InboundMediaMessage,
    InboundActionMessage,
    InboundLocationMessage,
]


class RCSMessage(TypedDict, total=False):
    text: Optional[str]
    media_url: Optional[str]
    cards: Optional[Sequence[Card]]
    quick_replies: Optional[Sequence[Action]]
