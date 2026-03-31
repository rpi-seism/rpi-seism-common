# rpi-seism-common

Shared Python library for the [rpi-seism](https://github.com/rpi-seism) project — a single source of truth for configuration schemas, validation logic, and WebSocket message types used across the `daemon`, `api`, and related services.

---

## Overview

`rpi-seism-common` is consumed as a Git dependency by every Python service in the stack. It enforces a consistent, validated data contract so that configuration errors are caught at startup rather than at runtime, and so that both the acquisition daemon and the API always agree on the shape of every data structure.

It provides two top-level namespaces:

- **`rpi_seism_common.settings`** — Pydantic models for the full station configuration (hardware, channels, jobs).
- **`rpi_seism_common.websocket_message`** — Base classes and enums for the live WebSocket protocol.

---

## Installation

The package is not published to PyPI. Add it as a Git source dependency with [uv](https://github.com/astral-sh/uv):

```toml
# pyproject.toml
[tool.uv.sources]
rpi-seism-common = { git = "https://github.com/rpi-seism/rpi-seism-common.git", branch = "main" }
```

Then add it to your project dependencies:

```toml
dependencies = [
    "rpi-seism-common",
]
```

**Runtime requirements:** Python ≥ 3.13, pydantic ≥ 2.12, pydantic-extra-types ≥ 2.11, pyaml ≥ 26.2.

---

## Settings

### Loading and saving

```python
from pathlib import Path
from rpi_seism_common.settings import Settings

# Load from YAML — creates a default config if the file does not exist
settings = Settings.load_settings(Path("data/config.yml"))

# Export back to YAML
settings.export_settings(Path("data/config.yml"))
```

### Full config reference

```yaml
# data/config.yml

start_date: "2026-01-01T00:00:00+00:00"  # Update when hardware changes (new StationXML epoch)
decimation_factor: 4                       # Daemon decimation before WebSocket broadcast

station:
  network: "XX"           # 1–2 char FDSN network code
  station: "RPI3"         # 1–5 char station identifier
  location_code: "00"     # 2-char SEED location code
  latitude: 0.0
  longitude: 0.0
  elevation: 0.0

channels:
  - name: "EHZ"           # 3-char SEED channel code
    adc_channel: 0        # ADS1256 differential input index (0–3)
    orientation: "vertical"
    sensitivity: 28.8     # Geophone sensitivity V·s/m
    analog_gain: 1.0      # Instrumentation amplifier gain (e.g. 100.0 for LT1167 ×100)

  - name: "EHN"
    adc_channel: 1
    orientation: "north"
    sensitivity: 28.8
    analog_gain: 1.0

  - name: "EHE"
    adc_channel: 2
    orientation: "east"
    sensitivity: 28.8
    analog_gain: 1.0

mcu:
  sampling_rate: 100        # Target output rate in Hz (after ADS1256 MUX cycling)
  adc_gain: 6               # PGA index: 0=×1 … 6=×64 (see PGA enum)
  adc_sample_rate: 11       # DataRate index: 11 = 2000 SPS (see DataRate enum)
  vref: 2.5                 # ADC reference voltage in volts

jobs_settings:
  reader:
    port: "/dev/ttyUSB0"
    baudrate: 250000

  writer:
    write_interval_sec: 1800  # SDS flush interval (10–86400 s)

  trigger:
    trigger_channel: "EHZ"
    sta_sec: 0.5              # Short-term average window (s)
    lta_sec: 10.0             # Long-term average window (s)
    thr_on: 3.5               # STA/LTA ratio to declare an event
    thr_off: 1.5              # STA/LTA ratio to clear an event

  notifiers:
    - url: "tgram://{bot_token}/{chat_id}/"
      enabled: true
```

---

## Schema reference

### `Settings`

Top-level model. Validates cross-field consistency at construction time:

- No duplicate ADC channel indices across `channels`.
- `trigger_channel` must match a name in `channels`.
- Final WebSocket rate (`sampling_rate / decimation_factor`) must be ≥ 1 Hz.

### `Station`

| Field | Type | Constraints |
|---|---|---|
| `network` | `str` | 1–2 chars, uppercase alphanumeric |
| `station` | `str` | 1–5 chars, uppercase alphanumeric |
| `location_code` | `str` | exactly 2 chars, or `--` for blank |
| `latitude` | `float` | −90 to +90 |
| `longitude` | `float` | −180 to +180 |
| `elevation` | `float` | metres |

### `Channel`

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | — | 3-char SEED code; 3rd char must match orientation (Z/N/E) |
| `adc_channel` | `int` | — | ADS1256 MUX index, 0–3 |
| `orientation` | `ChannelOrientation` | — | `vertical`, `north`, or `east` |
| `sensitivity` | `float` | `28.8` | Geophone sensitivity in V·s/m |
| `analog_gain` | `float` | `1.0` | Instrumentation amplifier voltage gain |

### `MCUSettings`

| Field | Type | Default | Description |
|---|---|---|---|
| `sampling_rate` | `int` | — | Target output Hz (1–1000) |
| `adc_gain` | `PGA` | `PGA_64` | ADS1256 PGA register value |
| `adc_sample_rate` | `DataRate` | `DRATE_2000SPS` | ADS1256 DRATE register value |
| `vref` | `float` | `2.5` | Reference voltage (0.1–5.5 V) |

A cross-validator rejects configurations where the ADC cannot complete 3-channel MUX cycling fast enough for the requested `sampling_rate`, and suggests the minimum `adc_sample_rate` required.

### `PGA` enum

| Name | Index | Input range (±) |
|---|---|---|
| `PGA_1` | 0 | 5 V |
| `PGA_2` | 1 | 2.5 V |
| `PGA_4` | 2 | 1.25 V |
| `PGA_8` | 3 | 625 mV |
| `PGA_16` | 4 | 312.5 mV |
| `PGA_32` | 5 | 156.25 mV |
| `PGA_64` | 6 | 78.125 mV |

### `DataRate` enum

| Name | Index | Output rate |
|---|---|---|
| `DRATE_2SPS` | 0 | 2.5 SPS |
| `DRATE_5SPS` | 1 | 5 SPS |
| `DRATE_10SPS` | 2 | 10 SPS |
| `DRATE_25SPS` | 4 | 25 SPS |
| `DRATE_50SPS` | 6 | 50 SPS |
| `DRATE_100SPS` | 8 | 100 SPS |
| `DRATE_500SPS` | 9 | 500 SPS |
| `DRATE_1000SPS` | 10 | 1000 SPS |
| `DRATE_2000SPS` | 11 | 2000 SPS |
| `DRATE_3750SPS` | 12 | 3750 SPS |
| `DRATE_7500SPS` | 13 | 7500 SPS |
| `DRATE_15000SPS` | 14 | 15000 SPS |
| `DRATE_30000SPS` | 15 | 30000 SPS |

### Jobs

**`Reader`** — serial port settings for the RS-422 link to the MCU.

| Field | Default | Description |
|---|---|---|
| `port` | `/dev/ttyUSB0` | Serial device path |
| `baudrate` | `250000` | UART baud rate (9600–2000000) |

**`Writer`** — MiniSEED/SDS flush schedule.

| Field | Default | Constraints |
|---|---|---|
| `write_interval_sec` | `1800` | 10–86400 s |

**`Trigger`** — STA/LTA earthquake detector.

| Field | Default | Description |
|---|---|---|
| `trigger_channel` | `EHZ` | Channel name to monitor |
| `sta_sec` | `0.5` | Short-term average window |
| `lta_sec` | `10.0` | Long-term average window |
| `thr_on` | `3.5` | ON threshold (must be > `thr_off`) |
| `thr_off` | `1.5` | OFF threshold |

A validator enforces LTA > STA and thr_on > thr_off to guarantee hysteresis.

**`Notifier`** — Apprise notification target.

| Field | Default |
|---|---|
| `url` | — |
| `enabled` | `true` |

---

## WebSocket messages

Base class for all messages sent over the live WebSocket feed:

```python
from rpi_seism_common.websocket_message import WebsocketMessage
from rpi_seism_common.websocket_message.enums import WebsocketMessageTypeEnum
```

### `WebsocketMessageTypeEnum`

| Name | Value |
|---|---|
| `DATA` | `0` |
| `STATE_OF_HEALTH` | `1` |

### `WebsocketMessage`

```python
class WebsocketMessage(BaseModel):
    type:      WebsocketMessageTypeEnum
    timestamp: datetime   # auto-filled to UTC now
```

Concrete message types (defined in the `daemon` service) subclass this and add a `payload` field typed to their specific Pydantic model.

---

## Development

```bash
# Clone and set up
git clone https://github.com/rpi-seism/rpi-seism-common.git
cd rpi-seism-common
uv sync

# Run validation against a config file
uv run python -c "
from pathlib import Path
from rpi_seism_common.settings import Settings
s = Settings.load_settings(Path('data/config.yml'))
print(s.model_dump_json(indent=2))
"
```

---

## Relationship to other rpi-seism repos

| Repo | Role | Uses common |
|---|---|---|
| `rpi-seism-common` | Shared schemas (this repo) | — |
| `rpi-seism-daemon` | Acquisition daemon | `Settings`, `WebsocketMessage` |
| `rpi-seism-api` | FastAPI backend | `Settings` |
| `rpi-seism-reader` | MCU firmware | — |
| `rpi-seism-web` | Angular dashboard | — |

---

## License

GPL-3.0 — see [LICENSE](LICENSE).