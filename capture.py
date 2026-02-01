"""
Capture module for WT Plotter.
Polls War Thunder localhost:8111 API at 1-second intervals.
"""
import time
import threading
import logging
import hashlib
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, List, Dict, Any, Tuple
import requests
import aiohttp
from requests.adapters import HTTPAdapter

import db
from map_hashes import lookup_map_info, BattleType, MapInfo

# =============================================================================
# FEATURE FLAGS
# =============================================================================
SAVE_RAW_DATA = False  # Set to True to save raw API responses for debugging
# =============================================================================

# Raw data folder for debug
RAW_DATA_DIR = Path(__file__).parent / "data" / "raw"
MAPS_DIR = Path(__file__).parent / "data" / "maps"

# API endpoints (same as WT-Plotter)
BASE_URL = "http://localhost:8111"
MAP_OBJ_URL = f"{BASE_URL}/map_obj.json"
MAP_IMG_URL = f"{BASE_URL}/map.img"
MAP_INFO_URL = f"{BASE_URL}/map_info.json"
INDICATORS_URL = f"{BASE_URL}/indicators"
STATE_URL = f"{BASE_URL}/state"

POLL_INTERVAL = 0.2

# Match end grace period - wait this many seconds before ending match when API fails
MATCH_END_GRACE_PERIOD = 20.0

logger = logging.getLogger(__name__)

