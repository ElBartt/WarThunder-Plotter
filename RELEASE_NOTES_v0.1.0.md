# WarThunder Plotter v0.1.0 — First Official Release

Welcome to the first official release of WarThunder Plotter! This version brings a portable Windows app, a modern local web interface, safe data handling, and an auto‑update flow to keep you current.

## Highlights
- Portable EXE (Windows): No Python or dependencies to install — double‑click and go.
- Live Capture: Automatically records positions and match metadata from the War Thunder local API.
- Web UI: Dashboard, match view, and live mode with responsive layout.
- Accurate Maps: Visualisation on correct maps, cached locally for performance.
- Analytics: Duration, number of positions, initial capture zones, and more.
- Data Management: Delete recorded matches; data stored locally next to the executable.
- System Tray: Windows tray icon with quick actions — Open and Quit.
- Single Instance: Prevents multiple simultaneous runs to avoid database corruption.
- Auto‑Update: Checks GitHub Releases on startup, downloads and swaps the EXE if a newer version is available.

## Download
- From the GitHub Release page, download: `WarThunderPlotter-portable.exe`.
- Place it anywhere you like. It will create and use a `data/` folder next to the EXE.

## Quick Start
1. Double‑click `WarThunderPlotter-portable.exe`.
2. Your browser opens automatically to the local web UI (Live view).
3. Start or join a War Thunder match; positions are captured in real time.
4. To exit cleanly, use:
   - The Quit button in the web UI header, or
   - The System Tray icon menu → "Quit".

## System Tray & Single Instance
- A Windows tray icon appears while the app runs:
  - "Open": Opens the local web UI.
  - "Quit": Stops capture and shuts down the server safely.
- If you launch the EXE while it’s already running, it will only open the browser and exit immediately (no second instance).

## Auto‑Update
- On startup, the portable EXE checks GitHub Releases for newer versions.
- If available, it downloads the new EXE, swaps it, and restarts.
- To disable auto‑update, set the environment variable:
  - `WT_PLOTTER_SKIP_UPDATE=1`

## Requirements
- War Thunder with local API enabled (`http://localhost:8111`).
- Windows (recommended for the portable EXE in this release).

## Notable Changes
- Introduced portable packaging with PyInstaller.
- Added systray integration (Open/Quit) for better UX.
- Enforced single‑instance behaviour to protect the database.
- Added `/shutdown` endpoint and UI Quit button for clean exit.
- Implemented an updater that fetches the latest portable EXE from GitHub Releases.
- Data directory resolution updated to store `data/` alongside the EXE when packaged.

## Feedback & Issues
- Please open an issue on GitHub to report bugs, request features, or ask questions.
- Contributions are welcome: fork → branch → PR with tests and a clear description.

Happy plotting! 🎯