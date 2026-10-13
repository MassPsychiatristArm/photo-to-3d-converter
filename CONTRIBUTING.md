# Contributing to photo-to-3d-converter

Thanks for wanting to make 2D photos pop into 3D. This is a hobbyist
open-source project; there's no corporate CLA, no Slack, no standups.
Just PRs.

## Ground rules

- **Python 3.11+** is the target runtime. 3.12 works. 3.10 is best-effort.
- **Windows is the primary platform.** macOS/Linux PRs are welcome but
  must not regress the Windows path.
- Keep the pipeline contract stable. Ingest handlers emit `JobTicket`
  objects; processors consume them; output drivers write artifacts.
  If you need a new field, add it with a default so older handlers
  keep working.
- Torch is optional at import time. Anything that hard-imports torch
  must live behind `core/backends/` so the CLI still boots without a
  GPU.

## Dev setup

```
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev,cuda]
python scripts/fetch_weights.py --profile quality
pytest -q
```

If you're on CPU only, drop `cuda` and use `--profile fast`.

## What we want PRs for

- New depth backends (MiDaS v3.1, Depth Anything V2, Marigold, etc.)
- Point-cloud meshing quality improvements
- Better EXIF / metadata round-tripping on output
- GUI polish (PySide6) — it's rough, we know
- Windows packaging (PyInstaller / Briefcase)

## What we'll bounce

- Anything that phones home. No telemetry, no analytics, no "anonymous
  usage stats." This is a local tool.
- Bundled weights. We fetch, we don't ship.
- Silent network calls during conversion.

## Commit style

Conventional-ish: `feat(depth): add Depth Anything V2 backend`,
`fix(ingest): handle HEIC orientation tag`, etc. Not enforced by CI,
but reviewers will grumble.

## Testing

Tests live in `tests/`. Unit tests should not require a GPU — mock the
backend or use the tiny fixture model in `tests/fixtures/`. Integration
tests marked `@pytest.mark.gpu` are skipped by default.