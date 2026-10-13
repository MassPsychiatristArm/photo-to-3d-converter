"""photo-to-3d-converter — AI 2D-to-3D photo conversion pipeline.

Public entry points live in :mod:`photo3d.cli`. The pipeline itself is
composed of three stages wired together by :class:`photo3d.core.pipeline.Pipeline`:

    ingest  ->  processors  ->  output drivers

Each stage is pluggable via the registries in :mod:`photo3d.core.registry`.
"""

__version__ = "0.6.2"
__all__ = ["__version__"]