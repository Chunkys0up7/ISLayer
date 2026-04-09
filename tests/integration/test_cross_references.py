"""Integration tests: cross-reference integrity across all triple files.

Scans all triple directories across all 3 demo processes and checks
frontmatter consistency, ID conventions, and anti-UI compliance.
"""

import re
import sys
from pathlib import Path

import pytest

_TESTS_DIR = Path(__file__).resolve().parent.parent
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from conftest import EXPECTED, EXAMPLES_DIR, discover_triple_dirs  # noqa: E402
from mda_io.frontmatter import read_frontmatter_file  # noqa: E402


# ---------------------------------------------------------------------------
# Collect all triple directories across all processes for parametrization
# ---------------------------------------------------------------------------

def _all_triple_dirs():
    """Discover every triple dir from all demo processes."""
    dirs = []
    for process_name in EXPECTED:
        process_dir = EXAMPLES_DIR / process_name
        for td in discover_triple_dirs(process_dir):
            dirs.append(td)
    return dirs


ALL_TRIPLE_DIRS = _all_triple_dirs()

# Provide a readable test ID for each triple dir
_triple_ids = [f"{td.parent.parent.name}/{td.parent.name}/{td.name}" for td in ALL_TRIPLE_DIRS]


@pytest.fixture(params=ALL_TRIPLE_DIRS, ids=_triple_ids)
def triple_dir(request):
    """Parametrized fixture yielding each triple directory."""
    return request.param


def _read_triple_fm(triple_dir: Path):
    """Read frontmatter from the three files in a triple directory."""
    cap_files = list(triple_dir.glob("*.cap.md"))
    int_files = list(triple_dir.glob("*.intent.md"))
    con_files = list(triple_dir.glob("*.contract.md"))
    assert cap_files, f"No *.cap.md in {triple_dir}"
    assert int_files, f"No *.intent.md in {triple_dir}"
    assert con_files, f"No *.contract.md in {triple_dir}"
    cap_fm, _ = read_frontmatter_file(cap_files[0])
    int_fm, _ = read_frontmatter_file(int_files[0])
    con_fm, _ = read_frontmatter_file(con_files[0])
    return cap_fm, int_fm, con_fm


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestTripleCompleteness:
    """Every triple directory must contain all three files."""

    def test_every_triple_has_three_files(self, triple_dir):
        cap = list(triple_dir.glob("*.cap.md"))
        intent = list(triple_dir.glob("*.intent.md"))
        contract = list(triple_dir.glob("*.contract.md"))
        assert len(cap) >= 1, f"Missing *.cap.md in {triple_dir.name}"
        assert len(intent) >= 1, f"Missing *.intent.md in {triple_dir.name}"
        assert len(contract) >= 1, f"Missing *.contract.md in {triple_dir.name}"


class TestCrossReferenceIntegrity:
    """Frontmatter cross-references between capsule/intent/contract must be consistent."""

    def test_capsule_intent_id_matches(self, triple_dir):
        cap_fm, int_fm, _ = _read_triple_fm(triple_dir)
        assert cap_fm.get("intent_id") == int_fm.get("intent_id"), (
            f"capsule.intent_id={cap_fm.get('intent_id')} != intent.intent_id={int_fm.get('intent_id')}"
        )

    def test_capsule_contract_id_matches(self, triple_dir):
        cap_fm, _, con_fm = _read_triple_fm(triple_dir)
        assert cap_fm.get("contract_id") == con_fm.get("contract_id"), (
            f"capsule.contract_id={cap_fm.get('contract_id')} != contract.contract_id={con_fm.get('contract_id')}"
        )

    def test_intent_capsule_id_matches(self, triple_dir):
        cap_fm, int_fm, _ = _read_triple_fm(triple_dir)
        assert int_fm.get("capsule_id") == cap_fm.get("capsule_id"), (
            f"intent.capsule_id={int_fm.get('capsule_id')} != capsule.capsule_id={cap_fm.get('capsule_id')}"
        )

    def test_intent_contract_ref_matches(self, triple_dir):
        _, int_fm, con_fm = _read_triple_fm(triple_dir)
        assert int_fm.get("contract_ref") == con_fm.get("contract_id"), (
            f"intent.contract_ref={int_fm.get('contract_ref')} != contract.contract_id={con_fm.get('contract_id')}"
        )

    def test_contract_intent_id_matches(self, triple_dir):
        _, int_fm, con_fm = _read_triple_fm(triple_dir)
        assert con_fm.get("intent_id") == int_fm.get("intent_id"), (
            f"contract.intent_id={con_fm.get('intent_id')} != intent.intent_id={int_fm.get('intent_id')}"
        )


