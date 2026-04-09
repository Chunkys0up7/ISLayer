"""Stage 6: Triple Validator — Validate all triples for consistency and completeness."""

from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import re
import sys
import os
import importlib.util
import json

_CLI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _CLI_DIR)


def _load_local(module_name: str, file_path: str):
    """Load a module from the cli/ tree, bypassing stdlib 'io' shadowing."""
    spec = importlib.util.spec_from_file_location(module_name, os.path.join(_CLI_DIR, file_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_frontmatter = _load_local("mda_io.frontmatter", "mda_io/frontmatter.py")
_schema_validator = _load_local("mda_io.schema_validator", "mda_io/schema_validator.py")
_yaml_io = _load_local("mda_io.yaml_io", "mda_io/yaml_io.py")

read_frontmatter_file = _frontmatter.read_frontmatter_file
SchemaValidator = _schema_validator.SchemaValidator
SchemaError = _schema_validator.SchemaError
read_yaml = _yaml_io.read_yaml


class CheckResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"


@dataclass
class CheckReport:
    check_id: int
    check_name: str
    result: CheckResult
    details: list[str] = field(default_factory=list)


@dataclass
class TripleValidation:
    triple_id: str
    capsule_path: Optional[str] = None
    intent_path: Optional[str] = None
    contract_path: Optional[str] = None
    checks: list[CheckReport] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.result in (CheckResult.PASS, CheckResult.SKIP, CheckResult.WARN) for c in self.checks)


@dataclass
class ValidationReport:
    overall_result: CheckResult
    triple_results: list[TripleValidation] = field(default_factory=list)
    process_checks: list[CheckReport] = field(default_factory=list)
    gap_summary: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "overall_result": self.overall_result.value,
            "triple_count": len(self.triple_results),
            "passed": sum(1 for t in self.triple_results if t.passed),
            "failed": sum(1 for t in self.triple_results if not t.passed),
            "triple_results": [
                {
                    "triple_id": t.triple_id,
                    "passed": t.passed,
                    "checks": [
                        {"id": c.check_id, "name": c.check_name, "result": c.result.value, "details": c.details}
                        for c in t.checks
                    ],
                }
                for t in self.triple_results
            ],
            "process_checks": [
                {"id": c.check_id, "name": c.check_name, "result": c.result.value, "details": c.details}
                for c in self.process_checks
            ],
            "gap_summary": self.gap_summary,
        }


# ID patterns — stem segments allow uppercase letters and digits (e.g., W2V)
CAPSULE_ID_PATTERN = re.compile(r"^CAP-[A-Z0-9]{2,3}-[A-Z0-9]{3}-\d{3}$")
INTENT_ID_PATTERN = re.compile(r"^INT-[A-Z0-9]{2,3}-[A-Z0-9]{3}-\d{3}$")
CONTRACT_ID_PATTERN = re.compile(r"^ICT-[A-Z0-9]{2,3}-[A-Z0-9]{3}-\d{3}$")


def run_validator(
    triples_dir: Path,
    decisions_dir: Optional[Path] = None,
    schemas_dir: Optional[Path] = None,
) -> ValidationReport:
    """Execute Stage 6: Validate all triples.

    Scans triples_dir and decisions_dir for triple directories
    (each containing .cap.md, .intent.md, .contract.md, triple.manifest.json).
    Runs 10 per-triple checks and 7 per-process checks.
    """
    report = ValidationReport(overall_result=CheckResult.PASS)

    # Discover all triple directories
    triple_dirs = _discover_triple_dirs(triples_dir, decisions_dir)

    # Load schema validator if schemas available
    validator = SchemaValidator(schemas_dir) if schemas_dir and schemas_dir.exists() else None

    # Per-triple checks
    all_capsule_data = {}  # capsule_id -> frontmatter dict
    all_intent_data = {}
    all_contract_data = {}
    all_gap_entries = []  # collect gaps across all triples

    for triple_dir in triple_dirs:
        tv = _validate_triple(triple_dir, validator)
        report.triple_results.append(tv)
        if not tv.passed:
            report.overall_result = CheckResult.FAIL

        # Collect data for process-level checks and gap summary
        if tv.capsule_path:
            try:
                cap_fm, _ = read_frontmatter_file(Path(tv.capsule_path))
                cap_id = cap_fm.get("capsule_id", "")
                all_capsule_data[cap_id] = cap_fm
                for gap in cap_fm.get("gaps", []):
                    if isinstance(gap, dict):
                        all_gap_entries.append(gap)
            except Exception:
                pass
        if tv.intent_path:
            try:
                int_fm, _ = read_frontmatter_file(Path(tv.intent_path))
                int_id = int_fm.get("intent_id", "")
                all_intent_data[int_id] = int_fm
                for gap in int_fm.get("gaps", []):
                    if isinstance(gap, dict):
                        all_gap_entries.append(gap)
            except Exception:
                pass
        if tv.contract_path:
            try:
                con_fm, _ = read_frontmatter_file(Path(tv.contract_path))
                con_id = con_fm.get("contract_id", "")
                all_contract_data[con_id] = con_fm
            except Exception:
                pass

    # Per-process checks (11-17)
    process_checks = _run_process_checks(
        report.triple_results, all_capsule_data, all_intent_data, all_contract_data
    )
    report.process_checks = process_checks
    for pc in process_checks:
        if pc.result == CheckResult.FAIL:
            report.overall_result = CheckResult.FAIL

    # Gap summary
    report.gap_summary = _compute_gap_summary(all_gap_entries)

    return report


