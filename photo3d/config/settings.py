"""Profile-based settings loader.

Profiles are YAML files under ``config/profiles/``. A user override at
``%APPDATA%/photo3d/settings.yaml`` (Windows) or
``~/.config/photo3d/settings.yaml`` (POSIX) is deep-merged on top.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field

ProfileName = Literal["fast", "balanced", "quality"]

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PROFILE_DIR = _REPO_ROOT / "config" / "profiles"


class DepthConfig(BaseModel):
    backend: str = "auto"
    target_long_side: int = Field(518, ge=64, le=4096)
    colorize: bool = True
    invert: bool = False


class MeshConfig(BaseModel):
    stride: int = Field(2, ge=1, le=16)
    depth_edge_threshold: float = Field(0.04, gt=0.0, lt=1.0)
    smooth_iterations: int = Field(3, ge=0, le=20)
    texture_size: int = Field(2048, ge=256, le=8192)


class Settings(BaseModel):
    profile: ProfileName = "fast"
    depth: DepthConfig = DepthConfig()
    mesh: MeshConfig = MeshConfig()
    max_megapixels: int = Field(128, ge=1, le=2048)
    device: str = "auto"
    log_level: str = "INFO"


def _user_override_path() -> Path | None:
    if os.name == "nt":
        base = os.environ.get("APPDATA")
        return Path(base) / "photo3d" / "settings.yaml" if base else None
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "photo3d" / "settings.yaml"


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, val in overlay.items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], val)
        else:
            out[key] = val
    return out


def load_settings(profile: ProfileName = "fast") -> Settings:
    """Load the named profile, then merge user overrides on top."""
    profile_file = _PROFILE_DIR / f"{profile}.yaml"
    raw: dict[str, Any] = {}
    if profile_file.exists():
        raw = yaml.safe_load(profile_file.read_text(encoding="utf-8")) or {}
    raw["profile"] = profile

    override = _user_override_path()
    if override and override.exists():
        raw = _deep_merge(raw, yaml.safe_load(override.read_text(encoding="utf-8")) or {})

    return Settings.model_validate(raw)