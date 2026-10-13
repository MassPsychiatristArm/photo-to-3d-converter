"""Classical fallback backend — a cheap luminance/gradient depth proxy.

This exists so the CLI boots and produces *something* without torch
installed. It is not a real depth model. It is a shape-correct stub
that lets the rest of the pipeline be developed and tested on machines
without a GPU.
"""
from __future__ import annotations

import cv2
import numpy as np

from photo3d.core.registry import register_backend


class MidasLiteBackend:
    """Luminance + vertical-gradient proxy. Fast, wrong, useful."""

    name = "midas-lite"

    def infer(self, ticket) -> np.ndarray:
        rgb = ticket.array
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
        gray /= max(gray.max(), 1.0)

        # Cheap pseudo-depth: brighter + higher in the frame == closer.
        h, w = gray.shape
        vertical = 1.0 - (np.arange(h, dtype=np.float32)[:, None] / h)
        blur = cv2.GaussianBlur(gray, (0, 0), sigmaX=3.0)
        depth = 0.6 * blur + 0.4 * vertical
        depth = (depth - depth.min()) / max(depth.ptp(), 1e-6)
        return depth.astype(np.float32)

    def release(self) -> None:
        return None


@register_backend("midas-lite")
def _factory() -> MidasLiteBackend:
    return MidasLiteBackend()