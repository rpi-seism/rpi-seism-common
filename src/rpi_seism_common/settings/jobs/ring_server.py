from pydantic import BaseModel, Field


class RingServer(BaseModel):
    """Configuration for the RingServer DataLink sender job."""

    enabled: bool = Field(
        default=False, description="Enable sending data to ringserver via DataLink"
    )
    host: str = Field(default="localhost", description="Ringserver host address")
    port: int = Field(
        default=16000,
        ge=1,
        le=65535,
        description="Ringserver DataLink port (default 16000)",
    )
    write_interval_sec: float = Field(
        default=1.0,
        gt=0.1,
        le=60,
        description="Interval in seconds to flush buffer and send records",
    )
    reconnect_delay_sec: float = Field(
        default=5.0,
        gt=1.0,
        le=300,
        description="Delay before reconnecting after connection loss",
    )
