from typing import Self

from pydantic import BaseModel, Field, field_validator, model_validator


class Trigger(BaseModel):
    """Configuration for the trigger processor."""

    # STA/LTA Window lengths in seconds
    sta_sec: float = Field(
        default=0.5, gt=0, le=10.0, description="Short-Term Average window"
    )
    lta_sec: float = Field(
        default=10.0, gt=0, le=300.0, description="Long-Term Average window"
    )

    # Trigger thresholds
    thr_on: float = Field(
        default=3.5, gt=1.0, description="Ratio required to start a trigger"
    )
    thr_off: float = Field(
        default=1.5, gt=0, description="Ratio required to end a trigger"
    )

    trigger_channel: str = Field(default="EHZ", min_length=3, max_length=3)

    @field_validator("trigger_channel")
    @classmethod
    def force_upper(cls, v: str) -> str:
        return v.upper()

    @model_validator(mode="after")
    def validate_trigger_logic(self) -> Self:
        # Window Logic: LTA must be significantly longer than STA
        # Standard practice is LTA >= 5x STA to avoid the LTA 'tracking' the event too quickly.
        if self.lta_sec <= self.sta_sec:
            raise ValueError(
                f"LTA window ({self.lta_sec}s) must be longer than STA window ({self.sta_sec}s)."
            )

        # Threshold Logic: Trigger ON must be higher than Trigger OFF
        # This provides 'Hysteresis', preventing rapid oscillation between ON and OFF.
        if self.thr_off >= self.thr_on:
            raise ValueError(
                f"Threshold OFF ({self.thr_off}) must be lower than Threshold ON ({self.thr_on}) "
                "to provide stable hysteresis."
            )

        return self