def _discover_triple_dirs(triples_dir: Path, decisions_dir: Optional[Path] = None) -> list[Path]:
    """Find all directories containing triple files."""
    dirs = []
    if triples_dir.exists():
        for d in sorted(triples_dir.iterdir()):
            if d.is_dir() and not d.name.startswith("_"):
                dirs.append(d)
    if decisions_dir and decisions_dir.exists():
        for d in sorted(decisions_dir.iterdir()):
            if d.is_dir():
                dirs.append(d)
    return dirs


def _validate_triple(triple_dir: Path, validator: Optional[SchemaValidator]) -> TripleValidation:
    """Run all 10 per-triple checks."""
    tv = TripleValidation(triple_id=triple_dir.name)

    # Find files
    cap_files = list(triple_dir.glob("*.cap.md"))
    intent_files = list(triple_dir.glob("*.intent.md"))
    contract_files = list(triple_dir.glob("*.contract.md"))

    # Check 1: All three files exist
    check1 = CheckReport(1, "Triple completeness", CheckResult.PASS)
    missing = []
    if not cap_files:
        missing.append("capsule (.cap.md)")
    if not intent_files:
        missing.append("intent (.intent.md)")
    if not contract_files:
        missing.append("contract (.contract.md)")
    if missing:
        check1.result = CheckResult.FAIL
        check1.details = [f"Missing: {', '.join(missing)}"]
    tv.checks.append(check1)

    if missing:
        # Can't continue with remaining checks
        for i in range(2, 11):
            tv.checks.append(CheckReport(i, f"Check {i}", CheckResult.SKIP, ["Skipped due to missing files"]))
        return tv

    # Read files
    tv.capsule_path = str(cap_files[0])
    tv.intent_path = str(intent_files[0])
    tv.contract_path = str(contract_files[0])

    cap_fm, cap_body = read_frontmatter_file(cap_files[0])
    int_fm, int_body = read_frontmatter_file(intent_files[0])
    con_fm, con_body = read_frontmatter_file(contract_files[0])

    # Check 2: ID convention conformance
    check2 = CheckReport(2, "ID convention", CheckResult.PASS)
    cap_id = cap_fm.get("capsule_id", "")
    int_id = int_fm.get("intent_id", "")
    con_id = con_fm.get("contract_id", "")
    if not CAPSULE_ID_PATTERN.match(cap_id):
        check2.result = CheckResult.FAIL
        check2.details.append(f"Invalid capsule_id: {cap_id}")
    if not INTENT_ID_PATTERN.match(int_id):
        check2.result = CheckResult.FAIL
        check2.details.append(f"Invalid intent_id: {int_id}")
    if not CONTRACT_ID_PATTERN.match(con_id):
        check2.result = CheckResult.FAIL
        check2.details.append(f"Invalid contract_id: {con_id}")
    tv.checks.append(check2)

    # Check 3: ID stem consistency
    check3 = CheckReport(3, "ID stem consistency", CheckResult.PASS)
    cap_stem = cap_id.replace("CAP-", "", 1) if cap_id.startswith("CAP-") else ""
    int_stem = int_id.replace("INT-", "", 1) if int_id.startswith("INT-") else ""
    con_stem = con_id.replace("ICT-", "", 1) if con_id.startswith("ICT-") else ""
    if not (cap_stem == int_stem == con_stem):
        check3.result = CheckResult.FAIL
        check3.details = [f"Stems don't match: CAP={cap_stem}, INT={int_stem}, ICT={con_stem}"]
    tv.checks.append(check3)

    # Check 4: Cross-reference integrity
    check4 = CheckReport(4, "Cross-references", CheckResult.PASS)
    # capsule.intent_id == intent.intent_id
    if cap_fm.get("intent_id") != int_id:
        check4.result = CheckResult.FAIL
        check4.details.append(f"capsule.intent_id ({cap_fm.get('intent_id')}) != intent.intent_id ({int_id})")
    # capsule.contract_id == contract.contract_id
    if cap_fm.get("contract_id") != con_id:
        check4.result = CheckResult.FAIL
        check4.details.append(f"capsule.contract_id ({cap_fm.get('contract_id')}) != contract.contract_id ({con_id})")
    # intent.capsule_id == capsule.capsule_id
    if int_fm.get("capsule_id") != cap_id:
        check4.result = CheckResult.FAIL
        check4.details.append(f"intent.capsule_id ({int_fm.get('capsule_id')}) != capsule.capsule_id ({cap_id})")
    # intent.contract_ref == contract.contract_id
    if int_fm.get("contract_ref") != con_id:
        check4.result = CheckResult.FAIL
        check4.details.append(f"intent.contract_ref ({int_fm.get('contract_ref')}) != contract.contract_id ({con_id})")
    # contract.intent_id == intent.intent_id
    if con_fm.get("intent_id") != int_id:
        check4.result = CheckResult.FAIL
        check4.details.append(f"contract.intent_id ({con_fm.get('intent_id')}) != intent.intent_id ({int_id})")
    tv.checks.append(check4)

    # Check 5: Status consistency
    check5 = CheckReport(5, "Status consistency", CheckResult.PASS)
    statuses = {cap_fm.get("status"), int_fm.get("status"), con_fm.get("status")}
    if len(statuses) > 1:
        check5.result = CheckResult.WARN
        check5.details = [
            f"Inconsistent statuses: capsule={cap_fm.get('status')}, "
            f"intent={int_fm.get('status')}, contract={con_fm.get('status')}"
        ]
    tv.checks.append(check5)

    # Check 6: Version consistency
    check6 = CheckReport(6, "Version consistency", CheckResult.PASS)
    versions = {cap_fm.get("version"), int_fm.get("version"), con_fm.get("version")}
    if len(versions) > 1:
        check6.result = CheckResult.WARN
        check6.details = [
            f"Inconsistent versions: capsule={cap_fm.get('version')}, "
            f"intent={int_fm.get('version')}, contract={con_fm.get('version')}"
        ]
    tv.checks.append(check6)

    # Check 7: Required fields for status
    check7 = CheckReport(7, "Required fields", CheckResult.PASS)
    for required in ["capsule_id", "bpmn_task_id", "version", "status"]:
        if not cap_fm.get(required):
            check7.result = CheckResult.FAIL
            check7.details.append(f"Capsule missing required field: {required}")
    for required in ["intent_id", "capsule_id", "goal", "goal_type", "version", "status"]:
        if not int_fm.get(required):
            check7.result = CheckResult.FAIL
            check7.details.append(f"Intent missing required field: {required}")
    for required in ["contract_id", "intent_id", "version", "status", "binding_status"]:
        if not con_fm.get(required):
            check7.result = CheckResult.FAIL
            check7.details.append(f"Contract missing required field: {required}")
    tv.checks.append(check7)

    # Check 8: Schema validation (if validator available)
    check8 = CheckReport(8, "Schema validation", CheckResult.PASS if validator else CheckResult.SKIP)
    if validator:
        for name, fm, validate_fn in [
            ("capsule", cap_fm, validator.validate_capsule),
            ("intent", int_fm, validator.validate_intent),
            ("contract", con_fm, validator.validate_contract),
        ]:
            errors = validate_fn(fm)
            if errors:
                check8.result = CheckResult.WARN  # Schema validation is warning-level, not blocking
                for e in errors[:5]:  # Limit to first 5 errors per file
                    check8.details.append(f"{name}: {e.path}: {e.message}")
    tv.checks.append(check8)

    # Check 9: Gap entries completeness
    check9 = CheckReport(9, "Gap completeness", CheckResult.PASS)
    for source, fm in [("capsule", cap_fm), ("intent", int_fm)]:
        gaps = fm.get("gaps", [])
        if isinstance(gaps, list):
            for i, gap in enumerate(gaps):
                if isinstance(gap, dict):
                    for gap_field in ["type", "description", "severity"]:
                        if gap_field not in gap:
                            check9.result = CheckResult.WARN
                            check9.details.append(f"{source} gap [{i}] missing field: {gap_field}")
    tv.checks.append(check9)

    # Check 10: Forbidden actions present in intent
    check10 = CheckReport(10, "Anti-UI compliance", CheckResult.PASS)
    hints = int_fm.get("execution_hints", {})
    forbidden = hints.get("forbidden_actions", []) if isinstance(hints, dict) else []
    required_forbidden = {"browser_automation", "screen_scraping", "ui_click", "rpa_style_macros"}
    missing_forbidden = required_forbidden - set(forbidden)
    if missing_forbidden:
        check10.result = CheckResult.WARN
        check10.details = [f"Missing forbidden_actions: {', '.join(sorted(missing_forbidden))}"]
    tv.checks.append(check10)

    return tv


