"""Windows system tray integration for WT Plotter (Open / Quit)."""
from __future__ import annotations

import threading
import webbrowser
from dataclasses import dataclass
from typing import Optional

import pystray
from PIL import Image, ImageDraw
import requests


@dataclass
class TrayConfig:
    host: str
    port: int
    product_name: str = "WT Plotter"


def _build_icon_image(size: int = 16) -> Image.Image:
    """Create a simple in-memory icon image."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Outer ring
    d.ellipse((0, 0, size - 1, size - 1), outline=(30, 144, 255, 255), width=2)
    # Inner point
    r = size // 5
    cx = cy = size // 2
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(250, 200, 30, 255))
    return img


class Tray:
    def __init__(self, cfg: TrayConfig) -> None:
        self.cfg = cfg
        self._icon: Optional[pystray.Icon] = None
        self._thread: Optional[threading.Thread] = None

    def _open(self, _=None) -> None:
        webbrowser.open(f"http://{self.cfg.host}:{self.cfg.port}/live")

    def _quit(self, _=None) -> None:
        try:
            requests.post(f"http://{self.cfg.host}:{self.cfg.port}/shutdown", timeout=2.0)
        except Exception:
            pass

    def start(self) -> None:
        if self._icon is not None:
            return
        image = _build_icon_image(16)
        menu = pystray.Menu(
            pystray.MenuItem("Open", self._open),
            pystray.MenuItem("Quit", self._quit),
        )
        self._icon = pystray.Icon(self.cfg.product_name, image, self.cfg.product_name, menu)
        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._icon is not None:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._icon = None


_tray: Optional[Tray] = None


def start_tray(host: str, port: int) -> None:
    global _tray
    if _tray is None:
        _tray = Tray(TrayConfig(host=host, port=port))
        _tray.start()


def stop_tray() -> None:
    global _tray
    if _tray is not None:
        _tray.stop()
        _tray = None
