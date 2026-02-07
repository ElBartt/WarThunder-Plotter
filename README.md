# 🚀 WarThunder Plotter

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Real-time position capture and interactive visualization for War Thunder matches.** Track your battles, analyze strategies, and relive epic moments with this powerful offline plotter.

WarThunder Plotter is a Python-based application that captures player positions in real-time during War Thunder matches via the game's local API (localhost:8111) and provides a web interface to visualize and analyze match data offline.

## ⚠️ Notes

- The tool captures live data only - it does not read replay files
- No personnal data is collected or stored; only match positions and metadata, everything is anonymous, I don't even know your nickname or account ID.

## ✨ Features

- 🎯 **Real-time Capture**: Automatically detects and records match positions
- 🌐 **Web Interface**: Modern, responsive web app for viewing matches
- 📊 **Live Tracking**: Follow matches in real-time with live updates
- 🗺️ **Map Visualization**: Displays positions on accurate game maps
- 📈 **Match Analytics**: View match duration, position counts, and statistics
- 🔄 **Multi-Mode Support**: Handles ground, air, and mixed battles
- 🗑️ **Data Management**: Delete old matches and manage storage
- 📱 **Responsive Design**: Works on desktop and mobile devices

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

## 📦 Windows Portable (No Python Needed)

If you just want a double-clickable app, download the portable EXE from GitHub Releases:

1. Go to the latest release on GitHub.
2. Download `WarThunderPlotter-portable.exe`.
3. Double-click it. The app starts in watch mode and opens your browser.

All data (database + maps) is stored next to the EXE in the `data/` folder.

### System Tray + Instance Unique

- Un icône s’affiche dans la zone de notification Windows avec les actions:
   - Open: ouvre l’interface web locale
   - Quit: arrête proprement la capture et le serveur
- Instance unique: si l’app est déjà lancée, un nouveau double-clic n’ouvre que le navigateur et se termine immédiatement (pas de deuxième instance, pas de corruption DB).

## 🔄 Auto-Update (GitHub Releases)

The portable EXE checks GitHub Releases on startup. If a newer version exists,
it downloads the new EXE and swaps it automatically, then restarts.

To disable updates, set the environment variable:

```bash
WT_PLOTTER_SKIP_UPDATE=1
```

## 🛠️ Build the Windows EXE (for maintainers)

```bash
build_windows.bat
```

Release flow:

1. Update `version.py` (e.g., `0.2.0`).
2. Build the EXE.
3. Create a GitHub Release tag `v0.2.0`.
4. Upload `dist/WarThunderPlotter-portable.exe` to the release assets.

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

## 🙏 Acknowledgments

- Built for the War Thunder community
- Uses Flask for the web framework
- SQLite for data storage
- Pillow for image processing

Thanks to [SGambe33](https://github.com/Sgambe33/WT-Plotter) for the groundwork on War Thunder plotting! I discovered this project after starting mine, and it inspired me to create this enhanced version with replayability and a modern web interface. (Thanks for map's hashes too!)

Thanks to [ValerieOSD](https://github.com/ValerieOSD/WarThunderRPC) for clean open source code that helped me making this project possible.

---

**Happy plotting! 🎯**