def _run_process_checks(
    triple_results: list[TripleValidation],
    capsule_data: dict,
    intent_data: dict,
    contract_data: dict,
) -> list[CheckReport]:
    """Run 7 per-process checks (checks 11-17)."""
    checks = []

    # Check 11: All triples pass per-triple validation
    check11 = CheckReport(11, "All triples valid", CheckResult.PASS)
    failed = [t.triple_id for t in triple_results if not t.passed]
    if failed:
        check11.result = CheckResult.FAIL
        check11.details = [f"Failed triples: {', '.join(failed)}"]
    checks.append(check11)

    # Check 12: Process graph connectivity
    # Verify that predecessor_ids and successor_ids form a connected graph
    check12 = CheckReport(12, "Process graph connectivity", CheckResult.PASS)
    all_cap_ids = set(capsule_data.keys())
    if all_cap_ids:
        # Check that every referenced predecessor/successor actually exists
        missing_refs = []
        for cap_id, fm in capsule_data.items():
            for pred_id in fm.get("predecessor_ids", []) or []:
                if pred_id and pred_id not in all_cap_ids:
                    missing_refs.append(f"{cap_id} references predecessor {pred_id} which does not exist")
            for succ_id in fm.get("successor_ids", []) or []:
                if succ_id and succ_id not in all_cap_ids:
                    missing_refs.append(f"{cap_id} references successor {succ_id} which does not exist")
        if missing_refs:
            check12.result = CheckResult.WARN
            check12.details = missing_refs[:10]  # Limit output
    else:
        check12.result = CheckResult.SKIP
        check12.details = ["No capsule data collected"]
    checks.append(check12)

    # Check 13: Predecessor/successor symmetry
    check13 = CheckReport(13, "Predecessor/successor validity", CheckResult.PASS)
    asymmetric = []
    for cap_id, fm in capsule_data.items():
        for succ_id in fm.get("successor_ids", []) or []:
            if succ_id and succ_id in capsule_data:
                succ_preds = capsule_data[succ_id].get("predecessor_ids", []) or []
                if cap_id not in succ_preds:
                    asymmetric.append(
                        f"{cap_id} lists {succ_id} as successor, but {succ_id} does not list {cap_id} as predecessor"
                    )
        for pred_id in fm.get("predecessor_ids", []) or []:
            if pred_id and pred_id in capsule_data:
                pred_succs = capsule_data[pred_id].get("successor_ids", []) or []
                if cap_id not in pred_succs:
                    asymmetric.append(
                        f"{cap_id} lists {pred_id} as predecessor, but {pred_id} does not list {cap_id} as successor"
                    )
    if asymmetric:
        check13.result = CheckResult.WARN
        check13.details = asymmetric[:10]
    elif not capsule_data:
        check13.result = CheckResult.SKIP
        check13.details = ["No capsule data collected"]
    checks.append(check13)

    # Check 14: Exception reference validity
    check14 = CheckReport(14, "Exception reference validity", CheckResult.PASS)
    invalid_exc = []
    for cap_id, fm in capsule_data.items():
        for exc_id in fm.get("exception_ids", []) or []:
            if exc_id and exc_id not in all_cap_ids:
                invalid_exc.append(f"{cap_id} references exception {exc_id} which does not exist")
    if invalid_exc:
        check14.result = CheckResult.WARN
        check14.details = invalid_exc[:10]
    elif not capsule_data:
        check14.result = CheckResult.SKIP
        check14.details = ["No capsule data collected"]
    checks.append(check14)

    # Check 15: Start/end events exist
    # At least one capsule should have no predecessors (start) and one should have no successors (end)
    check15 = CheckReport(15, "Start/end events exist", CheckResult.PASS)
    if capsule_data:
        starts = [
            cap_id
            for cap_id, fm in capsule_data.items()
            if not (fm.get("predecessor_ids") or [])
        ]
        ends = [
            cap_id
            for cap_id, fm in capsule_data.items()
            if not (fm.get("successor_ids") or [])
        ]
        if not starts:
            check15.result = CheckResult.WARN
            check15.details.append("No start node found (all capsules have predecessors)")
        if not ends:
            check15.result = CheckResult.WARN
            check15.details.append("No end node found (all capsules have successors)")
    else:
        check15.result = CheckResult.SKIP
        check15.details = ["No capsule data collected"]
    checks.append(check15)

    # Check 16: No circular dependencies
    check16 = CheckReport(16, "No circular dependencies", CheckResult.PASS)
    if capsule_data:
        cycle = _detect_cycle(capsule_data)
        if cycle:
            check16.result = CheckResult.FAIL
            check16.details = [f"Cycle detected: {' -> '.join(cycle)}"]
    else:
        check16.result = CheckResult.SKIP
        check16.details = ["No capsule data collected"]
    checks.append(check16)

    # Check 17: Gap tracking completeness
    check17 = CheckReport(17, "Gap tracking completeness", CheckResult.PASS)
    total_gaps = 0
    gaps_without_severity = 0
    for cap_id, fm in capsule_data.items():
        for gap in fm.get("gaps", []) or []:
            if isinstance(gap, dict):
                total_gaps += 1
                if "severity" not in gap:
                    gaps_without_severity += 1
    for int_id, fm in intent_data.items():
        for gap in fm.get("gaps", []) or []:
            if isinstance(gap, dict):
                total_gaps += 1
                if "severity" not in gap:
                    gaps_without_severity += 1
    if gaps_without_severity > 0:
        check17.result = CheckResult.WARN
        check17.details = [f"{gaps_without_severity} of {total_gaps} gaps missing severity"]
    elif not capsule_data and not intent_data:
        check17.result = CheckResult.SKIP
        check17.details = ["No capsule/intent data collected"]
    checks.append(check17)

    return checks


