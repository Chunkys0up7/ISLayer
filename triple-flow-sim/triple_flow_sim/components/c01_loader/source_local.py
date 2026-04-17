"""Local filesystem source for the Triple Loader.

Spec reference: files/01-triple-loader.md §B1 (Resolve source).
"""
from __future__ import annotations

from pathlib import Path


def resolve_local(path: Path) -> Path:
    """Validate a local corpus path. Returns absolute path.

    Raises:
        FileNotFoundError: If the path does not exist.
        NotADirectoryError: If the path exists but is not a directory.
    """
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"Local corpus path not found: {p}")
    if not p.is_dir():
        raise NotADirectoryError(f"Local corpus path is not a directory: {p}")
    return p
