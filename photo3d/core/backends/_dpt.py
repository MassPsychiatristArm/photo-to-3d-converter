"""DPT head shim.

Real implementation lives in the reference repo; this is the seam so the
backend module stays readable. Tests monkeypatch ``build_dpt_head`` to a
tiny identity module.
"""
from __future__ import annotations


def build_dpt_head():
    import torch.nn as nn  # noqa: PLC0415

    class _Passthrough(nn.Module):
        def forward(self, x):  # noqa: ANN001
            # Returns a channel-reduced map so downstream code has the right
            # shape even without real weights.
            return x.mean(dim=1, keepdim=True)

    return _Passthrough()