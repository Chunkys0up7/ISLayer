"""Unit tests for the native-format adapter (YAML/JSON-as-schema)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from triple_flow_sim.components.c01_loader.adapter_native import (
    discover_files,
    load_triple,
)


FULL_TRIPLE_DICT = {
    "triple_id": "T-001",
    "version": "1.0",
    "bpmn_node_id": "Task_Example",
    "bpmn_node_type": "task",
    "cim": {
        "intent": "A simple example task.",
        "regulatory_refs": [
            {"citation": "REG-1", "rule_text": "", "obligation_type": "references"}
        ],
        "business_rules": [
            {"rule_id": "BR-001", "rule_text": "Rule one"}
        ],
    },
    "pim": {
        "preconditions": [
            {"path": "borrower.exists", "predicate": "exists"}
        ],
        "postconditions": [
            {"path": "result.set", "predicate": "exists"}
        ],
        "state_reads": [
            {"path": "input.a", "type": "string"}
        ],
        "state_writes": [
            {"path": "output.b", "type": "decimal"}
        ],
    },
    "psm": {
        "enriched_content": [
            {
                "chunk_id": "T-001:purpose",
                "source_document": "test",
                "content_type": "knowledge",
                "text": "hello",
            }
        ],
        "prompt_scaffold": "agent-x",
        "tool_bindings": [
            {"tool_id": "api.example", "purpose": "rest"}
        ],
    },
}


@pytest.fixture
def native_yaml_file(tmp_path: Path) -> Path:
    f = tmp_path / "triple.yaml"
    f.write_text(yaml.safe_dump(FULL_TRIPLE_DICT), encoding="utf-8")
    return f


@pytest.fixture
def native_json_file(tmp_path: Path) -> Path:
    f = tmp_path / "triple.json"
    f.write_text(json.dumps(FULL_TRIPLE_DICT), encoding="utf-8")
    return f


def test_load_native_yaml_triple(native_yaml_file: Path):
    triple, err = load_triple(native_yaml_file, "native_yaml")
    assert err is None
    assert triple is not None
    assert triple.triple_id == "T-001"
    assert triple.source_path == str(native_yaml_file)
    assert triple.cim is not None
    assert triple.cim.intent == "A simple example task."
    assert triple.pim is not None
    assert triple.pim.preconditions is not None
    assert len(triple.pim.preconditions) == 1
    assert triple.pim.postconditions is not None
    assert len(triple.pim.state_reads or []) == 1
    assert triple.psm is not None
    assert len(triple.psm.enriched_content) == 1
    assert triple.psm.prompt_scaffold == "agent-x"


def test_load_native_json_triple(native_json_file: Path):
    triple, err = load_triple(native_json_file, "native_json")
    assert err is None
    assert triple is not None
    assert triple.triple_id == "T-001"


def test_load_native_malformed_yaml(tmp_path: Path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("key: : : not valid yaml : :\n  bad", encoding="utf-8")
    triple, err = load_triple(bad, "native_yaml")
    assert triple is None
    assert err is not None
    assert "error_message" in err
    assert err["path"] == str(bad)


def test_load_native_malformed_json(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text("{ not json", encoding="utf-8")
    triple, err = load_triple(bad, "native_json")
    assert triple is None
    assert err is not None
    assert "error_message" in err


def test_load_native_root_not_mapping(tmp_path: Path):
    bad = tmp_path / "list.yaml"
    bad.write_text("- one\n- two\n", encoding="utf-8")
    triple, err = load_triple(bad, "native_yaml")
    assert triple is None
    assert err is not None


def test_discover_files_yaml(tmp_path: Path):
    (tmp_path / "a.yaml").write_text("x: 1\n", encoding="utf-8")
    (tmp_path / "b.yml").write_text("x: 2\n", encoding="utf-8")
    (tmp_path / "c.json").write_text("{}", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "ignored.yaml").write_text("x: 3\n", encoding="utf-8")

    files = discover_files(tmp_path, "native_yaml", ignore_paths=[".git"])
    names = {f.name for f in files}
    assert names == {"a.yaml", "b.yml"}


def test_discover_files_json(tmp_path: Path):
    (tmp_path / "a.yaml").write_text("x: 1\n", encoding="utf-8")
    (tmp_path / "c.json").write_text("{}", encoding="utf-8")
    files = discover_files(tmp_path, "native_json", ignore_paths=[])
    assert [f.name for f in files] == ["c.json"]
