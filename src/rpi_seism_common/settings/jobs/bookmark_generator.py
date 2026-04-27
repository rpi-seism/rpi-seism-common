from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, TypeAdapter, model_validator
from pydantic_extra_types.coordinate import Latitude, Longitude


def _parse_url(url: str) -> HttpUrl:
    return TypeAdapter(HttpUrl).validate_python(url)


class BookmarkGenerator(BaseModel):
    enabled: bool = Field(
        default=True, description="Whether to generate bookmarks automatically"
    )

    api_server_url: HttpUrl = Field(
        default=_parse_url("https://api.yourservice.com/v1"),
        description="The base endpoint for the internal API server",
    )

    quakeml_url_template: str = Field(
        default="https://webservices.ingv.it/fdsnws/event/1/query?starttime={start}&endtime={end}&lat={station_lat}&lon={station_lon}&orderby=time&format=xml",
        description="URL template for QuakeML queries. Supports {start}, {end}, {station_lat}, {station_lon} placeholders.",
    )

    override_station_lat: Optional[Latitude] = Field(
        None, description="Manual override for station latitude (-90 to 90)"
    )

    override_station_lon: Optional[Longitude] = Field(
        None, description="Manual override for station longitude (-180 to 180)"
    )

    @model_validator(mode="after")
    def check_url_placeholders(self) -> "BookmarkGenerator":
        required = ["{start}", "{end}"]
        # Check for lat/lon placeholders only if they aren't hardcoded in the string
        if (
            self.override_station_lat is not None
            or self.override_station_lon is not None
        ):
            required.extend(["{station_lat}", "{station_lon}"])

        missing = [p for p in required if p not in self.quakeml_url_template]

        if missing:
            raise ValueError(
                f"quakeml_url_template is missing required placeholders: {', '.join(missing)}"
            )

        return self

    def get_formatted_url(
        self, start: str, end: str, station_lat: float, station_lon: float
    ) -> str:
        """
        Helper to resolve the URL using either overrides or passed station data.
        """
        lat = (
            self.override_station_lat
            if self.override_station_lat is not None
            else station_lat
        )
        lon = (
            self.override_station_lon
            if self.override_station_lon is not None
            else station_lon
        )

        return self.quakeml_url_template.format(
            start=start, end=end, station_lat=lat, station_lon=lon
        )
