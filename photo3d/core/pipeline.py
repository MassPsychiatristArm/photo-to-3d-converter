"""Pipeline orchestrator.

Wires the three stages: ingest -> processors -> output drivers.
Single-image and batch entry points share the same processor chain.

Concurrency: batch mode dispatches to a ThreadPoolExecutor. Processors
must be thread-safe; the default depth backends release the GIL during
torch forward passes, so this is a real speedup, not theatre.
"""
from __future__ import annotations

import concurrent.futures as cf
from pathlib import Path

from photo3d.config.settings import Settings
from photo3d.core.registry import DEPTH_BACKENDS, OUTPUT_DRIVERS
from photo3d.handlers.dispatcher import dispatch_ingest
from photo3d.models.scene import Scene
from photo3d.models.ticket import JobTicket
from photo3d.utils.logging import get_logger
from photo3d.utils.paths import ensure_dir, safe_join

log = get_logger(__name__)

SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png", ".heic", ".webp", ".tif", ".tiff", ".bmp"}


class Pipeline:
    def __init__(self, settings: Settings, workers: int = 1) -> None:
        self.settings = settings
        self.workers = workers

    def _build_backend(self, requested: str):
        name = requested if requested != "auto" else self._auto_backend()
        if name not in DEPTH_BACKENDS:
            raise KeyError(f"unknown depth backend: {name!r}")
        return DEPTH_BACKENDS[name]()

    def _auto_backend(self) -> str:
        # Prefer depth-anything-v2 if torch is importable and CUDA is present,
        # else fall back to the classical midas-lite stub.
        for name in ("depth-anything-v2", "midas-lite"):
            try:
                DEPTH_BACKENDS[name]
                return name
            except KeyError:
                continue
        raise RuntimeError("no depth backends registered")

    def run(self, image: Path, out_dir: Path, fmt: str, depth_backend: str, stride: int) -> JobTicket:
        ensure_dir(out_dir)
        ticket = dispatch_ingest(image)
        ticket.stride = stride

        backend = self._build_backend(depth_backend)
        depth = backend.infer(ticket)
        log.info("depth map %s -> %s", image.name, depth.shape)

        scene = self._process(ticket, depth)
        driver = OUTPUT_DRIVERS.get(fmt.lower())
        if driver is None:
            raise KeyError(f"no output driver for format {fmt!r}")
        out_path = safe_join(out_dir, f"{image.stem}.{fmt}")
        driver(scene, out_path)
        ticket.artifacts.append(out_path)
        return ticket

    def _process(self, ticket: JobTicket, depth) -> Scene:
        from processors.depth_refine import refine_depth
        from processors.pointcloud_builder import build_pointcloud
        from processors.mesher import mesh_from_pointcloud

        refined = refine_depth(depth, ticket, self.settings)
        cloud = build_pointcloud(refined, ticket, self.settings)
        scene = mesh_from_pointcloud(cloud, ticket, self.settings)
        return scene

    def run_batch(self, src: Path, out_dir: Path, fmt: str) -> list[JobTicket]:
        images = [p for p in sorted(src.rglob("*")) if p.suffix.lower() in SUPPORTED_SUFFIXES]
        if not images:
            return []
        results: list[JobTicket] = []
        with cf.ThreadPoolExecutor(max_workers=self.workers) as pool:
            futures = {
                pool.submit(self.run, img, out_dir, fmt, "auto", self.settings.mesh.stride): img
                for img in images
            }
            for fut in cf.as_completed(futures):
                img = futures[fut]
                try:
                    results.append(fut.result())
                except Exception as exc:  # noqa: BLE001
                    log.error("failed %s: %s", img.name, exc)
        return results