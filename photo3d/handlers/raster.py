"""Raster ingest handler.

Opens the image, applies EXIF orientation, converts to RGB, and returns
a JobTicket with the working-resolution array and metadata.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

from photo3d.core.registry import register_ingest
from photo3d.models.ticket import JobTicket
from photo3d.utils.logging import get_logger

log = get_logger(__name__)

_MAX_MEGAPIXELS = 128


@register_ingest(".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", "*")
def ingest_raster(image: Path) -> JobTicket:
    img = Image.open(image)
    img = ImageOps.exif_transpose(img).convert("RGB")

    mp = (img.width * img.height) / 1_000_000
    if mp > _MAX_MEGAPIXELS:
        raise ValueError(f"{image.name}: {mp:.1f} MP exceeds cap of {_MAX_MEGAPIXELS} MP")

    arr = np.asarray(img, dtype=np.uint8)
    return JobTicket(
        source=image,
        width=img.width,
        height=img.height,
        array=arr,
        color_space="sRGB",
        has_alpha=False,
    )