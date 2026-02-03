"""
Database module for WT Plotter.
Simple SQLite storage for matches and positions.
"""
import sqlite3
from pathlib import Path
from dataclasses import dataclass
from functools import cached_property
from typing import Optional, List, Dict
from datetime import datetime
import logging

DB_PATH = Path(__file__).parent / "data" / "matches.db"

_ENUM_TABLES = {
    "enum_colors": "color",
    "enum_types": "type",
    "enum_icons": "icon",
    "enum_army_types": "army_type",
    "enum_vehicle_types": "vehicle_type",
}

_ENUM_CACHE: Dict[str, Dict[str, int]] = {table: {} for table in _ENUM_TABLES}

logger = logging.getLogger(__name__)

@dataclass
class Match:
    id: int
    started_at: str
    ended_at: Optional[str]
    map_hash: str
    air_map_hash: Optional[str] = None
    initial_capture_count: Optional[int] = None
    initial_capture_x: Optional[float] = None
    initial_capture_y: Optional[float] = None
    nuke_detected: int = 0
    # Air view transformation parameters: x_air = a*x + b, y_air = c*y + d
    air_transform_a: Optional[float] = None
    air_transform_b: Optional[float] = None
    air_transform_c: Optional[float] = None
    air_transform_d: Optional[float] = None

    @cached_property
    def _map_info(self):
        from map_hashes import lookup_map_info, UNKNOWN_MAP_INFO
        if not self.map_hash:
            return UNKNOWN_MAP_INFO
        return lookup_map_info(self.map_hash)

    @cached_property
    def _air_map_info(self):
        from map_hashes import lookup_map_info, UNKNOWN_MAP_INFO
        if not self.air_map_hash:
            return UNKNOWN_MAP_INFO
        return lookup_map_info(self.air_map_hash)

    @property
    def map_name(self) -> str:
        return self._map_info.display_name

    @property
    def map_id(self) -> str:
        return self._map_info.map_id

    @property
    def battle_type(self) -> str:
        return self._map_info.battle_type.value

    @property
    def air_map_name(self) -> str:
        return self._air_map_info.display_name

    @property
    def air_map_id(self) -> str:
        return self._air_map_info.map_id

    @property
    def air_battle_type(self) -> str:
        return self._air_map_info.battle_type.value


@dataclass
class Position:
    id: int
    match_id: int
    x: float
    y: float
    color: str
    type: str
    icon: str
    timestamp: int  # milliseconds since match start
    is_poi: bool
    army_type: str = 'tank'  # 'tank' or 'air'
    vehicle_type: str = ''  # e.g., 'fr_leclerc_s1', 'rafale_c_f3'
    is_player_air: int = 0  # 1 if position is from player's aircraft, else 0
    is_player_air_view: int = 0  # 1 if air-view conditions detected for this tick
    x_ground: Optional[float] = None  # x converted back to ground reference frame
    y_ground: Optional[float] = None  # y converted back to ground reference frame


