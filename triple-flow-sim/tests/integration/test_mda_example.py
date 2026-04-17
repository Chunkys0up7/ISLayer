"""Smoke test: run inventory against the real MDA examples/income-verification corpus."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from triple_flow_sim.cli import cli


def test_mda_income_verification_loads_and_reports(tmp_path: Path):
    """Verifies the MDA adapter works end-to-end against real triples.

    This test uses the existing MDA examples. Many findings will be emitted
    (contract_missing dominates due to missing pim.postconditions), which is
    the expected Phase 1 value delivery — hundreds of findings surface the
    authoring backlog.
    """
    # Skip if examples path doesn't exist (portability).
    examples_dir = (
        Path(__file__).resolve().parent.parent.parent.parent
        / "examples"
        / "income-verification"
    )
    if not examples_dir.exists():
        pytest.skip("MDA examples not available in this environment")

    # Write a loader config pointing at the real examples.
    config_yaml = tmp_path / "mda.yaml"
    config_yaml.write_text(
        "source_format: mda_triple_dir\n"
        "source:\n"
        "  type: local\n"
        f"  path: {examples_dir.as_posix()}\n"
        "content_chunk_extraction:\n"
        "  by_section: true\n"
        "strict_mode: false\n"
        "ignore_paths: [\".git\", \"_manifest.json\"]\n",
        encoding="utf-8",
    )
    bpmn_path = examples_dir / "bpmn" / "income-verification.bpmn"

    out_dir = tmp_path / "reports"
    runner = CliRunner()
    args = [
        "inventory",
        "--corpus-config", str(config_yaml),
        "--out", str(out_dir),
    ]
    if bpmn_path.exists():
        args.extend(["--bpmn", str(bpmn_path)])

    result = runner.invoke(cli, args, catch_exceptions=False)
    assert result.exit_code == 0, result.output

    run_dirs = [d for d in out_dir.iterdir() if d.is_dir()]
    assert len(run_dirs) == 1
    report = json.loads(
        (run_dirs[0] / "inventory.json").read_text(encoding="utf-8")
    )

    # MDA triples have: triples + decisions (~8 for income-verification).
    assert report["total_triples"] >= 7

    # Findings will be substantial — assert some core classes appear.
    finding_classes = {f["defect_class"] for f in report["findings"]}
    # At minimum, contract_missing should fire because MDA triples have no
    # pim.postconditions.
    assert "contract_missing" in finding_classes
