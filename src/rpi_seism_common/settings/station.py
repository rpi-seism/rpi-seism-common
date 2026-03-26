import re

from pydantic import BaseModel, Field, field_validator
from pydantic_extra_types.coordinate import Longitude, Latitude


class Station(BaseModel):
    """
    Pydantic model representing a seismic station. This class defines the structure of a station's
    configuration.
    """
    location_code: str = Field(default="00", min_length=2, max_length=2, description="Location ID")
    network: str = Field(..., min_length=1, max_length=2, description="FDSN Network Code")
    station: str = Field(..., min_length=1, max_length=5, description="Station identifier")
    latitude: Latitude
    longitude: Longitude
    elevation: float

    @field_validator('network', 'station', 'location_code')
    @classmethod
    def force_uppercase_alphanumeric(cls, v: str) -> str:
        """Ensure codes are uppercase and contain only valid alphanumeric characters."""
        v = v.upper()
        # SEED standards allow A-Z and 0-9. 
        # Note: Location code can sometimes be '--' to represent empty/blank.
        if v == "--":
            return v
            
        if not re.match(r"^[A-Z0-9]+$", v):
            raise ValueError(f"Code '{v}' must be alphanumeric.")
        return v

    @field_validator('location_code')
    @classmethod
    def handle_empty_location(cls, v: str) -> str:
        """Standardize empty location codes as '--' if blank or whitespace provided."""
        if not v or v.strip() == "":
            return "--"
        return v
