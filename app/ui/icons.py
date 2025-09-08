from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from PySide6.QtGui import QPixmap

# Directory containing technique icons
ICONS_DIR = Path(__file__).resolve().parents[2] / "assets" / "icons" / "techniques"


@lru_cache(maxsize=None)
def get_technique_icon(name: str) -> Optional[QPixmap]:
    """Return QPixmap for given technique name if available.

    Parameters
    ----------
    name: str
        Technique identifier, e.g. "open" or "mute".

    Returns
    -------
    Optional[QPixmap]
        Loaded pixmap or ``None`` if the icon file does not exist.
    """
    for ext in (".svg", ".png"):
        path = ICONS_DIR / f"{name}{ext}"
        if path.exists():
            return QPixmap(str(path))
    return None
