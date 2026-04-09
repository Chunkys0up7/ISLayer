"""MkDocs documentation generator — creates a navigable site from process repo structure."""

from pathlib import Path
from typing import Optional
import shutil
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib.util
def _load_io(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mda_io", f"{name}.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
frontmatter_mod = _load_io("frontmatter")
yaml_io = _load_io("yaml_io")

from jinja2 import Environment, FileSystemLoader


def generate_docs(project_root: Path, config, engine_root: Optional[Path] = None) -> Path:
    """Generate MkDocs overlay for a process repo.

    Args:
        project_root: Path to the process repo root (e.g., examples/income-verification/)
        config: Config object
        engine_root: Path to engine repo root (for corpus and templates)

    Returns:
        Path to generated mkdocs.yml
    """
    docs_dir = project_root / "docs"
    if docs_dir.exists():
        shutil.rmtree(docs_dir)
    docs_dir.mkdir()

    # Resolve engine root (for templates and corpus)
    if engine_root is None:
        # Try to find engine root from config paths
        schemas_path = config.get("pipeline.schemas")
        if isinstance(schemas_path, str):
            engine_root = (project_root / schemas_path).resolve().parent
        elif isinstance(schemas_path, dict):
            # Config has individual schema paths — derive engine root from first one
            first_schema = next(iter(schemas_path.values()), "../../schemas/capsule.schema.json")
            engine_root = (project_root / first_schema).resolve().parent.parent
        else:
            engine_root = project_root.parent.parent  # Default: assume examples/{name}/

    # Set up Jinja2
    templates_dir = engine_root / "templates" / "mkdocs"
    env = Environment(loader=FileSystemLoader(str(templates_dir)), keep_trailing_newline=True)

    # Gather data
    process_name = config.get("process.name", project_root.name.replace("-", " ").title())
    process_id = config.get("process.id", "")

    # Scan triples and decisions (handle different config key patterns)
    triples_path = config.get("paths.triples") or config.get("output.triples_dir") or "triples"
    decisions_path = config.get("paths.decisions") or config.get("output.decisions_dir") or "decisions"
    tasks = _scan_triples(project_root / triples_path)
    for t in tasks:
        t["section"] = "tasks"
    decisions = _scan_triples(project_root / decisions_path)
    for d in decisions:
        d["section"] = "decisions"

    # Gather status data
    all_triples = tasks + decisions
    status_table = []
    total_gaps = 0
    status_counts = {"draft": 0, "review": 0, "approved": 0, "current": 0, "deprecated": 0}
    unbound_count = 0

    for t in all_triples:
        status_counts[t.get("status", "draft")] = status_counts.get(t.get("status", "draft"), 0) + 1
        if t.get("binding") == "unbound":
            unbound_count += 1
        total_gaps += t.get("gap_count", 0)
        status_table.append({
            "name": t["name"],
            "slug": t["slug"],
            "type": t.get("task_type", ""),
            "status": t.get("status", "draft"),
            "binding": t.get("binding", "unknown"),
            "gaps": t.get("gap_count", 0),
            "section": t.get("section", "tasks"),
        })

    summary = {
        "total": len(all_triples),
        "by_status": status_counts,
        "gap_count": total_gaps,
        "unbound_count": unbound_count,
    }

    # Generate docs/index.md
    readme_path = project_root / "README.md"
    readme_content = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    # Strip the title (first # line) since we generate our own
    lines = readme_content.split("\n")
    if lines and lines[0].startswith("# "):
        readme_content = "\n".join(lines[1:]).strip()

    _render_template(env, "index.md.j2", docs_dir / "index.md", {
        "process_name": process_name,
        "readme_content": readme_content,
        "status_table": status_table,
        "summary": summary,
    })

    # Generate docs/flow/
    flow_dir = docs_dir / "flow"
    flow_dir.mkdir()

    graph_path = config.get("paths.graph") or config.get("output.graph_dir") or "graph"
    graph_visual_path = project_root / graph_path / "graph-visual.md"
    mermaid_content = ""
    if graph_visual_path.exists():
        mermaid_content = graph_visual_path.read_text(encoding="utf-8")

    _render_template(env, "flow.md.j2", flow_dir / "diagram.md", {
        "process_name": process_name,
        "mermaid_content": mermaid_content,
    })

    graph_yaml_path = project_root / graph_path / "process-graph.yaml"
    graph_yaml_content = ""
    if graph_yaml_path.exists():
        graph_yaml_content = graph_yaml_path.read_text(encoding="utf-8")

    _render_template(env, "graph.md.j2", flow_dir / "graph.md", {
        "process_name": process_name,
        "graph_yaml": graph_yaml_content,
    })

    # Generate docs/tasks/ and docs/decisions/ — copy triple files with wrapper
    for t in tasks:
        _generate_triple_pages(env, t, docs_dir / "tasks" / t["slug"], "tasks", all_triples)
    for d in decisions:
        _generate_triple_pages(env, d, docs_dir / "decisions" / d["slug"], "decisions", all_triples)

    # Generate docs/corpus/ — filter corpus docs matching this process
    corpus_sections = []
    corpus_dir = config.corpus_dir
    if corpus_dir.exists():
        corpus_index_path = corpus_dir / "corpus.config.yaml"
        if corpus_index_path.exists():
            corpus_index = yaml_io.read_yaml(corpus_index_path)
            corpus_docs = corpus_index.get("documents", [])

            # Filter by process_id
            matching_docs = []
            for doc in corpus_docs:
                applies = doc.get("applies_to", {})
                proc_ids = applies.get("process_ids", [])
                if process_id in proc_ids or not proc_ids:  # Include if no filter or matches
                    matching_docs.append(doc)

            # Group by doc_type
            from collections import defaultdict
            by_type = defaultdict(list)
            type_names = {
                "procedure": "Procedures", "policy": "Policies", "regulation": "Regulations",
                "rule": "Rules", "data-dictionary": "Data Dictionary", "system": "Systems",
                "training": "Training", "glossary": "Glossary",
            }
            for doc in matching_docs:
                by_type[doc.get("doc_type", "other")].append(doc)

            corpus_docs_dir = docs_dir / "corpus"
            corpus_docs_dir.mkdir()

            for doc_type, docs in sorted(by_type.items()):
                type_name = type_names.get(doc_type, doc_type.title())
                corpus_sections.append({"type": doc_type, "type_name": type_name})

                # Copy each corpus doc into docs/corpus/
                doc_entries = []
                for doc in docs:
                    src = corpus_dir / doc.get("path", "")
                    if src.exists():
                        dest = corpus_docs_dir / f"{doc.get('corpus_id', 'unknown').lower()}.md"
                        # Read and strip frontmatter delimiters for cleaner rendering
                        fm, body = frontmatter_mod.read_frontmatter_file(src)
                        title = fm.get("title", doc.get("title", ""))
                        # Write a clean version with metadata table + body
                        metadata_table = f"| Field | Value |\n|-------|-------|\n"
                        metadata_table += f"| **ID** | `{fm.get('corpus_id', '')}` |\n"
                        metadata_table += f"| **Type** | {fm.get('doc_type', '')} |\n"
                        metadata_table += f"| **Domain** | {fm.get('domain', '')} |\n"
                        metadata_table += f"| **Status** | {fm.get('status', '')} |\n"
                        metadata_table += f"| **Version** | {fm.get('version', '')} |\n"
                        if fm.get("tags"):
                            metadata_table += f"| **Tags** | {', '.join(fm.get('tags', []))} |\n"

                        rendered = f"# {title}\n\n{metadata_table}\n---\n\n{body}"
                        dest.write_text(rendered, encoding="utf-8")

                        doc_entries.append({
                            "corpus_id": doc.get("corpus_id", ""),
                            "title": title,
                            "slug": doc.get("corpus_id", "").lower(),
                            "path": f"{doc.get('corpus_id', 'unknown').lower()}.md",
                            "status": doc.get("status", ""),
                            "tags": doc.get("tags", []),
                        })

                _render_template(env, "corpus-section.md.j2", corpus_docs_dir / f"{doc_type}.md", {
                    "type_name": type_name,
                    "documents": doc_entries,
                })

    # Generate docs/gaps/
    gaps_dir = docs_dir / "gaps"
    gaps_dir.mkdir()
    gaps = _collect_gaps(project_root, config)
    gap_summary = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for g in gaps:
        sev = g.get("severity", "medium")
        gap_summary[sev] = gap_summary.get(sev, 0) + 1

    _render_template(env, "gaps.md.j2", gaps_dir / "index.md", {
        "gaps": gaps,
        "summary": gap_summary,
    })

    # Generate docs/audit/
    audit_dir = docs_dir / "audit"
    audit_dir.mkdir()

    audit_path = config.get("paths.audit") or config.get("output.audit_dir") or "audit"
    ingestion_log = ""
    il_path = project_root / audit_path / "ingestion-log.yaml"
    if il_path.exists():
        ingestion_log = il_path.read_text(encoding="utf-8")

    change_log = ""
    cl_path = project_root / audit_path / "change-log.yaml"
    if cl_path.exists():
        change_log = cl_path.read_text(encoding="utf-8")

    _render_template(env, "audit.md.j2", audit_dir / "index.md", {
        "ingestion_log": ingestion_log,
        "change_log": change_log,
    })

    # Generate mkdocs.yml
    nav_tasks = [{"slug": t["slug"], "name": t["name"]} for t in tasks]
    nav_decisions = [{"slug": d["slug"], "name": d["name"]} for d in decisions]

    _render_template(env, "mkdocs.yml.j2", project_root / "mkdocs.yml", {
        "process_name": process_name,
        "site_name": f"{process_name} — MDA Intent Layer",
        "nav_tasks": nav_tasks,
        "nav_decisions": nav_decisions,
        "has_corpus": bool(corpus_sections),
        "corpus_sections": corpus_sections,
    })

    return project_root / "mkdocs.yml"


def _scan_triples(triples_dir: Path) -> list[dict]:
    """Scan a triples/ or decisions/ directory for triple subdirectories."""
    results = []
    if not triples_dir.exists():
        return results

    for d in sorted(triples_dir.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue

        triple = {"slug": d.name, "name": d.name.replace("-", " ").title(), "dir": d}

        # Read capsule frontmatter for metadata
        for cap in d.glob("*.cap.md"):
            fm, _ = frontmatter_mod.read_frontmatter_file(cap)
            triple["name"] = fm.get("bpmn_task_name", triple["name"])
            triple["task_type"] = fm.get("bpmn_task_type", "")
            triple["status"] = fm.get("status", "draft")
            triple["capsule_id"] = fm.get("capsule_id", "")
            triple["intent_id"] = fm.get("intent_id", "")
            triple["contract_id"] = fm.get("contract_id", "")
            triple["predecessor_ids"] = fm.get("predecessor_ids", [])
            triple["successor_ids"] = fm.get("successor_ids", [])
            triple["gap_count"] = len(fm.get("gaps", []))
            triple["capsule_file"] = str(cap)
            break

        # Read contract for binding status
        for con in d.glob("*.contract.md"):
            fm, _ = frontmatter_mod.read_frontmatter_file(con)
            triple["binding"] = fm.get("binding_status", "unknown")
            triple["contract_file"] = str(con)
            break

        for intent in d.glob("*.intent.md"):
            triple["intent_file"] = str(intent)
            break

        results.append(triple)

    return results


def _generate_triple_pages(env, triple_data: dict, output_dir: Path, section: str, all_triples: list):
    """Generate wrapped triple pages for a single triple."""
    output_dir.mkdir(parents=True, exist_ok=True)

    task_name = triple_data["name"]
    slug = triple_data["slug"]

    # Build cross-reference links
    capsule_link = {"name": "Capsule", "url": "capsule.md"}
    intent_link = {"name": "Intent", "url": "intent.md"}
    contract_link = {"name": "Contract", "url": "contract.md"}

    # Build predecessor/successor links
    predecessor_links = _resolve_links(triple_data.get("predecessor_ids", []), all_triples, section)
    successor_links = _resolve_links(triple_data.get("successor_ids", []), all_triples, section)

    template_vars = {
        "task_name": task_name,
        "capsule_link": capsule_link,
        "intent_link": intent_link,
        "contract_link": contract_link,
        "predecessor_links": predecessor_links,
        "successor_links": successor_links,
    }

    # Copy each file with wrapper
    for file_key, file_type, dest_name in [
        ("capsule_file", "Knowledge Capsule", "capsule.md"),
        ("intent_file", "Intent Specification", "intent.md"),
        ("contract_file", "Integration Contract", "contract.md"),
    ]:
        src_path = triple_data.get(file_key)
        if src_path and Path(src_path).exists():
            fm, body = frontmatter_mod.read_frontmatter_file(Path(src_path))

            # Build metadata table from frontmatter
            metadata_table = "| Field | Value |\n|-------|-------|\n"
            for k, v in fm.items():
                if isinstance(v, (list, dict)):
                    continue  # Skip complex fields for the table
                if v is not None and v != "":
                    metadata_table += f"| **{k}** | `{v}` |\n"

            content = f"{metadata_table}\n---\n\n{body}"

            _render_template(env, "triple-wrapper.md.j2", output_dir / dest_name, {
                **template_vars,
                "triple_type": file_type,
                "content": content,
            })
        else:
            # File not found — generate placeholder
            (output_dir / dest_name).write_text(f"# {task_name} — {file_type}\n\n*File not found.*\n", encoding="utf-8")


def _resolve_links(ids: list, all_triples: list, current_section: str) -> list[dict]:
    """Resolve capsule IDs to navigable links."""
    links = []
    for cap_id in ids:
        for t in all_triples:
            if t.get("capsule_id") == cap_id:
                # Determine target section based on the triple's source
                target_section = t.get("section", "tasks")
                rel = f"../../{target_section}/{t['slug']}/capsule.md"
                links.append({"name": t["name"], "url": rel})
                break
    return links


def _collect_gaps(project_root: Path, config) -> list[dict]:
    """Collect all gaps from capsule frontmatter and GAP-*.md files."""
    gaps = []

    # From capsule frontmatter
    for base, alt_key in [("triples", "output.triples_dir"), ("decisions", "output.decisions_dir")]:
        base_dir = project_root / (config.get(f"paths.{base}") or config.get(alt_key) or base)
        if not base_dir.exists():
            continue
        for d in base_dir.iterdir():
            if not d.is_dir() or d.name.startswith("_"):
                continue
            for cap in d.glob("*.cap.md"):
                fm, _ = frontmatter_mod.read_frontmatter_file(cap)
                for gap in fm.get("gaps", []):
                    if isinstance(gap, dict):
                        gap["triple"] = d.name
                        gap["id"] = gap.get("type", "unknown")
                        gaps.append(gap)

    # From standalone gap files
    gaps_dir = project_root / (config.get("paths.gaps") or config.get("output.gaps_dir") or "gaps")
    if gaps_dir.exists():
        for gap_file in sorted(gaps_dir.glob("GAP-*.md")):
            fm, body = frontmatter_mod.read_frontmatter_file(gap_file)
            if fm:
                gaps.append({
                    "id": fm.get("gap_id", gap_file.stem),
                    "severity": fm.get("severity", "medium"),
                    "type": fm.get("gap_type", "unknown"),
                    "triple": fm.get("triple", "process-level"),
                    "description": fm.get("description", body[:100] if body else ""),
                })

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    gaps.sort(key=lambda g: severity_order.get(g.get("severity", "medium"), 99))

    return gaps


def _render_template(env, template_name: str, output_path: Path, context: dict):
    """Render a Jinja2 template to a file."""
    template = env.get_template(template_name)
    content = template.render(**context)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
