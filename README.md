# 🚀 WarThunder Plotter

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Real-time position capture and interactive visualization for War Thunder matches.** Track your battles, analyze strategies, and relive epic moments with this powerful offline plotter.

WarThunder Plotter is a Python-based application that captures player positions in real-time during War Thunder matches via the game's local API (localhost:8111) and provides a web interface to visualize and analyze match data offline.

## ✨ Features

- 🎯 **Real-time Capture**: Automatically detects and records match positions
- 🌐 **Web Interface**: Modern, responsive web app for viewing matches
- 📊 **Live Tracking**: Follow matches in real-time with live updates
- 🗺️ **Map Visualization**: Displays positions on accurate game maps
- 📈 **Match Analytics**: View match duration, position counts, and statistics
- 🔄 **Multi-Mode Support**: Handles ground, air, and mixed battles
- 🗑️ **Data Management**: Delete old matches and manage storage
- 📱 **Responsive Design**: Works on desktop and mobile devices

## WTHM (Central Aggregation)

This repository now includes a minimal central ingestion server and client-side sync to aggregate matches from multiple users.

- Client sync: when a match ends, an envelope (schema v1) is posted to the central server.
- Server (Flask): receives `/ingest` and stores the match, ticks, and positions into the same schema.

### Enable client sync

Edit `config.py` and set:

- `SYNC_SETTINGS.enabled = True`
- `SYNC_SETTINGS.server_url = "http://localhost:8000"` (or your VPS URL)
- Optionally set `auth_token` and `client_id`.

### Run the ingestion server locally

```
python wthm_server/app.py
```

The server exposes `POST /ingest` and `GET /health`.

### Envelope Schema (v1)

- `schema_version`: integer (currently `1`)
- `client_id`: optional identifier of the sender
- `match`: match detail payload compatible with existing viewer
- `ticks`: array of `{id, timestamp (ms), army_type, vehicle_type, is_player_air, is_player_air_view}`
- `positions`: array of `{tick_id, x, y, color, type, icon, is_poi, x_ground, y_ground}`

The server expands these into the central DB using the same tables and enums.

### Notes on maintainability

- The ingestion is schema-versioned via `schema_version`.
- Server validation is minimal and avoids application logic; it centralizes data only.
- Future schema changes can be coordinated by bumping `SYNC_SETTINGS.schema_version` and updating the server to accept the new structure.
## 📋 Requirements

- **Python**: 3.8 or higher
- **War Thunder**: Running with local API enabled (localhost:8111)
- **Dependencies**: Listed in `requirements.txt`

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ElBartt/WarThunder-Plotter.git
   cd WarThunder-Plotter
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   setup_offline_plotter.bat
   ```

3. **Run the setup script** (optional, for offline plotting):
   ```bash
   # Windows
   run_watch.bat
   ```

## 🎮 Usage

### Quick Start

Run the application in watch mode (capture + web server):
```bash
python app.py watch
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

### Commands

#### Start Web Server Only
```bash
python app.py serve
```
- Launches the web interface without starting capture
- Useful for viewing previously recorded matches

#### Start Capture Only
```bash
python app.py capture
```
- Captures match data in the background
- No web interface

#### Watch Mode (Recommended)
```bash
python app.py watch --port 5000 --host 127.0.0.1
```
- Runs both capture and web server simultaneously
- Access live view at [http://127.0.0.1:5000/live](http://127.0.0.1:5000/live)

### Command Options

#### Server Options (for `serve` and `watch`)
- `--port 5000`: Server port (default: 5000)
- `--host 127.0.0.1`: Server host (default: 127.0.0.1)

## 📁 Data Structure

- `data/matches.db`: SQLite database storing matches and positions
- `data/maps/`: Directory containing map images (downloaded once per map)
- Map images are cached locally for performance and reusability

## 🌟 Key Features Explained

### Real-time Capture
The application connects to War Thunder's local API to capture:
- Player positions (x, y coordinates)
- Vehicle types and army affiliations
- Match metadata (map, battle type, timestamps)
- POI (Points of Interest) data

### Web Interface
- **Dashboard**: List all recorded matches with statistics
- **Match Viewer**: Interactive map with position trails
- **Live View**: Real-time updates during active matches
- **Match Details**: Duration, position count, map information

### Map Support
- Automatic map detection and downloading
- Support for ground, air, and hybrid battles
- Accurate coordinate transformation for visualization

## 🛠️ Development

### Project Structure
```
WarThunder-Plotter/
├── app.py              # Main Flask application and CLI
├── capture.py          # Position capture logic
├── db.py               # Database operations
├── map_hashes.py       # Map hash definitions
├── requirements.txt    # Python dependencies
├── static/             # CSS, JS assets
├── templates/          # HTML templates
├── data/               # Match data and maps
└── README.md           # This file
```

### Running from Source
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Run in development mode
python app.py watch --port 5000
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Notes

- The tool captures live data only - it does not read replay files
- Requires War Thunder to be running with the local API enabled
- Map grouping considers battle mode (ground/air)
- When switching from ground to air during a match, air map data is stored as secondary metadata

## 🙏 Acknowledgments

- Built for the War Thunder community
- Uses Flask for the web framework
- SQLite for data storage
- Pillow for image processing

---

**Happy plotting! 🎯**
