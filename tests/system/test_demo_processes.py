"""System tests: full validation of all 3 demo processes.

Runs the Stage 6 validator against every demo process and checks
that no FAIL-level issues exist, and that structural invariants hold.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

_TESTS_DIR = Path(__file__).resolve().parent.parent
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from conftest import (  # noqa: E402
    PROJECT_ROOT,
    CLI_DIR,
    EXAMPLES_DIR,
    SCHEMAS_DIR,
    EXPECTED,
    discover_triple_dirs,
)


# ---------------------------------------------------------------------------
# Load the validator module
# ---------------------------------------------------------------------------

def _load_validator():
    file_path = CLI_DIR / "pipeline" / "stage6_validator.py"
    spec = importlib.util.spec_from_file_location(
        "pipeline.stage6_validator", str(file_path)
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


validator_mod = _load_validator()


def _validate_process(process_name: str):
    """Run the validator on a named demo process and return the report."""
    process_dir = EXAMPLES_DIR / process_name
    return validator_mod.run_validator(
        triples_dir=process_dir / "triples",
        decisions_dir=process_dir / "decisions",
        schemas_dir=SCHEMAS_DIR,
    )


# ---------------------------------------------------------------------------
# Per-process validation tests
# ---------------------------------------------------------------------------


class TestDemoProcessValidation:
    """Each demo process should pass validation without FAIL-level checks."""

    def test_loan_origination_validates(self):
        """loan-origination: no FAIL-level per-triple checks."""
        report = _validate_process("loan-origination")
        for tv in report.triple_results:
            fails = [c for c in tv.checks if c.result == validator_mod.CheckResult.FAIL]
            assert not fails, (
                f"loan-origination triple {tv.triple_id} has FAILs: "
                f"{[(c.check_name, c.details) for c in fails]}"
            )

    def test_income_verification_validates(self):
        """income-verification: no FAIL-level per-triple checks."""
        report = _validate_process("income-verification")
        for tv in report.triple_results:
            fails = [c for c in tv.checks if c.result == validator_mod.CheckResult.FAIL]
            assert not fails, (
                f"income-verification triple {tv.triple_id} has FAILs: "
                f"{[(c.check_name, c.details) for c in fails]}"
            )

    def test_property_appraisal_validates(self):
        """property-appraisal: no FAIL-level per-triple checks."""
        report = _validate_process("property-appraisal")
        for tv in report.triple_results:
            fails = [c for c in tv.checks if c.result == validator_mod.CheckResult.FAIL]
            assert not fails, (
                f"property-appraisal triple {tv.triple_id} has FAILs: "
                f"{[(c.check_name, c.details) for c in fails]}"
            )


# ---------------------------------------------------------------------------
# Structural invariant tests
# ---------------------------------------------------------------------------


class TestDemoProcessStructure:
    """Structural checks across all 3 demo processes."""

    def test_all_processes_have_start_and_end(self):
        """Every process should have at least 1 capsule with no predecessors
        and 1 capsule with no successors."""
        from mda_io.frontmatter import read_frontmatter_file

        for process_name in EXPECTED:
            process_dir = EXAMPLES_DIR / process_name
            triple_dirs = discover_triple_dirs(process_dir)

            has_start = False
            has_end = False

            for td in triple_dirs:
                cap_files = list(td.glob("*.cap.md"))
                if not cap_files:
                    continue
                fm, _ = read_frontmatter_file(cap_files[0])
                preds = fm.get("predecessor_ids") or []
                succs = fm.get("successor_ids") or []
                if not preds:
                    has_start = True
                if not succs:
                    has_end = True

            assert has_start, (
                f"{process_name}: no capsule without predecessors (start node)"
            )
            assert has_end, (
                f"{process_name}: no capsule without successors (end node)"
            )

    def test_all_processes_triple_coverage(self):
        """Triple directory count must match expected total_triples for each process."""
        for process_name, expected in EXPECTED.items():
            process_dir = EXAMPLES_DIR / process_name
            triple_dirs = discover_triple_dirs(process_dir)
            assert len(triple_dirs) == expected["total_triples"], (
                f"{process_name}: expected {expected['total_triples']} triple dirs, "
                f"got {len(triple_dirs)}"
            )
