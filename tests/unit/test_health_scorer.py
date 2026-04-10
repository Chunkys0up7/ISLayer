"""Tests for the health scoring engine."""
import sys, os
from pathlib import Path
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "cli"))

import importlib.util
def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

scorer = _load_module("health_scorer", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "cli", "pipeline", "health_scorer.py"))
report_gen = _load_module("report_generator", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "cli", "pipeline", "report_generator.py"))

_TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _TESTS_DIR)
from conftest import PROJECT_ROOT, EXAMPLES_DIR, SCHEMAS_DIR, CORPUS_DIR
from config.loader import load_config
from models.report import HealthGrade, grade_from_score, grade_label, ProcessReport


class TestGradeFromScore:
    def test_grade_a(self):
        assert grade_from_score(95) == HealthGrade.A
    def test_grade_b(self):
        assert grade_from_score(85) == HealthGrade.B
    def test_grade_c(self):
        assert grade_from_score(75) == HealthGrade.C
    def test_grade_d(self):
        assert grade_from_score(65) == HealthGrade.D
    def test_grade_f(self):
        assert grade_from_score(50) == HealthGrade.F
    def test_grade_boundary_90(self):
        assert grade_from_score(90) == HealthGrade.A
    def test_grade_boundary_0(self):
        assert grade_from_score(0) == HealthGrade.F


class TestGradeLabel:
    def test_labels(self):
        assert grade_label(HealthGrade.A) == "Excellent"
        assert grade_label(HealthGrade.B) == "Good"
        assert grade_label(HealthGrade.C) == "Acceptable"
        assert grade_label(HealthGrade.D) == "Needs Work"
        assert grade_label(HealthGrade.F) == "Critical"


class TestScoreProcess:
    def test_income_verification_scores(self):
        """Income verification process produces valid scores."""
        config = load_config(EXAMPLES_DIR / "income-verification" / "mda.config.yaml")
        report = scorer.score_process(EXAMPLES_DIR / "income-verification", config, SCHEMAS_DIR, CORPUS_DIR)

        assert isinstance(report, ProcessReport)
        assert 0 <= report.health_score <= 100
        assert report.grade in HealthGrade
        assert len(report.triple_scores) == 8  # 6 triples + 2 decisions
        assert report.process_id == "Process_IncomeVerification"

    def test_all_triples_scored(self):
        config = load_config(EXAMPLES_DIR / "income-verification" / "mda.config.yaml")
        report = scorer.score_process(EXAMPLES_DIR / "income-verification", config, SCHEMAS_DIR, CORPUS_DIR)

        for ts in report.triple_scores:
            assert 0 <= ts.health_score <= 100
            assert len(ts.dimensions) == 5
            assert ts.grade in HealthGrade

    def test_dimension_weights_sum_to_1(self):
        config = load_config(EXAMPLES_DIR / "income-verification" / "mda.config.yaml")
        report = scorer.score_process(EXAMPLES_DIR / "income-verification", config, SCHEMAS_DIR, CORPUS_DIR)

        for ts in report.triple_scores:
            total_weight = sum(d.weight for d in ts.dimensions)
            assert abs(total_weight - 1.0) < 0.01

    def test_gap_summary_populated(self):
        config = load_config(EXAMPLES_DIR / "income-verification" / "mda.config.yaml")
        report = scorer.score_process(EXAMPLES_DIR / "income-verification", config, SCHEMAS_DIR, CORPUS_DIR)

        gs = report.gap_summary
        assert gs.total == gs.critical + gs.high + gs.medium + gs.low

    def test_graph_integrity(self):
        config = load_config(EXAMPLES_DIR / "income-verification" / "mda.config.yaml")
        report = scorer.score_process(EXAMPLES_DIR / "income-verification", config, SCHEMAS_DIR, CORPUS_DIR)

        assert report.graph_integrity.cycles == False
        assert report.graph_integrity.start_events >= 1

    def test_to_dict_round_trips(self):
        config = load_config(EXAMPLES_DIR / "income-verification" / "mda.config.yaml")
        report = scorer.score_process(EXAMPLES_DIR / "income-verification", config, SCHEMAS_DIR, CORPUS_DIR)
        d = report.to_dict()

        assert "health_score" in d
        assert "grade" in d
        assert "triple_scores" in d
        assert len(d["triple_scores"]) == 8


class TestReportGenerator:
    def test_xml_output(self):
        config = load_config(EXAMPLES_DIR / "income-verification" / "mda.config.yaml")
        report = scorer.score_process(EXAMPLES_DIR / "income-verification", config, SCHEMAS_DIR, CORPUS_DIR)
        xml = report_gen.generate_xml(report)

        assert xml.startswith("<?xml")
        assert "<mda-report" in xml
        assert "<health-score" in xml
        assert "<triple" in xml

    def test_json_output(self):
        config = load_config(EXAMPLES_DIR / "income-verification" / "mda.config.yaml")
        report = scorer.score_process(EXAMPLES_DIR / "income-verification", config, SCHEMAS_DIR, CORPUS_DIR)
        json_str = report_gen.generate_json(report)

        import json
        data = json.loads(json_str)
        assert "health_score" in data
        assert "triple_scores" in data

    def test_yaml_output(self):
        config = load_config(EXAMPLES_DIR / "income-verification" / "mda.config.yaml")
        report = scorer.score_process(EXAMPLES_DIR / "income-verification", config, SCHEMAS_DIR, CORPUS_DIR)
        yaml_str = report_gen.generate_yaml(report)

        import yaml
        data = yaml.safe_load(yaml_str)
        assert "health_score" in data

    def test_write_xml_file(self, tmp_path):
        config = load_config(EXAMPLES_DIR / "income-verification" / "mda.config.yaml")
        report = scorer.score_process(EXAMPLES_DIR / "income-verification", config, SCHEMAS_DIR, CORPUS_DIR)
        out = tmp_path / "report.xml"
        report_gen.write_report(report, out, "xml")

        assert out.exists()
        content = out.read_text()
        assert "<mda-report" in content

    def test_all_three_processes(self):
        """All 3 demo processes produce valid reports."""
        for proc in ["loan-origination", "income-verification", "property-appraisal"]:
            config = load_config(EXAMPLES_DIR / proc / "mda.config.yaml")
            report = scorer.score_process(EXAMPLES_DIR / proc, config, SCHEMAS_DIR, CORPUS_DIR)
            assert 0 <= report.health_score <= 100
            assert len(report.triple_scores) > 0
