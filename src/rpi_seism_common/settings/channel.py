import re

from pydantic import BaseModel, Field, field_validator

from .enums import ChannelOrientation


class Channel(BaseModel):
    """
    Pydantic model for a seismic data channel. This class defines the structure
    of a channel configuration, including its name, associated ADC channel, and orientation.
    It is used within the Settings model to represent individual channels in the configuration.
    """
    name: str = Field(..., min_length=3, max_length=3, description="3-character SEED code")
    adc_channel: int = Field(..., ge=0, le=3, description="Physical ADC differential input index")
    orientation: ChannelOrientation
    sensitivity: float = Field(default=28.8, gt=0, description="Sensitivity in V·s/m")
    analog_gain: float = Field(default=1.0, ge=1.0, description="Fixed analog front-end gain factor")
    natural_frequency: float = Field(default=4.5, ge=1.0, description=r"Sensor natural frequency ($f_n$) in Hz")
    damping: float = Field(default=0.707, ge=0, le=2.0, description=r"Damping ratio ($\zeta$), typically 0.707")

    @field_validator('name')
    @classmethod
    def validate_seed_channel_name(cls, v: str) -> str:
        """
        Validates the 3-character SEED channel name.
        Matches regex for alphanumeric characters (standard seismic notation).
        """
        v = v.upper()
        if not re.match(r"^[A-Z0-9]{3}$", v):
            raise ValueError(f"Channel name '{v}' must be a 3-character alphanumeric SEED code.")
        return v

    @field_validator('name')
    @classmethod
    def validate_orientation_suffix(cls, v: str, info) -> str:
        """
        Cross-validates that the 3rd character of the name matches the orientation enum.
        """
        orientation_map = {
            ChannelOrientation.VERTICAL: 'Z',
            ChannelOrientation.NORTH: 'N',
            ChannelOrientation.EAST: 'E',
        }
        
        # In Pydantic V2, 'info.data' contains the fields already validated
        selected_orientation = info.data.get('orientation')
        
        if selected_orientation in orientation_map:
            expected_char = orientation_map[selected_orientation]
            if v[2] != expected_char:
                raise ValueError(
                    f"Orientation mismatch: Channel '{v}' ends in '{v[2]}', "
                    f"but orientation is set to {selected_orientation.name} (expected suffix '{expected_char}')."
                )
        return v
