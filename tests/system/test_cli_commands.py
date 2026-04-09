"""System tests: CLI command invocation via subprocess.

Runs the ``mda`` CLI as a subprocess and checks exit codes and stdout.
Uses PYTHONIOENCODING=utf-8 for Windows compatibility.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

_TESTS_DIR = Path(__file__).resolve().parent.parent
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from conftest import PROJECT_ROOT, CLI_DIR, EXAMPLES_DIR  # noqa: E402


# Build a clean env with UTF-8 encoding and cli/ on PYTHONPATH
def _cli_env():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # Ensure cli/ is importable
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(CLI_DIR) + (os.pathsep + existing if existing else "")
    return env


def _run_mda(*args, cwd=None, timeout=60):
    """Run ``python mda.py <args>`` and return CompletedProcess."""
    cmd = [sys.executable, str(CLI_DIR / "mda.py")] + list(args)
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=_cli_env(),
    )


class TestCLICommands:
    """Invoke CLI commands and verify exit codes / output."""

    def test_mda_help(self):
        """``mda --help`` should exit 0 and mention MDA."""
        result = _run_mda("--help")
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "MDA" in result.stdout or "mda" in result.stdout.lower(), (
            f"Help output does not mention MDA: {result.stdout[:200]}"
        )

    def test_mda_parse(self):
        """``mda parse <bpmn>`` should exit 0."""
        bpmn_path = EXAMPLES_DIR / "loan-origination" / "bpmn" / "loan-origination.bpmn"
        result = _run_mda("parse", str(bpmn_path))
        assert result.returncode == 0, (
            f"mda parse failed (rc={result.returncode}): {result.stderr}"
        )

    def test_mda_status(self):
        """``mda status`` in income-verification should exit 0."""
        cwd = EXAMPLES_DIR / "income-verification"
        result = _run_mda("status", cwd=cwd)
        assert result.returncode == 0, (
            f"mda status failed (rc={result.returncode}): {result.stderr}"
        )

    def test_mda_validate(self):
        """``mda validate`` in income-verification should not crash."""
        cwd = EXAMPLES_DIR / "income-verification"
        result = _run_mda("validate", cwd=cwd)
        # Accept 0 (pass) or 1 (validation warnings) -- just not a crash
        assert result.returncode in (0, 1), (
            f"mda validate crashed (rc={result.returncode}): {result.stderr}"
        )

    def test_mda_config(self):
        """``mda config`` in income-verification should exit 0."""
        cwd = EXAMPLES_DIR / "income-verification"
        result = _run_mda("config", cwd=cwd)
        assert result.returncode == 0, (
            f"mda config failed (rc={result.returncode}): {result.stderr}"
        )

    def test_mda_gaps(self):
        """``mda gaps`` in income-verification should exit 0."""
        cwd = EXAMPLES_DIR / "income-verification"
        result = _run_mda("gaps", cwd=cwd)
        assert result.returncode == 0, (
            f"mda gaps failed (rc={result.returncode}): {result.stderr}"
        )

    def test_mda_corpus_search(self):
        """``mda corpus search income`` should exit 0."""
        cwd = EXAMPLES_DIR / "income-verification"
        result = _run_mda("corpus", "search", "income", cwd=cwd)
        assert result.returncode == 0, (
            f"mda corpus search failed (rc={result.returncode}): {result.stderr}"
        )

    def test_mda_graph_mermaid(self):
        """``mda graph --format mermaid`` should exit 0."""
        cwd = EXAMPLES_DIR / "income-verification"
        result = _run_mda("graph", "--format", "mermaid", cwd=cwd)
        assert result.returncode == 0, (
            f"mda graph --format mermaid failed (rc={result.returncode}): {result.stderr}"
        )

    def test_mda_no_command(self):
        """``mda`` with no arguments should exit non-zero."""
        result = _run_mda()
        assert result.returncode != 0, (
            "mda with no args should exit non-zero but got 0"
        )
