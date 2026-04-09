"""Integration tests: pipeline stages 1, 2, and 6.

Loads stage modules via importlib to handle their sys.path hacks.
"""

import importlib.util
import os
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
    CORPUS_DIR,
    ONTOLOGY_DIR,
    EXPECTED,
)


# ---------------------------------------------------------------------------
# Load pipeline modules via importlib (they manipulate sys.path internally)
# ---------------------------------------------------------------------------

def _load_pipeline_module(name: str):
    """Load a pipeline module from cli/pipeline/ using importlib."""
    file_path = CLI_DIR / "pipeline" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(
        f"pipeline.{name}", str(file_path)
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


stage1 = _load_pipeline_module("stage1_parser")
stage2 = _load_pipeline_module("stage2_enricher")
stage6 = _load_pipeline_module("stage6_validator")


# Convenience references
IV_BPMN = EXAMPLES_DIR / "income-verification" / "bpmn" / "income-verification.bpmn"
IV_DIR = EXAMPLES_DIR / "income-verification"


# ---------------------------------------------------------------------------
# Stage 1 tests
# ---------------------------------------------------------------------------


class TestStage1Parser:
    """Stage 1: BPMN Parser."""

    def test_stage1_runs(self):
        """run_parser should return a ParsedModel without error."""
        model = stage1.run_parser(IV_BPMN)
        assert model is not None
        assert len(model.nodes) > 0

    def test_stage1_annotates_nodes(self, ontology_dir):
        """With ontology_dir, nodes should gain a triple_type attribute."""
        model = stage1.run_parser(IV_BPMN, ontology_dir=ontology_dir)
        annotated = [
            n for n in model.nodes
            if "triple_type" in n.attributes
        ]
        assert len(annotated) > 0, (
            "No nodes were annotated with triple_type from the ontology"
        )


# ---------------------------------------------------------------------------
# Stage 2 tests
# ---------------------------------------------------------------------------


class TestStage2Enricher:
    """Stage 2: Corpus Enricher."""

    @pytest.fixture
    def parsed_model(self):
        return stage1.run_parser(IV_BPMN, ontology_dir=ONTOLOGY_DIR)

    def test_stage2_runs(self, parsed_model):
        """run_enricher should return an EnrichedModel without error."""
        enriched = stage2.run_enricher(parsed_model, CORPUS_DIR)
        assert enriched is not None

    def test_stage2_has_enrichments(self, parsed_model):
        """Number of enrichments should equal number of nodes."""
        enriched = stage2.run_enricher(parsed_model, CORPUS_DIR)
        assert len(enriched.node_enrichments) == len(parsed_model.nodes)

    def test_stage2_finds_matches(self, parsed_model):
        """At least 1 node should have a procedure match."""
        enriched = stage2.run_enricher(parsed_model, CORPUS_DIR)
        found = [
            ne for ne in enriched.node_enrichments.values()
            if ne.procedure.found
        ]
        assert len(found) >= 1, "No nodes matched any corpus procedure"

    def test_stage2_produces_gaps(self, parsed_model):
        """Enrichment should produce at least 1 gap."""
        enriched = stage2.run_enricher(parsed_model, CORPUS_DIR)
        assert len(enriched.gaps) > 0, "Expected at least 1 gap"

    def test_stage2_gap_summary(self, parsed_model):
        """Gap list should contain gaps with required fields."""
        enriched = stage2.run_enricher(parsed_model, CORPUS_DIR)
        for gap in enriched.gaps:
            assert gap.gap_id, "Gap missing gap_id"
            assert gap.severity, "Gap missing severity"


# ---------------------------------------------------------------------------
# Stage 1 -> Stage 2 chain test
# ---------------------------------------------------------------------------


class TestPipelineChain:
    """Chaining Stage 1 -> Stage 2."""

    def test_stage1_to_stage2_chain(self):
        """Parsing then enriching should produce consistent node counts."""
        model = stage1.run_parser(IV_BPMN, ontology_dir=ONTOLOGY_DIR)
        enriched = stage2.run_enricher(model, CORPUS_DIR)
        assert len(enriched.node_enrichments) == len(model.nodes), (
            f"Enrichment count ({len(enriched.node_enrichments)}) != "
            f"node count ({len(model.nodes)})"
        )


# ---------------------------------------------------------------------------
# Stage 6 tests
# ---------------------------------------------------------------------------


class TestStage6Validator:
    """Stage 6: Triple Validator."""

    def test_stage6_runs(self):
        """run_validator should return a ValidationReport without error."""
        report = stage6.run_validator(
            triples_dir=IV_DIR / "triples",
            decisions_dir=IV_DIR / "decisions",
            schemas_dir=SCHEMAS_DIR,
        )
        assert report is not None

    def test_stage6_demo_no_failures(self):
        """Income-verification should have no FAIL-level per-triple checks."""
        report = stage6.run_validator(
            triples_dir=IV_DIR / "triples",
            decisions_dir=IV_DIR / "decisions",
            schemas_dir=SCHEMAS_DIR,
        )
        for tv in report.triple_results:
            fail_checks = [
                c for c in tv.checks
                if c.result == stage6.CheckResult.FAIL
            ]
            assert not fail_checks, (
                f"Triple {tv.triple_id} has FAIL checks: "
                f"{[(c.check_name, c.details) for c in fail_checks]}"
            )

    def test_stage6_report_structure(self):
        """ValidationReport must have triple_results and process_checks lists."""
        report = stage6.run_validator(
            triples_dir=IV_DIR / "triples",
            decisions_dir=IV_DIR / "decisions",
            schemas_dir=SCHEMAS_DIR,
        )
        assert isinstance(report.triple_results, list)
        assert isinstance(report.process_checks, list)
        assert len(report.triple_results) > 0
        assert len(report.process_checks) > 0
