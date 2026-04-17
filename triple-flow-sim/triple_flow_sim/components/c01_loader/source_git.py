"""Git clone integration for the Triple Loader.

Spec reference: files/01-triple-loader.md §B1 (Resolve source).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

try:
    import git  # type: ignore
except ImportError:  # pragma: no cover
    git = None  # type: ignore


_URL_SANITIZE_RE = re.compile(r"[^A-Za-z0-9._-]+")


def _sanitize_url(url: str) -> str:
    """Turn an SSH/HTTPS URL into a filesystem-safe directory name."""
    return _URL_SANITIZE_RE.sub("_", url).strip("_")


def clone_or_update(
    ssh_url: str,
    branch: str = "main",
    cache_root: Optional[Path] = None,
) -> Path:
    """Clone (or fetch latest) a bitbucket repo via SSH. Returns local path.

    cache_root defaults to ./cache/repos/. Repo is cloned into
    cache_root/<sanitized_url>/<branch>/.

    Args:
        ssh_url: SSH URL (e.g. git@bitbucket.org:team/triples.git)
        branch: Branch to check out (defaults to main)
        cache_root: Where to place cached clones; defaults to cwd/cache/repos

    Returns:
        Absolute path to the local working tree.

    Raises:
        RuntimeError: If gitpython is not installed.
        git.exc.GitCommandError: On SSH authentication or network failure
            (re-raised with a clearer message).
    """
    if git is None:
        raise RuntimeError(
            "gitpython is not installed. Install with `pip install gitpython`."
        )

    if cache_root is None:
        cache_root = Path.cwd() / "cache" / "repos"

    cache_root = Path(cache_root).resolve()
    target_dir = cache_root / _sanitize_url(ssh_url) / branch
    target_dir.parent.mkdir(parents=True, exist_ok=True)

    if (target_dir / ".git").is_dir():
        # Update existing clone.
        try:
            repo = git.Repo(target_dir)
            origin = repo.remote()
            origin.fetch()
            repo.git.checkout(branch)
            origin.pull(branch)
        except git.exc.GitCommandError as exc:  # type: ignore[attr-defined]
            raise RuntimeError(
                f"Failed to fetch/update repo {ssh_url} at branch {branch}: {exc}"
            ) from exc
    else:
        # Fresh clone.
        try:
            git.Repo.clone_from(ssh_url, target_dir, branch=branch)
        except git.exc.GitCommandError as exc:  # type: ignore[attr-defined]
            raise RuntimeError(
                f"Failed to clone repo {ssh_url} (branch={branch}). "
                f"Check SSH keys and network: {exc}"
            ) from exc

    return target_dir
