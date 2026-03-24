from pydantic import BaseModel, Field
from datetime import datetime, UTC

from .enums import WebsocketMessageTypeEnum


class WebsocketMessage(BaseModel):
    """Base class for all websocket messages"""
    type: WebsocketMessageTypeEnum
    timestamp: datetime = Field(default_factory=datetime.now(UTC))
