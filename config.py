"""Shared configuration and defaults for the WT Plotter modules."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Tuple

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"


@dataclass(frozen=True)
class PathSettings:
    """Filesystem paths used by the application."""

    data_dir: Path = DATA_DIR
    maps_dir: Path = DATA_DIR / "maps"
    raw_dir: Path = DATA_DIR / "raw"
    db_path: Path = DATA_DIR / "matches.db"
    missing_hash_log: Path = DATA_DIR / "missing_map_hashes.log"


@dataclass(frozen=True)
class AppSettings:
    """Web application defaults."""

    host: str = "127.0.0.1"
    port: int = 5000
    datetime_format: str = "%Y-%m-%d %H:%M:%S"


@dataclass(frozen=True)
class MapDefaults:
    """Defaults for map metadata and lookups."""

    invalid_map_ids: Tuple[str, ...] = ("", "unknown", "no_map")
    unknown_map_id: str = "unknown"
    unknown_map_name: str = "Unknown Map"
    unknown_map_key: str = "unknown_map"


@dataclass(frozen=True)
class CaptureEndpoints:
    """Telemetry endpoints exposed by the game client."""

    base_url: str = "http://localhost:8111"
    map_obj_path: str = "map_obj.json"
    map_img_path: str = "map.img"
    map_info_path: str = "map_info.json"
    indicators_path: str = "indicators"

    @property
    def map_obj_url(self) -> str:
        return f"{self.base_url}/{self.map_obj_path}"

    @property
    def map_img_url(self) -> str:
        return f"{self.base_url}/{self.map_img_path}"

    @property
    def map_info_url(self) -> str:
        return f"{self.base_url}/{self.map_info_path}"

    @property
    def indicators_url(self) -> str:
        return f"{self.base_url}/{self.indicators_path}"


@dataclass(frozen=True)
class CaptureDefaults:
    """Defaults used during capture and reporting."""

    army_type: str = "tank"
    vehicle_type: str = ""
    air_army_type: str = "air"


@dataclass(frozen=True)
class CaptureFilters:
    """Filters and identifiers for map objects."""

    air_defence_icons: Tuple[str, ...] = ("airdefence", "air_defence")
    excluded_icons: Tuple[str, ...] = ("player", "airdefence", "air_defence")
    excluded_types: Tuple[str, ...] = (
        "aircraft",
        "airfield",
        "respawn_base_fighter",
    )
    capture_zone_type: str = "capture_zone"
    poi_types: Tuple[str, ...] = (
        "capture_zone",
        "respawn_base_tank",
        "respawn_base_fighter",
        "airfield",
    )


@dataclass(frozen=True)
class CaptureSettings:
    """Capture timing and state thresholds."""

    poll_interval: float = 0.2
    match_end_grace_period: float = 20.0
    save_raw_data: bool = False
    signature_rounding: int = 4
    valid_coord_min: float = 0.0
    valid_coord_max: float = 1.0


@dataclass(frozen=True)
class CaptureTimeouts:
    """Timeouts for network and threading operations."""

    session: float = 2.0
    map_info: float = 2.0
    map_image: float = 3.0
    current_map_image: float = 1.0
    async_map_info: float = 1.0
    async_indicators: float = 1.0
    async_map_obj: float = 1.0
    thread_join: float = 3.0


@dataclass(frozen=True)
class TransformSettings:
    """Thresholds for air-view transformation fitting."""

    min_points: int = 3
    scale_max: float = 0.5
    error_max: float = 0.01


@dataclass(frozen=True)
class HashSettings:
    """Hash lookup configuration."""

    tolerance: int = 42


@dataclass(frozen=True)
class DbSettings:
    """Database configuration and precision settings."""

    pragmas: Mapping[str, str] = field(
        default_factory=lambda: {
            "foreign_keys": "ON",
            "journal_mode": "WAL",
            "synchronous": "NORMAL",
            "temp_store": "MEMORY",
            "auto_vacuum": "INCREMENTAL",
            "busy_timeout": "5000",
        }
    )
    position_precision: int = 5
    capture_precision: int = 6


@dataclass(frozen=True)
class SyncSettings:
    """Remote sync configuration for central aggregation (WTHM)."""

    enabled: bool = False
    server_url: str = "http://localhost:8000"
    ingest_path: str = "/ingest"
    auth_token: str = ""
    client_id: str = ""
    schema_version: int = 1
    timeout: float = 5.0
    retries: int = 2


PATHS = PathSettings()
APP_SETTINGS = AppSettings()
MAP_DEFAULTS = MapDefaults()
CAPTURE_ENDPOINTS = CaptureEndpoints()
CAPTURE_DEFAULTS = CaptureDefaults()
CAPTURE_FILTERS = CaptureFilters()
CAPTURE_SETTINGS = CaptureSettings()
CAPTURE_TIMEOUTS = CaptureTimeouts()
TRANSFORM_SETTINGS = TransformSettings()
HASH_SETTINGS = HashSettings()
DB_SETTINGS = DbSettings()
SYNC_SETTINGS = SyncSettings()
