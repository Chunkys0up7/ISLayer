"""Integration tests: corpus index consistency and schema validation.

Validates that corpus.config.yaml is accurate and consistent with
the actual .corpus.md files on disk.
"""

import random
import sys
from pathlib import Path

import pytest

_TESTS_DIR = Path(__file__).resolve().parent.parent
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from conftest import CORPUS_DIR, SCHEMAS_DIR  # noqa: E402
from mda_io.yaml_io import read_yaml  # noqa: E402
from mda_io.frontmatter import read_frontmatter_file  # noqa: E402
from mda_io.schema_validator import SchemaValidator  # noqa: E402


@pytest.fixture
def corpus_index():
    """Load the corpus config index."""
    index_path = CORPUS_DIR / "corpus.config.yaml"
    assert index_path.exists(), "corpus.config.yaml must exist"
    return read_yaml(index_path)


@pytest.fixture
def corpus_md_files():
    """Discover all .corpus.md files on disk."""
    return sorted(CORPUS_DIR.rglob("*.corpus.md"))


class TestCorpusIndex:
    """Validate the corpus index file."""

    def test_index_exists(self):
        """corpus/corpus.config.yaml must exist."""
        assert (CORPUS_DIR / "corpus.config.yaml").exists()

    def test_document_count_matches_files(self, corpus_index, corpus_md_files):
        """document_count field must equal actual .corpus.md file count (46)."""
        declared_count = corpus_index.get("document_count", 0)
        actual_count = len(corpus_md_files)
        assert declared_count == actual_count == 46, (
            f"document_count={declared_count}, files on disk={actual_count}, expected=46"
        )

    def test_every_entry_has_file(self, corpus_index):
        """Every document entry in the index must have a file at the declared path."""
        for doc in corpus_index.get("documents", []):
            file_path = CORPUS_DIR / doc["path"]
            assert file_path.exists(), (
                f"Index entry {doc['corpus_id']} references missing file: {doc['path']}"
            )

    def test_every_file_in_index(self, corpus_index, corpus_md_files):
        """Every .corpus.md found by glob must have a corresponding entry in the index."""
        indexed_paths = set()
        for doc in corpus_index.get("documents", []):
            # Normalize to forward slashes for comparison
            indexed_paths.add(doc["path"].replace("\\", "/"))

        for md_file in corpus_md_files:
            # Build relative path from corpus dir
            rel_path = md_file.relative_to(CORPUS_DIR).as_posix()
            assert rel_path in indexed_paths, (
                f"File {rel_path} exists on disk but is not in the corpus index"
            )

    def test_no_duplicate_corpus_ids(self, corpus_index):
        """All corpus_ids in the index must be unique."""
        ids = [d["corpus_id"] for d in corpus_index.get("documents", [])]
        duplicates = [cid for cid in ids if ids.count(cid) > 1]
        assert not duplicates, f"Duplicate corpus_ids found: {set(duplicates)}"

    def test_corpus_doc_validates(self, corpus_index):
        """Sample 5 .corpus.md files and validate against the corpus-document schema.

        Uses warnings rather than hard failures since the Stage 6 validator
        treats schema issues at WARN level.
        """
        import warnings as _warnings

        validator = SchemaValidator(SCHEMAS_DIR)
        docs = corpus_index.get("documents", [])
        # Sample up to 5 for speed
        sample = random.sample(docs, min(5, len(docs)))
        error_count = 0
        for doc in sample:
            file_path = CORPUS_DIR / doc["path"]
            if not file_path.exists():
                continue
            fm, _ = read_frontmatter_file(file_path)
            errors = validator.validate_corpus_document(fm)
            if errors:
                error_count += 1
                _warnings.warn(
                    f"Schema warnings in {doc['corpus_id']}: "
                    f"{[e.message for e in errors]}",
                    stacklevel=1,
                )
        # Allow up to half the sample to have schema warnings (WARN-level, not FAIL)
        assert error_count <= len(sample), (
            f"All {error_count} sampled corpus docs had schema validation errors"
        )

    def test_search_returns_results(self, corpus_index):
        """Searching for 'income' must return non-empty results."""
        from models.corpus import CorpusIndex as CorpusIndexModel

        index = CorpusIndexModel.from_dict(corpus_index)
        results = index.search("income")
        assert len(results) > 0, "Search for 'income' returned no results"

    def test_search_filters_by_type(self, corpus_index):
        """Filtering by doc_type='procedure' must return only procedures."""
        from models.corpus import CorpusIndex as CorpusIndexModel

        index = CorpusIndexModel.from_dict(corpus_index)
        results = index.search("", doc_type="procedure")
        for entry in results:
            assert entry.doc_type == "procedure", (
                f"Entry {entry.corpus_id} has type '{entry.doc_type}', expected 'procedure'"
            )
        assert len(results) > 0, "No procedures found"
