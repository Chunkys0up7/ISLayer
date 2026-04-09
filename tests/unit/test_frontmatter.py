"""Unit tests for cli/mda_io/frontmatter.py — YAML frontmatter parsing."""

import sys
import os
import pytest
from pathlib import Path

_TESTS_DIR = Path(__file__).parent.parent.resolve()
_PROJECT_ROOT = _TESTS_DIR.parent.resolve()
sys.path.insert(0, str(_PROJECT_ROOT / "cli"))

from mda_io.frontmatter import (
    parse_frontmatter,
    read_frontmatter_file,
    write_frontmatter_file,
    update_frontmatter,
)

EXAMPLES_DIR = _PROJECT_ROOT / "examples"


class TestParseFrontmatterBasic:
    """parse_frontmatter with simple key-value YAML."""

    def test_basic_parse(self):
        content = "---\nkey: val\n---\nbody"
        fm, body = parse_frontmatter(content)
        assert fm == {"key": "val"}
        assert body == "body"


class TestParseFrontmatterEmptyYaml:
    """parse_frontmatter with empty YAML block returns empty dict."""

    def test_empty_yaml(self):
        content = "---\n---\nbody text"
        fm, body = parse_frontmatter(content)
        assert fm == {}
        assert "body text" in body


class TestParseFrontmatterNoDelimiters:
    """parse_frontmatter with no --- delimiters returns empty dict and full content."""

    def test_no_delimiters(self):
        content = "just plain text\nno frontmatter here"
        fm, body = parse_frontmatter(content)
        assert fm == {}
        assert body == content


class TestParseFrontmatterNoClosingDelimiter:
    """parse_frontmatter with opening --- but no closing --- returns empty dict."""

    def test_no_closing_delimiter(self):
        content = "---\nkey: val\nno closing"
        fm, body = parse_frontmatter(content)
        assert fm == {}
        assert body == content


class TestParseFrontmatterComplexNested:
    """parse_frontmatter with nested YAML structures."""

    def test_complex_nested(self):
        content = "---\nparent:\n  child: value\n  list:\n    - one\n    - two\n---\nbody"
        fm, body = parse_frontmatter(content)
        assert fm["parent"]["child"] == "value"
        assert fm["parent"]["list"] == ["one", "two"]
        assert body == "body"


class TestWriteReadRoundTrip:
    """write_frontmatter_file then read_frontmatter_file round-trips."""

    def test_round_trip(self, tmp_path):
        path = tmp_path / "test.md"
        fm = {"title": "Test", "version": "1.0"}
        body = "# Hello\n\nThis is content.\n"
        write_frontmatter_file(path, fm, body)
        fm2, body2 = read_frontmatter_file(path)
        assert fm2["title"] == "Test"
        assert fm2["version"] == "1.0"
        assert "# Hello" in body2
        assert "This is content." in body2


class TestRoundTripWithLists:
    """round-trip preserves list values in frontmatter."""

    def test_round_trip_with_lists(self, tmp_path):
        path = tmp_path / "list.md"
        fm = {"tags": ["alpha", "beta", "gamma"], "count": 3}
        body = "Body text\n"
        write_frontmatter_file(path, fm, body)
        fm2, body2 = read_frontmatter_file(path)
        assert fm2["tags"] == ["alpha", "beta", "gamma"]
        assert fm2["count"] == 3
        assert "Body text" in body2


class TestReadRealCapsuleFile:
    """read_frontmatter_file on a real capsule file extracts the correct capsule_id."""

    def test_read_real_capsule(self):
        path = (
            EXAMPLES_DIR
            / "loan-origination"
            / "triples"
            / "assess-dti"
            / "assess-dti.cap.md"
        )
        fm, body = read_frontmatter_file(path)
        assert fm["capsule_id"] == "CAP-LO-DTI-001"
        assert fm["bpmn_task_type"] == "businessRuleTask"
        assert fm["process_id"] == "Process_LoanOrigination"


class TestUpdatePreservesBody:
    """update_frontmatter modifies a field while preserving the body and other fields."""

    def test_update_preserves_body(self, tmp_path):
        path = tmp_path / "update.md"
        fm = {"title": "Original", "status": "draft", "count": 5}
        body = "# Keep this body\n\nParagraph.\n"
        write_frontmatter_file(path, fm, body)

        update_frontmatter(path, {"status": "approved"})

        fm2, body2 = read_frontmatter_file(path)
        assert fm2["status"] == "approved"
        assert fm2["title"] == "Original"
        assert fm2["count"] == 5
        assert "# Keep this body" in body2
        assert "Paragraph." in body2


class TestUpdatePreservesOtherFields:
    """update_frontmatter adds new fields without removing existing ones."""

    def test_update_adds_field(self, tmp_path):
        path = tmp_path / "add.md"
        fm = {"a": 1, "b": 2}
        body = "body\n"
        write_frontmatter_file(path, fm, body)

        update_frontmatter(path, {"c": 3})

        fm2, _ = read_frontmatter_file(path)
        assert fm2["a"] == 1
        assert fm2["b"] == 2
        assert fm2["c"] == 3
