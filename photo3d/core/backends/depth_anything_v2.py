"""Depth Anything V2 backend.

Weights are fetched by ``scripts/fetch_weights.py`` into ``weights/``.
This module imports torch lazily so that ``photo3d --help`` still works
on machines without a CUDA toolchain.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from photo3d.core.registry import register_backend

_WEIGHTS = Path(__file__).resolve().parents[3] / "weights" / "depth_anything_v2_vits.safetensors"


class DepthAnythingV2Backend:
    """Small ViT-S variant. ~24M params, ~90ms/frame on an RTX 3060 @ 518px."""

    name = "depth-anything-v2"

    def __init__(self, device: str = "auto") -> None:
        import torch  # noqa: PLC0415 — lazy on purpose

        self._torch = torch
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        if not _WEIGHTS.exists():
            raise FileNotFoundError(
                f"weights missing: {_WEIGHTS}. Run scripts/fetch_weights.py first."
            )
        self._model = self._load()

    def _load(self):
        # Placeholder loader. Real loader wires the ViT-S encoder + DPT head
        # and reads the safetensors shard. Kept behind a method so tests can
        # monkeypatch it without touching the file system.
        from photo3d.core.backends._dpt import build_dpt_head  # noqa: PLC0415

        torch = self._torch
        head = build_dpt_head().to(self.device).eval()
        return head

    def infer(self, ticket) -> np.ndarray:
        torch = self._torch
        rgb = ticket.array
        # Normalize to the model's expected input: float32 in [0,1], CHW.
        x = torch.from_numpy(rgb).float().permute(2, 0, 1).unsqueeze(0) / 255.0
        x = x.to(self.device)
        with torch.inference_mode():
            depth = self._model(x)
        d = depth.squeeze().detach().cpu().numpy()
        return ((d - d.min()) / max(d.ptp(), 1e-6)).astype(np.float32)

    def release(self) -> None:
        try:
            self._torch.cuda.empty_cache()
        except Exception:  # noqa: BLE001
            pass


@register_backend("depth-anything-v2")
def _factory() -> DepthAnythingV2Backend:
    return DepthAnythingV2Backend()