"""Unit tests for cli/config/loader.py — configuration loading."""

import sys
import os
import pytest
from pathlib import Path

_TESTS_DIR = Path(__file__).parent.parent.resolve()
_PROJECT_ROOT = _TESTS_DIR.parent.resolve()
sys.path.insert(0, str(_PROJECT_ROOT / "cli"))

from config.loader import Config, find_config, load_config, _deep_merge

EXAMPLES_DIR = _PROJECT_ROOT / "examples"
PROJECT_ROOT = _PROJECT_ROOT


# ---------------------------------------------------------------------------
# find_config
# ---------------------------------------------------------------------------

class TestFindConfigFromExampleDir:
    """find_config discovers mda.config.yaml when starting in an example dir."""

    def test_find_config(self):
        example_dir = EXAMPLES_DIR / "loan-origination"
        result = find_config(example_dir)
        assert result is not None
        assert result.name == "mda.config.yaml"


class TestFindConfigFromRoot:
    """find_config returns None from filesystem root (no mda.config.yaml there)."""

    def test_find_config_from_root(self):
        root = Path("/")
        result = find_config(root)
        assert result is None


# ---------------------------------------------------------------------------
# load_config
# ---------------------------------------------------------------------------

class TestLoadConfigProcessId:
    """load_config from loan-origination has the correct process.id."""

    def test_process_id(self):
        config_path = EXAMPLES_DIR / "loan-origination" / "mda.config.yaml"
        cfg = load_config(config_path)
        assert cfg.get("process.id") == "Process_LoanOrigination"


class TestGetDottedKey:
    """Config.get with a dotted key drills into nested dicts."""

    def test_get_dotted(self):
        data = {"a": {"b": {"c": 42}}}
        cfg = Config(data)
        assert cfg.get("a.b.c") == 42


class TestGetWithDefault:
    """Config.get returns the default when the key path does not exist."""

    def test_get_default(self):
        cfg = Config({"a": 1})
        assert cfg.get("missing.key", "fallback") == "fallback"


class TestSetCreatesNestedKey:
    """Config.set creates intermediate dicts and stores the value."""

    def test_set_nested(self):
        cfg = Config({})
        cfg.set("x.y.z", "hello")
        assert cfg.get("x.y.z") == "hello"


class TestResolvePath:
    """Config.resolve_path returns an absolute Path."""

    def test_resolve_path(self):
        config_path = EXAMPLES_DIR / "loan-origination" / "mda.config.yaml"
        cfg = load_config(config_path)
        resolved = cfg.resolve_path("source.bpmn_file")
        assert resolved.is_absolute()
        assert "bpmn" in str(resolved)


# ---------------------------------------------------------------------------
# _deep_merge
# ---------------------------------------------------------------------------

class TestDeepMergeNested:
    """_deep_merge recursively merges nested dicts."""

    def test_deep_merge_nested(self):
        base = {"a": {"b": 1, "c": 2}, "d": 3}
        override = {"a": {"c": 99, "e": 5}}
        result = _deep_merge(base, override)
        assert result["a"]["b"] == 1      # preserved from base
        assert result["a"]["c"] == 99     # overridden
        assert result["a"]["e"] == 5      # added
        assert result["d"] == 3           # preserved


class TestDeepMergeOverride:
    """_deep_merge replaces non-dict values entirely."""

    def test_deep_merge_override(self):
        base = {"a": [1, 2], "b": "old"}
        override = {"a": [3, 4], "b": "new"}
        result = _deep_merge(base, override)
        assert result["a"] == [3, 4]
        assert result["b"] == "new"


# ---------------------------------------------------------------------------
# load_config without file uses defaults
# ---------------------------------------------------------------------------

class TestLoadWithoutConfigFile:
    """load_config with a nonexistent path returns config with default values."""

    def test_defaults(self, tmp_path):
        missing = tmp_path / "nonexistent" / "mda.config.yaml"
        cfg = load_config(missing)
        # Should have default values from DEFAULTS
        assert cfg.get("defaults.status") == "draft"
        assert cfg.get("llm.provider") is not None
