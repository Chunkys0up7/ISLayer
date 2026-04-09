"""JSON Schema validation wrapper."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from jsonschema import validate, ValidationError, Draft7Validator


@dataclass
class SchemaError:
    path: str  # JSON pointer path to the failing field
    message: str
    schema_path: str  # Which schema rule failed


class SchemaValidator:
    def __init__(self, schemas_dir: Path):
        """Load all schemas from the schemas/ directory."""
        self._schemas: dict[str, dict] = {}
        for schema_file in schemas_dir.glob("*.schema.json"):
            with open(schema_file, encoding="utf-8") as f:
                schema = json.load(f)
            name = schema_file.stem.replace(".schema", "")
            self._schemas[name] = schema

    @property
    def available_schemas(self) -> list[str]:
        """Return the names of all loaded schemas."""
        return list(self._schemas.keys())

    def validate_capsule(self, frontmatter: dict) -> list[SchemaError]:
        """Validate capsule frontmatter against capsule.schema.json."""
        return self._validate(frontmatter, "capsule")

    def validate_intent(self, frontmatter: dict) -> list[SchemaError]:
        """Validate intent frontmatter against intent.schema.json."""
        return self._validate(frontmatter, "intent")

    def validate_contract(self, frontmatter: dict) -> list[SchemaError]:
        """Validate contract frontmatter against contract.schema.json."""
        return self._validate(frontmatter, "contract")

    def validate_corpus_document(self, frontmatter: dict) -> list[SchemaError]:
        """Validate corpus document frontmatter against corpus-document.schema.json."""
        return self._validate(frontmatter, "corpus-document")

    def validate_triple_manifest(self, manifest: dict) -> list[SchemaError]:
        """Validate triple manifest against triple-manifest.schema.json."""
        return self._validate(manifest, "triple-manifest")

    def _validate(self, data: dict, schema_name: str) -> list[SchemaError]:
        """Core validation against a named schema."""
        schema = self._schemas.get(schema_name)
        if not schema:
            return [SchemaError("", f"Schema '{schema_name}' not found", "")]

        errors = []
        validator = Draft7Validator(schema)
        for error in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
            errors.append(
                SchemaError(
                    path="/".join(str(p) for p in error.absolute_path),
                    message=error.message,
                    schema_path="/".join(
                        str(p) for p in error.absolute_schema_path
                    ),
                )
            )
        return errors
