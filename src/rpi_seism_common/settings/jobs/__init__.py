from pydantic import BaseModel

from .trigger import Trigger
from .notifier import Notifier
from .writer import Writer
from .reader import Reader
from .ring_server import RingServer


class JobsSettings(BaseModel):
    """Pydantic model for job-related settings."""
    trigger: Trigger
    notifiers: list[Notifier]
    writer: Writer
    reader: Reader
    ring_server: RingServer
