"""Unit tests for cli/mda_io/schema_validator.py — JSON schema validation."""

import sys
import os
import pytest
from pathlib import Path

_TESTS_DIR = Path(__file__).parent.parent.resolve()
_PROJECT_ROOT = _TESTS_DIR.parent.resolve()
sys.path.insert(0, str(_PROJECT_ROOT / "cli"))

from mda_io.schema_validator import SchemaValidator
from mda_io.frontmatter import read_frontmatter_file

SCHEMAS_DIR = _PROJECT_ROOT / "schemas"
EXAMPLES_DIR = _PROJECT_ROOT / "examples"


@pytest.fixture
def validator():
    return SchemaValidator(SCHEMAS_DIR)


# ---------------------------------------------------------------------------
# Schema loading
# ---------------------------------------------------------------------------

class TestLoadsAllSchemas:
    """SchemaValidator loads all 5 expected schemas."""

    def test_all_schemas_loaded(self, validator):
        names = set(validator._schemas.keys())
        expected = {"capsule", "intent", "contract", "corpus-document", "triple-manifest", "jobaid"}
        assert expected == names


# ---------------------------------------------------------------------------
# Valid capsule from real file
# ---------------------------------------------------------------------------

class TestValidCapsuleFromFile:
    """Real capsule frontmatter from assess-dti passes validation."""

    def test_valid_capsule(self, validator):
        path = (
            EXAMPLES_DIR
            / "loan-origination"
            / "triples"
            / "assess-dti"
            / "assess-dti.cap.md"
        )
        fm, _ = read_frontmatter_file(path)
        errors = validator.validate_capsule(fm)
        assert errors == [], f"Unexpected errors: {errors}"


# ---------------------------------------------------------------------------
# Missing required field
# ---------------------------------------------------------------------------

class TestMissingRequiredField:
    """Removing capsule_id from valid data produces validation errors."""

    def test_missing_capsule_id(self, validator):
        path = (
            EXAMPLES_DIR
            / "loan-origination"
            / "triples"
            / "assess-dti"
            / "assess-dti.cap.md"
        )
        fm, _ = read_frontmatter_file(path)
        del fm["capsule_id"]
        errors = validator.validate_capsule(fm)
        assert len(errors) > 0
        assert any("capsule_id" in e.message for e in errors)


# ---------------------------------------------------------------------------
# Bad ID pattern
# ---------------------------------------------------------------------------

class TestBadIdPattern:
    """A capsule_id that does not match the pattern fails validation."""

    def test_bad_id_pattern(self, validator):
        path = (
            EXAMPLES_DIR
            / "loan-origination"
            / "triples"
            / "assess-dti"
            / "assess-dti.cap.md"
        )
        fm, _ = read_frontmatter_file(path)
        fm["capsule_id"] = "BAD-ID-FORMAT"
        errors = validator.validate_capsule(fm)
        assert len(errors) > 0
        # The error should be about the capsule_id pattern
        capsule_errors = [e for e in errors if e.path == "capsule_id"]
        assert len(capsule_errors) > 0


# ---------------------------------------------------------------------------
# Valid intent
# ---------------------------------------------------------------------------

class TestValidIntent:
    """Minimal valid intent frontmatter passes validation."""

    def test_valid_intent(self, validator):
        data = {
            "intent_id": "INT-LO-DTI-001",
            "capsule_id": "CAP-LO-DTI-001",
            "bpmn_task_id": "Task_AssessDTI",
            "version": "1.0",
            "status": "draft",
            "goal": "Assess debt-to-income ratio",
            "goal_type": "decision",
            "contract_ref": "ICT-LO-DTI-001",
            "generated_from": "loan-origination.bpmn",
            "generated_date": "2026-04-09T00:00:00Z",
            "generated_by": "MDA Demo",
        }
        errors = validator.validate_intent(data)
        assert errors == [], f"Unexpected errors: {errors}"


# ---------------------------------------------------------------------------
# Valid contract
# ---------------------------------------------------------------------------

class TestValidContract:
    """Minimal valid contract frontmatter passes validation."""

    def test_valid_contract(self, validator):
        data = {
            "contract_id": "ICT-LO-DTI-001",
            "intent_id": "INT-LO-DTI-001",
            "version": "1.0",
            "status": "draft",
            "binding_status": "unbound",
            "generated_from": "loan-origination.bpmn",
            "generated_date": "2026-04-09T00:00:00Z",
            "generated_by": "MDA Demo",
        }
        errors = validator.validate_contract(data)
        assert errors == [], f"Unexpected errors: {errors}"


# ---------------------------------------------------------------------------
# Valid corpus document
# ---------------------------------------------------------------------------

class TestValidCorpusDoc:
    """Minimal valid corpus document frontmatter passes validation."""

    def test_valid_corpus_doc(self, validator):
        data = {
            "corpus_id": "CRP-PRC-MTG-001",
            "title": "Test Document",
            "slug": "test-document",
            "doc_type": "procedure",
            "domain": "Mortgage Lending",
            "version": "1.0",
            "status": "current",
            "author": "Test Author",
            "last_modified": "2026-04-09T00:00:00Z",
            "last_modified_by": "Test",
            "source": "internal",
        }
        errors = validator.validate_corpus_document(data)
        assert errors == [], f"Unexpected errors: {errors}"


# ---------------------------------------------------------------------------
# Unknown schema name
# ---------------------------------------------------------------------------

class TestUnknownSchemaName:
    """Validating against a non-existent schema name returns an error."""

    def test_unknown_schema(self, validator):
        errors = validator._validate({}, "nonexistent-schema")
        assert len(errors) == 1
        assert "not found" in errors[0].message


# ---------------------------------------------------------------------------
# Multiple missing fields
# ---------------------------------------------------------------------------

class TestMultipleMissingFields:
    """An empty dict produces multiple required-field errors for capsule schema."""

    def test_multiple_errors(self, validator):
        errors = validator.validate_capsule({})
        # The capsule schema has 15 required fields
        assert len(errors) >= 5, f"Expected many errors, got {len(errors)}"
        messages = " ".join(e.message for e in errors)
        assert "capsule_id" in messages
        assert "bpmn_task_id" in messages
        assert "version" in messages
