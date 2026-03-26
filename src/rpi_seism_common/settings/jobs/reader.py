from pydantic import BaseModel, Field


class Reader(BaseModel):
    """Configuration for the reader job."""
    port: str = Field(
        default="/dev/ttyUSB0",
        description="The serial device path (e.g., /dev/ttyAMA0 or COM3)"
    )
    baudrate: int = Field(
        default=250000,
        ge=9600,
        le=2000000,
        description="Bits per second for the UART interface"
    )
