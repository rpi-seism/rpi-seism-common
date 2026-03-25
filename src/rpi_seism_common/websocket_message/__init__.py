from pydantic import BaseModel, Field
from datetime import datetime, UTC

from .enums import WebsocketMessageTypeEnum


class WebsocketMessage(BaseModel):
    """Base class for all websocket messages"""
    type: WebsocketMessageTypeEnum
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def to_json(self):
        return self.model_dump_json()
