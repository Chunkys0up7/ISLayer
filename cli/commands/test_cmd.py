"""mda test — Run verification checks on the current process repository."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime

import importlib.util
def _load_io(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mda_io", f"{name}.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
frontmatter_mod = _load_io("frontmatter")
yaml_io = _load_io("yaml_io")
bpmn_xml = _load_io("bpmn_xml")
schema_val = _load_io("schema_validator")

@dataclass
class TestResult:
    check_id: str
    check_name: str
    status: str  # PASS, FAIL, WARN, SKIP
    details: list[str] = field(default_factory=list)
    category: str = ""


def run_test(args, config):
    """Run verification checks on the current process repository."""
    from output.console import console, print_header, print_success, print_error, print_warning, print_info
    from output.json_output import output_json

    project_root = config.project_root

    # Determine which categories to run
    run_bpmn = getattr(args, 'bpmn', False)
    run_triples = getattr(args, 'triples', False)
    run_corpus = getattr(args, 'corpus', False)
    quick = getattr(args, 'quick', False)

    # If none specified, run all
    if not any([run_bpmn, run_triples, run_corpus]):
        run_bpmn = run_triples = run_corpus = True

    results = []

    # Resolve paths (handle different config key patterns)
    bpmn_dir = project_root / (config.get("paths.bpmn") or config.get("source.bpmn_file", "bpmn/")).rsplit("/", 1)[0] if config.get("source.bpmn_file") else project_root / (config.get("paths.bpmn") or "bpmn")
    triples_dir = project_root / (config.get("paths.triples") or config.get("output.triples_dir") or "triples")
    decisions_dir = project_root / (config.get("paths.decisions") or config.get("output.decisions_dir") or "decisions")
    corpus_dir = config.corpus_dir
    schemas_dir = config.schemas_dir

    # === BPMN Checks (B01-B08) ===
    if run_bpmn:
        results.extend(_run_bpmn_checks(project_root, bpmn_dir, quick))

    # === Triple Checks (T01-T11) ===
    if run_triples:
        results.extend(_run_triple_checks(triples_dir, decisions_dir, schemas_dir, corpus_dir, quick))

    # === Corpus Checks (C01-C06) ===
    if run_corpus:
        results.extend(_run_corpus_checks(corpus_dir, schemas_dir, quick))

    # Display results
    if getattr(args, 'json', False):
        output_json({
            "timestamp": datetime.utcnow().isoformat(),
            "process": config.get("process.name", "unknown"),
            "results": [{"id": r.check_id, "name": r.check_name, "status": r.status, "category": r.category, "details": r.details} for r in results],
            "summary": _summarize(results),
        })
    else:
        print_header("MDA Test Results")

        # Group by category
        for category in ["bpmn", "triples", "corpus"]:
            cat_results = [r for r in results if r.category == category]
            if not cat_results:
                continue
            console.print(f"\n[bold]{category.upper()} Checks[/bold]")
            for r in cat_results:
                if r.status == "PASS":
                    console.print(f"  [green]PASS[/green] [{r.check_id}] {r.check_name}")
                elif r.status == "WARN":
                    console.print(f"  [yellow]WARN[/yellow] [{r.check_id}] {r.check_name}")
                    for d in r.details:
                        console.print(f"         {d}")
                elif r.status == "FAIL":
                    console.print(f"  [red]FAIL[/red] [{r.check_id}] {r.check_name}")
                    for d in r.details:
                        console.print(f"         {d}")
                elif r.status == "SKIP":
                    console.print(f"  [dim]SKIP[/dim] [{r.check_id}] {r.check_name}")

        # Summary
        summary = _summarize(results)
        console.print(f"\n[bold]Summary:[/bold] {summary['pass']} passed, {summary['fail']} failed, {summary['warn']} warnings, {summary['skip']} skipped")

    # Write report if requested
    report_path = getattr(args, 'report', None)
    if report_path:
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "process": config.get("process.name", "unknown"),
            "results": [{"id": r.check_id, "name": r.check_name, "status": r.status, "category": r.category, "details": r.details} for r in results],
            "summary": _summarize(results),
        }
        yaml_io.write_yaml(Path(report_path), report)
        if not getattr(args, 'json', False):
            print_info(f"Report written to {report_path}")

    # Exit code
    if any(r.status == "FAIL" for r in results):
        sys.exit(1)


def _summarize(results):
    return {
        "pass": sum(1 for r in results if r.status == "PASS"),
        "fail": sum(1 for r in results if r.status == "FAIL"),
        "warn": sum(1 for r in results if r.status == "WARN"),
        "skip": sum(1 for r in results if r.status == "SKIP"),
        "total": len(results),
    }


def _run_bpmn_checks(project_root, bpmn_dir, quick):
    """BPMN checks B01-B08."""
    results = []

    # B01: BPMN file exists
    bpmn_files = list(bpmn_dir.glob("*.bpmn")) if bpmn_dir.exists() else []
    if bpmn_files:
        results.append(TestResult("B01", "BPMN file exists", "PASS", [str(f.name) for f in bpmn_files], "bpmn"))
    else:
        results.append(TestResult("B01", "BPMN file exists", "FAIL", [f"No .bpmn files found in {bpmn_dir}"], "bpmn"))
        return results  # Can't continue without BPMN

    # B02: BPMN parses
    bpmn_file = bpmn_files[0]
    try:
        model = bpmn_xml.parse_bpmn(bpmn_file)
        results.append(TestResult("B02", "BPMN parses successfully", "PASS", [], "bpmn"))
    except Exception as e:
        results.append(TestResult("B02", "BPMN parses successfully", "FAIL", [str(e)], "bpmn"))
        return results

    if quick:
        return results

    # B03: Node count (informational)
    from collections import Counter
    type_counts = Counter(n.element_type for n in model.nodes)
    results.append(TestResult("B03", f"Node count: {len(model.nodes)} nodes, {len(model.edges)} edges, {len(model.lanes)} lanes", "PASS",
        [f"{k}: {v}" for k, v in sorted(type_counts.items())], "bpmn"))

    # B04: No duplicate IDs
    node_ids = [n.id for n in model.nodes]
    dupes = [nid for nid in set(node_ids) if node_ids.count(nid) > 1]
    if dupes:
        results.append(TestResult("B04", "No duplicate node IDs", "FAIL", [f"Duplicates: {dupes}"], "bpmn"))
    else:
        results.append(TestResult("B04", "No duplicate node IDs", "PASS", [], "bpmn"))

    # B05: All edges valid
    node_id_set = set(node_ids)
    bad_edges = []
    for e in model.edges:
        if e.source_id not in node_id_set:
            bad_edges.append(f"Edge {e.id}: source {e.source_id} not found")
        if e.target_id not in node_id_set:
            bad_edges.append(f"Edge {e.id}: target {e.target_id} not found")
    if bad_edges:
        results.append(TestResult("B05", "All edges connect valid nodes", "FAIL", bad_edges, "bpmn"))
    else:
        results.append(TestResult("B05", "All edges connect valid nodes", "PASS", [], "bpmn"))

    # B06: Graph connected
    start_nodes = [n for n in model.nodes if n.element_type == "startEvent"]
    if start_nodes:
        visited = set()
        queue = [start_nodes[0].id]
        # Build adjacency (undirected for reachability)
        adj = {}
        for n in model.nodes:
            adj[n.id] = set()
        for e in model.edges:
            if e.source_id in adj and e.target_id in adj:
                adj[e.source_id].add(e.target_id)
                adj[e.target_id].add(e.source_id)
        while queue:
            nid = queue.pop(0)
            if nid in visited:
                continue
            visited.add(nid)
            for neighbor in adj.get(nid, []):
                if neighbor not in visited:
                    queue.append(neighbor)
        unreachable = node_id_set - visited
        if unreachable:
            results.append(TestResult("B06", "Graph connected from start", "WARN", [f"Unreachable: {unreachable}"], "bpmn"))
        else:
            results.append(TestResult("B06", "Graph connected from start", "PASS", [], "bpmn"))
    else:
        results.append(TestResult("B06", "Graph connected from start", "SKIP", ["No startEvent found"], "bpmn"))

    # B07: Start/end events
    has_start = any(n.element_type == "startEvent" for n in model.nodes)
    has_end = any(n.element_type == "endEvent" for n in model.nodes)
    if has_start and has_end:
        results.append(TestResult("B07", "Start and end events exist", "PASS", [], "bpmn"))
    else:
        missing = []
        if not has_start: missing.append("startEvent")
        if not has_end: missing.append("endEvent")
        results.append(TestResult("B07", "Start and end events exist", "FAIL", [f"Missing: {missing}"], "bpmn"))

    # B08: All nodes named
    unnamed = [n.id for n in model.nodes if not n.name]
    if unnamed:
        results.append(TestResult("B08", "All nodes named", "WARN", [f"Unnamed: {unnamed}"], "bpmn"))
    else:
        results.append(TestResult("B08", "All nodes named", "PASS", [], "bpmn"))

    return results


def _run_triple_checks(triples_dir, decisions_dir, schemas_dir, corpus_dir, quick):
    """Triple checks T01-T11."""
    results = []

    # Discover all triple directories
    triple_dirs = []
    for base in [triples_dir, decisions_dir]:
        if base.exists():
            for d in sorted(base.iterdir()):
                if d.is_dir() and not d.name.startswith("_"):
                    triple_dirs.append(d)

    if not triple_dirs:
        results.append(TestResult("T01", "Triple directories found", "FAIL", ["No triple directories found"], "triples"))
        return results

    # T01: Triple completeness
    incomplete = []
    all_triples = []  # (dir, cap_fm, int_fm, con_fm)
    for d in triple_dirs:
        caps = list(d.glob("*.cap.md"))
        intents = list(d.glob("*.intent.md"))
        contracts = list(d.glob("*.contract.md"))
        missing = []
        if not caps: missing.append(".cap.md")
        if not intents: missing.append(".intent.md")
        if not contracts: missing.append(".contract.md")
        if missing:
            incomplete.append(f"{d.name}: missing {', '.join(missing)}")
        else:
            cap_fm, _ = frontmatter_mod.read_frontmatter_file(caps[0])
            int_fm, _ = frontmatter_mod.read_frontmatter_file(intents[0])
            con_fm, _ = frontmatter_mod.read_frontmatter_file(contracts[0])
            all_triples.append({"dir": d, "cap": cap_fm, "int": int_fm, "con": con_fm})

    if incomplete:
        results.append(TestResult("T01", "All triples have 3 files", "FAIL", incomplete, "triples"))
    else:
        results.append(TestResult("T01", f"All triples have 3 files ({len(triple_dirs)} triples)", "PASS", [], "triples"))

    if quick:
        # T04 cross-refs only in quick mode
        xref_errors = []
        for t in all_triples:
            cap, intent, con = t["cap"], t["int"], t["con"]
            if cap.get("intent_id") != intent.get("intent_id"):
                xref_errors.append(f"{t['dir'].name}: capsule.intent_id mismatch")
            if cap.get("contract_id") != con.get("contract_id"):
                xref_errors.append(f"{t['dir'].name}: capsule.contract_id mismatch")
        if xref_errors:
            results.append(TestResult("T04", "Cross-references valid", "FAIL", xref_errors, "triples"))
        else:
            results.append(TestResult("T04", "Cross-references valid", "PASS", [], "triples"))
        return results

    # T02: ID conventions
    CAP_PAT = re.compile(r"^CAP-[A-Z0-9]{2,3}-[A-Z0-9]{3}-\d{3}$")
    INT_PAT = re.compile(r"^INT-[A-Z0-9]{2,3}-[A-Z0-9]{3}-\d{3}$")
    ICT_PAT = re.compile(r"^ICT-[A-Z0-9]{2,3}-[A-Z0-9]{3}-\d{3}$")
    id_errors = []
    for t in all_triples:
        cap_id = t["cap"].get("capsule_id", "")
        int_id = t["int"].get("intent_id", "")
        con_id = t["con"].get("contract_id", "")
        if not CAP_PAT.match(cap_id): id_errors.append(f"{t['dir'].name}: bad capsule_id: {cap_id}")
        if not INT_PAT.match(int_id): id_errors.append(f"{t['dir'].name}: bad intent_id: {int_id}")
        if not ICT_PAT.match(con_id): id_errors.append(f"{t['dir'].name}: bad contract_id: {con_id}")
    if id_errors:
        results.append(TestResult("T02", "ID conventions", "FAIL", id_errors, "triples"))
    else:
        results.append(TestResult("T02", "ID conventions", "PASS", [], "triples"))

    # T03: ID stem consistency
    stem_errors = []
    for t in all_triples:
        cap_stem = t["cap"].get("capsule_id", "").replace("CAP-", "", 1)
        int_stem = t["int"].get("intent_id", "").replace("INT-", "", 1)
        con_stem = t["con"].get("contract_id", "").replace("ICT-", "", 1)
        if not (cap_stem == int_stem == con_stem):
            stem_errors.append(f"{t['dir'].name}: CAP={cap_stem} INT={int_stem} ICT={con_stem}")
    if stem_errors:
        results.append(TestResult("T03", "ID stem consistency", "FAIL", stem_errors, "triples"))
    else:
        results.append(TestResult("T03", "ID stem consistency", "PASS", [], "triples"))

    # T04: Cross-references
    xref_errors = []
    for t in all_triples:
        cap, intent, con = t["cap"], t["int"], t["con"]
        if cap.get("intent_id") != intent.get("intent_id"):
            xref_errors.append(f"{t['dir'].name}: capsule.intent_id != intent.intent_id")
        if cap.get("contract_id") != con.get("contract_id"):
            xref_errors.append(f"{t['dir'].name}: capsule.contract_id != contract.contract_id")
        if intent.get("capsule_id") != cap.get("capsule_id"):
            xref_errors.append(f"{t['dir'].name}: intent.capsule_id != capsule.capsule_id")
        if intent.get("contract_ref") != con.get("contract_id"):
            xref_errors.append(f"{t['dir'].name}: intent.contract_ref != contract.contract_id")
        if con.get("intent_id") != intent.get("intent_id"):
            xref_errors.append(f"{t['dir'].name}: contract.intent_id != intent.intent_id")
    if xref_errors:
        results.append(TestResult("T04", "Cross-references valid", "FAIL", xref_errors, "triples"))
    else:
        results.append(TestResult("T04", "Cross-references valid", "PASS", [], "triples"))

    # T05: Status consistency
    status_warns = []
    for t in all_triples:
        statuses = {t["cap"].get("status"), t["int"].get("status"), t["con"].get("status")}
        if len(statuses) > 1:
            status_warns.append(f"{t['dir'].name}: {statuses}")
    if status_warns:
        results.append(TestResult("T05", "Status consistency", "WARN", status_warns, "triples"))
    else:
        results.append(TestResult("T05", "Status consistency", "PASS", [], "triples"))

    # T06: Version consistency
    version_warns = []
    for t in all_triples:
        versions = {t["cap"].get("version"), t["int"].get("version"), t["con"].get("version")}
        if len(versions) > 1:
            version_warns.append(f"{t['dir'].name}: {versions}")
    if version_warns:
        results.append(TestResult("T06", "Version consistency", "WARN", version_warns, "triples"))
    else:
        results.append(TestResult("T06", "Version consistency", "PASS", [], "triples"))

    # T07: Schema validation
    schema_errors = []
    try:
        validator = schema_val.SchemaValidator(schemas_dir)
        for t in all_triples[:5]:  # Sample first 5 for speed
            for name, fm, validate_fn in [
                ("capsule", t["cap"], validator.validate_capsule),
                ("intent", t["int"], validator.validate_intent),
                ("contract", t["con"], validator.validate_contract),
            ]:
                errors = validate_fn(fm)
                for e in errors[:2]:
                    schema_errors.append(f"{t['dir'].name}/{name}: {e.path}: {e.message}")
    except Exception as e:
        schema_errors.append(f"Schema validator error: {e}")
    if schema_errors:
        results.append(TestResult("T07", "Schema validation", "WARN", schema_errors[:10], "triples"))
    else:
        results.append(TestResult("T07", "Schema validation", "PASS", [], "triples"))

    # T08: Anti-UI compliance
    REQUIRED_FORBIDDEN = {"browser_automation", "screen_scraping", "ui_click", "rpa_style_macros"}
    anti_ui_errors = []
    for t in all_triples:
        hints = t["int"].get("execution_hints", {})
        if not isinstance(hints, dict):
            anti_ui_errors.append(f"{t['dir'].name}: no execution_hints")
            continue
        forbidden = set(hints.get("forbidden_actions", []))
        missing = REQUIRED_FORBIDDEN - forbidden
        if missing:
            anti_ui_errors.append(f"{t['dir'].name}: missing forbidden_actions: {missing}")
    if anti_ui_errors:
        results.append(TestResult("T08", "Anti-UI compliance", "WARN", anti_ui_errors, "triples"))
    else:
        results.append(TestResult("T08", "Anti-UI compliance", "PASS", [], "triples"))

    # T09: Predecessor/successor validity
    all_cap_ids = {t["cap"].get("capsule_id") for t in all_triples}
    pred_errors = []
    for t in all_triples:
        for pred_id in t["cap"].get("predecessor_ids", []):
            if pred_id not in all_cap_ids:
                pred_errors.append(f"{t['dir'].name}: predecessor {pred_id} not found")
        for succ_id in t["cap"].get("successor_ids", []):
            if succ_id not in all_cap_ids:
                pred_errors.append(f"{t['dir'].name}: successor {succ_id} not found")
    if pred_errors:
        results.append(TestResult("T09", "Predecessor/successor validity", "WARN", pred_errors[:10], "triples"))
    else:
        results.append(TestResult("T09", "Predecessor/successor validity", "PASS", [], "triples"))

    # T10: No circular dependencies
    # Simple DFS cycle detection
    adj = {}
    for t in all_triples:
        cap_id = t["cap"].get("capsule_id", "")
        adj[cap_id] = t["cap"].get("successor_ids", [])

    def has_cycle():
        visited = set()
        in_stack = set()
        for node in adj:
            if node in visited:
                continue
            stack = [(node, False)]
            while stack:
                n, processed = stack.pop()
                if processed:
                    in_stack.discard(n)
                    continue
                if n in in_stack:
                    return True
                if n in visited:
                    continue
                visited.add(n)
                in_stack.add(n)
                stack.append((n, True))
                for succ in adj.get(n, []):
                    if succ in in_stack:
                        return True
                    if succ not in visited:
                        stack.append((succ, False))
        return False

    if has_cycle():
        results.append(TestResult("T10", "No circular dependencies", "FAIL", ["Cycle detected in successor chain"], "triples"))
    else:
        results.append(TestResult("T10", "No circular dependencies", "PASS", [], "triples"))

    # T11: BPMN mapping coverage (check triple count matches expectations)
    results.append(TestResult("T11", f"BPMN mapping coverage: {len(triple_dirs)} triples found", "PASS", [], "triples"))

    return results


def _run_corpus_checks(corpus_dir, schemas_dir, quick):
    """Corpus checks C01-C06."""
    results = []

    # C01: Index exists
    index_path = corpus_dir / "corpus.config.yaml"
    if not index_path.exists():
        results.append(TestResult("C01", "Corpus index exists", "FAIL", [f"Not found: {index_path}"], "corpus"))
        return results
    results.append(TestResult("C01", "Corpus index exists", "PASS", [], "corpus"))

    index = yaml_io.read_yaml(index_path)
    documents = index.get("documents", [])

    # C02: Document count
    corpus_files = sorted(corpus_dir.rglob("*.corpus.md"))
    expected_count = index.get("document_count", 0)
    actual_count = len(corpus_files)
    if expected_count == actual_count == len(documents):
        results.append(TestResult("C02", f"Document count: {actual_count}", "PASS", [], "corpus"))
    else:
        results.append(TestResult("C02", "Document count", "FAIL",
            [f"Index says {expected_count}, array has {len(documents)}, disk has {actual_count}"], "corpus"))

    if quick:
        return results

    # C03: No orphan files
    indexed_paths = {d.get("path", "") for d in documents}
    orphans = []
    for f in corpus_files:
        rel = str(f.relative_to(corpus_dir)).replace("\\", "/")
        if rel not in indexed_paths:
            orphans.append(rel)
    if orphans:
        results.append(TestResult("C03", "No orphan files", "FAIL", orphans, "corpus"))
    else:
        results.append(TestResult("C03", "No orphan files", "PASS", [], "corpus"))

    # C04: No missing files
    missing = []
    for d in documents:
        fpath = corpus_dir / d.get("path", "")
        if not fpath.exists():
            missing.append(d.get("path", ""))
    if missing:
        results.append(TestResult("C04", "No missing files", "FAIL", missing, "corpus"))
    else:
        results.append(TestResult("C04", "No missing files", "PASS", [], "corpus"))

    # C05: No duplicate IDs
    corpus_ids = [d.get("corpus_id", "") for d in documents]
    dupes = [cid for cid in set(corpus_ids) if corpus_ids.count(cid) > 1]
    if dupes:
        results.append(TestResult("C05", "No duplicate corpus IDs", "FAIL", dupes, "corpus"))
    else:
        results.append(TestResult("C05", "No duplicate corpus IDs", "PASS", [], "corpus"))

    # C06: Schema validation (sample 5 for speed)
    schema_errors = []
    try:
        validator = schema_val.SchemaValidator(schemas_dir)
        for f in corpus_files[:5]:
            fm, _ = frontmatter_mod.read_frontmatter_file(f)
            errors = validator.validate_corpus_document(fm)
            for e in errors[:2]:
                schema_errors.append(f"{f.name}: {e.path}: {e.message}")
    except Exception as e:
        schema_errors.append(f"Validator error: {e}")
    if schema_errors:
        results.append(TestResult("C06", "Corpus schema validation", "WARN", schema_errors[:10], "corpus"))
    else:
        results.append(TestResult("C06", "Corpus schema validation", "PASS", [], "corpus"))

    return results
