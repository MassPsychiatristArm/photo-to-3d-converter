"""Suffix-based ingest dispatch.

Falls back to the generic raster handler if the suffix is unknown, so a
mislabeled .jpg that's really a PNG still works.
"""
from __future__ import annotations

from pathlib import Path

from photo3d.core.registry import INGEST_HANDLERS
from photo3d.models.ticket import JobTicket


def dispatch_ingest(image: Path) -> JobTicket:
    suffix = image.suffix.lower()
    handler = INGEST_HANDLERS.get(suffix) or INGEST_HANDLERS.get("*")
    if handler is None:
        raise KeyError(f"no ingest handler registered for {suffix!r}")
    ticket = handler(image)
    if not isinstance(ticket, JobTicket):
        raise TypeError(f"handler {handler!r} returned {type(ticket).__name__}, not JobTicket")
    return ticket