from enum import Enum


class WebsocketMessageTypeEnum(Enum):
    """WebsocketMessage Type Enum"""
    DATA = 0,
    STATE_OF_HEALTH = 1
