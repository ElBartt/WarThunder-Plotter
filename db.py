"""
Database module for WT Plotter.
Simple SQLite storage for matches and positions.
"""
import sqlite3
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
import logging
import json

DB_PATH = Path(__file__).parent / "data" / "matches.db"

logger = logging.getLogger(__name__)

@dataclass
class Match:
    id: int
    started_at: str
    ended_at: Optional[str]
    map_hash: str
    map_name: str
    map_id: Optional[str] = None
    battle_type: Optional[str] = None
    air_map_hash: Optional[str] = None
    air_map_id: Optional[str] = None
    air_map_name: Optional[str] = None
    air_battle_type: Optional[str] = None
    map_image: Optional[bytes] = None


@dataclass
class Position:
    id: int
    match_id: int
    x: float
    y: float
    color: str
    type: str
    icon: str
    timestamp: float  # seconds since match start
    is_poi: bool
    army_type: str = 'tank'  # 'tank' or 'air'
    vehicle_type: str = ''  # e.g., 'fr_leclerc_s1', 'rafale_c_f3'
    dx: Optional[float] = None
    dy: Optional[float] = None
    is_player_air: int = 0  # 1 if position is from player's aircraft, else 0


def get_connection() -> sqlite3.Connection:
    """Get database connection, creating tables if needed."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    _create_tables(conn)
    return conn


def _create_tables(conn: sqlite3.Connection):
    """Create database tables."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            map_hash TEXT,
            map_name TEXT,
            map_id TEXT,
            battle_type TEXT,
            air_map_hash TEXT,
            air_map_id TEXT,
            air_map_name TEXT,
            air_battle_type TEXT,
            map_image BLOB
        );
        
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            x REAL NOT NULL,
            y REAL NOT NULL,
            dx REAL,
            dy REAL,
            color TEXT NOT NULL,
            type TEXT NOT NULL,
            icon TEXT NOT NULL,
            timestamp REAL NOT NULL,
            is_poi INTEGER NOT NULL DEFAULT 0,
            army_type TEXT NOT NULL DEFAULT 'tank',
            vehicle_type TEXT NOT NULL DEFAULT '',
            is_player_air INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (match_id) REFERENCES matches(id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_positions_match ON positions(match_id);
        CREATE INDEX IF NOT EXISTS idx_positions_timestamp ON positions(match_id, timestamp);
    """)
    conn.commit()

    # Migration: add army_type column if missing (for existing databases)
    try:
        conn.execute("ALTER TABLE positions ADD COLUMN army_type TEXT NOT NULL DEFAULT 'tank'")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    # Migration: add vehicle_type column if missing
    try:
        conn.execute("ALTER TABLE positions ADD COLUMN vehicle_type TEXT NOT NULL DEFAULT ''")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    # Migration: add dx column if missing
    try:
        conn.execute("ALTER TABLE positions ADD COLUMN dx REAL")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    # Migration: add dy column if missing
    try:
        conn.execute("ALTER TABLE positions ADD COLUMN dy REAL")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    # Migration: add is_player_air column if missing
    try:
        conn.execute("ALTER TABLE positions ADD COLUMN is_player_air INTEGER NOT NULL DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Migrations for matches table metadata
    try:
        conn.execute("ALTER TABLE matches ADD COLUMN map_id TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        conn.execute("ALTER TABLE matches ADD COLUMN battle_type TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        conn.execute("ALTER TABLE matches ADD COLUMN air_map_hash TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        conn.execute("ALTER TABLE matches ADD COLUMN air_map_id TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        conn.execute("ALTER TABLE matches ADD COLUMN air_map_name TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        conn.execute("ALTER TABLE matches ADD COLUMN air_battle_type TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists

def start_match(
    conn: sqlite3.Connection,
    map_hash: str = "",
    map_name: str = "",
    map_id: Optional[str] = None,
    battle_type: Optional[str] = None,
    map_image: bytes = None
) -> int:
    """Start a new match, returns match ID."""
    cur = conn.execute(
        """INSERT INTO matches
           (started_at, map_hash, map_name, map_id, battle_type, map_image)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (datetime.now().isoformat(), map_hash, map_name, map_id, battle_type, map_image)
    )
    conn.commit()
    return cur.lastrowid


def update_match_air_map(
    conn: sqlite3.Connection,
    match_id: int,
    air_map_hash: str,
    air_map_name: str,
    air_map_id: Optional[str] = None,
    air_battle_type: Optional[str] = None
):
    """Update air map metadata for a match."""
    conn.execute(
        """UPDATE matches
           SET air_map_hash = ?,
               air_map_name = ?,
               air_map_id = ?,
               air_battle_type = ?
           WHERE id = ?""",
        (air_map_hash, air_map_name, air_map_id, air_battle_type, match_id)
    )
    conn.commit()


def end_match(conn: sqlite3.Connection, match_id: int):
    """Mark a match as ended."""
    conn.execute(
        "UPDATE matches SET ended_at = ? WHERE id = ?",
        (datetime.now().isoformat(), match_id)
    )
    conn.commit()


def add_positions(conn: sqlite3.Connection, match_id: int, positions: List[dict]):
    """Add multiple positions to a match."""
    if not positions:
        return

    conn.executemany(
        """INSERT INTO positions (match_id, x, y, dx, dy, color, type, icon, timestamp, is_poi, army_type, vehicle_type, is_player_air)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [(
            match_id,
            p['x'],
            p['y'],
            p.get('dx'),
            p.get('dy'),
            p['color'],
            p['type'],
            p['icon'],
            p['timestamp'],
            p.get('is_poi', 0),
            p.get('army_type', 'tank'),
            p.get('vehicle_type', ''),
            p.get('is_player_air', 0)
        ) for p in positions]
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


def get_positions(conn: sqlite3.Connection, match_id: int, since_ts: float = 0) -> List[Position]:
    """Get positions for a match, optionally since a given timestamp."""
    rows = conn.execute(
        """SELECT * FROM positions WHERE match_id = ? AND timestamp >= ? ORDER BY timestamp""",
        (match_id, since_ts)
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


def close_orphaned_matches(conn: sqlite3.Connection) -> int:
    """Close any matches that were left without ended_at (e.g., after hard quit).
    Returns the number of matches closed."""
    cur = conn.execute(
        "UPDATE matches SET ended_at = datetime('now') WHERE ended_at IS NULL"
    )
    conn.commit()
    return cur.rowcount
