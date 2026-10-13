"""Depth backend protocol.

A backend takes a JobTicket (which holds the decoded numpy RGB array)
and returns a float32 depth map in [0, 1], shape (H, W), matching the
ticket's working resolution.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np

from photo3d.models.ticket import JobTicket


@runtime_checkable
class DepthBackend(Protocol):
    name: str

    def infer(self, ticket: JobTicket) -> np.ndarray:
        """Return float32 depth map, shape (H, W), values in [0, 1]."""
        ...

    def release(self) -> None:
        """Free GPU memory if the backend holds any."""
        ...