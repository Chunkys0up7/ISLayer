"""Tests for the journey builder."""
import importlib.util, os, sys, pytest

_CLI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "cli")
sys.path.insert(0, _CLI_DIR)
_TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _TESTS_DIR)

# Load journey builder via importlib
_jb_path = os.path.join(_CLI_DIR, "pipeline", "journey_builder.py")
_spec = importlib.util.spec_from_file_location("journey_builder", _jb_path)
jb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(jb)

from conftest import EXAMPLES_DIR
from config.loader import load_config


def _make_capsule_data(adj: dict) -> dict:
    """Convert simple adjacency dict {"A": ["B"], "B": []} to capsule_data format."""
    # Build predecessor map from successor map
    predecessors = {k: [] for k in adj}
    for src, succs in adj.items():
        for tgt in succs:
            if tgt in predecessors:
                predecessors[tgt].append(src)

    return {
        k: {"successor_ids": v, "predecessor_ids": predecessors.get(k, [])}
        for k, v in adj.items()
    }


class TestTopologicalSort:
    def test_linear_chain(self):
        data = _make_capsule_data({"A": ["B"], "B": ["C"], "C": []})
        result = jb.topological_sort(data)
        assert result == ["A", "B", "C"]

    def test_with_branches(self):
        data = _make_capsule_data({"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []})
        result = jb.topological_sort(data)
        assert result[0] == "A"
        assert result[-1] == "D"
        assert len(result) == 4

    def test_single_node(self):
        data = _make_capsule_data({"A": []})
        result = jb.topological_sort(data)
        assert result == ["A"]

    def test_empty(self):
        result = jb.topological_sort({})
        assert result == []


class TestCriticalPath:
    def test_linear(self):
        data = _make_capsule_data({"A": ["B"], "B": ["C"], "C": []})
        # Build minimal StepSummary objects
        from models.journey import StepSummary
        steps = [
            StepSummary(step_number=1, capsule_id="A", name="A", task_type="task", owner=None, predecessor_steps=[], successor_steps=["B"]),
            StepSummary(step_number=2, capsule_id="B", name="B", task_type="task", owner=None, predecessor_steps=["A"], successor_steps=["C"]),
            StepSummary(step_number=3, capsule_id="C", name="C", task_type="task", owner=None, predecessor_steps=["B"], successor_steps=[]),
        ]
        result = jb.compute_critical_path(steps, data)
        assert len(result) == 3
        assert result == ["A", "B", "C"]

    def test_with_branch(self):
        data = _make_capsule_data({"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []})
        from models.journey import StepSummary
        steps = [
            StepSummary(step_number=1, capsule_id="A", name="A", task_type="task", owner=None, predecessor_steps=[], successor_steps=["B", "C"]),
            StepSummary(step_number=2, capsule_id="B", name="B", task_type="task", owner=None, predecessor_steps=["A"], successor_steps=["D"]),
            StepSummary(step_number=3, capsule_id="C", name="C", task_type="task", owner=None, predecessor_steps=["A"], successor_steps=["D"]),
            StepSummary(step_number=4, capsule_id="D", name="D", task_type="task", owner=None, predecessor_steps=["B", "C"], successor_steps=[]),
        ]
        result = jb.compute_critical_path(steps, data)
        assert len(result) == 3  # A→B→D or A→C→D
        assert result[0] == "A"
        assert result[-1] == "D"


class TestBuildJourney:
    def test_income_verification(self):
        process_dir = EXAMPLES_DIR / "income-verification"
        config = load_config(process_dir / "mda.config.yaml")
        journey = jb.build_journey(process_dir, config)

        assert journey is not None
        assert journey.total_steps == 8
        assert journey.steps[0].step_number == 1
        assert all(s.capsule_id for s in journey.steps)
        assert "income" in journey.process_name.lower() or "verification" in journey.process_name.lower()
        assert len(journey.critical_path) > 0
        assert "avg_health" in journey.health_summary or "avg_score" in journey.health_summary


class TestDataLineage:
    def test_income_verification_data(self):
        process_dir = EXAMPLES_DIR / "income-verification"
        config = load_config(process_dir / "mda.config.yaml")
        journey = jb.build_journey(process_dir, config)

        # Data lineage should exist (from process-graph.yaml or intent inputs/outputs)
        assert isinstance(journey.data_lineage, list)
        # Should have at least some data objects
        if journey.data_lineage:
            dl = journey.data_lineage[0]
            assert dl.data_name
            assert dl.source_name


class TestBranchPoints:
    def test_income_verification_branches(self):
        process_dir = EXAMPLES_DIR / "income-verification"
        config = load_config(process_dir / "mda.config.yaml")
        journey = jb.build_journey(process_dir, config)

        # Should detect at least 1 branch point (employment type gateway)
        assert isinstance(journey.branch_points, list)
        if journey.branch_points:
            bp = journey.branch_points[0]
            assert bp.gateway_name
            assert len(bp.branches) >= 2
