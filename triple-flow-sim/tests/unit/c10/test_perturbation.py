"""Tests for the perturbation and ablation generators."""
from __future__ import annotations

import pytest

from triple_flow_sim.components.c10_perturbation import (
    AblationGenerator,
    PerturbationGenerator,
    PerturbationSpec,
)
from triple_flow_sim.components.c10_perturbation.ablation import (
    ablate_triple,
)
from triple_flow_sim.components.c10_perturbation.perturbation import (
    apply_perturbation,
)
from triple_flow_sim.contracts import (
    ContentChunk,
    PIMLayer,
    PSMLayer,
    StateFieldRef,
    Triple,
)


def test_drop_removes_path():
    state = {"a": {"b": 1, "c": 2}}
    out = apply_perturbation(
        state, PerturbationSpec(kind="drop", path="a.b")
    )
    assert "b" not in out["a"]
    assert out["a"]["c"] == 2


def test_null_sets_path_to_none():
    state = {"x": 5}
    out = apply_perturbation(
        state, PerturbationSpec(kind="null", path="x")
    )
    assert out["x"] is None


def test_truncate_halves_string():
    state = {"s": "abcdef"}
    out = apply_perturbation(
        state, PerturbationSpec(kind="truncate", path="s")
    )
    assert len(out["s"]) <= 3


def test_corrupt_changes_type():
    state = {"n": 42}
    out = apply_perturbation(
        state, PerturbationSpec(kind="corrupt", path="n", seed=1)
    )
    assert not isinstance(out["n"], int) or isinstance(out["n"], bool)


def test_perturbation_plan_covers_every_read_x_kind():
    t = Triple(
        triple_id="T",
        pim=PIMLayer(
            state_reads=[
                StateFieldRef(path="a"), StateFieldRef(path="b"),
            ]
        ),
    )
    specs = PerturbationGenerator().plan(t)
    # 2 reads × 4 kinds = 8
    assert len(specs) == 8
    kinds = {s.kind for s in specs}
    assert kinds == {"drop", "null", "truncate", "corrupt"}


def test_perturbation_invalid_kind_raises():
    with pytest.raises(ValueError):
        apply_perturbation({}, PerturbationSpec(kind="explode", path="x"))


def test_ablation_removes_chunk():
    t = Triple(
        triple_id="T",
        psm=PSMLayer(
            enriched_content=[
                ContentChunk(chunk_id="c1", text="keep"),
                ContentChunk(chunk_id="c2", text="drop"),
            ]
        ),
    )
    ablated = ablate_triple(t, "c2")
    ids = {c.chunk_id for c in ablated.psm.enriched_content}
    assert ids == {"c1"}


def test_ablation_plan_one_spec_per_chunk():
    t = Triple(
        triple_id="T",
        psm=PSMLayer(
            enriched_content=[
                ContentChunk(chunk_id="c1"),
                ContentChunk(chunk_id="c2"),
                ContentChunk(chunk_id="c3"),
            ]
        ),
    )
    specs = AblationGenerator().plan(t)
    assert {s.chunk_id for s in specs} == {"c1", "c2", "c3"}