class TestIDConventions:
    """ID format and stem consistency checks."""

    def test_id_stems_consistent(self, triple_dir):
        """Stripping CAP-/INT-/ICT- prefix, stems must match across all 3 files."""
        cap_fm, int_fm, con_fm = _read_triple_fm(triple_dir)
        cap_id = cap_fm.get("capsule_id", "")
        int_id = int_fm.get("intent_id", "")
        con_id = con_fm.get("contract_id", "")
        cap_stem = cap_id.replace("CAP-", "", 1) if cap_id.startswith("CAP-") else cap_id
        int_stem = int_id.replace("INT-", "", 1) if int_id.startswith("INT-") else int_id
        con_stem = con_id.replace("ICT-", "", 1) if con_id.startswith("ICT-") else con_id
        assert cap_stem == int_stem == con_stem, (
            f"Stems differ: CAP={cap_stem}, INT={int_stem}, ICT={con_stem}"
        )

    def test_capsule_id_pattern(self, triple_dir):
        cap_fm, _, _ = _read_triple_fm(triple_dir)
        cap_id = cap_fm.get("capsule_id", "")
        assert re.match(r"^CAP-[A-Z0-9]{2,3}-[A-Z0-9]{3}-\d{3}$", cap_id), (
            f"capsule_id '{cap_id}' does not match expected pattern"
        )

    def test_intent_id_pattern(self, triple_dir):
        _, int_fm, _ = _read_triple_fm(triple_dir)
        int_id = int_fm.get("intent_id", "")
        assert re.match(r"^INT-[A-Z0-9]{2,3}-[A-Z0-9]{3}-\d{3}$", int_id), (
            f"intent_id '{int_id}' does not match expected pattern"
        )

    def test_contract_id_pattern(self, triple_dir):
        _, _, con_fm = _read_triple_fm(triple_dir)
        con_id = con_fm.get("contract_id", "")
        assert re.match(r"^ICT-[A-Z0-9]{2,3}-[A-Z0-9]{3}-\d{3}$", con_id), (
            f"contract_id '{con_id}' does not match expected pattern"
        )


class TestConsistency:
    """Status and version must be consistent across all 3 files."""

    def test_status_consistent(self, triple_dir):
        cap_fm, int_fm, con_fm = _read_triple_fm(triple_dir)
        statuses = {cap_fm.get("status"), int_fm.get("status"), con_fm.get("status")}
        assert len(statuses) == 1, (
            f"Inconsistent statuses: cap={cap_fm.get('status')}, "
            f"int={int_fm.get('status')}, con={con_fm.get('status')}"
        )

    def test_version_consistent(self, triple_dir):
        cap_fm, int_fm, con_fm = _read_triple_fm(triple_dir)
        versions = {cap_fm.get("version"), int_fm.get("version"), con_fm.get("version")}
        assert len(versions) == 1, (
            f"Inconsistent versions: cap={cap_fm.get('version')}, "
            f"int={int_fm.get('version')}, con={con_fm.get('version')}"
        )


class TestAntiUICompliance:
    """Intent files must enforce forbidden UI actions."""

    def test_anti_ui_forbidden_actions(self, triple_dir):
        _, int_fm, _ = _read_triple_fm(triple_dir)
        hints = int_fm.get("execution_hints", {})
        forbidden = set(hints.get("forbidden_actions", []) if isinstance(hints, dict) else [])
        required = {"browser_automation", "screen_scraping", "ui_click", "rpa_style_macros"}
        missing = required - forbidden
        assert not missing, (
            f"Intent in {triple_dir.name} missing forbidden_actions: {missing}"
        )


class TestCorpusRefsValid:
    """Capsule corpus_refs must reference IDs that exist in corpus.config.yaml."""

    def test_corpus_refs_valid(self, triple_dir, corpus_dir):
        from mda_io.yaml_io import read_yaml

        # Load corpus index
        index_path = corpus_dir / "corpus.config.yaml"
        if not index_path.exists():
            pytest.skip("corpus.config.yaml not found")
        index = read_yaml(index_path)
        valid_ids = {d["corpus_id"] for d in index.get("documents", [])}

        cap_files = list(triple_dir.glob("*.cap.md"))
        if not cap_files:
            pytest.skip("No capsule file")
        cap_fm, _ = read_frontmatter_file(cap_files[0])

        corpus_refs = cap_fm.get("corpus_refs", [])
        if not corpus_refs:
            return  # No refs to validate

        for ref in corpus_refs:
            ref_id = ref.get("corpus_id", ref) if isinstance(ref, dict) else ref
            assert ref_id in valid_ids, (
                f"corpus_ref '{ref_id}' in {triple_dir.name} not found in corpus index"
            )
