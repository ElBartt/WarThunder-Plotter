"""
Capture module for WT Plotter.
Uses requests and aiohttp to poll the localhost telemetry API.
"""
from __future__ import annotations

import asyncio
from datetime import datetime
import hashlib
import json
import logging
from pathlib import Path
import re
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

import aiohttp
import numpy as np
import requests
from requests.adapters import HTTPAdapter

import db
from map_hashes import BattleType, MapInfo, lookup_map_info

SAVE_RAW_DATA = False
RAW_DATA_DIR = Path(__file__).parent / "data" / "raw"
MAPS_DIR = Path(__file__).parent / "data" / "maps"

BASE_URL = "http://localhost:8111"
MAP_OBJ_URL = f"{BASE_URL}/map_obj.json"
MAP_IMG_URL = f"{BASE_URL}/map.img"
MAP_INFO_URL = f"{BASE_URL}/map_info.json"
INDICATORS_URL = f"{BASE_URL}/indicators"

POLL_INTERVAL = 0.2
MATCH_END_GRACE_PERIOD = 20.0

logger = logging.getLogger(__name__)

class Capturer:
    """Capture match data by polling the War Thunder localhost API."""
    
    def __init__(
        self,
        on_match_start: Optional[Callable[[int], None]] = None,
        on_match_end: Optional[Callable[[int], None]] = None,
        on_position: Optional[Callable[[int, List[dict]], None]] = None,
    ):
        self.conn = db.get_connection()
        self.running = False
        self.thread: Optional[threading.Thread] = None

        self.current_match_id: Optional[int] = None
        self.match_start_time: float = 0
        self.poi_captured = False
        self.has_map_image = False
        self.match_end_grace_start: Optional[float] = None
        self.current_map_hash: str = ""
        self.current_map_info: Optional[MapInfo] = None
        self.current_air_map_hash: str = ""
        self._last_poi_signature: Optional[Tuple[Tuple[Any, ...], ...]] = None
        self.current_match_nuke_detected = False
        self.initial_capture_set = False

        self._prev_tick_ground_objects: List[Dict[str, Any]] = []
        self._prev_tick_was_air_view = False
        self._air_transform_computed = False
        self._air_transform_params: Optional[Tuple[float, float, float, float]] = None

        self.current_army_type: str = "tank"
        self.current_vehicle_type: str = ""

        self.raw_data: List[Dict[str, Any]] = []
        if SAVE_RAW_DATA:
            RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

        self.on_match_start = on_match_start
        self.on_match_end = on_match_end
        self.on_position = on_position

        self.session = requests.Session()
        self.session.timeout = 2.0
        adapter = HTTPAdapter(pool_connections=1, pool_maxsize=1, max_retries=0)
        self.session.mount("http://localhost:8111", adapter)
        self.session.headers.update({"Connection": "keep-alive"})
    
    def start(self) -> None:
        """Start the capture loop in a background thread."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        logger.info("Capture started")
    
    def stop(self) -> None:
        """Stop the capture loop."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=3.0)
        logger.info("Capture stopped")
    
    def _loop(self) -> None:
        """Main capture loop running at the configured poll interval."""
        while self.running:
            try:
                self._tick()
            except Exception as e:
                logger.error("Capture error: %s", e)
            time.sleep(POLL_INTERVAL)
    
    def _tick(self) -> None:
        """Run a single capture tick using a map-validity state machine."""
        async def fetch_all():
            """Fetch map info, indicators, and map objects concurrently."""
            async with aiohttp.ClientSession() as session:
                tasks = [
                    self._get_map_info_async(session),
                    self._get_indicators_data_async(session),
                    self._get_map_obj_data_async(session)
                ]
                return await asyncio.gather(*tasks)
        
        map_info, indicators_data, map_obj_data = asyncio.run(fetch_all())
        
        match_running = map_info.get("valid", False) if map_info else False
        
        if not self.has_map_image and match_running:
            self._start_match()
        elif self.has_map_image and match_running:
            self.match_end_grace_start = None
            self._capture_positions_with_data(indicators_data, map_obj_data)
        elif self.has_map_image and not match_running:
            current_map_hash = self._get_current_map_hash()
            if current_map_hash:
                hash_map_info = lookup_map_info(current_map_hash)
                if (
                    hash_map_info.display_name == "No Map"
                    or hash_map_info.map_id == "no_map"
                ):
                    logger.info("Map changed to 'No Map', ending match")
                    self._end_match()
                elif current_map_hash != self.current_map_hash:
                    if self._is_nuke_map_switch(self.current_map_info, hash_map_info):
                        logger.info(
                            "Nuke detected (map switch %s -> %s), keeping current match",
                            self.current_map_hash,
                            current_map_hash,
                        )
                        self._mark_match_nuke()
                        self.match_end_grace_start = None
                    else:
                        logger.info(
                            "Map changed during grace period (%s -> %s), starting new match",
                            self.current_map_hash,
                            current_map_hash,
                        )
                        self._end_match()
                        self._start_match()
                else:
                    current_time = time.time()
                    if self.match_end_grace_start is None:
                        self.match_end_grace_start = current_time
                        logger.info(
                            "Match temporarily invalid, starting %ss grace period",
                            MATCH_END_GRACE_PERIOD,
                        )
                    elif (
                        current_time - self.match_end_grace_start
                        >= MATCH_END_GRACE_PERIOD
                    ):
                        logger.info(
                            "Match invalid for %ss, ending match",
                            MATCH_END_GRACE_PERIOD,
                        )
                        self._end_match()
            else:
                current_time = time.time()
                if self.match_end_grace_start is None:
                    self.match_end_grace_start = current_time
                    logger.info(
                        "Match temporarily invalid, starting %ss grace period",
                        MATCH_END_GRACE_PERIOD,
                    )
                elif current_time - self.match_end_grace_start >= MATCH_END_GRACE_PERIOD:
                    logger.info(
                        "Match invalid for %ss, ending match",
                        MATCH_END_GRACE_PERIOD,
                    )
                    self._end_match()
    
    async def _get_map_info_async(
        self,
        session: aiohttp.ClientSession,
    ) -> Optional[Dict[str, Any]]:
        """Get current map_info.json data asynchronously."""
        try:
            logger.debug("Getting map info from map_info.json endpoint")
            async with session.get(
                MAP_INFO_URL,
                timeout=aiohttp.ClientTimeout(total=1.0),
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception as e:
            logger.warning("Failed to get map info: %s", e)
        return None

    async def _get_indicators_data_async(
        self,
        session: aiohttp.ClientSession,
    ) -> Optional[Dict[str, Any]]:
        """Get indicators data asynchronously."""
        try:
            logger.debug("Getting indicators data from indicators endpoint")
            async with session.get(
                INDICATORS_URL,
                timeout=aiohttp.ClientTimeout(total=1.0),
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception as e:
            logger.warning("Failed to get indicators data: %s", e)
        return None

    async def _get_map_obj_data_async(
        self,
        session: aiohttp.ClientSession,
    ) -> Optional[List[Dict[str, Any]]]:
        """Get map objects data asynchronously."""
        try:
            logger.debug("Getting map objects data from map_obj.json endpoint")
            async with session.get(
                MAP_OBJ_URL,
                timeout=aiohttp.ClientTimeout(total=1.0),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if isinstance(data, list):
                        return data
        except Exception as e:
            logger.warning("Failed to get map objects data: %s", e)
        return None
    
    def _start_match(self) -> None:
        """Start tracking a new match."""
        logger.info("Match started - loading map")
        self.match_start_time = time.time()
        self.poi_captured = False
        self.has_map_image = True
        self.match_end_grace_start = None
        self.raw_data = []

        map_hash = ""
        map_image = None
        map_name = "Unknown Map"
        map_id = None
        map_info: Optional[MapInfo] = None

        try:
            resp = self.session.get(MAP_INFO_URL, timeout=2.0)
            if resp.status_code == 200:
                map_info = resp.json()
                if SAVE_RAW_DATA:
                    self.raw_data.append(
                        {
                            "endpoint": "map_info.json",
                            "timestamp": 0,
                            "data": map_info,
                        }
                    )
        except Exception as e:
            logger.debug("Failed to capture map_info.json: %s", e)

        try:
            resp = self.session.get(MAP_IMG_URL, timeout=3.0)
            if resp.status_code == 200:
                map_image = resp.content
                map_hash = self._compute_dhash(map_image)
                map_info = lookup_map_info(map_hash)
                map_name = map_info.display_name
                map_id = map_info.map_id
                logger.info(
                    "Map hash: %s (%s chars) -> %s",
                    map_hash,
                    len(map_hash),
                    map_name,
                )
        except Exception as e:
            logger.warning("Failed to get map image: %s", e)

        if map_image:
            self._save_map_image(map_image, map_id, map_hash)

        self.current_match_id = db.start_match(self.conn, map_hash=map_hash)
        self.current_map_hash = map_hash
        self.current_map_info = map_info
        self.current_air_map_hash = ""
        self._last_poi_signature = None
        self.current_match_nuke_detected = False
        self.initial_capture_set = False
        self._prev_tick_ground_objects = []
        self._prev_tick_was_air_view = False
        self._air_transform_computed = False
        self._air_transform_params = None
        
        if self.on_match_start:
            self.on_match_start(self.current_match_id)

        async def fetch_initial():
            """Fetch indicators and map objects for the first capture tick."""
            async with aiohttp.ClientSession() as session:
                indicators_task = self._get_indicators_data_async(session)
                map_obj_task = self._get_map_obj_data_async(session)
                indicators_data, map_obj_data = await asyncio.gather(
                    indicators_task,
                    map_obj_task,
                )
                return indicators_data, map_obj_data

        indicators_data, map_obj_data = asyncio.run(fetch_initial())
        self._capture_positions_with_data(indicators_data, map_obj_data)

    def _end_match(self) -> None:
        """End the current match."""

        if SAVE_RAW_DATA and self.current_match_id and self.raw_data:
            self._save_raw_data()

        if self.current_match_id:
            db.end_match(self.conn, self.current_match_id)
            if self.on_match_end:
                self.on_match_end(self.current_match_id)

        self.current_match_id = None
        self.poi_captured = False
        self.has_map_image = False
        self.match_end_grace_start = None
        self.current_map_info = None
        self.current_air_map_hash = ""
        self._last_poi_signature = None
        self.raw_data = []
        self.current_match_nuke_detected = False
        self.initial_capture_set = False
        self._prev_tick_ground_objects = []
        self._prev_tick_was_air_view = False
        self._air_transform_computed = False
        self._air_transform_params = None
    
    def _capture_positions_with_data(
        self,
        indicators_data: Optional[Dict[str, Any]],
        map_obj_data: Optional[List[Dict[str, Any]]],
    ) -> None:
        """Capture current positions using pre-fetched data."""
        if not self.current_match_id:
            return

        try:
            logger.debug("Capturing positions from pre-fetched data")

            army_type = indicators_data.get("army") if indicators_data else None
            vehicle_type = indicators_data.get("type", "") if indicators_data else ""
            if "/" in vehicle_type:
                vehicle_type = vehicle_type.split("/", 1)[1]
            vehicle_type = vehicle_type if vehicle_type else None

            if army_type:
                self.current_army_type = army_type
            if vehicle_type:
                self.current_vehicle_type = vehicle_type

            self._maybe_capture_air_map(army_type)

            if not map_obj_data:
                return

            objects = map_obj_data

            poi_types = ("capture_zone",)
            poi_signature_list: List[Tuple[Any, ...]] = []
            capture_zone_positions: List[Tuple[float, float]] = []
            airdefence_seen = False
            for obj in objects:
                x = obj.get("x", -1)
                y = obj.get("y", -1)
                if x <= 0 or x >= 1 or y <= 0 or y >= 1:
                    continue
                icon = obj.get("icon", "")
                if isinstance(icon, str) and icon.lower() in (
                    "airdefence",
                    "air_defence",
                ):
                    airdefence_seen = True
                obj_type = obj.get("type", "unknown")
                if obj_type in poi_types:
                    poi_signature_list.append((obj_type, round(x, 4), round(y, 4)))
                if obj_type == "capture_zone":
                    capture_zone_positions.append((x, y))

            poi_signature_list.sort()
            poi_signature = tuple(poi_signature_list)
            poi_changed = False
            if self._last_poi_signature is not None and poi_signature != self._last_poi_signature:
                poi_changed = True
            self._last_poi_signature = poi_signature

            if not self.initial_capture_set and capture_zone_positions:
                count = len(capture_zone_positions)
                sum_x = sum(p[0] for p in capture_zone_positions)
                sum_y = sum(p[1] for p in capture_zone_positions)
                avg_x = sum_x / count
                avg_y = sum_y / count
                try:
                    db.update_match_initial_capture(
                        self.conn,
                        self.current_match_id,
                        initial_capture_count=count,
                        initial_capture_x=avg_x,
                        initial_capture_y=avg_y,
                    )
                    self.initial_capture_set = True
                except Exception as e:
                    logger.warning("Failed to store initial capture zones: %s", e)

            timestamp = time.time() - self.match_start_time

            is_air_view_now = (
                army_type == "air" or airdefence_seen or poi_changed
            )

            if (
                is_air_view_now
                and not self._prev_tick_was_air_view
                and not self._air_transform_computed
            ):
                if self._prev_tick_ground_objects and objects:
                    transform = self._compute_air_transform(
                        self._prev_tick_ground_objects,
                        objects,
                    )
                    if transform:
                        self._air_transform_params = transform
                        self._air_transform_computed = True
                        a, b, c, d = transform
                        db.update_match_air_transform(
                            self.conn,
                            self.current_match_id,
                            a,
                            b,
                            c,
                            d,
                        )
                        logger.info(
                            "Air transform stored for match %s",
                            self.current_match_id,
                        )

            self._prev_tick_was_air_view = is_air_view_now
            self._prev_tick_ground_objects = [
                obj
                for obj in objects
                if 0 < obj.get("x", -1) < 1 and 0 < obj.get("y", -1) < 1
            ]

            if SAVE_RAW_DATA:
                logger.debug("Saving raw map_obj.json data for debug")
                self.raw_data.append(
                    {
                        "endpoint": "map_obj.json",
                        "timestamp": timestamp,
                        "data": objects,
                    }
                )
                if indicators_data:
                    self.raw_data.append(
                        {
                            "endpoint": "indicators",
                            "timestamp": timestamp,
                            "data": indicators_data,
                        }
                    )

            positions = []

            logger.debug("Processing map objects for position capture")
            for obj in objects:
                x = obj.get("x", -1)
                y = obj.get("y", -1)
                if x <= 0 or x >= 1 or y <= 0 or y >= 1:
                    continue

                obj_type = obj.get("type", "unknown")
                is_poi = obj_type in (
                    "capture_zone",
                    "respawn_base_tank",
                    "respawn_base_fighter",
                    "airfield",
                )
                if is_poi and obj_type != "capture_zone" and self.poi_captured:
                    continue

                pos = {
                    "x": x,
                    "y": y,
                    "color": obj.get("color", "#FFFFFF"),
                    "type": obj_type,
                    "icon": obj.get("icon", "unknown"),
                    "timestamp": timestamp,
                    "is_poi": 1 if is_poi else 0,
                    "army_type": army_type or "tank",
                    "vehicle_type": vehicle_type or "",
                    "is_player_air": 1 if (army_type == "air") else 0,
                    "is_player_air_view": 1 if is_air_view_now else 0,
                }

                if is_air_view_now and self._air_transform_params:
                    x_ground, y_ground = self._apply_inverse_transform(x, y)
                    pos["x_ground"] = x_ground
                    pos["y_ground"] = y_ground

                positions.append(pos)

            if positions:
                logger.debug("Captured %s positions", len(positions))
                db.add_positions(self.conn, self.current_match_id, positions)
                if self.on_position:
                    self.on_position(self.current_match_id, positions)

            if any(pos["is_poi"] for pos in positions):
                self.poi_captured = True

            logger.debug("Finished capturing positions")
        except Exception as e:
            logger.warning("Failed to capture positions: %s", e)

    def _maybe_capture_air_map(self, army_type: Optional[str]) -> None:
        """Capture air map metadata when transitioning to air for ground battles."""
        if not self.current_match_id or not self.current_map_info:
            return
        if army_type != "air":
            return
        if self.current_air_map_hash:
            return
        if self.current_map_info.battle_type == BattleType.AIR:
            return

        map_image, map_hash = self._get_current_map_image_and_hash()
        if not map_hash:
            return
        if map_hash == self.current_map_hash:
            return

        air_info = lookup_map_info(map_hash)
        if map_image:
            self._save_map_image(map_image, air_info.map_id, map_hash)

        db.update_match_air_map(
            self.conn,
            self.current_match_id,
            air_map_hash=map_hash,
        )
        self.current_air_map_hash = map_hash

    def _save_map_image(
        self,
        map_image: bytes,
        map_id: Optional[str],
        map_hash: Optional[str],
    ) -> None:
        """Save the map image if it is not already on disk."""
        if not map_image:
            return
        if map_id in (None, "", "unknown", "no_map"):
            map_key = map_hash or "unknown_map"
        else:
            map_key = map_id
        MAPS_DIR.mkdir(parents=True, exist_ok=True)
        file_path = MAPS_DIR / f"{map_key}.png"
        if file_path.exists():
            return
        try:
            file_path.write_bytes(map_image)
        except Exception as e:
            logger.warning("Failed to save map image to disk: %s", e)

    def _get_current_map_image_and_hash(
        self,
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """Return the current map image and its computed hash."""
        try:
            resp = self.session.get(MAP_IMG_URL, timeout=1.0)
            if resp.status_code == 200:
                map_image = resp.content
                return map_image, self._compute_dhash(map_image)
        except Exception as e:
            logger.debug("Failed to get current map image: %s", e)
        return None, None
    
    def _compute_dhash(self, image_data: bytes, size: int = 16) -> str:
        """
        Compute a difference hash using horizontal pixel comparisons.
        The output matches the WT-Plotter hash format.
        """
        try:
            from PIL import Image
            import io

            img = Image.open(io.BytesIO(image_data))
            img = img.convert("L")
            img = img.resize((size, size - 1), Image.Resampling.LANCZOS)

            pixels = list(img.getdata())
            hash_bits = []
            width = size
            height = size - 1

            for y in range(height):
                for x in range(width - 1):
                    left = pixels[y * width + x]
                    right = pixels[y * width + x + 1]
                    hash_bits.append(1 if left > right else 0)

            hex_str = ""
            for i in range(0, len(hash_bits), 4):
                nibble = hash_bits[i : i + 4]
                while len(nibble) < 4:
                    nibble.append(0)
                value = (nibble[0] << 3) | (nibble[1] << 2) | (nibble[2] << 1) | nibble[3]
                hex_str += format(value, "x")

            logger.debug("Computed dhash: %s (%s chars)", hex_str, len(hex_str))
            return hex_str
        except Exception as e:
            logger.warning("Failed to compute dhash: %s", e)
            return hashlib.md5(image_data).hexdigest()[:16]

    def _get_current_map_hash(self) -> Optional[str]:
        """Return the current map hash for grace-period checks."""
        _, map_hash = self._get_current_map_image_and_hash()
        return map_hash

    def _save_raw_data(self) -> None:
        """Save collected raw data to a JSON file."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"match_{self.current_match_id}_{timestamp}.json"
            filepath = RAW_DATA_DIR / filename

            with open(filepath, "w", encoding="utf-8") as handle:
                json.dump(
                    {
                        "match_id": self.current_match_id,
                        "captured_at": timestamp,
                        "tick_count": len(
                            [
                                data
                                for data in self.raw_data
                                if data["endpoint"] == "map_obj.json"
                            ]
                        ),
                        "raw_responses": self.raw_data,
                    },
                    handle,
                    indent=2,
                )

            logger.info("Raw data saved: %s", filepath)
        except Exception as e:
            logger.warning("Failed to save raw data: %s", e)

    def _mark_match_nuke(self) -> None:
        """Persist a nuke detection flag for the current match."""
        if not self.current_match_id:
            return
        if self.current_match_nuke_detected:
            return
        db.update_match_nuke(self.conn, self.current_match_id, 1)
        self.current_match_nuke_detected = True

    @staticmethod
    def _normalize_map_name(name: Optional[str]) -> str:
        """Normalize map names for comparison."""
        if not name:
            return ""
        normalized = name.strip()
        normalized = re.sub(r"^[^A-Za-z0-9]+", "", normalized)
        return normalized.strip().lower()

    def _get_map_base_name(self, info: Optional[MapInfo]) -> str:
        """Return a normalized map name for switch detection."""
        if not info:
            return ""
        return self._normalize_map_name(info.display_name)

    def _is_nuke_map_switch(
        self,
        previous: Optional[MapInfo],
        current: Optional[MapInfo],
    ) -> bool:
        """Return True when a ground or naval map switches to its air variant."""
        if not previous or not current:
            return False
        if previous.battle_type not in (BattleType.GROUND, BattleType.NAVAL):
            return False
        if current.battle_type != BattleType.AIR:
            return False
        prev_name = self._get_map_base_name(previous)
        curr_name = self._get_map_base_name(current)
        return bool(prev_name) and prev_name == curr_name

    def _compute_air_transform(
        self,
        prev_objects: List[Dict[str, Any]],
        curr_objects: List[Dict[str, Any]],
    ) -> Optional[Tuple[float, float, float, float]]:
        """
        Compute air view transformation parameters by matching ground objects.
        Returns (a, b, c, d) where x_air = a*x_ground + b and y_air = c*y_ground + d.
        """
        excluded_icons = {
            "player",
            "Player",
            "airdefence",
            "air_defence",
            "AirDefence",
        }
        excluded_types = {"aircraft", "airfield", "respawn_base_fighter"}

        def is_ground_object(obj: Dict[str, Any]) -> bool:
            """Return True for ground objects that should be used for matching."""
            icon = obj.get("icon", "")
            obj_type = obj.get("type", "")
            if icon in excluded_icons:
                return False
            if obj_type in excluded_types:
                return False
            return True

        prev_ground = [o for o in prev_objects if is_ground_object(o)]
        curr_ground = [o for o in curr_objects if is_ground_object(o)]

        if len(prev_ground) < 3 or len(curr_ground) < 3:
            logger.debug(
                "Not enough ground objects for transform: prev=%s, curr=%s",
                len(prev_ground),
                len(curr_ground),
            )
            return None

        prev_by_icon: Dict[str, List[Dict[str, Any]]] = {}
        for obj in prev_ground:
            icon = obj.get("icon", "unknown")
            if icon not in prev_by_icon:
                prev_by_icon[icon] = []
            prev_by_icon[icon].append(obj)

        curr_by_icon: Dict[str, List[Dict[str, Any]]] = {}
        for obj in curr_ground:
            icon = obj.get("icon", "unknown")
            if icon not in curr_by_icon:
                curr_by_icon[icon] = []
            curr_by_icon[icon].append(obj)

        x1_list, y1_list, x2_list, y2_list = [], [], [], []
        for icon, prev_list in prev_by_icon.items():
            curr_list = curr_by_icon.get(icon, [])
            for i, prev_obj in enumerate(prev_list):
                if i < len(curr_list):
                    curr_obj = curr_list[i]
                    x1_list.append(prev_obj.get("x", 0))
                    y1_list.append(prev_obj.get("y", 0))
                    x2_list.append(curr_obj.get("x", 0))
                    y2_list.append(curr_obj.get("y", 0))

        if len(x1_list) < 3:
            logger.debug(
                "Not enough matched objects for transform: %s",
                len(x1_list),
            )
            return None

        x1 = np.array(x1_list)
        y1 = np.array(y1_list)
        x2 = np.array(x2_list)
        y2 = np.array(y2_list)

        A_x = np.column_stack([x1, np.ones_like(x1)])
        params_x, residuals_x, _, _ = np.linalg.lstsq(A_x, x2, rcond=None)
        a, b = params_x

        A_y = np.column_stack([y1, np.ones_like(y1)])
        params_y, residuals_y, _, _ = np.linalg.lstsq(A_y, y2, rcond=None)
        c, d = params_y

        if a <= 0 or c <= 0:
            logger.warning("Invalid transform scale factors: a=%s, c=%s", a, c)
            return None
        if a > 0.5 or c > 0.5:
            logger.debug(
                "Transform scale too large (not air zoom): a=%s, c=%s",
                a,
                c,
            )
            return None

        x2_pred = a * x1 + b
        y2_pred = c * y1 + d
        error_x = np.mean(np.abs(x2_pred - x2))
        error_y = np.mean(np.abs(y2_pred - y2))

        if error_x > 0.01 or error_y > 0.01:
            logger.warning(
                "Transform error too high: err_x=%s, err_y=%s",
                error_x,
                error_y,
            )
            return None

        logger.info(
            "Air transform computed: a=%.6f, b=%.6f, c=%.6f, d=%.6f "
            "(error: %.6f, %.6f)",
            a,
            b,
            c,
            d,
            error_x,
            error_y,
        )
        return (a, b, c, d)

    def _apply_inverse_transform(self, x: float, y: float) -> Tuple[float, float]:
        """Convert air-view coordinates back to ground reference frame."""
        if not self._air_transform_params:
            return x, y
        a, b, c, d = self._air_transform_params
        if a == 0 or c == 0:
            return x, y
        x_ground = (x - b) / a
        y_ground = (y - d) / c
        return x_ground, y_ground

_capturer: Optional[Capturer] = None


def get_capturer() -> Capturer:
    """Return the global capturer instance."""
    global _capturer
    if _capturer is None:
        _capturer = Capturer()
    return _capturer


def start_capture() -> None:
    """Start capturing."""
    get_capturer().start()


def stop_capture() -> None:
    """Stop capturing."""
    if _capturer:
        _capturer.stop()
