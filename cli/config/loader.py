"""Config loading: find mda.config.yaml, merge with defaults, apply env overrides."""

import copy
import os
from pathlib import Path
from typing import Optional

import yaml

from .defaults import DEFAULTS


class Config:
    """Holds merged configuration with dotted-key access and path resolution."""

    def __init__(self, data: dict, config_path: Optional[Path] = None):
        self._data = data
        self.config_path = config_path
        self.project_root = config_path.parent if config_path else Path.cwd()

    def get(self, dotted_key: str, default=None):
        """Get a config value by dotted key (e.g., 'llm.provider')."""
        keys = dotted_key.split(".")
        value = self._data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, dotted_key: str, value) -> None:
        """Set a config value by dotted key."""
        keys = dotted_key.split(".")
        target = self._data
        for key in keys[:-1]:
            if key not in target or not isinstance(target[key], dict):
                target[key] = {}
            target = target[key]
        target[keys[-1]] = value

    def resolve_path(self, dotted_key: str) -> Path:
        """Resolve a path config value relative to project root."""
        raw = self.get(dotted_key, "")
        return (self.project_root / raw).resolve()

    @property
    def schemas_dir(self) -> Path:
        return self.resolve_path("pipeline.schemas")

    @property
    def ontology_dir(self) -> Path:
        return self.resolve_path("pipeline.ontology")

    @property
    def corpus_dir(self) -> Path:
        return self.resolve_path("paths.corpus")

    @property
    def llm_provider(self) -> str:
        return os.environ.get(
            "MDA_LLM_PROVIDER", self.get("llm.provider", "anthropic")
        )

    @property
    def llm_model(self) -> str:
        return os.environ.get(
            "MDA_LLM_MODEL", self.get("llm.model", "claude-sonnet-4-20250514")
        )

    @property
    def llm_api_key(self) -> Optional[str]:
        env_var = self.get("llm.api_key_env", "ANTHROPIC_API_KEY")
        return os.environ.get(env_var)

    def to_dict(self) -> dict:
        return copy.deepcopy(self._data)


def find_config(start_dir: Optional[Path] = None) -> Optional[Path]:
    """Walk up from start_dir looking for mda.config.yaml (like git does for .git)."""
    current = (start_dir or Path.cwd()).resolve()
    while True:
        candidate = current / "mda.config.yaml"
        if candidate.exists():
            return candidate
        parent = current.parent
        if parent == current:
            return None
        current = parent


def load_config(config_path: Optional[Path] = None) -> "Config":
    """Load config from file, merge with defaults, apply env overrides."""
    data = copy.deepcopy(DEFAULTS)

    if config_path is None:
        config_path = find_config()

    if config_path and config_path.exists():
        with open(config_path) as f:
            file_data = yaml.safe_load(f) or {}
        data = _deep_merge(data, file_data)

    return Config(data, config_path)


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
