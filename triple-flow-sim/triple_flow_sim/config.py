"""Configuration loader for the Triple Flow Simulator.

Loads YAML config files with optional env-variable overrides.
See config/loader.default.yaml for the canonical structure.

Spec reference: files/01-triple-loader.md §Inputs (loader.config.yaml).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

import yaml


DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config" / "loader.default.yaml"


class Config:
    """Simple dotted-key config accessor."""

    def __init__(self, data: dict, source_path: Optional[Path] = None) -> None:
        self._data = data
        self.source_path = source_path
        # Project root is the directory containing the config file, or cwd
        self.project_root = source_path.parent if source_path else Path.cwd()

    def get(self, dotted_key: str, default: Any = None) -> Any:
        """Get a value by dotted key (e.g. 'source.path')."""
        keys = dotted_key.split(".")
        value: Any = self._data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def to_dict(self) -> dict:
        return dict(self._data)


def load_config(config_path: Optional[Path] = None) -> Config:
    """Load a YAML config file.

    Args:
        config_path: Path to a YAML file. If None, loads the default config.

    Returns:
        Config object with dotted-key access.
    """
    import copy

    # Load default first
    default_data: dict = {}
    if DEFAULT_CONFIG_PATH.exists():
        with open(DEFAULT_CONFIG_PATH) as f:
            default_data = yaml.safe_load(f) or {}

    if config_path is None:
        return Config(default_data, DEFAULT_CONFIG_PATH)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        user_data = yaml.safe_load(f) or {}

    # Deep merge: user values override defaults
    merged = _deep_merge(copy.deepcopy(default_data), user_data)
    return Config(merged, config_path)


def _deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
