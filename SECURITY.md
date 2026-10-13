# Security Policy

## Scope

photo-to-3d-converter runs **entirely on your machine**. It does not
phone home, does not upload your photos, and does not run a network
service unless you deliberately start the optional HTTP ingest server
(`photo3d serve`).

## Reporting a vulnerability

Open a private security advisory on GitHub, or email the maintainer
listed in `pyproject.toml`. Please don't open a public issue for
anything exploitable.

We'll acknowledge within 72 hours and aim to ship a fix within 14 days
for anything rated high or above.

## Things we care about

- **Path traversal** in the HTTP ingest server (`services/http_ingest.py`).
  All user-supplied paths must go through `utils/paths.py:safe_join`.
- **Pickle loading.** We never load `.pkl` or `.pt` files from
  untrusted sources. Weight files are fetched from pinned HTTPS URLs
  with SHA-256 verification in `scripts/fetch_weights.py`.
- **Subprocess calls.** The C++ meshing accelerator (`native/mesh_accel`)
  is invoked via `subprocess.run` with a fixed argv list — no shell=True.
- **EXIF metadata.** Malformed EXIF from untrusted images is parsed by
  Pillow; we pin a minimum version in `pyproject.toml` and fuzz the
  ingest path in `tests/test_ingest_exif.py`.

## Out of scope

- Running untrusted model weights. If you download a `.safetensors`
  from a random Discord, that's on you.
- Denial of service via absurdly large input images. We cap at
  128 megapixels and document the cap.

## Supported versions

Only the latest minor release gets security fixes. We're a hobby
project; upgrade.