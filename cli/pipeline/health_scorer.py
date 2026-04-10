"""Health scoring engine — scores each triple and the overall process."""

import re
import sys, os
from pathlib import Path
from datetime import datetime
from typing import Optional
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib.util
def _load_io(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mda_io", f"{name}.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
frontmatter_mod = _load_io("frontmatter")
yaml_io = _load_io("yaml_io")
schema_val = _load_io("schema_validator")

from models.report import (
    ProcessReport, TripleScore, DimensionScore, GapEntry, GapSummary,
    TripleFileInfo, CorpusCoverage, GraphIntegrity,
    HealthGrade, grade_from_score, grade_label
)

# Required forbidden actions for anti-UI compliance
REQUIRED_FORBIDDEN = {"browser_automation", "screen_scraping", "ui_click", "rpa_style_macros"}

# ID patterns
CAP_PAT = re.compile(r"^CAP-[A-Z0-9]{2,3}-[A-Z0-9]{3}-\d{3}$")
INT_PAT = re.compile(r"^INT-[A-Z0-9]{2,3}-[A-Z0-9]{3}-\d{3}$")
ICT_PAT = re.compile(r"^ICT-[A-Z0-9]{2,3}-[A-Z0-9]{3}-\d{3}$")

# Dimension weights
WEIGHTS = {
    "completeness": 0.30,
    "consistency": 0.25,
    "schema_compliance": 0.20,
    "knowledge_coverage": 0.15,
    "anti_ui_compliance": 0.10,
}


def score_process(project_root: Path, config, schemas_dir: Optional[Path] = None, corpus_dir: Optional[Path] = None) -> ProcessReport:
    """Score the entire process and generate a report."""
    # Resolve paths
    triples_path = config.get("paths.triples") or config.get("output.triples_dir") or "triples"
    decisions_path = config.get("paths.decisions") or config.get("output.decisions_dir") or "decisions"
    triples_dir = project_root / triples_path
    decisions_dir = project_root / decisions_path

    process_id = config.get("process.id", "unknown")
    process_name = config.get("process.name", project_root.name.replace("-", " ").title())

    # Load schema validator
    validator = schema_val.SchemaValidator(schemas_dir) if schemas_dir and schemas_dir.exists() else None

    # Discover and score triples
    triple_dirs = _discover_triple_dirs(triples_dir, decisions_dir)
    triple_scores = []
    all_gaps = []
    all_capsule_ids = set()
    all_cap_data = {}
    total_schema_violations = 0
    total_xref_errors = 0
    triples_with_corpus_refs = 0

    for td in triple_dirs:
        ts = _score_triple(td, validator)
        triple_scores.append(ts)
        all_gaps.extend(ts.gaps)
        total_schema_violations += sum(1 for d in ts.dimensions if d.name == "schema_compliance" for det in d.details)
        total_xref_errors += sum(1 for d in ts.dimensions if d.name == "consistency" and d.details)

        # Collect capsule data for graph checks
        for f in ts.files:
            if f.artifact_type == "capsule":
                all_capsule_ids.add(f.artifact_id)
        # Check corpus refs
        cap_files = list(td.glob("*.cap.md"))
        if cap_files:
            fm, _ = frontmatter_mod.read_frontmatter_file(cap_files[0])
            all_cap_data[fm.get("capsule_id", "")] = fm
            if fm.get("corpus_refs"):
                triples_with_corpus_refs += 1

    # Gap summary
    gap_summary = GapSummary(total=len(all_gaps))
    for g in all_gaps:
        if g.severity == "critical": gap_summary.critical += 1
        elif g.severity == "high": gap_summary.high += 1
        elif g.severity == "medium": gap_summary.medium += 1
        elif g.severity == "low": gap_summary.low += 1

    # Corpus coverage
    corpus_doc_count = 0
    if corpus_dir and corpus_dir.exists():
        corpus_doc_count = len(list(corpus_dir.rglob("*.corpus.md")))
    corpus_cov = CorpusCoverage(
        matched_docs=triples_with_corpus_refs,  # simplified
        total_corpus_docs=corpus_doc_count,
        triples_with_corpus_refs=triples_with_corpus_refs,
    )

    # Graph integrity
    graph = _check_graph_integrity(all_cap_data)

    # Process health score
    triple_avg = sum(ts.health_score for ts in triple_scores) / max(len(triple_scores), 1)
    graph_score = 100.0
    if not graph.connected: graph_score -= 40
    if graph.cycles: graph_score -= 30
    if graph.start_events == 0: graph_score -= 15
    if graph.end_events == 0: graph_score -= 15

    corpus_score = 100.0 * (triples_with_corpus_refs / max(len(triple_scores), 1))

    process_score = (triple_avg * 0.70) + (graph_score * 0.15) + (corpus_score * 0.15)
    process_score = max(0.0, min(100.0, process_score))
    process_grade = grade_from_score(process_score)

    return ProcessReport(
        process_id=process_id,
        process_name=process_name,
        generated=datetime.utcnow().isoformat() + "Z",
        health_score=process_score,
        grade=process_grade,
        grade_label=grade_label(process_grade),
        gap_summary=gap_summary,
        schema_violations=total_schema_violations,
        cross_ref_errors=total_xref_errors,
        triple_scores=triple_scores,
        corpus_coverage=corpus_cov,
        graph_integrity=graph,
    )


def _discover_triple_dirs(triples_dir, decisions_dir):
    dirs = []
    for base in [triples_dir, decisions_dir]:
        if base.exists():
            for d in sorted(base.iterdir()):
                if d.is_dir() and not d.name.startswith("_"):
                    dirs.append(d)
    return dirs


def _score_triple(triple_dir: Path, validator) -> TripleScore:
    """Score a single triple on 5 dimensions."""
    cap_files = list(triple_dir.glob("*.cap.md"))
    int_files = list(triple_dir.glob("*.intent.md"))
    con_files = list(triple_dir.glob("*.contract.md"))

    # Read frontmatter
    cap_fm = {}; cap_body = ""
    int_fm = {}; int_body = ""
    con_fm = {}; con_body = ""
    if cap_files: cap_fm, cap_body = frontmatter_mod.read_frontmatter_file(cap_files[0])
    if int_files: int_fm, int_body = frontmatter_mod.read_frontmatter_file(int_files[0])
    if con_files: con_fm, con_body = frontmatter_mod.read_frontmatter_file(con_files[0])

    triple_id = cap_fm.get("capsule_id", "").replace("CAP-", "") or triple_dir.name
    triple_name = cap_fm.get("bpmn_task_name", triple_dir.name)
    task_type = cap_fm.get("bpmn_task_type", "unknown")

    # Collect gaps
    gaps = []
    for gap in cap_fm.get("gaps", []):
        if isinstance(gap, dict):
            gaps.append(GapEntry(
                gap_type=gap.get("type", "unknown"),
                severity=gap.get("severity", "medium"),
                description=gap.get("description", ""),
                triple_id=triple_id,
                source="capsule_frontmatter",
            ))

    # File info
    files = []
    if cap_fm: files.append(TripleFileInfo("capsule", cap_fm.get("capsule_id", ""), cap_fm.get("status", "unknown")))
    if int_fm: files.append(TripleFileInfo("intent", int_fm.get("intent_id", ""), int_fm.get("status", "unknown")))
    if con_fm: files.append(TripleFileInfo("contract", con_fm.get("contract_id", ""), con_fm.get("status", "unknown"), con_fm.get("binding_status")))

    # === Dimension 1: Completeness (30%) ===
    comp_score = 100.0
    comp_details = []
    if not cap_files: comp_score -= 20; comp_details.append("Missing capsule file")
    if not int_files: comp_score -= 20; comp_details.append("Missing intent file")
    if not con_files: comp_score -= 20; comp_details.append("Missing contract file")
    # Check required fields
    for req in ["capsule_id", "bpmn_task_id", "version", "status"]:
        if not cap_fm.get(req): comp_score -= 10; comp_details.append(f"Capsule missing {req}")
    for req in ["intent_id", "goal", "goal_type"]:
        if not int_fm.get(req): comp_score -= 10; comp_details.append(f"Intent missing {req}")
    for req in ["contract_id", "binding_status"]:
        if not con_fm.get(req): comp_score -= 10; comp_details.append(f"Contract missing {req}")
    # Critical gaps
    critical_gaps = [g for g in gaps if g.severity == "critical"]
    comp_score -= 15 * len(critical_gaps)
    if critical_gaps: comp_details.append(f"{len(critical_gaps)} critical gap(s)")
    comp_score = max(0.0, comp_score)

    # === Dimension 2: Consistency (25%) ===
    cons_score = 100.0
    cons_details = []
    # Cross-ref checks
    if cap_fm.get("intent_id") and int_fm.get("intent_id") and cap_fm["intent_id"] != int_fm["intent_id"]:
        cons_score -= 25; cons_details.append("capsule.intent_id mismatch")
    if cap_fm.get("contract_id") and con_fm.get("contract_id") and cap_fm["contract_id"] != con_fm["contract_id"]:
        cons_score -= 25; cons_details.append("capsule.contract_id mismatch")
    if int_fm.get("capsule_id") and cap_fm.get("capsule_id") and int_fm["capsule_id"] != cap_fm["capsule_id"]:
        cons_score -= 25; cons_details.append("intent.capsule_id mismatch")
    if int_fm.get("contract_ref") and con_fm.get("contract_id") and int_fm["contract_ref"] != con_fm["contract_id"]:
        cons_score -= 25; cons_details.append("intent.contract_ref mismatch")
    # Status/version consistency
    statuses = {cap_fm.get("status"), int_fm.get("status"), con_fm.get("status")} - {None}
    if len(statuses) > 1: cons_score -= 10; cons_details.append(f"Status mismatch: {statuses}")
    versions = {cap_fm.get("version"), int_fm.get("version"), con_fm.get("version")} - {None}
    if len(versions) > 1: cons_score -= 10; cons_details.append(f"Version mismatch: {versions}")
    # ID stem consistency
    cap_stem = cap_fm.get("capsule_id", "").replace("CAP-", "", 1)
    int_stem = int_fm.get("intent_id", "").replace("INT-", "", 1)
    con_stem = con_fm.get("contract_id", "").replace("ICT-", "", 1)
    stems = {cap_stem, int_stem, con_stem} - {""}
    if len(stems) > 1: cons_score -= 25; cons_details.append(f"ID stems differ: {stems}")
    cons_score = max(0.0, cons_score)

    # === Dimension 3: Schema Compliance (20%) ===
    schema_score = 100.0
    schema_details = []
    if validator:
        for name, fm, validate_fn in [("capsule", cap_fm, validator.validate_capsule), ("intent", int_fm, validator.validate_intent), ("contract", con_fm, validator.validate_contract)]:
            if fm:
                errors = validate_fn(fm)
                for e in errors[:3]:
                    schema_score -= 5
                    schema_details.append(f"{name}: {e.path}: {e.message}"[:80])
    schema_score = max(0.0, schema_score)

    # === Dimension 4: Knowledge Coverage (15%) ===
    know_score = 100.0
    know_details = []
    # Check if corpus_refs populated
    if not cap_fm.get("corpus_refs"):
        know_score -= 20; know_details.append("No corpus_refs in capsule")
    # Check if key body sections have content (not just TODO)
    if cap_body:
        if "<!-- TODO" in cap_body or len(cap_body.strip()) < 100:
            know_score -= 20; know_details.append("Capsule body has TODO stubs or is too short")
        for section in ["Procedure", "Business Rules"]:
            if section not in cap_body:
                know_score -= 10; know_details.append(f"Missing section: {section}")
    else:
        know_score -= 40; know_details.append("Empty capsule body")
    # Bonus for corpus refs
    if cap_fm.get("corpus_refs") and len(cap_fm["corpus_refs"]) >= 2:
        know_score = min(100.0, know_score + 10)
        know_details.append(f"+10 bonus for {len(cap_fm['corpus_refs'])} corpus refs")
    know_score = max(0.0, know_score)

    # === Dimension 5: Anti-UI Compliance (10%) ===
    aui_score = 100.0
    aui_details = []
    hints = int_fm.get("execution_hints", {})
    if isinstance(hints, dict):
        forbidden = set(hints.get("forbidden_actions", []))
        missing = REQUIRED_FORBIDDEN - forbidden
        if missing:
            aui_score = 0.0
            aui_details.append(f"Missing forbidden_actions: {missing}")
    else:
        aui_score = 0.0
        aui_details.append("No execution_hints in intent")

    # Build dimensions
    dimensions = [
        DimensionScore("completeness", comp_score, WEIGHTS["completeness"], comp_details),
        DimensionScore("consistency", cons_score, WEIGHTS["consistency"], cons_details),
        DimensionScore("schema_compliance", schema_score, WEIGHTS["schema_compliance"], schema_details),
        DimensionScore("knowledge_coverage", know_score, WEIGHTS["knowledge_coverage"], know_details),
        DimensionScore("anti_ui_compliance", aui_score, WEIGHTS["anti_ui_compliance"], aui_details),
    ]

    # Weighted score
    health_score = sum(d.score * d.weight for d in dimensions)
    health_score = max(0.0, min(100.0, health_score))

    return TripleScore(
        triple_id=triple_id,
        triple_name=triple_name,
        bpmn_task_type=task_type,
        health_score=health_score,
        grade=grade_from_score(health_score),
        dimensions=dimensions,
        gaps=gaps,
        files=files,
    )


def _check_graph_integrity(capsule_data: dict) -> GraphIntegrity:
    """Check graph connectivity, cycles, and start/end events."""
    if not capsule_data:
        return GraphIntegrity(connected=False, cycles=False, start_events=0, end_events=0)

    # Find start/end nodes (no predecessors / no successors)
    start_events = 0
    end_events = 0
    for cap_id, fm in capsule_data.items():
        preds = fm.get("predecessor_ids", [])
        succs = fm.get("successor_ids", [])
        if not preds: start_events += 1
        if not succs: end_events += 1

    # Connectivity: BFS from first start node
    adj = {}
    for cap_id, fm in capsule_data.items():
        adj[cap_id] = set()
        for s in fm.get("successor_ids", []):
            adj[cap_id].add(s)
        for p in fm.get("predecessor_ids", []):
            if p in capsule_data:
                adj.setdefault(p, set()).add(cap_id)

    # BFS
    all_ids = set(capsule_data.keys())
    visited = set()
    start = next((cid for cid, fm in capsule_data.items() if not fm.get("predecessor_ids")), next(iter(all_ids), None))
    if start:
        queue = deque([start])
        while queue:
            n = queue.popleft()
            if n in visited: continue
            visited.add(n)
            for neighbor in adj.get(n, []):
                if neighbor not in visited and neighbor in all_ids:
                    queue.append(neighbor)
    connected = visited == all_ids or len(all_ids) <= 1

    # Cycle detection: DFS
    has_cycle = False
    dfs_visited = set()
    in_stack = set()
    for node in all_ids:
        if node in dfs_visited: continue
        stack = [(node, False)]
        while stack:
            n, processed = stack.pop()
            if processed:
                in_stack.discard(n)
                continue
            if n in in_stack:
                has_cycle = True
                break
            if n in dfs_visited: continue
            dfs_visited.add(n)
            in_stack.add(n)
            stack.append((n, True))
            for s in capsule_data.get(n, {}).get("successor_ids", []):
                if s in in_stack:
                    has_cycle = True
                    break
                if s not in dfs_visited and s in all_ids:
                    stack.append((s, False))
            if has_cycle: break
        if has_cycle: break

    return GraphIntegrity(connected=connected, cycles=has_cycle, start_events=start_events, end_events=end_events)
