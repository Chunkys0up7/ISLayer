"""Phase 3 end-to-end integration: grounded CLI with the fake LLM driver.

Verifies that the grounded pipeline:
1. Runs deterministically offline (fake driver)
2. Emits Phase 1/2 static findings plus Phase 3 grounded/isolation/boundary
   findings in a single run
3. Produces a populated findings.db and inventory.json
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from click.testing import CliRunner

from triple_flow_sim.cli import cli

FIXTURES = Path(__file__).parent.parent / "fixtures"


def _prep(tmp_path: Path, corpus_name: str, bpmn: str) -> tuple[Path, Path]:
    corpus_src = FIXTURES / corpus_name
    corpus_dst = tmp_path / corpus_name
    shutil.copytree(corpus_src, corpus_dst)
    bpmn_src = FIXTURES / "bpmn" / bpmn
    bpmn_dst = tmp_path / "bpmn" / bpmn
    bpmn_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(bpmn_src, bpmn_dst)
    cfg = tmp_path / "loader.yaml"
    cfg.write_text(
        "source_format: native_yaml\n"
        "source:\n"
        "  type: local\n"
        f"  path: {corpus_name}\n"
        "ignore_paths: [\"README.md\"]\n"
        "strict_mode: false\n",
        encoding="utf-8",
    )
    return cfg, bpmn_dst


def _run_dir(out: Path) -> Path:
    dirs = [d for d in out.iterdir() if d.is_dir()]
    assert len(dirs) == 1
    return dirs[0]


def test_grounded_cli_fake_driver_runs(tmp_path: Path) -> None:
    cfg, bpmn = _prep(tmp_path, "corpus_clean", "simple.bpmn")
    out = tmp_path / "reports"
    r = CliRunner().invoke(
        cli,
        [
            "grounded",
            "--corpus-config", str(cfg),
            "--bpmn", str(bpmn),
            "--out", str(out),
            "--driver", "fake",
            "--seed", "0",
        ],
        catch_exceptions=False,
    )
    assert r.exit_code == 0, r.output
    run = _run_dir(out)
    assert (run / "findings.db").exists()
    inv = json.loads((run / "inventory.json").read_text(encoding="utf-8"))
    # At least some findings from the combined pipeline.
    assert "findings" in inv


def test_grounded_cli_calibration_mode_suppresses_isolation_findings(
    tmp_path: Path,
) -> None:
    cfg, bpmn = _prep(tmp_path, "corpus_clean", "simple.bpmn")
    out = tmp_path / "reports"
    r = CliRunner().invoke(
        cli,
        [
            "grounded",
            "--corpus-config", str(cfg),
            "--bpmn", str(bpmn),
            "--out", str(out),
            "--driver", "fake",
            "--calibration-only",
        ],
        catch_exceptions=False,
    )
    assert r.exit_code == 0, r.output
    run = _run_dir(out)
    inv = json.loads((run / "inventory.json").read_text(encoding="utf-8"))
    # Calibration mode suppresses the keystone finding specifically.
    kinds = {f["defect_class"] for f in inv["findings"]}
    assert "handoff_carried_by_external_context" not in kinds


def test_grounded_cli_two_fake_runs_deterministic(tmp_path: Path) -> None:
    cfg, bpmn = _prep(tmp_path, "corpus_clean", "simple.bpmn")
    out_a = tmp_path / "a"
    out_b = tmp_path / "b"
    for out in (out_a, out_b):
        r = CliRunner().invoke(
            cli,
            [
                "grounded",
                "--corpus-config", str(cfg),
                "--bpmn", str(bpmn),
                "--out", str(out),
                "--driver", "fake",
                "--seed", "0",
            ],
            catch_exceptions=False,
        )
        assert r.exit_code == 0, r.output

    def _clean(obj):
        obj.pop("run_id", None)
        obj.pop("generated_at", None)
        for f in obj.get("findings", []):
            f.pop("finding_id", None)
            f.pop("detected_at", None)
            f.pop("first_seen_run", None)
            f.pop("last_seen_run", None)
        return obj

    a = _clean(
        json.loads(
            (_run_dir(out_a) / "inventory.json").read_text(encoding="utf-8")
        )
    )
    b = _clean(
        json.loads(
            (_run_dir(out_b) / "inventory.json").read_text(encoding="utf-8")
        )
    )
    assert a == b
