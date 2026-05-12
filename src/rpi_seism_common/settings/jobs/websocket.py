from pydantic import BaseModel, Field


class Websocket(BaseModel):
    enabled: bool = Field(
        default=True, description="Whether to enable or not websocket streaming"
    )

    decimation_factor: int = Field(
        default=4,
        gt=0,
        description="Factor by which to decimate the data stream (Hz)",
    )

    host: str = Field(
        default="127.0.0.1", description="The host address for the websocket server"
    )

    port: int = Field(
        default=8765, ge=1, le=65535, description="The port to connect to"
    )

    @property
    def url(self) -> str:
        """Helper to construct the full websocket URL."""
        return f"ws://{self.host}:{self.port}{self.path}"
