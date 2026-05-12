from pydantic import BaseModel

from .bookmark_generator import BookmarkGenerator
from .dayplot import Dayplot
from .notifier import Notifier
from .reader import Reader
from .ring_server import RingServer
from .trigger import Trigger
from .websocket import Websocket
from .writer import Writer


class JobsSettings(BaseModel):
    """Pydantic model for job-related settings."""

    trigger: Trigger
    notifiers: list[Notifier]
    writer: Writer
    reader: Reader
    ring_server: RingServer
    dayplot: Dayplot
    bookmark_generator: BookmarkGenerator
    websocket: Websocket
