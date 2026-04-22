from pydantic import BaseModel, Field


class Dayplot(BaseModel):
    enabled: bool = Field(
        default=True, description="Whether to generate daily drum plots"
    )

    low_cutoff: float = Field(
        default=0.1,
        gt=0,
        description="Lower frequency bound for the dayplot filter (Hz)",
    )

    high_cutoff: float = Field(
        default=15.0,
        gt=0,
        description="Upper frequency bound for the dayplot filter (Hz)",
    )

    shutdown_timeout: int = Field(
        default=30,
        ge=1,
        le=120,
        description="Time to wait for the plotter to finish rendering and file I/O before exit",
    )
