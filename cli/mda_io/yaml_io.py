"""YAML read/write helpers."""

import yaml
from pathlib import Path
from typing import Any


def read_yaml(path: Path) -> Any:
    """Read a YAML file and return the parsed data."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(path: Path, data: Any) -> None:
    """Write data to a YAML file with readable formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            data,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        )


def read_yaml_string(content: str) -> Any:
    """Parse a YAML string."""
    return yaml.safe_load(content)


def dump_yaml_string(data: Any) -> str:
    """Dump data to a YAML string."""
    return yaml.dump(
        data,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )
