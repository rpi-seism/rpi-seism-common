from pydantic import BaseModel, Field


class Writer(BaseModel):
    """Configuration for the writer job."""
    write_interval_sec: float = Field(
        default=1800, 
        gt=10, 
        le=86400, 
        description="Interval in seconds to flush buffer and rotate files"
    )
