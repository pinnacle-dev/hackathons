from typing import Optional, Union, Literal, TypedDict, Sequence
from pydantic import BaseModel
from rcs import Card, Action


class ButtonPayload(BaseModel):
    """
    Represents the payload data related to the button.

    Attributes:
        title (str): The title of the button.
        payload (str): The payload associated with the button.
        execute (str): The execute command associated with the action.
        sent (str): The timestamp when the message was sent. Format (yyyy-mm-ddThh:mm:ss) in GMT 0
        fromNum (str): The sender's phone number.
    """

    title: Optional[str] = None
    payload: Optional[str] = None
    execute: Optional[str] = None
    sent: str
    fromNum: str


# Types related to crafting a message
MediaType = Union[
    Literal["text"],
    Literal["image"],
    Literal["audio"],
    Literal["video"],
    Literal["file"],
]
"""
MediaType represents the type of media that can be sent in a message.

Attributes:
    text: Represents a text message.
    image: Represents an image message.
    audio: Represents an audio message.
    video: Represents a video message.
    file: Represents a file message.
"""


class MessagePayload(BaseModel):
    """
    Represents the payload data related to the message.

    Attributes:
        text (str): The text of the message.
        mediaType (MediaType): The type of media being sent.
        media (str): The URL of the media being sent.
        sent (str): The timestamp when the message was sent. Format (yyyy-mm-ddThh:mm:ss) in GMT 0
        fromNum (str): The sender's phone number.
    """

    text: Optional[str] = None
    mediaType: Optional[MediaType] = None
    media: Optional[str] = None
    sent: str
    fromNum: str


class PayloadData(BaseModel):
    """
    Represents the payload data received from a message.

    Attributes:
        messageType (str): The type of the message (e.g., "message", "postback").
        buttonPayload (Optional[ButtonPayload]): The payload data related to the button, if applicable.
        messagePayload (Optional[MessagePayload]): The payload data related to the message, if applicable.
    """

    messageType: str
    buttonPayload: Optional[ButtonPayload] = None
    messagePayload: Optional[MessagePayload] = None


class RCSMessage(TypedDict, total=False):
    text: Optional[str]
    media_url: Optional[str]
    cards: Optional[Sequence[Card]]
    quick_replies: Optional[Sequence[Action]]


class RCSCheckResult(TypedDict):
    is_enabled: bool
    standalone_rich_card: bool
    carousel_rich_card: bool
    create_calendar_event_action: bool
    dial_action: bool
    open_url_action: bool
    share_location_action: bool
    view_location_action: bool
