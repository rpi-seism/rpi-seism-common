from datetime import UTC, datetime
from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel, model_validator

from .channel import Channel
from .jobs import JobsSettings
from .mcu_settings import MCUSettings
from .station import Station


class Settings(BaseModel):
    """
    Pydantic model for application settings. This class defines the structure of the
    configuration, provides methods to load and save settings from/to a YAML file,
    and includes a method to update existing settings with new values.
    """

    station: Station
    start_date: datetime  # Update only when hardware configuration changes (triggers new StationXML epoch)

    decimation_factor: int
    channels: list[Channel]
    mcu: MCUSettings

    jobs_settings: JobsSettings

    @model_validator(mode="after")
    def validate_global_consistency(self) -> Self:
        """
        Performs cross-model validation to ensure hardware and software
        logic are in sync.
        """
        # Ensure no duplicate ADC channels are assigned
        adc_indices = [c.adc_channel for c in self.channels]
        if len(adc_indices) != len(set(adc_indices)):
            raise ValueError(
                f"Duplicate ADC channels detected in configuration: {adc_indices}"
            )

        # Ensure the trigger channel exists in the channel list
        channel_names = {c.name for c in self.channels}
        trigger_target = self.jobs_settings.trigger.trigger_channel
        if trigger_target not in channel_names:
            raise ValueError(
                f"Trigger target '{trigger_target}' not found in defined channels: {channel_names}"
            )

        # Check Decimation vs Sampling Rate
        # If your MCU samples at 100Hz and decimation is 4, your final rate is 25Hz.
        final_rate = self.mcu.sampling_rate / self.decimation_factor
        if final_rate < 1.0:
            raise ValueError(
                f"Final sample rate ({final_rate}Hz) is too low. Increase sampling_rate."
            )

        nyquist_freq = final_rate / 2.0
        if self.jobs_settings.dayplot.enabled and self.jobs_settings.dayplot.high_cutoff >= nyquist_freq:
            raise ValueError(
                f"Dayplot high_cutoff ({self.dayplot.high_cutoff}Hz) must be lower than "
                f"Nyquist frequency ({nyquist_freq}Hz). Increase sampling_rate or decrease filter."
            )

        return self

    def export_settings(self, settings_file_path: Path):
        """
        Export the current settings to a YAML file. This method serializes the settings
        to a YAML format and saves it to a predefined location.
        """

        with open(settings_file_path, "w", encoding="UTF-8") as settings_file:
            yaml.dump(self.model_dump(mode="json"), settings_file, indent=2)

    def update_from(self, new: "Settings") -> None:
        """
        Update the current settings with values from another Settings instance.
        This method iterates over all fields defined in the Settings model and updates
        the current instance's attributes with the corresponding values from the new instance.
        """
        for field in Settings.model_fields:
            setattr(self, field, getattr(new, field))

    @classmethod
    def load_settings(cls, settings_file_path: Path | str):
        """
        Load settings from a YAML file. If the file does not exist, it creates a new one
        with default settings. This method checks for the existence of the configuration file,
        and if it is not found, it generates a default configuration and saves it.
        If the file exists, it reads the YAML content and initializes a
        Settings instance with the loaded values.
        """

        if isinstance(settings_file_path, str):
            settings_file_path = Path(settings_file_path)

        # If YAML config does not exist
        if not settings_file_path.exists():
            if not settings_file_path.parent.exists():
                settings_file_path.parent.mkdir()
            # Otherwise create default config
            settings = cls.get_default_settings()

            with open(settings_file_path, "w", encoding="UTF-8") as yml_file:
                yaml.dump(settings.model_dump(mode="json"), yml_file, indent=2)

            return settings

        # Load existing YAML config
        with open(settings_file_path, "r", encoding="UTF-8") as yml_file:
            raw_data = yaml.safe_load(yml_file) or {}

        # Pydantic will fill in any missing fields with defaults defined in your sub-models
        settings = cls(**raw_data)

        # We compare the keys in the YAML file to the keys produced by model_dump
        if cls._is_config_incomplete(raw_data, settings.model_dump(mode="json")):
            settings.export_settings(settings_file_path)

        return settings

    @staticmethod
    def _is_config_incomplete(raw: dict, processed: dict) -> bool:
        """
        Recursively checks if the raw dictionary is missing any keys
        that exist in the processed (defaulted) dictionary.
        """
        for key, value in processed.items():
            if key not in raw:
                return True
            if isinstance(value, dict) and isinstance(raw.get(key), dict):
                if Settings._is_config_incomplete(raw[key], value):
                    return True
        return False

    @classmethod
    def get_default_settings(cls):
        """
        Generate a default Settings instance with predefined values. This method creates
        a new Settings object populated with default values for all fields,
        including a sample list of channels. This is useful for initializing
        the application with a known configuration when no existing settings file is found.
        """
        data = {
            "start_date": datetime.now(tz=UTC).isoformat(),
            "decimation_factor": 4,
            "station": {
                "location_code": "00",
                "network": "XX",
                "station": "RPI3",
                "latitude": 0.0,
                "longitude": 0.0,
                "elevation": 0.0,
            },
            "channels": [
                {
                    "name": "EHZ",
                    "adc_channel": 0,
                    "orientation": "vertical",
                },
                {
                    "name": "EHN",
                    "adc_channel": 1,
                    "orientation": "north",
                },
                {
                    "name": "EHE",
                    "adc_channel": 2,
                    "orientation": "east",
                },
            ],
            "mcu": {"sampling_rate": 100, "adc_gain": 6, "adc_sample_rate": 11},
            "jobs_settings": {
                "notifiers": [
                    {"url": "tgram://{bot_token}/{chat_id}/", "enabled": True}
                ],
                "trigger": {
                    "sta_sec": 0.5,
                    "lta_sec": 10.0,
                    "thr_on": 3.5,
                    "thr_off": 1.5,
                    "trigger_channel": "EHZ",
                },
                "writer": {"write_interval_sec": 1800},
                "reader": {"port": "/dev/ttyUSB0", "baudrate": 250000},
                "ring_server": {"enabled": False},
                "dayplot": {"enabled": True},
            },
        }

        return cls(**data)
