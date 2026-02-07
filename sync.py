"""Client-side sync of match data to central WTHM server.
Builds a versioned envelope and sends it at match end.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import requests

import db
from models import MatchDetailPayload
from config import SYNC_SETTINGS
from map_hashes import lookup_map_info

logger = logging.getLogger(__name__)


def _build_match_detail(conn, match_id: int) -> Dict[str, Any]:
    match = db.get_match(conn, match_id)
    if not match:
        raise ValueError(f"Match {match_id} not found")
    map_info = lookup_map_info(match.map_hash)
    payload = MatchDetailPayload.from_match(match, map_info).to_dict()
    return payload


def build_envelope(conn, match_id: int) -> Dict[str, Any]:
    """Build a complete sync envelope for a match, including ticks and positions.

    Envelope schema (v1):
    {
      schema_version: int,
      client_id: str,
      match: MatchDetailPayload,
      ticks: [{id, timestamp, army_type, vehicle_type, is_player_air, is_player_air_view}],
      positions: [{tick_id, x, y, color, type, icon, is_poi, x_ground, y_ground}]
    }
    """
    match_payload = _build_match_detail(conn, match_id)
    bundle = db.get_positions_bundle(conn, match_id, since_ts_ms=0)
    ticks: List[Dict[str, Any]] = bundle.get("ticks", [])
    positions: List[Dict[str, Any]] = bundle.get("positions", [])
    return {
        "schema_version": SYNC_SETTINGS.schema_version,
        "client_id": SYNC_SETTINGS.client_id,
        "match": match_payload,
        "ticks": ticks,
        "positions": positions,
    }


def send_envelope(envelope: Dict[str, Any]) -> Optional[requests.Response]:
    """POST the envelope to the remote ingestion endpoint."""
    if not SYNC_SETTINGS.enabled:
        logger.info("Remote sync disabled; skipping send")
        return None

    url = SYNC_SETTINGS.server_url.rstrip("/") + SYNC_SETTINGS.ingest_path
    headers = {"Content-Type": "application/json"}
    if SYNC_SETTINGS.auth_token:
        headers["Authorization"] = f"Bearer {SYNC_SETTINGS.auth_token}"

    last_exc: Optional[Exception] = None
    for attempt in range(1, SYNC_SETTINGS.retries + 1):
        try:
            resp = requests.post(url, json=envelope, headers=headers, timeout=SYNC_SETTINGS.timeout)
            if resp.status_code < 300:
                logger.info("WTHM sync OK (attempt %s)", attempt)
                return resp
            else:
                logger.warning("WTHM sync error %s: %s", resp.status_code, resp.text)
        except Exception as e:
            last_exc = e
            logger.warning("WTHM sync failed (attempt %s): %s", attempt, e)
    if last_exc:
        logger.error("WTHM sync failed after %s attempts: %s", SYNC_SETTINGS.retries, last_exc)
    return None


def sync_match(conn, match_id: int) -> None:
    """Build and send the envelope for a given match ID."""
    try:
        envelope = build_envelope(conn, match_id)
        send_envelope(envelope)
    except Exception as e:
        logger.error("Failed to sync match %s: %s", match_id, e)
