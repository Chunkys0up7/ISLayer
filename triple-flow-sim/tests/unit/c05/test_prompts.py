"""Tests for the prompt templates."""
from __future__ import annotations

import pytest

from triple_flow_sim.components.c05_llm.prompts import (
    TEMPLATE_VERSION,
    list_templates,
    render,
)


def test_version_is_set():
    assert TEMPLATE_VERSION


def test_registry_contains_all_levels():
    ids = list_templates()
    assert "level1_full_content" in ids
    assert "level2_declared_only" in ids
    assert "level3_minimum" in ids
    assert "grounded_task" in ids
    assert "grounded_gateway" in ids


def test_level1_renders_content_chunks():
    rendered = render(
        "level1_full_content",
        triple_id="T1",
        bpmn_node_id="node1",
        bpmn_node_type="task",
        intent="Do the thing",
        content_chunks=[{"chunk_id": "c1", "text": "hello"}],
        state_reads=[],
        state_writes=[],
        state_json="{}",
    )
    assert "c1" in rendered.prompt
    assert "hello" in rendered.prompt
    assert "Do the thing" in rendered.prompt


def test_unknown_template_raises():
    with pytest.raises(KeyError):
        render("no_such_template")
