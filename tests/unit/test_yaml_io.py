"""Unit tests for cli/mda_io/yaml_io.py — YAML read/write helpers."""

import sys
import os
import pytest
from pathlib import Path

# Resolve project paths relative to this file
_TESTS_DIR = Path(__file__).parent.parent.resolve()
_PROJECT_ROOT = _TESTS_DIR.parent.resolve()
sys.path.insert(0, str(_PROJECT_ROOT / "cli"))

from mda_io.yaml_io import read_yaml, write_yaml, read_yaml_string, dump_yaml_string

CORPUS_DIR = _PROJECT_ROOT / "corpus"


class TestYamlRoundTrip:
    """write_yaml then read_yaml returns the same data."""

    def test_round_trip(self, tmp_path):
        data = {"key": "value", "nested": {"a": 1, "b": [2, 3]}}
        path = tmp_path / "test.yaml"
        write_yaml(path, data)
        result = read_yaml(path)
        assert result == data


class TestReadRealFile:
    """read_yaml can load a real project file."""

    def test_read_corpus_config(self):
        path = CORPUS_DIR / "corpus.config.yaml"
        data = read_yaml(path)
        assert isinstance(data, dict)
        assert "documents" in data
        assert data["version"] == "1.0"


class TestReadYamlString:
    """read_yaml_string parses inline YAML content."""

    def test_parse_string(self):
        content = "key: value\nlist:\n  - a\n  - b\n"
        result = read_yaml_string(content)
        assert result == {"key": "value", "list": ["a", "b"]}


class TestDumpYamlString:
    """dump_yaml_string serialises data to a YAML string."""

    def test_dump_string(self):
        data = {"key": "value", "number": 42}
        result = dump_yaml_string(data)
        assert "key: value" in result
        assert "number: 42" in result
        # Should be parseable back
        assert read_yaml_string(result) == data


class TestCreatesParentDirs:
    """write_yaml creates intermediate directories."""

    def test_creates_parent_dirs(self, tmp_path):
        nested = tmp_path / "a" / "b" / "c" / "data.yaml"
        write_yaml(nested, {"x": 1})
        assert nested.exists()
        assert read_yaml(nested) == {"x": 1}


class TestEmptyFile:
    """read_yaml returns None for an empty file."""

    def test_empty_file_returns_none(self, tmp_path):
        empty = tmp_path / "empty.yaml"
        empty.write_text("", encoding="utf-8")
        result = read_yaml(empty)
        assert result is None
