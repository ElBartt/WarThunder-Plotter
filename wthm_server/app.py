"""Minimal WTHM ingestion server (Flask).
Receives match envelopes and stores them in the central DB using the same schema.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from flask import Flask, jsonify, request

import sqlite3

# Reuse client DB schema helpers
import db
from config import PATHS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wthm_server")


def get_connection() -> sqlite3.Connection:
    # Central server DB path can be adjusted here if needed
    conn = sqlite3.connect(str(PATHS.db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Ensure tables exist as per shared schema
    # Reusing internal helpers
    db._configure_connection(conn)  # type: ignore
    db._create_tables(conn)  # type: ignore
    return conn


conn = get_connection()


app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/ingest", methods=["POST"])
def ingest():
    try:
        envelope: Dict[str, Any] = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "invalid_json"}), 400

    schema_version = int(envelope.get("schema_version", 0))
    if schema_version != 1:
        return jsonify({"error": "unsupported_schema", "expected": 1}), 400

    match = envelope.get("match") or {}
    ticks: List[Dict[str, Any]] = envelope.get("ticks") or []
    positions: List[Dict[str, Any]] = envelope.get("positions") or []

    # Insert match row preserving client timestamps and metadata
    cur = conn.execute(
        """
        INSERT INTO matches (
            started_at, ended_at, map_hash, air_map_hash,
            initial_capture_count, initial_capture_x, initial_capture_y,
            nuke_detected, air_transform_a, air_transform_b, air_transform_c, air_transform_d
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            match.get("started_at"),
            match.get("ended_at"),
            match.get("map_hash"),
            match.get("air_map_hash"),
            match.get("initial_capture_count"),
            match.get("initial_capture_x"),
            match.get("initial_capture_y"),
            int(match.get("nuke_detected", 0)),
            match.get("air_transform_a"),
            match.get("air_transform_b"),
            match.get("air_transform_c"),
            match.get("air_transform_d"),
        ),
    )
    central_match_id = cur.lastrowid
    conn.commit()

    # Group positions by tick_id for per-tick insertion with proper metadata
    positions_by_tick: Dict[int, List[Dict[str, Any]]] = {}
    for p in positions:
        tid = int(p.get("tick_id", 0))
        positions_by_tick.setdefault(tid, []).append(p)

    # Make a dict of ticks by id for quick lookup
    ticks_by_id = {int(t.get("id")): t for t in ticks}

    inserted_positions = 0
    for tid, pos_list in positions_by_tick.items():
        tick = ticks_by_id.get(tid)
        if not tick:
            continue
        # Build payload compatible with db.add_positions
        timestamp_seconds = float(tick.get("timestamp", 0)) / 1000.0
        army_type = tick.get("army_type")
        vehicle_type = tick.get("vehicle_type")
        is_player_air = int(tick.get("is_player_air", 0))
        is_player_air_view = int(tick.get("is_player_air_view", 0))

        payload_positions: List[Dict[str, Any]] = []
        for p in pos_list:
            payload_positions.append(
                {
                    "x": float(p.get("x", 0.0)),
                    "y": float(p.get("y", 0.0)),
                    "color": p.get("color", ""),
                    "type": p.get("type", ""),
                    "icon": p.get("icon", ""),
                    "timestamp": timestamp_seconds,
                    "is_poi": int(p.get("is_poi", 0)),
                    "army_type": army_type,
                    "vehicle_type": vehicle_type,
                    "is_player_air": is_player_air,
                    "is_player_air_view": is_player_air_view,
                    "x_ground": p.get("x_ground"),
                    "y_ground": p.get("y_ground"),
                }
            )
        # Insert via shared helper (creates tick + positions)
        db.add_positions(conn, central_match_id, payload_positions)
        inserted_positions += len(payload_positions)

    logger.info("Ingested match %s -> central_id=%s, ticks=%s, positions=%s",
                match.get("id"), central_match_id, len(ticks), inserted_positions)

    return jsonify({"ok": True, "central_match_id": central_match_id, "positions": inserted_positions})


def run(host: str = "127.0.0.1", port: int = 8000):
    logger.info("Starting WTHM ingestion server on http://%s:%s", host, port)
    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == "__main__":
    run()
