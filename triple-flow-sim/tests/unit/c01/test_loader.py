"""Integration-style tests for the TripleLoader facade.

These tests copy the MDA examples into tmp_path to exercise the full B1..B8
pipeline, including the on-disk cache.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest
import yaml

# Verify source_git imports cleanly (spec requirement; no network tests).
from triple_flow_sim.components.c01_loader import source_git  # noqa: F401
from triple_flow_sim.components.c01_loader import TripleLoader
from triple_flow_sim.config import Config


EXAMPLES_ROOT = (
    Path(__file__).parent.parent.parent.parent.parent
    / "examples"
    / "income-verification"
)


@pytest.fixture
def mda_corpus(tmp_path: Path) -> Path:
    """Copy the MDA corpus into tmp so each test gets an isolated tree."""
    dst = tmp_path / "corpus"
    shutil.copytree(EXAMPLES_ROOT, dst)
    return dst


def _make_config(corpus_root: Path, cache_root: Path) -> Config:
    data = {
        "source_format": "mda_triple_dir",
        "source": {"type": "local", "path": str(corpus_root)},
        "field_mapping": {},
        "content_chunk_extraction": {"by_section": True},
        "strict_mode": False,
        "ignore_paths": [".git", ".cache"],
        "cache_root": str(cache_root),
    }
    cfg_file = corpus_root.parent / "loader.config.yaml"
    cfg_file.write_text(yaml.safe_dump(data), encoding="utf-8")
    return Config(data, cfg_file)


@pytest.fixture
def loader(mda_corpus: Path, tmp_path: Path) -> TripleLoader:
    cache_root = tmp_path / "cache"
    cfg = _make_config(mda_corpus, cache_root)
    return TripleLoader(cfg)


def test_load_mda_from_local(loader: TripleLoader):
    triple_set, report = loader.load()

    assert len(triple_set) == 8, f"expected 8 triples, got {len(triple_set)}"
    assert report.successful_loads == 8
    assert report.identity_failures == []
    assert report.failed_loads == []

    assert re.fullmatch(r"[0-9a-f]{64}", report.corpus_version_hash)
    assert triple_set.corpus_version_hash == report.corpus_version_hash

    # Spot-check one known id.
    assert any(tid.startswith("CAP-IV-W2V") for tid in triple_set.triples)


def test_cache_roundtrip(loader: TripleLoader):
    ts1, report = loader.load()
    ts2 = loader.load_from_cache(report.corpus_version_hash)

    assert set(ts1.triples.keys()) == set(ts2.triples.keys())
    for tid, t1 in ts1.triples.items():
        t2 = ts2.triples[tid]
        assert t1.triple_id == t2.triple_id
        assert t1.version == t2.version
        assert t1.bpmn_node_id == t2.bpmn_node_id
        assert t1.bpmn_node_type == t2.bpmn_node_type


def test_determinism(mda_corpus: Path, tmp_path: Path):
    cache1 = tmp_path / "cache1"
    cache2 = tmp_path / "cache2"
    loader_a = TripleLoader(_make_config(mda_corpus, cache1))
    loader_b = TripleLoader(_make_config(mda_corpus, cache2))

    _, report_a = loader_a.load()
    _, report_b = loader_b.load()

    assert report_a.corpus_version_hash == report_b.corpus_version_hash


def test_gateway_predicates_populated(loader: TripleLoader):
    """The BPMN file under corpus/bpmn/*.bpmn should drive gateway predicates."""
    ts, _ = loader.load()
    gateway = next(
        (t for t in ts.triples.values() if t.bpmn_node_id == "Gateway_EmploymentType"),
        None,
    )
    assert gateway is not None
    assert gateway.pim is not None
    assert gateway.pim.decision_predicates is not None
    assert len(gateway.pim.decision_predicates) >= 2


def test_cache_missing_raises(loader: TripleLoader):
    with pytest.raises(FileNotFoundError):
        loader.load_from_cache("0" * 64)
