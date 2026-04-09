"""Shared test fixtures for the MDA Intent Layer test suite."""

import sys
import os
from pathlib import Path
import pytest

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
CLI_DIR = PROJECT_ROOT / "cli"
EXAMPLES_DIR = PROJECT_ROOT / "examples"
SCHEMAS_DIR = PROJECT_ROOT / "schemas"
CORPUS_DIR = PROJECT_ROOT / "corpus"
ONTOLOGY_DIR = PROJECT_ROOT / "ontology"

# Add CLI to sys.path for imports
sys.path.insert(0, str(CLI_DIR))

# Expected counts per demo process (ground truth for assertions)
EXPECTED = {
    "loan-origination": {
        "total_nodes": 13,
        "edges": 13,
        "lanes": 3,
        "data_objects": 4,
        "triples": 8,
        "decisions": 2,
        "total_triples": 10,
        "bpmn_file": "loan-origination.bpmn",
        "process_id": "Process_LoanOrigination",
        "id_prefix": "LO",
    },
    "income-verification": {
        "total_nodes": 11,
        "edges": 11,
        "lanes": 2,
        "data_objects": 4,
        "triples": 6,
        "decisions": 2,
        "total_triples": 8,
        "bpmn_file": "income-verification.bpmn",
        "process_id": "Process_IncomeVerification",
        "id_prefix": "IV",
    },
    "property-appraisal": {
        "total_nodes": 12,
        "edges": 12,
        "lanes": 3,
        "data_objects": 4,
        "triples": 7,
        "decisions": 2,
        "total_triples": 9,
        "bpmn_file": "property-appraisal.bpmn",
        "process_id": "Process_PropertyAppraisal",
        "id_prefix": "PA",
    },
}

PROCESS_NAMES = list(EXPECTED.keys())


@pytest.fixture
def project_root():
    return PROJECT_ROOT


@pytest.fixture
def schemas_dir():
    return SCHEMAS_DIR


@pytest.fixture
def corpus_dir():
    return CORPUS_DIR


@pytest.fixture
def ontology_dir():
    return ONTOLOGY_DIR


@pytest.fixture(params=PROCESS_NAMES)
def example_process(request):
    """Parametrized fixture yielding each demo process with its expected counts."""
    name = request.param
    process_dir = EXAMPLES_DIR / name
    expected = EXPECTED[name]
    bpmn_path = process_dir / "bpmn" / expected["bpmn_file"]
    return {
        "name": name,
        "dir": process_dir,
        "bpmn_path": bpmn_path,
        "triples_dir": process_dir / "triples",
        "decisions_dir": process_dir / "decisions",
        "expected": expected,
    }


@pytest.fixture
def loan_origination_bpmn():
    return EXAMPLES_DIR / "loan-origination" / "bpmn" / "loan-origination.bpmn"


@pytest.fixture
def income_verification_bpmn():
    return EXAMPLES_DIR / "income-verification" / "bpmn" / "income-verification.bpmn"


def discover_triple_dirs(process_dir):
    """Find all triple directories (triples/ + decisions/) in a process."""
    dirs = []
    for base in ["triples", "decisions"]:
        base_dir = process_dir / base
        if base_dir.exists():
            for d in sorted(base_dir.iterdir()):
                if d.is_dir() and not d.name.startswith("_"):
                    dirs.append(d)
    return dirs
