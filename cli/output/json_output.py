"""JSON output formatter for --json flag."""

import json
import sys
from dataclasses import asdict, is_dataclass
from typing import Any


def output_json(data: Any, indent: int = 2) -> None:
    """Print data as JSON to stdout."""
    if is_dataclass(data) and not isinstance(data, type):
        data = asdict(data)
    print(json.dumps(data, indent=indent, default=str))


def output_json_error(error: str, details: Any = None) -> None:
    """Print error as JSON to stderr."""
    obj: dict[str, Any] = {"error": error}
    if details:
        obj["details"] = details
    print(json.dumps(obj, indent=2, default=str), file=sys.stderr)
