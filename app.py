"""
WT Plotter - War Thunder match visualizer.
Flask web application for viewing live and recorded matches.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, Response, request
import click

import db
import capture

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MAPS_DIR = Path(__file__).parent / "data" / "maps"

def create_app():
    """Create Flask application."""
    app = Flask(__name__)
    
    # Template filter for dates
    @app.template_filter('dt')
    def format_datetime(value):
        if not value:
            return ''
        try:
            dt = datetime.fromisoformat(value)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return value
    
    # Database connection
    conn = db.get_connection()
    
    # Close any orphaned matches from previous hard quit
    orphaned = db.close_orphaned_matches(conn)
    if orphaned:
        logger.info(f"Closed {orphaned} orphaned match(es) from previous session")
    
    # --- Web Routes ---
    
    @app.route('/')
    def index():
        """Dashboard - list all matches."""
        matches = db.get_all_matches(conn)
        # Add position counts
        match_data = []
        for m in matches:
            duration_seconds = None
            if m.started_at:
                try:
                    start_dt = datetime.fromisoformat(m.started_at)
                    end_dt = datetime.fromisoformat(m.ended_at) if m.ended_at else datetime.now()
                    duration_seconds = max(0, int((end_dt - start_dt).total_seconds()))
                except Exception:
                    duration_seconds = None
            count = db.get_positions_count(conn, m.id)
            match_data.append({
                'id': m.id,
                'started_at': m.started_at,
                'ended_at': m.ended_at,
                'map_name': m.map_name or 'Unknown',
                'air_map_name': getattr(m, 'air_map_name', None),
                'nuke_detected': getattr(m, 'nuke_detected', 0),
                'initial_capture_count': getattr(m, 'initial_capture_count', None),
                'duration_seconds': duration_seconds,
                'position_count': count,
                'is_active': m.ended_at is None
            })
        return render_template('index.html', matches=match_data)
    
    @app.route('/match/<int:match_id>')
    def match_view(match_id: int):
        """View a specific match."""
        match = db.get_match(conn, match_id)
        if not match:
            return "Match not found", 404
        is_live = match.ended_at is None
        return render_template('match.html', match=match, is_live=is_live)
    
    @app.route('/live')
    def live_view():
        """Live match view - shows active match or waiting screen."""
        active = db.get_active_match(conn)
        if active:
            return render_template('match.html', match=active, is_live=True)
        return render_template('waiting.html')
    
    # --- API Routes ---
    
    @app.route('/api/matches')
    def api_matches():
        """Get all matches."""
        matches = db.get_all_matches(conn)
        return jsonify([{
            'id': m.id,
            'started_at': m.started_at,
            'ended_at': m.ended_at,
            'map_name': m.map_name,
            'map_id': getattr(m, 'map_id', None),
            'battle_type': getattr(m, 'battle_type', None),
            'air_map_name': getattr(m, 'air_map_name', None),
            'nuke_detected': getattr(m, 'nuke_detected', 0),
            'initial_capture_count': getattr(m, 'initial_capture_count', None),
            'initial_capture_x': getattr(m, 'initial_capture_x', None),
            'initial_capture_y': getattr(m, 'initial_capture_y', None),
            'position_count': db.get_positions_count(conn, m.id)
        } for m in matches])
    
    @app.route('/api/match/<int:match_id>')
    def api_match(match_id: int):
        """Get match details."""
        match = db.get_match(conn, match_id)
        if not match:
            return jsonify({'error': 'Not found'}), 404
        return jsonify({
            'id': match.id,
            'started_at': match.started_at,
            'ended_at': match.ended_at,
            'map_name': match.map_name,
            'map_hash': match.map_hash,
            'map_id': getattr(match, 'map_id', None),
            'battle_type': getattr(match, 'battle_type', None),
            'air_map_hash': getattr(match, 'air_map_hash', None),
            'air_map_id': getattr(match, 'air_map_id', None),
            'air_map_name': getattr(match, 'air_map_name', None),
            'air_battle_type': getattr(match, 'air_battle_type', None),
            'nuke_detected': getattr(match, 'nuke_detected', 0),
            'initial_capture_count': getattr(match, 'initial_capture_count', None),
            'initial_capture_x': getattr(match, 'initial_capture_x', None),
            'initial_capture_y': getattr(match, 'initial_capture_y', None),
            'air_transform_a': getattr(match, 'air_transform_a', None),
            'air_transform_b': getattr(match, 'air_transform_b', None),
            'air_transform_c': getattr(match, 'air_transform_c', None),
            'air_transform_d': getattr(match, 'air_transform_d', None)
        })
    
    @app.route('/api/match/<int:match_id>/positions')
    def api_positions(match_id: int):
        """Get positions for a match."""
        since_raw = request.args.get('since', '0')
        try:
            if isinstance(since_raw, str) and '.' in since_raw:
                since = int(float(since_raw) * 1000)
            else:
                since = int(since_raw)
        except (ValueError, TypeError):
            since = 0
        positions = db.get_positions(conn, match_id, since_ts_ms=since)
        return jsonify([{
            'x': p.x,
            'y': p.y,
            'color': p.color,
            'type': p.type,
            'icon': p.icon,
            'timestamp': p.timestamp,
            'is_poi': p.is_poi,
            'army_type': getattr(p, 'army_type', 'tank'),
            'vehicle_type': getattr(p, 'vehicle_type', ''),
            'is_player_air': getattr(p, 'is_player_air', 0),
            'is_player_air_view': getattr(p, 'is_player_air_view', 0),
            'x_ground': getattr(p, 'x_ground', None),
            'y_ground': getattr(p, 'y_ground', None)
        } for p in positions])
    
    @app.route('/api/match/<int:match_id>/map.png')
    def api_map_image(match_id: int):
        """Get the map image for a match."""
        match = db.get_match(conn, match_id)
        if not match:
            return '', 404
        map_id = getattr(match, 'map_id', None)
        if map_id in (None, '', 'unknown', 'no_map'):
            map_key = match.map_hash
        else:
            map_key = map_id
        if not map_key:
            return '', 404
        map_path = MAPS_DIR / f"{map_key}.png"
        if not map_path.exists():
            return '', 404
        return Response(map_path.read_bytes(), mimetype='image/png')
    
    @app.route('/api/active')
    def api_active():
        """Get the active match (if any)."""
        active = db.get_active_match(conn)
        if active:
            return jsonify({
                'id': active.id,
                'started_at': active.started_at,
                'map_name': active.map_name
            })
        return jsonify(None)
    
    @app.route('/api/status')
    def api_status():
        """Get capture status."""
        capturer = capture.get_capturer()
        active = db.get_active_match(conn)
        return jsonify({
            'capturing': capturer.running,
            'active_match_id': active.id if active else None,
            'army_type': getattr(capturer, 'current_army_type', 'tank'),
            'vehicle_type': getattr(capturer, 'current_vehicle_type', '')
        })
    
    @app.route('/api/match/<int:match_id>', methods=['DELETE'])
    def api_delete_match(match_id: int):
        """Delete a match and all its positions."""
        match = db.get_match(conn, match_id)
        if not match:
            return jsonify({'error': 'Not found'}), 404
        
        # Don't allow deleting active match
        active = db.get_active_match(conn)
        if active and active.id == match_id:
            return jsonify({'error': 'Cannot delete active match'}), 400
        
        db.delete_match(conn, match_id)
        return jsonify({'success': True})
    
    return app


# --- CLI Commands ---

@click.group()
def cli():
    """WT Plotter - War Thunder match visualizer."""
    pass


@cli.command()
@click.option('--port', default=5000, help='Port to run the server on')
@click.option('--host', default='127.0.0.1', help='Host to bind to')
def serve(port: int, host: str):
    """Start the web server only (no capture)."""
    app = create_app()
    logger.info(f"Starting web server on http://{host}:{port}")
    app.run(host=host, port=port, debug=False, threaded=True)


@cli.command()
def capture_cmd():
    """Start capture only (no web server)."""
    logger.info("Starting capture mode")
    logger.info("Press Ctrl+C to stop")
    
    def on_start(match_id):
        logger.info(f"Match {match_id} started")
    
    def on_end(match_id):
        logger.info(f"Match {match_id} ended")
    
    def on_position(match_id, positions):
        logger.info(f"Match {match_id}: captured {len(positions)} positions")
    
    capturer = capture.Capturer(
        on_match_start=on_start,
        on_match_end=on_end,
        on_position=on_position
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
@click.option('--port', default=5000, help='Port to run the server on')
@click.option('--host', default='127.0.0.1', help='Host to bind to')
def watch(port: int, host: str):
    """Start both capture and web server."""
    logger.info("Starting watch mode (capture + web server)")
    
    def on_start(match_id):
        logger.info(f"Match {match_id} started")
    
    def on_end(match_id):
        logger.info(f"Match {match_id} ended")
    
    def on_position(match_id, positions):
        # Count non-POI positions
        regular = [p for p in positions if not p.get('is_poi')]
        if regular:
            logger.info(f"Match {match_id}: +{len(regular)} positions")

    capturer = capture.Capturer(
        on_match_start=on_start,
        on_match_end=on_end,
        on_position=on_position
    )
    
    capturer.start()
    
    app = create_app()
    logger.info(f"Web server: http://{host}:{port}")
    logger.info(f"Live view: http://{host}:{port}/live")
    
    try:
        app.run(host=host, port=port, debug=False, threaded=True)
    finally:
        capturer.stop()


def main():
    cli()


if __name__ == '__main__':
    main()
