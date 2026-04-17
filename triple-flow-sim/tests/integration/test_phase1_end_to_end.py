"""End-to-end integration tests for Phase 1: load -> graph -> inventory -> classify -> report."""
from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from triple_flow_sim.cli import cli


FIXTURES = Path(__file__).parent.parent / "fixtures"


def _prep_fixtures(tmp_path: Path, corpus_name: str, bpmn_filename: str) -> tuple[Path, Path]:
    """Copy a corpus and its BPMN to tmp_path, write a loader YAML. Returns (config_path, bpmn_path)."""
    corpus_src = FIXTURES / corpus_name
    corpus_dst = tmp_path / corpus_name
    shutil.copytree(corpus_src, corpus_dst)

    bpmn_src = FIXTURES / "bpmn" / bpmn_filename
    bpmn_dst = tmp_path / "bpmn" / bpmn_filename
    bpmn_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(bpmn_src, bpmn_dst)

    config_path = tmp_path / "loader.yaml"
    config_path.write_text(
        "source_format: native_yaml\n"
        "source:\n"
        "  type: local\n"
        f"  path: {corpus_name}\n"
        "ignore_paths: [\"README.md\"]\n"
        "strict_mode: false\n",
        encoding="utf-8",
    )
    return config_path, bpmn_dst


def _find_run_dir(out_dir: Path) -> Path:
    run_dirs = [d for d in out_dir.iterdir() if d.is_dir()]
    assert len(run_dirs) == 1, f"Expected exactly one run dir, got {run_dirs}"
    return run_dirs[0]


def test_clean_corpus_produces_minimal_findings(tmp_path: Path):
    config_path, bpmn_path = _prep_fixtures(tmp_path, "corpus_clean", "simple.bpmn")
    out_dir = tmp_path / "reports"

    runner = CliRunner()
    result = runner.invoke(cli, [
        "inventory",
        "--corpus-config", str(config_path),
        "--bpmn", str(bpmn_path),
        "--out", str(out_dir),
    ], catch_exceptions=False)
    assert result.exit_code == 0, result.output

    run_dir = _find_run_dir(out_dir)
    md_path = run_dir / "inventory.md"
    json_path = run_dir / "inventory.json"
    db_path = run_dir / "findings.db"
    assert md_path.exists()
    assert json_path.exists()
    assert db_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    # Core invariant signals should be absent for a clean corpus; only
    # naming-drift "suspect" (cosmetic/low confidence) findings are allowed.
    core_signals = {
        "missing_identity_field", "missing_layer", "empty_or_multi_sentence_intent",
        "missing_contract_field", "gateway_missing_predicates", "orphan_obligation",
        "state_flow_gap", "empty_content", "unparseable_predicate",
        "unresolved_regulatory_ref", "orphan_triple", "orphan_bpmn_node",
    }
    detection_counts = data["stats"].get("detection_counts", {}) or {}
    core_hits = sum(
        v for k, v in detection_counts.items() if k in core_signals
    )
    assert core_hits == 0, f"Expected no core findings on clean corpus, got: {detection_counts}"

    # Markdown should exist with the header
    md_content = md_path.read_text(encoding="utf-8")
    assert "Inventory Report" in md_content


def test_seeded_corpus_detects_every_class(tmp_path: Path):
    config_path, bpmn_path = _prep_fixtures(
        tmp_path, "corpus_seeded", "simple_seeded.bpmn"
    )
    out_dir = tmp_path / "reports"

    runner = CliRunner()
    result = runner.invoke(cli, [
        "inventory",
        "--corpus-config", str(config_path),
        "--bpmn", str(bpmn_path),
        "--out", str(out_dir),
    ], catch_exceptions=False)
    assert result.exit_code == 0, result.output

    run_dir = _find_run_dir(out_dir)
    data = json.loads((run_dir / "inventory.json").read_text(encoding="utf-8"))

    finding_classes = {f["defect_class"] for f in data["findings"]}
    expected = {
        "content_missing",
        "contract_missing",
        "evaluability_gap",
        "state_flow_gap",
    }
    missing = expected - finding_classes
    assert not missing, (
        f"Expected defect_classes missing from findings: {missing}. "
        f"Actual classes: {finding_classes}"
    )


def test_two_runs_produce_identical_inventory_json(tmp_path: Path):
    config_path, bpmn_path = _prep_fixtures(tmp_path, "corpus_clean", "simple.bpmn")

    out_a = tmp_path / "reports_a"
    out_b = tmp_path / "reports_b"

    runner = CliRunner()
    for out_dir in (out_a, out_b):
        result = runner.invoke(cli, [
            "inventory",
            "--corpus-config", str(config_path),
            "--bpmn", str(bpmn_path),
            "--out", str(out_dir),
        ], catch_exceptions=False)
        assert result.exit_code == 0, result.output

    a = json.loads((_find_run_dir(out_a) / "inventory.json").read_text(encoding="utf-8"))
    b = json.loads((_find_run_dir(out_b) / "inventory.json").read_text(encoding="utf-8"))

    def _strip(d: dict) -> dict:
        d = copy.deepcopy(d)
        d.pop("run_id", None)
        d.pop("generated_at", None)
        # Strip per-run fields from findings that naturally change
        for f in d.get("findings", []):
            f.pop("finding_id", None)
            f.pop("detected_at", None)
            f.pop("first_seen_run", None)
            f.pop("last_seen_run", None)
        return d

    assert _strip(a) == _strip(b)
