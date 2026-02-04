"""
WT Plotter - War Thunder match visualizer.
Flask web application for viewing live and recorded matches.
"""
from __future__ import annotations

from datetime import datetime
import logging
from pathlib import Path
import sqlite3
from typing import Any, Dict, Optional

import click
from flask import Flask, Response, jsonify, render_template, request

import capture
import db
from map_hashes import MapInfo, UNKNOWN_MAP_INFO, lookup_map_info

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

MAPS_DIR = Path(__file__).parent / "data" / "maps"


def _resolve_map_info(map_hash: Optional[str]) -> MapInfo:
    """Return a map metadata entry, defaulting to unknown on empty hashes."""
    if not map_hash:
        return UNKNOWN_MAP_INFO
    return lookup_map_info(map_hash)


def _format_datetime(value: Optional[str]) -> str:
    """Format ISO timestamps for templates while tolerating invalid input."""
    if not value:
        return ""
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return value
    return parsed.strftime("%Y-%m-%d %H:%M:%S")


def _calculate_duration_seconds(match: db.Match) -> Optional[int]:
    """Return match duration in seconds, or None if timestamps are invalid."""
    if not match.started_at:
        return None
    try:
        start_dt = datetime.fromisoformat(match.started_at)
        end_dt = (
            datetime.fromisoformat(match.ended_at)
            if match.ended_at
            else datetime.now()
        )
    except ValueError:
        return None
    return max(0, int((end_dt - start_dt).total_seconds()))


def _build_match_summary(
    match: db.Match,
    conn: sqlite3.Connection,
) -> Dict[str, Any]:
    """Build the match summary payload used by the index view."""
    map_info = _resolve_map_info(match.map_hash)
    air_info = (
        _resolve_map_info(match.air_map_hash) if match.air_map_hash else None
    )
    return {
        "id": match.id,
        "started_at": match.started_at,
        "ended_at": match.ended_at,
        "map_name": map_info.display_name,
        "air_map_name": air_info.display_name if air_info else None,
        "nuke_detected": getattr(match, "nuke_detected", 0),
        "initial_capture_count": getattr(match, "initial_capture_count", None),
        "duration_seconds": _calculate_duration_seconds(match),
        "position_count": db.get_positions_count(conn, match.id),
        "is_active": match.ended_at is None,
    }


def _build_match_payload(
    match: db.Match,
    conn: sqlite3.Connection,
) -> Dict[str, Any]:
    """Build the API payload for listing matches."""
    map_info = _resolve_map_info(match.map_hash)
    return {
        "id": match.id,
        "started_at": match.started_at,
        "ended_at": match.ended_at,
        "map_name": map_info.display_name,
        "map_id": map_info.map_id,
        "battle_type": map_info.battle_type.value,
        "nuke_detected": getattr(match, "nuke_detected", 0),
        "initial_capture_count": getattr(match, "initial_capture_count", None),
        "initial_capture_x": getattr(match, "initial_capture_x", None),
        "initial_capture_y": getattr(match, "initial_capture_y", None),
        "position_count": db.get_positions_count(conn, match.id),
    }


def _build_match_detail_payload(match: db.Match) -> Dict[str, Any]:
    """Build the API payload for a single match."""
    map_info = _resolve_map_info(match.map_hash)
    return {
        "id": match.id,
        "started_at": match.started_at,
        "ended_at": match.ended_at,
        "map_name": map_info.display_name,
        "map_hash": match.map_hash,
        "map_id": map_info.map_id,
        "battle_type": map_info.battle_type.value,
        "nuke_detected": getattr(match, "nuke_detected", 0),
        "initial_capture_count": getattr(match, "initial_capture_count", None),
        "initial_capture_x": getattr(match, "initial_capture_x", None),
        "initial_capture_y": getattr(match, "initial_capture_y", None),
        "air_transform_a": getattr(match, "air_transform_a", None),
        "air_transform_b": getattr(match, "air_transform_b", None),
        "air_transform_c": getattr(match, "air_transform_c", None),
        "air_transform_d": getattr(match, "air_transform_d", None),
    }


def _parse_since_ms(raw_value: Any) -> int:
    """Parse the since value into milliseconds, accepting floats in seconds."""
    if isinstance(raw_value, str) and "." in raw_value:
        return int(float(raw_value) * 1000)
    return int(raw_value)


def _select_map_key(map_info: MapInfo, map_hash: str) -> Optional[str]:
    """Resolve the map image key for image lookups."""
    map_id = map_info.map_id
    if map_id in (None, "", "unknown", "no_map"):
        return map_hash or None
    return map_id


def _register_template_filters(app: Flask) -> None:
    """Register template filters used by the views."""

    @app.template_filter("dt")
    def dt_filter(value: Optional[str]) -> str:
        return _format_datetime(value)


