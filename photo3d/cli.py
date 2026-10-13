"""Typer-based command-line entry point.

Commands:
    convert     run the full ingest -> processors -> drivers pipeline
    batch       convert every image under a directory
    inspect     dump the parsed JobTicket for a single input (no conversion)
    backends    list registered depth backends and their availability
    serve       start the optional HTTP ingest server (localhost only)
"""
from __future__ import annotations

import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from photo3d.core.pipeline import Pipeline
from photo3d.core.registry import DEPTH_BACKENDS, INGEST_HANDLERS, OUTPUT_DRIVERS
from photo3d.config.settings import load_settings
from photo3d.utils.logging import configure_logging

app = typer.Typer(add_completion=False, help="AI 2D-to-3D photo converter.")
console = Console()
log = logging.getLogger("photo3d.cli")


@app.command()
def convert(
    image: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    out: Path = typer.Option(Path("outputs"), "--out", "-o", help="Output directory."),
    profile: str = typer.Option("fast", "--profile", "-p", help="fast | balanced | quality"),
    fmt: str = typer.Option("glb", "--format", "-f", help="glb | obj | ply | stl"),
    depth_backend: str = typer.Option("auto", "--depth", help="Registered backend name or 'auto'."),
    point_stride: int = typer.Option(2, "--stride", help="Point-cloud downsample stride (>=1)."),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Convert a single image into a textured 3D mesh."""
    configure_logging(verbose)
    settings = load_settings(profile=profile)
    pipeline = Pipeline(settings)
    ticket = pipeline.run(image=image, out_dir=out, fmt=fmt,
                          depth_backend=depth_backend, stride=point_stride)
    console.print(f"[green]ok[/] wrote {ticket.artifacts[0]}")


@app.command()
def batch(
    src: Path = typer.Argument(..., exists=True, file_okay=False),
    out: Path = typer.Option(Path("outputs"), "--out", "-o"),
    profile: str = typer.Option("fast", "--profile", "-p"),
    fmt: str = typer.Option("glb", "--format", "-f"),
    jobs: int = typer.Option(1, "--jobs", "-j", min=1, max=16),
) -> None:
    """Convert every supported image under SRC."""
    configure_logging(False)
    settings = load_settings(profile=profile)
    pipeline = Pipeline(settings, workers=jobs)
    results = pipeline.run_batch(src, out, fmt)
    console.print(f"[green]ok[/] {len(results)} mesh(es) written to {out}")


@app.command()
def inspect(image: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    """Parse the ingest ticket for an image without running conversion."""
    from photo3d.handlers.dispatcher import dispatch_ingest

    ticket = dispatch_ingest(image)
    table = Table(title=f"JobTicket — {image.name}")
    table.add_column("field"); table.add_column("value")
    for k, v in ticket.model_dump().items():
        table.add_row(k, str(v)[:80])
    console.print(table)


@app.command()
def backends() -> None:
    """List registered depth backends and whether their deps are importable."""
    table = Table(title="Depth backends")
    table.add_column("name"); table.add_column("available"); table.add_column("notes")
    for name, factory in DEPTH_BACKENDS.items():
        try:
            factory  # presence check only
            avail = "[green]yes[/]"
        except Exception as exc:  # noqa: BLE001
            avail = f"[red]no[/] ({exc.__class__.__name__})"
        table.add_row(name, avail, getattr(factory, "__doc__", "") or "")
    console.print(table)


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", help="Bind address. Localhost by default."),
    port: int = typer.Option(8787, help="Port."),
) -> None:
    """Start the localhost-only HTTP ingest server."""
    from photo3d.services.http_ingest import run_server

    console.print(f"[yellow]listening[/] http://{host}:{port} — localhost only, ctrl-c to stop")
    run_server(host=host, port=port)


if __name__ == "__main__":
    app()