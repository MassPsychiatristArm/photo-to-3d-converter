"""EXIF extraction handler.

Runs alongside `raster` — the dispatcher picks one handler per suffix,
but the pipeline calls `extract_exif` explicitly when it needs the
metadata block for output sidecars.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import ExifTags, Image

_TAGS = {v: k for k, v in ExifTags.TAGS.items()}


def extract_exif(path: Path) -> dict[str, Any]:
    """Return a JSON-safe EXIF dict. Missing tags are simply absent."""
    try:
        with Image.open(path) as img:
            raw = img.getexif()
    except Exception:  # noqa: BLE001
        return {}

    out: dict[str, Any] = {}
    for tag_id, value in raw.items():
        name = ExifTags.TAGS.get(tag_id, str(tag_id))
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")
        out[name] = value
    return out
</｜｜DSML｜｜ parameter>
</｜｜DSML｜｜ invoke>
</｜｜DSML｜｜ calls>