class Capturer:
    """
    Captures match data from War Thunder localhost API.
    Follows WT-Plotter state machine logic.
    """
    
    def __init__(self, on_match_start: Callable = None, on_match_end: Callable = None,
                 on_position: Callable = None):
        self.conn = db.get_connection()
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # State tracking (like WT-Plotter: map_image presence = in-match state)
        self.current_match_id: Optional[int] = None
        self.match_start_time: float = 0
        self.poi_captured = False
        self.has_map_image = False  # Key state: True = in match
        self.match_end_grace_start: Optional[float] = None  # When match first became invalid
        self.current_map_hash: str = ""  # Current map hash for change detection
        self.current_map_info: Optional[MapInfo] = None
        self.current_air_map_hash: str = ""
        
        # Current live state (for UI feedback)
        self.current_army_type: str = 'tank'
        self.current_vehicle_type: str = ''

        # Raw data collection for debug
        self.raw_data: List[Dict[str, Any]] = []
        if SAVE_RAW_DATA:
            RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Callbacks
        self.on_match_start = on_match_start
        self.on_match_end = on_match_end
        self.on_position = on_position
        
        # HTTP session for keep-alive
        self.session = requests.Session()
        self.session.timeout = 2.0
        # Configure adapter for localhost to handle connection resets better
        adapter = HTTPAdapter(pool_connections=1, pool_maxsize=1, max_retries=0)
        self.session.mount('http://localhost:8111', adapter)
        self.session.headers.update({'Connection': 'keep-alive'})
    
    def start(self):
        """Start the capture loop in a background thread."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        logger.info("Capture started")
    
    def stop(self):
        """Stop the capture loop."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=3.0)
        logger.info("Capture stopped")
    
    def _loop(self):
        """Main capture loop - runs every second."""
        while self.running:
            try:
                self._tick()
            except Exception as e:
                logger.error(f"Capture error: {e}")
            time.sleep(POLL_INTERVAL)
    
    def _tick(self):
        """
        Single capture tick - follows WT-Plotter state machine:
        - shouldLoadMap: no map image + valid=true → start match
        - shouldUpdateMarkers: has map image + valid=true → capture positions
        - shouldEndMatch: has map image + valid=false → end match
        """
        # Fetch all three endpoints concurrently using async
        async def fetch_all():
            async with aiohttp.ClientSession() as session:
                tasks = [
                    self._get_map_info_async(session),
                    self._get_indicators_data_async(session),
                    self._get_map_obj_data_async(session)
                ]
                return await asyncio.gather(*tasks)
        
        map_info, indicators_data, map_obj_data = asyncio.run(fetch_all())
        
        match_running = map_info.get('valid', False) if map_info else False
        
        if not self.has_map_image and match_running:
            # shouldLoadMap: Start new match
            self._start_match()
        elif self.has_map_image and match_running:
            # shouldUpdateMarkers: Capture positions
            # Reset grace period since match is running again
            self.match_end_grace_start = None
            self._capture_positions_with_data(indicators_data, map_obj_data)
        elif self.has_map_image and not match_running:
            # Check if this is actually a new match (map changed) or grace period handling
            current_map_hash = self._get_current_map_hash()
            if current_map_hash:
                base_context = "ground"
                if self.current_map_info:
                    base_context = self.current_map_info.battle_type.value
                map_info = lookup_map_info(current_map_hash, context=base_context)
                if map_info.display_name == "No Map" or map_info.map_id == "no_map":
                    # Map changed to "No Map" - match has ended
                    logger.info("Map changed to 'No Map', ending match")
                    self._end_match()
                elif current_map_hash != self.current_map_hash:
                    # Map changed! This is a new match, not a recovery
                    logger.info(f"Map changed during grace period ({self.current_map_hash} -> {current_map_hash}), starting new match")
                    self._end_match()  # End the old match
                    self._start_match()  # Start new match immediately
                else:
                    # Same map, handle grace period
                    current_time = time.time()
                    if self.match_end_grace_start is None:
                        # Start grace period
                        self.match_end_grace_start = current_time
                        logger.info(f"Match temporarily invalid, starting {MATCH_END_GRACE_PERIOD}s grace period")
                    elif current_time - self.match_end_grace_start >= MATCH_END_GRACE_PERIOD:
                        # Grace period expired, end match
                        logger.info(f"Match invalid for {MATCH_END_GRACE_PERIOD}s, ending match")
                        self._end_match()
                    # else: still in grace period, continue match
            else:
                # No hash available, handle grace period
                current_time = time.time()
                if self.match_end_grace_start is None:
                    # Start grace period
                    self.match_end_grace_start = current_time
                    logger.info(f"Match temporarily invalid, starting {MATCH_END_GRACE_PERIOD}s grace period")
                elif current_time - self.match_end_grace_start >= MATCH_END_GRACE_PERIOD:
                    # Grace period expired, end match
                    logger.info(f"Match invalid for {MATCH_END_GRACE_PERIOD}s, ending match")
                    self._end_match()
                # else: still in grace period, continue match
        # else: no map image and not running = waiting for match
    
    async def _get_map_info_async(self, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        """Get current map_info.json data asynchronously."""
        try:
            logger.debug("Getting map info from map_info.json endpoint")
            async with session.get(MAP_INFO_URL, timeout=aiohttp.ClientTimeout(total=1.0)) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception as e:
            logger.warning(f"Failed to get map info: {e}")
        return None

    async def _get_indicators_data_async(self, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        """Get indicators data asynchronously."""
        try:
            logger.debug("Getting indicators data from indicators endpoint")
            async with session.get(INDICATORS_URL, timeout=aiohttp.ClientTimeout(total=1.0)) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception as e:
            logger.warning(f"Failed to get indicators data: {e}")
        return None

    async def _get_map_obj_data_async(self, session: aiohttp.ClientSession) -> Optional[List[Dict[str, Any]]]:
        """Get map objects data asynchronously."""
        try:
            logger.debug("Getting map objects data from map_obj.json endpoint")
            async with session.get(MAP_OBJ_URL, timeout=aiohttp.ClientTimeout(total=1.0)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if isinstance(data, list):
                        return data
        except Exception as e:
            logger.warning(f"Failed to get map objects data: {e}")
        return None
    
    def _start_match(self):
        """Start tracking a new match."""
        logger.info("Match started - loading map")
        self.match_start_time = time.time()
        self.poi_captured = False
        self.has_map_image = True  # Mark as in-match state
        self.match_end_grace_start = None  # Reset grace period
        self.raw_data = []  # Reset raw data collection
        
        map_hash = ""
        map_image = None
        map_name = "Unknown Map"
        map_id = None
        battle_type = None
        map_info: Optional[MapInfo] = None
        
        # Capture initial map_info for raw data
        try:
            resp = self.session.get(MAP_INFO_URL, timeout=2.0)
            if resp.status_code == 200:
                map_info = resp.json()
                if SAVE_RAW_DATA:
                    self.raw_data.append({
                        'endpoint': 'map_info.json',
                        'timestamp': 0,
                        'data': map_info
                    })
        except:
            pass
        
        try:
            # Get map image first - we need dhash for map name lookup
            resp = self.session.get(MAP_IMG_URL, timeout=3.0)
            if resp.status_code == 200:
                map_image = resp.content
                map_hash = self._compute_dhash(map_image)
                # Use dhash lookup to get readable map metadata (like WT-Plotter)
                map_info = lookup_map_info(map_hash, context="ground")
                map_name = map_info.display_name
                map_id = map_info.map_id
                battle_type = map_info.battle_type.value
                logger.info(f"Map hash: {map_hash} ({len(map_hash)} chars) -> {map_name}")
        except Exception as e:
            logger.warning(f"Failed to get map image: {e}")

        if map_image:
            self._save_map_image(map_image, map_id, map_hash)
        
        # Create match in database
        self.current_match_id = db.start_match(
            self.conn,
            map_hash=map_hash,
            map_name=map_name,
            map_id=map_id,
            battle_type=battle_type,
            map_image=None
        )
        
        # Store current map hash for change detection
        self.current_map_hash = map_hash
        self.current_map_info = map_info
        self.current_air_map_hash = ""
        
        if self.on_match_start:
            self.on_match_start(self.current_match_id)
        
        # Immediately capture initial positions
        async def fetch_initial():
            async with aiohttp.ClientSession() as session:
                indicators_task = self._get_indicators_data_async(session)
                map_obj_task = self._get_map_obj_data_async(session)
                indicators_data, map_obj_data = await asyncio.gather(indicators_task, map_obj_task)
                return indicators_data, map_obj_data
        
        indicators_data, map_obj_data = asyncio.run(fetch_initial())
        self._capture_positions_with_data(indicators_data, map_obj_data)
    
    def _end_match(self):
        """End the current match."""
        logger.info("Match ended")
        
        # Save raw data before clearing
        if SAVE_RAW_DATA and self.current_match_id and self.raw_data:
            self._save_raw_data()
        
        if self.current_match_id:
            db.end_match(self.conn, self.current_match_id)
            if self.on_match_end:
                self.on_match_end(self.current_match_id)
        
        # Clear state (like WT-Plotter clearing map image)
        self.current_match_id = None
        self.poi_captured = False
        self.has_map_image = False  # Key: prevents new match until valid=true again
        self.match_end_grace_start = None  # Reset grace period
        self.current_map_hash = ""  # Reset map hash
        self.current_map_info = None
        self.current_air_map_hash = ""
        self.raw_data = []
    
    def _capture_positions_with_data(self, indicators_data: Optional[Dict[str, Any]], map_obj_data: Optional[List[Dict[str, Any]]]):
        """Capture current positions using pre-fetched data."""
        if not self.current_match_id:
            return
        
        try:
            logger.debug("Capturing positions from pre-fetched data")

            # Use pre-fetched indicators data
            army_type = indicators_data.get('army') if indicators_data else None
            vehicle_type = indicators_data.get('type', '') if indicators_data else ''
            # Remove model prefix (tankModels/, aircraftModels/, etc.)
            if '/' in vehicle_type:
                vehicle_type = vehicle_type.split('/', 1)[1]
            vehicle_type = vehicle_type if vehicle_type else None
            
            self.current_army_type = army_type or 'tank'
            self.current_vehicle_type = vehicle_type or ''

            self._maybe_capture_air_map(army_type)
            
            # Use pre-fetched map_obj data
            if not map_obj_data:
                return
            
            objects = map_obj_data
            
            timestamp = time.time() - self.match_start_time
            
            # Save raw data for debug
            if SAVE_RAW_DATA:
                logger.debug("Saving raw map_obj.json data for debug")
                self.raw_data.append({
                    'endpoint': 'map_obj.json',
                    'timestamp': timestamp,
                    'data': objects
                })
                if indicators_data:
                    self.raw_data.append({
                        'endpoint': 'indicators',
                        'timestamp': timestamp,
                        'data': indicators_data
                    })
            
            positions = []
            
            logger.debug("Processing map objects for position capture")
            for obj in objects:
                x = obj.get('x', -1)
                y = obj.get('y', -1)
                dx = obj.get('dx')
                dy = obj.get('dy')

                # Skip invalid positions (WT-Plotter validation)
                if x <= 0 or x >= 1 or y <= 0 or y >= 1:
                    continue

                obj_type = obj.get('type', 'unknown')

                # On enregistre tout, même aircraft, mais le viewer devra ignorer type==aircraft

                is_poi = obj_type in ('capture_zone', 'respawn_base_tank', 'respawn_base_fighter', 'airfield')

                # Skip POI if already captured (like WT-Plotter), but continue capturing capture zones
                if is_poi and obj_type != 'capture_zone' and self.poi_captured:
                    continue

                pos = {
                    'x': x,
                    'y': y,
                    'color': obj.get('color', '#FFFFFF'),
                    'type': obj_type,
                    'icon': obj.get('icon', 'unknown'),
                    'timestamp': timestamp,
                    'is_poi': 1 if is_poi else 0,
                    'army_type': army_type or 'tank',
                    'vehicle_type': vehicle_type or '',
                    'is_player_air': 1 if (army_type == 'air') else 0
                }
                # Ajout dx/dy si présents
                if dx is not None:
                    pos['dx'] = dx
                if dy is not None:
                    pos['dy'] = dy
                positions.append(pos)
            
            if positions:
                logger.debug(f"Captured {len(positions)} positions")
                db.add_positions(self.conn, self.current_match_id, positions)
                if self.on_position:
                    self.on_position(self.current_match_id, positions)
            
            # Mark POI as captured after first successful capture
            if any(p['is_poi'] for p in positions):
                self.poi_captured = True
                
            logger.debug("Finished capturing positions")
        except Exception as e:
            logger.warning(f"Failed to capture positions: {e}")

    def _maybe_capture_air_map(self, army_type: Optional[str]):
        if not self.current_match_id or not self.current_map_info:
            return
        if army_type != 'air':
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

        air_context = "air"
        if self.current_map_info.battle_type == BattleType.GROUND:
            air_context = "air_in_ground"
        elif self.current_map_info.battle_type == BattleType.NAVAL:
            air_context = "air_in_naval"
        air_info = lookup_map_info(map_hash, context=air_context)
        if map_image:
            self._save_map_image(map_image, air_info.map_id, map_hash)

        db.update_match_air_map(
            self.conn,
            self.current_match_id,
            air_map_hash=map_hash,
            air_map_name=air_info.display_name,
            air_map_id=air_info.map_id,
            air_battle_type=air_info.battle_type.value
        )
        self.current_air_map_hash = map_hash

    def _save_map_image(self, map_image: bytes, map_id: Optional[str], map_hash: Optional[str]):
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
            logger.warning(f"Failed to save map image to disk: {e}")

    def _get_current_map_image_and_hash(self) -> Tuple[Optional[bytes], Optional[str]]:
        try:
            resp = self.session.get(MAP_IMG_URL, timeout=1.0)
            if resp.status_code == 200:
                map_image = resp.content
                return map_image, self._compute_dhash(map_image)
        except Exception as e:
            logger.debug(f"Failed to get current map image: {e}")
        return None, None
    
    def _compute_dhash(self, image_data: bytes, size: int = 16) -> str:
        """
        Compute difference hash (dhash) matching WT-Plotter's algorithm.
        - Resize to size x (size-1) = 16x15 by default
        - Compare horizontally adjacent pixels (left > right = 1)
        - Produces 56 hex characters
        """
        try:
            from PIL import Image
            import io
            
            img = Image.open(io.BytesIO(image_data))
            img = img.convert('L')  # Grayscale
            # WT-Plotter: scaled(size, size - 1) = 16x15
            img = img.resize((size, size - 1), Image.Resampling.LANCZOS)
            
            # Compare horizontally adjacent pixels (like WT-Plotter)
            pixels = list(img.getdata())
            hash_bits = []
            width = size
            height = size - 1
            
            for y in range(height):
                for x in range(width - 1):
                    left = pixels[y * width + x]
                    right = pixels[y * width + x + 1]
                    # WT-Plotter: left > right = 1
                    hash_bits.append(1 if left > right else 0)
            
            # Convert to hex string (4 bits per hex char)
            hex_str = ''
            for i in range(0, len(hash_bits), 4):
                nibble = hash_bits[i:i+4]
                while len(nibble) < 4:
                    nibble.append(0)
                value = (nibble[0] << 3) | (nibble[1] << 2) | (nibble[2] << 1) | nibble[3]
                hex_str += format(value, 'x')
            
            logger.debug(f"Computed dhash: {hex_str} ({len(hex_str)} chars)")
            return hex_str
        except Exception as e:
            logger.warning(f"Failed to compute dhash: {e}")
            # Fallback to md5
            return hashlib.md5(image_data).hexdigest()[:16]

    def _get_current_map_hash(self) -> Optional[str]:
        """Get current map hash for change detection during grace period."""
        _, map_hash = self._get_current_map_image_and_hash()
        return map_hash
    
    def _save_raw_data(self):
        """Save collected raw data to JSON file for debugging."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"match_{self.current_match_id}_{timestamp}.json"
            filepath = RAW_DATA_DIR / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'match_id': self.current_match_id,
                    'captured_at': timestamp,
                    'tick_count': len([d for d in self.raw_data if d['endpoint'] == 'map_obj.json']),
                    'raw_responses': self.raw_data
                }, f, indent=2)
            
            logger.info(f"Raw data saved: {filepath}")
        except Exception as e:
            logger.warning(f"Failed to save raw data: {e}")


# Global capturer instance
_capturer: Optional[Capturer] = None


def get_capturer() -> Capturer:
    """Get or create the global capturer instance."""
    global _capturer
    if _capturer is None:
        _capturer = Capturer()
    return _capturer


def start_capture():
    """Start capturing."""
    get_capturer().start()


def stop_capture():
    """Stop capturing."""
    if _capturer:
        _capturer.stop()