def _detect_cycle(capsule_data: dict) -> Optional[list[str]]:
    """Detect a cycle in the capsule predecessor/successor graph using DFS.

    Returns a list of capsule IDs forming the cycle, or None if no cycle exists.
    """
    # Build adjacency list from successor_ids
    adj: dict[str, list[str]] = {}
    for cap_id, fm in capsule_data.items():
        succs = fm.get("successor_ids", []) or []
        adj[cap_id] = [s for s in succs if s in capsule_data]

    WHITE, GRAY, BLACK = 0, 1, 2
    color = {cap_id: WHITE for cap_id in capsule_data}
    parent: dict[str, Optional[str]] = {cap_id: None for cap_id in capsule_data}

    def dfs(node: str) -> Optional[list[str]]:
        color[node] = GRAY
        for neighbor in adj.get(node, []):
            if color.get(neighbor) == GRAY:
                # Back edge found — reconstruct cycle
                cycle = [neighbor, node]
                current = node
                while parent.get(current) and parent[current] != neighbor:
                    current = parent[current]
                    cycle.append(current)
                cycle.reverse()
                return cycle
            if color.get(neighbor) == WHITE:
                parent[neighbor] = node
                result = dfs(neighbor)
                if result:
                    return result
        color[node] = BLACK
        return None

    for cap_id in capsule_data:
        if color[cap_id] == WHITE:
            result = dfs(cap_id)
            if result:
                return result

    return None


def _compute_gap_summary(gap_entries: list[dict]) -> dict:
    """Compute gap counts from collected gap entries."""
    by_severity: dict[str, int] = {}
    by_type: dict[str, int] = {}

    for gap in gap_entries:
        severity = gap.get("severity", "unknown")
        by_severity[severity] = by_severity.get(severity, 0) + 1
        gap_type = gap.get("type", "unknown")
        by_type[gap_type] = by_type.get(gap_type, 0) + 1

    return {
        "total": len(gap_entries),
        "by_severity": by_severity,
        "by_type": by_type,
    }
