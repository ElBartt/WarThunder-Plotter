"""Shared payload models and validation helpers for WT Plotter."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import db
from map_hashes import MapInfo


@dataclass(frozen=True)
class MatchPayloadBase:
    """Base payload fields shared across match responses."""

    match_id: int
    started_at: str
    ended_at: Optional[str]
    map_name: str
    nuke_detected: int
    initial_capture_count: Optional[int]

    def validate(self) -> None:
        """Validate required fields for the payload."""
        if self.match_id is None:
            raise ValueError("match_id is required")
        if not self.started_at:
            raise ValueError("started_at is required")
        if not self.map_name:
            raise ValueError("map_name is required")

    def to_dict(self) -> Dict[str, Any]:
        """Return the payload as a dict."""
        self.validate()
        return {
            "id": self.match_id,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "map_name": self.map_name,
            "nuke_detected": self.nuke_detected,
            "initial_capture_count": self.initial_capture_count,
        }


@dataclass(frozen=True)
class MatchSummaryPayload(MatchPayloadBase):
    """Payload for the dashboard summary list."""

    air_map_name: Optional[str]
    duration_seconds: Optional[int]
    position_count: int
    is_active: bool

    @classmethod
    def from_match(
        cls,
        match: db.Match,
        map_info: MapInfo,
        air_info: Optional[MapInfo],
        position_count: int,
        duration_seconds: Optional[int],
    ) -> "MatchSummaryPayload":
        """Create a summary payload from a match instance."""
        return cls(
            match_id=match.id,
            started_at=match.started_at,
            ended_at=match.ended_at,
            map_name=map_info.display_name,
            nuke_detected=getattr(match, "nuke_detected", 0),
            initial_capture_count=getattr(match, "initial_capture_count", None),
            air_map_name=air_info.display_name if air_info else None,
            duration_seconds=duration_seconds,
            position_count=position_count,
            is_active=match.ended_at is None,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Return the summary payload as a dict."""
        payload = super().to_dict()
        payload.update(
            {
                "air_map_name": self.air_map_name,
                "duration_seconds": self.duration_seconds,
                "position_count": self.position_count,
                "is_active": self.is_active,
            }
        )
        return payload


@dataclass(frozen=True)
class MatchListPayload(MatchPayloadBase):
    """Payload for listing matches in the API."""

    map_id: Optional[str]
    battle_type: str
    initial_capture_x: Optional[float]
    initial_capture_y: Optional[float]
    position_count: int

    @classmethod
    def from_match(
        cls,
        match: db.Match,
        map_info: MapInfo,
        position_count: int,
    ) -> "MatchListPayload":
        """Create a list payload from a match instance."""
        return cls(
            match_id=match.id,
            started_at=match.started_at,
            ended_at=match.ended_at,
            map_name=map_info.display_name,
            nuke_detected=getattr(match, "nuke_detected", 0),
            initial_capture_count=getattr(match, "initial_capture_count", None),
            map_id=map_info.map_id,
            battle_type=map_info.battle_type.value,
            initial_capture_x=getattr(match, "initial_capture_x", None),
            initial_capture_y=getattr(match, "initial_capture_y", None),
            position_count=position_count,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Return the list payload as a dict."""
        payload = super().to_dict()
        payload.update(
            {
                "map_id": self.map_id,
                "battle_type": self.battle_type,
                "initial_capture_x": self.initial_capture_x,
                "initial_capture_y": self.initial_capture_y,
                "position_count": self.position_count,
            }
        )
        return payload


@dataclass(frozen=True)
class MatchDetailPayload(MatchPayloadBase):
    """Payload for the match detail API."""

    map_hash: str
    map_id: Optional[str]
    battle_type: str
    initial_capture_x: Optional[float]
    initial_capture_y: Optional[float]
    air_transform_a: Optional[float]
    air_transform_b: Optional[float]
    air_transform_c: Optional[float]
    air_transform_d: Optional[float]

    @classmethod
    def from_match(
        cls,
        match: db.Match,
        map_info: MapInfo,
    ) -> "MatchDetailPayload":
        """Create a detail payload from a match instance."""
        return cls(
            match_id=match.id,
            started_at=match.started_at,
            ended_at=match.ended_at,
            map_name=map_info.display_name,
            nuke_detected=getattr(match, "nuke_detected", 0),
            initial_capture_count=getattr(match, "initial_capture_count", None),
            map_hash=match.map_hash,
            map_id=map_info.map_id,
            battle_type=map_info.battle_type.value,
            initial_capture_x=getattr(match, "initial_capture_x", None),
            initial_capture_y=getattr(match, "initial_capture_y", None),
            air_transform_a=getattr(match, "air_transform_a", None),
            air_transform_b=getattr(match, "air_transform_b", None),
            air_transform_c=getattr(match, "air_transform_c", None),
            air_transform_d=getattr(match, "air_transform_d", None),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Return the detail payload as a dict."""
        payload = super().to_dict()
        payload.update(
            {
                "map_hash": self.map_hash,
                "map_id": self.map_id,
                "battle_type": self.battle_type,
                "initial_capture_x": self.initial_capture_x,
                "initial_capture_y": self.initial_capture_y,
                "air_transform_a": self.air_transform_a,
                "air_transform_b": self.air_transform_b,
                "air_transform_c": self.air_transform_c,
                "air_transform_d": self.air_transform_d,
            }
        )
        return payload


@dataclass
class PositionEntry:
    """Payload for a single captured position entry."""

    x: float
    y: float
    color: str
    obj_type: str
    icon: str
    timestamp: float
    is_poi: int
    army_type: str
    vehicle_type: str
    is_player_air: int
    is_player_air_view: int
    x_ground: Optional[float] = None
    y_ground: Optional[float] = None

    def validate(self) -> None:
        """Validate required fields for a position entry."""
        if self.timestamp is None:
            raise ValueError("timestamp is required")
        if self.color is None:
            raise ValueError("color is required")
        if self.obj_type is None:
            raise ValueError("obj_type is required")
        if self.icon is None:
            raise ValueError("icon is required")

    def set_ground(self, x_ground: float, y_ground: float) -> None:
        """Set ground coordinates for air-view positions."""
        self.x_ground = x_ground
        self.y_ground = y_ground

    def to_dict(self) -> Dict[str, Any]:
        """Return the position entry as a dict."""
        self.validate()
        return {
            "x": self.x,
            "y": self.y,
            "color": self.color,
            "type": self.obj_type,
            "icon": self.icon,
            "timestamp": self.timestamp,
            "is_poi": int(self.is_poi),
            "army_type": self.army_type,
            "vehicle_type": self.vehicle_type,
            "is_player_air": int(self.is_player_air),
            "is_player_air_view": int(self.is_player_air_view),
            "x_ground": self.x_ground,
            "y_ground": self.y_ground,
        }
