"""Native-format triple adapter.

Reads YAML/JSON files that conform directly to files/triple-schema.md with
full cim/pim/psm nesting and produces Triple pydantic objects.

Spec reference: files/01-triple-loader.md §B2-B4.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import yaml
from pydantic import ValidationError

from triple_flow_sim.contracts.triple import Triple


def discover_files(
    root: Path,
    source_format: str,
    ignore_paths: list[str],
) -> list[Path]:
    """Walk root. Return list of *.yaml or *.json files (per source_format).

    Skip any path containing an ignore_paths entry.

    Args:
        root: Corpus root directory.
        source_format: One of 'native_yaml' or 'native_json'.
        ignore_paths: Substrings — if any appears in a path, that path is skipped.

    Returns:
        Sorted list of matching absolute file paths.
    """
    if source_format == "native_yaml":
        suffixes = (".yaml", ".yml")
    elif source_format == "native_json":
        suffixes = (".json",)
    else:
        raise ValueError(
            f"Unsupported source_format for native adapter: {source_format}"
        )

    ignore_paths = ignore_paths or []
    results: list[Path] = []

    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in suffixes:
            continue
        as_str = str(p)
        if any(ignore in as_str for ignore in ignore_paths):
            continue
        results.append(p.resolve())

    return sorted(results)


def load_triple(
    file_path: Path,
    source_format: str,
) -> tuple[Optional[Triple], Optional[dict]]:
    """Parse one file into a Triple.

    Returns (triple, error) where:
      triple is None and error is a dict {path, error_message} on parse failure
      triple is a Triple and error is None on success

    Preserves _source_path on the triple via Triple.source_path.
    """
    try:
        text = Path(file_path).read_text(encoding="utf-8")
    except OSError as exc:
        return None, {"path": str(file_path), "error_message": f"read failed: {exc}"}

    # Parse the text.
    try:
        if source_format == "native_yaml":
            data = yaml.safe_load(text)
        elif source_format == "native_json":
            data = json.loads(text)
        else:
            return None, {
                "path": str(file_path),
                "error_message": f"unsupported source_format: {source_format}",
            }
    except (yaml.YAMLError, json.JSONDecodeError) as exc:
        return None, {
            "path": str(file_path),
            "error_message": f"parse failed: {exc}",
        }

    if not isinstance(data, dict):
        return None, {
            "path": str(file_path),
            "error_message": "root of native triple file must be a mapping",
        }

    # Validate via pydantic.
    try:
        triple = Triple.model_validate(data)
    except ValidationError as exc:
        return None, {
            "path": str(file_path),
            "error_message": f"schema validation failed: {exc}",
        }

    triple.source_path = str(file_path)
    return triple, None
