"""Plugin registries.

Three registries, one per pipeline stage:
    INGEST_HANDLERS   suffix -> callable(Path) -> JobTicket
    DEPTH_BACKENDS    name   -> callable() -> DepthBackend
    OUTPUT_DRIVERS    fmt    -> callable(Scene, Path) -> Path

Registries are populated by import side effects in the corresponding
packages. Do not import those packages from here — that inverts the
dependency graph and breaks lazy loading.
"""
from __future__ import annotations

from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from photo3d.models.ticket import JobTicket
    from photo3d.core.backends.base import DepthBackend
    from photo3d.models.scene import Scene

IngestHandler = Callable[[object], "JobTicket"]
DepthBackendFactory = Callable[[], "DepthBackend"]
OutputDriver = Callable[["Scene", object], object]

INGEST_HANDLERS: dict[str, IngestHandler] = {}
DEPTH_BACKENDS: dict[str, DepthBackendFactory] = {}
OUTPUT_DRIVERS: dict[str, OutputDriver] = {}


def register_ingest(*suffixes: str) -> Callable[[IngestHandler], IngestHandler]:
    def deco(fn: IngestHandler) -> IngestHandler:
        for s in suffixes:
            INGEST_HANDLERS[s.lower()] = fn
        return fn
    return deco


def register_backend(name: str) -> Callable[[DepthBackendFactory], DepthBackendFactory]:
    def deco(fn: DepthBackendFactory) -> DepthBackendFactory:
        DEPTH_BACKENDS[name] = fn
        return fn
    return deco


def register_driver(*fmts: str) -> Callable[[OutputDriver], OutputDriver]:
    def deco(fn: OutputDriver) -> OutputDriver:
        for f in fmts:
            OUTPUT_DRIVERS[f.lower()] = fn
        return fn
    return deco