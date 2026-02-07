"""Lightweight GitHub Releases updater for the Windows portable build."""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Optional, Tuple

import requests

from version import __version__

GITHUB_OWNER = "ElBartt"
GITHUB_REPO = "WarThunder-Plotter"
ASSET_SUFFIX = ".exe"
PRODUCT_NAME = "WarThunder Plotter"
UPDATE_ENV_SKIP = "WT_PLOTTER_SKIP_UPDATE"
UPDATE_TIMEOUT = 4.0


@dataclass(frozen=True)
class ReleaseInfo:
    """Resolved update metadata from GitHub Releases."""

    version: str
    asset_name: str
    asset_url: str


def _is_frozen() -> bool:
    """Return True when running from a bundled executable."""
    return bool(getattr(sys, "frozen", False))


def _parse_version(tag: str) -> Tuple[int, int, int]:
    """Parse a version tag into a comparable tuple."""
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", tag)
    if not match:
        return (0, 0, 0)
    return tuple(int(group) for group in match.groups())


def _is_newer_version(current: str, latest: str) -> bool:
    """Return True when latest version is newer than current."""
    return _parse_version(latest) > _parse_version(current)


def _latest_release_url() -> str:
    """Return the GitHub API URL for the latest release."""
    return (
        f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
    )


def _fetch_latest_release() -> Optional[dict[str, Any]]:
    """Fetch the latest release metadata from GitHub."""
    try:
        response = requests.get(
            _latest_release_url(),
            headers={"User-Agent": PRODUCT_NAME},
            timeout=UPDATE_TIMEOUT,
        )
        if response.status_code != 200:
            return None
        return response.json()
    except requests.RequestException:
        return None


def _select_asset(assets: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
    """Pick the best matching asset for the portable Windows build."""
    if not assets:
        return None
    exe_assets = [asset for asset in assets if asset.get("name", "").endswith(ASSET_SUFFIX)]
    if not exe_assets:
        return None
    portable = [asset for asset in exe_assets if "portable" in asset.get("name", "").lower()]
    return portable[0] if portable else exe_assets[0]


def _resolve_update_info() -> Optional[ReleaseInfo]:
    """Return update metadata if a newer release is available."""
    data = _fetch_latest_release()
    if not data:
        return None
    tag_name = str(data.get("tag_name", "")).strip()
    if not tag_name:
        return None
    if not _is_newer_version(__version__, tag_name):
        return None
    asset = _select_asset(data.get("assets", []))
    if not asset:
        return None
    asset_name = str(asset.get("name", "")).strip()
    asset_url = str(asset.get("browser_download_url", "")).strip()
    if not asset_name or not asset_url:
        return None
    return ReleaseInfo(version=tag_name, asset_name=asset_name, asset_url=asset_url)


def _download_asset(info: ReleaseInfo, target_dir: Path) -> Path:
    """Download the release asset to the target directory."""
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / info.asset_name
    response = requests.get(info.asset_url, stream=True, timeout=UPDATE_TIMEOUT)
    response.raise_for_status()
    with target_path.open("wb") as handle:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                handle.write(chunk)
    return target_path


def _write_update_script(
    current_exe: Path,
    new_exe: Path,
    pid: int,
) -> Path:
    """Write a temporary CMD script that swaps binaries once the app exits."""
    script_path = Path(tempfile.gettempdir()) / "wt_plotter_update.cmd"
    script_content = (
        "@echo off\n"
        "setlocal\n"
        f"set CURRENT=\"{current_exe}\"\n"
        f"set NEW=\"{new_exe}\"\n"
        f"set OLD=\"{current_exe}.old\"\n"
        "set PID=" + str(pid) + "\n"
        ":wait\n"
        "tasklist /FI \"PID eq %PID%\" | find \"%PID%\" >nul\n"
        "if not errorlevel 1 (\n"
        "  timeout /t 1 >nul\n"
        "  goto wait\n"
        ")\n"
        "if exist %OLD% del /f /q %OLD%\n"
        "move /y %CURRENT% %OLD% >nul\n"
        "move /y %NEW% %CURRENT% >nul\n"
        "start \"\" %CURRENT%\n"
        "endlocal\n"
    )
    script_path.write_text(script_content, encoding="utf-8")
    return script_path


def _launch_update_script(script_path: Path) -> None:
    """Launch the update script detached from the current process."""
    subprocess.Popen(
        ["cmd", "/c", str(script_path)],
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def check_and_update_on_start() -> None:
    """Check for updates and apply them if possible."""
    if not _is_frozen():
        return
    if os.environ.get(UPDATE_ENV_SKIP):
        return

    info = _resolve_update_info()
    if not info:
        return

    current_exe = Path(sys.executable)
    temp_dir = Path(tempfile.gettempdir()) / "wt_plotter_update"
    try:
        new_exe = _download_asset(info, temp_dir)
    except requests.RequestException:
        return

    script_path = _write_update_script(current_exe, new_exe, os.getpid())
    _launch_update_script(script_path)
    sys.exit(0)
