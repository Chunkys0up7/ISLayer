"""Inventory report renderer.

Produces markdown and JSON artifacts from an InventoryReport + list[Finding].
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from triple_flow_sim.components.c02_inventory import InventoryReport
from triple_flow_sim.components.c02_inventory.completeness_matrix import render_markdown
from triple_flow_sim.contracts import Finding


def render_markdown_report(
    report: InventoryReport,
    findings: list[Finding],
    run_id: str,
) -> str:
    """Produce a human-readable markdown report."""
    now = datetime.utcnow().isoformat() + "Z"
    total_findings = len(findings)
    stats = report.stats or {}
    simulatable = stats.get("simulatable_triple_count", "n/a")
    excluded = stats.get("excluded_triple_count", 0)

    lines: list[str] = []
    lines.append("# Triple Flow Simulator — Inventory Report")
    lines.append("")
    lines.append(f"- Run ID: `{run_id}`")
    lines.append(f"- Generated at: {now}")
    lines.append(f"- Corpus version hash: `{report.corpus_version_hash}`")
    lines.append(f"- Total triples: {report.total_triples}")
    lines.append(f"- Findings: {total_findings}")
    lines.append(f"- Simulatable triples: {simulatable}")
    lines.append(f"- Excluded triples: {excluded}")
    lines.append("")

    # Summary section
    lines.append("## Summary")
    lines.append("")
    detection_counts = stats.get("detection_counts", {}) or {}
    if detection_counts:
        lines.append("| signal_type | count |")
        lines.append("|---|---|")
        for sig, count in sorted(
            detection_counts.items(), key=lambda kv: -int(kv[1])
        ):
            lines.append(f"| {sig} | {count} |")
    else:
        lines.append("*(no detections)*")
    lines.append("")

    # Exclusions
    lines.append("## Exclusions")
    lines.append("")
    if report.exclusions:
        lines.append("| triple_id | reason | detail |")
        lines.append("|---|---|---|")
        for excl in report.exclusions:
            lines.append(f"| {excl.triple_id} | {excl.reason} | {excl.detail} |")
    else:
        lines.append("*(none)*")
    lines.append("")

    # Findings grouped by defect_class
    lines.append("## Findings")
    lines.append("")
    if findings:
        by_class: dict[str, list[Finding]] = defaultdict(list)
        for f in findings:
            by_class[f.defect_class.value].append(f)
        class_counts = Counter({k: len(v) for k, v in by_class.items()})
        for cls, _count in class_counts.most_common():
            items = by_class[cls]
            lines.append(f"### {cls} ({len(items)})")
            lines.append("")
            for f in items:
                lines.append(f"- `{f.primary_triple_id}` — {f.summary}")
            lines.append("")
    else:
        lines.append("*(no findings)*")
        lines.append("")

    # Completeness matrix
    lines.append("## Completeness Matrix")
    lines.append("")
    lines.append(render_markdown(report.completeness_matrix))
    lines.append("")

    # Graph status
    if report.graph_warning:
        lines.append("## Graph Status")
        lines.append("")
        lines.append(report.graph_warning)
        lines.append("")

    return "\n".join(lines)


def render_json_report(
    report: InventoryReport,
    findings: list[Finding],
    run_id: str,
) -> dict:
    """Produce a machine-readable JSON report."""
    return {
        "run_id": run_id,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "corpus_version_hash": report.corpus_version_hash,
        "total_triples": report.total_triples,
        "stats": report.stats,
        "exclusions": [e.model_dump() for e in report.exclusions],
        "completeness_matrix": report.completeness_matrix,
        "findings": [f.model_dump(mode="json") for f in findings],
        "graph_warning": report.graph_warning,
    }


def write_reports(
    report: InventoryReport,
    findings: list[Finding],
    run_id: str,
    out_dir: Path,
) -> dict:
    """Write markdown + JSON reports to out_dir. Returns {markdown_path, json_path}."""
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / "inventory.md"
    json_path = out_dir / "inventory.json"
    md_path.write_text(
        render_markdown_report(report, findings, run_id),
        encoding="utf-8",
    )
    json_path.write_text(
        json.dumps(render_json_report(report, findings, run_id), indent=2, default=str),
        encoding="utf-8",
    )
    return {"markdown_path": md_path, "json_path": json_path}