def get_connection() -> sqlite3.Connection:
    """Get database connection, creating tables if needed."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    _configure_connection(conn)
    _create_tables(conn)
    return conn


def _configure_connection(conn: sqlite3.Connection):
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA temp_store = MEMORY")
    conn.execute("PRAGMA auto_vacuum = INCREMENTAL")
    conn.execute("PRAGMA busy_timeout = 5000")


def _reset_enum_cache():
    for table_cache in _ENUM_CACHE.values():
        table_cache.clear()


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?",
        (table_name,)
    ).fetchone()
    return row is not None


def _ensure_enum_value(conn: sqlite3.Connection, table_name: str, value: Optional[str]) -> int:
    if value is None:
        value = ""
    cache = _ENUM_CACHE[table_name]
    cached = cache.get(value)
    if cached is not None:
        return cached
    conn.execute(
        f"INSERT OR IGNORE INTO {table_name} (value) VALUES (?)",
        (value,)
    )
    row = conn.execute(
        f"SELECT id FROM {table_name} WHERE value = ?",
        (value,)
    ).fetchone()
    value_id = row["id"]
    cache[value] = value_id
    return value_id


def _quantize_coord(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    return round(float(value), 5)


def _to_timestamp_ms(seconds: float) -> int:
    return int(round(float(seconds) * 1000))


def _create_tables(conn: sqlite3.Connection):
    """Create database tables for the current schema."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            map_hash TEXT,
            air_map_hash TEXT,
            initial_capture_count INTEGER,
            initial_capture_x REAL,
            initial_capture_y REAL,
            nuke_detected INTEGER NOT NULL DEFAULT 0,
            air_transform_a REAL,
            air_transform_b REAL,
            air_transform_c REAL,
            air_transform_d REAL
        );

        CREATE TABLE IF NOT EXISTS enum_colors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS enum_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS enum_icons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS enum_army_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS enum_vehicle_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value TEXT NOT NULL UNIQUE
        );
        
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            x REAL NOT NULL,
            y REAL NOT NULL,
            color_id INTEGER NOT NULL,
            type_id INTEGER NOT NULL,
            icon_id INTEGER NOT NULL,
            timestamp_ms INTEGER NOT NULL,
            is_poi INTEGER NOT NULL DEFAULT 0,
            army_type_id INTEGER NOT NULL,
            vehicle_type_id INTEGER NOT NULL,
            is_player_air INTEGER NOT NULL DEFAULT 0,
            is_player_air_view INTEGER NOT NULL DEFAULT 0,
            x_ground REAL,
            y_ground REAL,
            FOREIGN KEY (match_id) REFERENCES matches(id),
            FOREIGN KEY (color_id) REFERENCES enum_colors(id),
            FOREIGN KEY (type_id) REFERENCES enum_types(id),
            FOREIGN KEY (icon_id) REFERENCES enum_icons(id),
            FOREIGN KEY (army_type_id) REFERENCES enum_army_types(id),
            FOREIGN KEY (vehicle_type_id) REFERENCES enum_vehicle_types(id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_positions_match ON positions(match_id);
        CREATE INDEX IF NOT EXISTS idx_positions_timestamp ON positions(match_id, timestamp_ms);
    """)
    conn.commit()

def start_match(
    conn: sqlite3.Connection,
    map_hash: str = "",
    nuke_detected: int = 0
) -> int:
    """Start a new match, returns match ID."""
    cur = conn.execute(
        """INSERT INTO matches
           (started_at, map_hash, nuke_detected)
           VALUES (?, ?, ?)""",
        (datetime.now().isoformat(), map_hash, nuke_detected)
    )
    conn.commit()
    return cur.lastrowid


def update_match_air_map(
    conn: sqlite3.Connection,
    match_id: int,
    air_map_hash: str
):
    """Update air map metadata for a match."""
    conn.execute(
        """UPDATE matches
           SET air_map_hash = ?
           WHERE id = ?""",
        (air_map_hash, match_id)
    )
    conn.commit()


def end_match(conn: sqlite3.Connection, match_id: int):
    """Mark a match as ended."""
    conn.execute(
        "UPDATE matches SET ended_at = ? WHERE id = ?",
        (datetime.now().isoformat(), match_id)
    )
    conn.commit()


def update_match_nuke(conn: sqlite3.Connection, match_id: int, nuke_detected: int = 1):
    """Mark a match as a nuke match."""
    conn.execute(
        "UPDATE matches SET nuke_detected = ? WHERE id = ?",
        (nuke_detected, match_id)
    )
    conn.commit()


def update_match_initial_capture(
    conn: sqlite3.Connection,
    match_id: int,
    initial_capture_count: int,
    initial_capture_x: float,
    initial_capture_y: float
):
    """Store initial capture-zone count and barycenter for a match."""
    conn.execute(
        """UPDATE matches
           SET initial_capture_count = ?,
               initial_capture_x = ?,
               initial_capture_y = ?
           WHERE id = ?""",
        (
            initial_capture_count,
            round(float(initial_capture_x), 6),
            round(float(initial_capture_y), 6),
            match_id
        )
    )
    conn.commit()


def update_match_air_transform(
    conn: sqlite3.Connection,
    match_id: int,
    a: float,
    b: float,
    c: float,
    d: float
):
    """Store air view transformation parameters for a match.
    
    The transformation is: x_air = a*x_ground + b, y_air = c*y_ground + d
    To convert back: x_ground = (x_air - b) / a, y_ground = (y_air - d) / c
    """
    conn.execute(
        """UPDATE matches
           SET air_transform_a = ?,
               air_transform_b = ?,
               air_transform_c = ?,
               air_transform_d = ?
           WHERE id = ?""",
        (a, b, c, d, match_id)
    )
    conn.commit()


def add_positions(conn: sqlite3.Connection, match_id: int, positions: List[dict]):
    """Add multiple positions to a match."""
    if not positions:
        return

    rows = []
    for p in positions:
        color_id = _ensure_enum_value(conn, "enum_colors", p.get('color', ''))
        type_id = _ensure_enum_value(conn, "enum_types", p.get('type', ''))
        icon_id = _ensure_enum_value(conn, "enum_icons", p.get('icon', ''))
        army_type_id = _ensure_enum_value(conn, "enum_army_types", p.get('army_type', 'tank'))
        vehicle_type_id = _ensure_enum_value(conn, "enum_vehicle_types", p.get('vehicle_type', ''))

        rows.append((
            match_id,
            _quantize_coord(p['x']),
            _quantize_coord(p['y']),
            color_id,
            type_id,
            icon_id,
            _to_timestamp_ms(p['timestamp']),
            p.get('is_poi', 0),
            army_type_id,
            vehicle_type_id,
            p.get('is_player_air', 0),
            p.get('is_player_air_view', 0),
            _quantize_coord(p.get('x_ground')),
            _quantize_coord(p.get('y_ground'))
        ))

    conn.executemany(
        """INSERT INTO positions (
                match_id, x, y, color_id, type_id, icon_id, timestamp_ms,
                is_poi, army_type_id, vehicle_type_id, is_player_air, is_player_air_view,
                x_ground, y_ground
           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        rows
    )
    conn.commit()


def get_active_match(conn: sqlite3.Connection) -> Optional[Match]:
    """Get the currently active (not ended) match."""
    row = conn.execute(
        "SELECT * FROM matches WHERE ended_at IS NULL ORDER BY id DESC LIMIT 1"
    ).fetchone()
    if row:
        return Match(**dict(row))
    return None


def get_match(conn: sqlite3.Connection, match_id: int) -> Optional[Match]:
    """Get a specific match by ID."""
    row = conn.execute("SELECT * FROM matches WHERE id = ?", (match_id,)).fetchone()
    if row:
        return Match(**dict(row))
    return None


def get_all_matches(conn: sqlite3.Connection) -> List[Match]:
    """Get all matches, newest first."""
    rows = conn.execute(
        "SELECT * FROM matches ORDER BY started_at DESC"
    ).fetchall()
    return [Match(**dict(row)) for row in rows]


def get_positions(conn: sqlite3.Connection, match_id: int, since_ts_ms: int = 0) -> List[Position]:
    """Get positions for a match, optionally since a given timestamp (ms)."""
    rows = conn.execute(
        """
        SELECT
            p.id,
            p.match_id,
            p.x,
            p.y,
            c.value AS color,
            t.value AS type,
            i.value AS icon,
            p.timestamp_ms AS timestamp,
            p.is_poi,
            at.value AS army_type,
            vt.value AS vehicle_type,
            p.is_player_air,
            p.is_player_air_view,
            p.x_ground,
            p.y_ground
        FROM positions p
        LEFT JOIN enum_colors c ON c.id = p.color_id
        LEFT JOIN enum_types t ON t.id = p.type_id
        LEFT JOIN enum_icons i ON i.id = p.icon_id
        LEFT JOIN enum_army_types at ON at.id = p.army_type_id
        LEFT JOIN enum_vehicle_types vt ON vt.id = p.vehicle_type_id
        WHERE p.match_id = ? AND p.timestamp_ms >= ?
        ORDER BY p.timestamp_ms
        """,
        (match_id, int(since_ts_ms))
    ).fetchall()
    return [Position(**dict(row)) for row in rows]


def get_positions_count(conn: sqlite3.Connection, match_id: int) -> int:
    """Get the number of positions for a match."""
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM positions WHERE match_id = ?", (match_id,)
    ).fetchone()
    return row['cnt'] if row else 0


def delete_match(conn: sqlite3.Connection, match_id: int):
    """Delete a match and its positions."""
    conn.execute("DELETE FROM positions WHERE match_id = ?", (match_id,))
    conn.execute("DELETE FROM matches WHERE id = ?", (match_id,))
    conn.commit()
    try:
        conn.execute("VACUUM")
    except sqlite3.OperationalError:
        logger.warning("VACUUM failed after delete")


def close_orphaned_matches(conn: sqlite3.Connection) -> int:
    """Close any matches that were left without ended_at (e.g., after hard quit).
    Returns the number of matches closed."""
    cur = conn.execute(
        "UPDATE matches SET ended_at = datetime('now') WHERE ended_at IS NULL"
    )
    conn.commit()
    return cur.rowcount