def _register_routes(app: Flask, conn: sqlite3.Connection) -> None:
    """Register web and API routes for the Flask application."""

    @app.route("/")
    def index() -> str:
        """Render the dashboard listing all matches."""
        matches = db.get_all_matches(conn)
        match_data = [_build_match_summary(match, conn) for match in matches]
        return render_template("index.html", matches=match_data)

    @app.route("/match/<int:match_id>")
    def match_view(match_id: int):
        """Render a specific match view."""
        match = db.get_match(conn, match_id)
        if not match:
            return "Match not found", 404
        is_live = match.ended_at is None
        return render_template("match.html", match=match, is_live=is_live)

    @app.route("/live")
    def live_view():
        """Render the live view or waiting screen."""
        active = db.get_active_match(conn)
        if active:
            return render_template("match.html", match=active, is_live=True)
        return render_template("waiting.html")

    @app.route("/api/matches")
    def api_matches():
        """Return the list of matches as JSON."""
        matches = db.get_all_matches(conn)
        payload = [_build_match_payload(match, conn) for match in matches]
        return jsonify(payload)

    @app.route("/api/match/<int:match_id>")
    def api_match(match_id: int):
        """Return match details as JSON."""
        match = db.get_match(conn, match_id)
        if not match:
            return jsonify({"error": "Not found"}), 404
        return jsonify(_build_match_detail_payload(match))

    @app.route("/api/match/<int:match_id>/positions")
    def api_positions(match_id: int):
        """Return positions for a match as JSON."""
        since_raw = request.args.get("since", "0")
        try:
            since = _parse_since_ms(since_raw)
        except (ValueError, TypeError):
            since = 0
        bundle = db.get_positions_bundle(conn, match_id, since_ts_ms=since)
        return jsonify(bundle)

    @app.route("/api/match/<int:match_id>/map.png")
    def api_map_image(match_id: int):
        """Return the map image for a match."""
        match = db.get_match(conn, match_id)
        if not match:
            return "", 404
        map_info = _resolve_map_info(match.map_hash)
        map_key = _select_map_key(map_info, match.map_hash)
        if not map_key:
            return "", 404
        map_path = MAPS_DIR / f"{map_key}.png"
        if not map_path.exists():
            return "", 404
        return Response(map_path.read_bytes(), mimetype="image/png")

    @app.route("/api/active")
    def api_active():
        """Return the active match metadata if present."""
        active = db.get_active_match(conn)
        if not active:
            return jsonify(None)
        return jsonify(
            {
                "id": active.id,
                "started_at": active.started_at,
                "map_name": active.map_name,
            }
        )

    @app.route("/api/status")
    def api_status():
        """Return capture status metadata."""
        capturer = capture.get_capturer()
        active = db.get_active_match(conn)
        army_type = getattr(capturer, "current_army_type", "tank")
        vehicle_type = getattr(capturer, "current_vehicle_type", "")
        if active and (not army_type or not vehicle_type):
            latest_tick = db.get_latest_tick(conn, active.id)
            if latest_tick:
                army_type = army_type or latest_tick.army_type
                vehicle_type = vehicle_type or latest_tick.vehicle_type
        return jsonify(
            {
                "capturing": capturer.running,
                "active_match_id": active.id if active else None,
                "army_type": army_type or "tank",
                "vehicle_type": vehicle_type or "",
            }
        )

    @app.route("/api/match/<int:match_id>", methods=["DELETE"])
    def api_delete_match(match_id: int):
        """Delete a match and all its positions."""
        match = db.get_match(conn, match_id)
        if not match:
            return jsonify({"error": "Not found"}), 404
        active = db.get_active_match(conn)
        if active and active.id == match_id:
            return jsonify({"error": "Cannot delete active match"}), 400
        db.delete_match(conn, match_id)
        return jsonify({"success": True})


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    _register_template_filters(app)
    conn = db.get_connection()
    orphaned = db.close_orphaned_matches(conn)
    if orphaned:
        logger.info(
            "Closed %s orphaned match(es) from previous session",
            orphaned,
        )
    _register_routes(app, conn)
    return app


@click.group()
def cli() -> None:
    """WT Plotter - War Thunder match visualizer."""


@cli.command()
@click.option("--port", default=5000, help="Port to run the server on")
@click.option("--host", default="127.0.0.1", help="Host to bind to")
def serve(port: int, host: str) -> None:
    """Start the web server only (no capture)."""
    app = create_app()
    logger.info("Starting web server on http://%s:%s", host, port)
    app.run(host=host, port=port, debug=False, threaded=True)


@cli.command("capture")
def capture_cmd() -> None:
    """Start capture only (no web server)."""
    logger.info("Starting capture mode")
    logger.info("Press Ctrl+C to stop")

    def on_start(match_id: int) -> None:
        logger.info("Match %s started", match_id)

    def on_end(match_id: int) -> None:
        logger.info("Match %s ended", match_id)

    def on_position(match_id: int, positions: list[dict]) -> None:
        logger.info("Match %s: captured %s positions", match_id, len(positions))

    capturer = capture.Capturer(
        on_match_start=on_start,
        on_match_end=on_end,
        on_position=on_position,
    )

    try:
        capturer.start()
        while True:
            import time

            time.sleep(1)
    except KeyboardInterrupt:
        capturer.stop()
        logger.info("Capture stopped")


@cli.command()
@click.option("--port", default=5000, help="Port to run the server on")
@click.option("--host", default="127.0.0.1", help="Host to bind to")
def watch(port: int, host: str) -> None:
    """Start both capture and web server."""
    logger.info("Starting watch mode (capture + web server)")

    def on_start(match_id: int) -> None:
        logger.info("Match %s started", match_id)

    def on_end(match_id: int) -> None:
        logger.info("Match %s ended", match_id)

    def on_position(match_id: int, positions: list[dict]) -> None:
        regular = [pos for pos in positions if not pos.get("is_poi")]
        if regular:
            logger.info("Match %s: +%s positions", match_id, len(regular))

    capturer = capture.Capturer(
        on_match_start=on_start,
        on_match_end=on_end,
        on_position=on_position,
    )
    capturer.start()

    app = create_app()
    logger.info("Web server: http://%s:%s", host, port)
    logger.info("Live view: http://%s:%s/live", host, port)

    try:
        app.run(host=host, port=port, debug=False, threaded=True)
    finally:
        capturer.stop()


def main() -> None:
    """Run the CLI entrypoint."""
    cli()


if __name__ == "__main__":
    main()
