"""Report rendering.

Spec reference: files/13-report-builder.md §B1..B5.

Produces the flagship artefacts for SMEs and maintainers:
- backlog.md — ordered triage list (severity × blast radius × confidence)
- heatmap.json — defect_class × layer counts
- regression.md — findings newly REGRESSED compared to a reference run
- dossier/<triple_id>.md — everything known about one triple
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Optional

from triple_flow_sim.contracts import Finding


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------
_SEVERITY_ORDER = {
    "regulatory": 0,
    "correctness": 1,
    "efficiency": 2,
    "cosmetic": 3,
}
_CONFIDENCE_ORDER = {"high": 0, "medium": 1, "low": 2}


def _rank(finding: Finding) -> tuple:
    sev = _SEVERITY_ORDER.get(finding.severity.value, 99)
    conf = _CONFIDENCE_ORDER.get(finding.confidence.value, 99)
    blast = -int(finding.journeys_affected_count or 0)
    crit = 0 if finding.is_on_critical_path else 1
    return (sev, crit, blast, conf, finding.defect_class.value)


# ---------------------------------------------------------------------------
# Backlog
# ---------------------------------------------------------------------------
def render_backlog(findings: Iterable[Finding]) -> str:
    ordered = sorted(findings, key=_rank)
    lines = [
        "# Triple Flow Simulator — Triage Backlog",
        "",
        "Findings ordered by severity, critical-path impact, blast radius, "
        "and confidence.",
        "",
        "| # | Severity | Class | Layer | Triple | Node | Confidence | Blast | Critical | Summary |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for i, f in enumerate(ordered, start=1):
        lines.append(
            "| {n} | {sev} | {cls} | {lay} | {tri} | {node} | {conf} | "
            "{blast} ({pct:.0f}%) | {crit} | {summary} |".format(
                n=i,
                sev=f.severity.value,
                cls=f.defect_class.value,
                lay=f.layer.value,
                tri=f.primary_triple_id or "—",
                node=f.bpmn_node_id or "—",
                conf=f.confidence.value,
                blast=f.journeys_affected_count or 0,
                pct=f.journeys_affected_pct or 0.0,
                crit="yes" if f.is_on_critical_path else "no",
                summary=(f.summary or "").replace("|", "\\|")[:120],
            )
        )
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Heatmap
# ---------------------------------------------------------------------------
def render_heatmap(findings: Iterable[Finding]) -> dict:
    matrix: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    totals_by_class: Counter = Counter()
    totals_by_layer: Counter = Counter()
    for f in findings:
        cls = f.defect_class.value
        lay = f.layer.value
        matrix[cls][lay] += 1
        totals_by_class[cls] += 1
        totals_by_layer[lay] += 1
    return {
        "matrix": {c: dict(cols) for c, cols in matrix.items()},
        "totals_by_class": dict(totals_by_class),
        "totals_by_layer": dict(totals_by_layer),
    }


# ---------------------------------------------------------------------------
# Regression delta
# ---------------------------------------------------------------------------
def render_regression_delta(
    current: Iterable[Finding],
    previous: Iterable[Finding],
) -> str:
    cur_ids = {f.finding_id for f in current}
    prev_ids = {f.finding_id for f in previous}
    new = cur_ids - prev_ids
    resolved = prev_ids - cur_ids
    lines = [
        "# Triple Flow Simulator — Regression Delta",
        "",
        f"New findings: {len(new)}",
        f"Resolved findings: {len(resolved)}",
        "",
        "## New",
    ]
    by_id = {f.finding_id: f for f in current}
    for fid in sorted(new):
        f = by_id[fid]
        lines.append(
            f"- {f.defect_class.value} on {f.primary_triple_id or '—'}: {f.summary}"
        )
    lines.append("")
    lines.append("## Resolved")
    prev_by_id = {f.finding_id: f for f in previous}
    for fid in sorted(resolved):
        f = prev_by_id[fid]
        lines.append(
            f"- {f.defect_class.value} on {f.primary_triple_id or '—'}: {f.summary}"
        )
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Per-triple dossier
# ---------------------------------------------------------------------------
def render_triple_dossier(
    triple_id: str, findings: Iterable[Finding]
) -> str:
    relevant = [
        f for f in findings
        if f.primary_triple_id == triple_id
        or triple_id in (f.related_triple_ids or [])
    ]
    lines = [
        f"# Dossier: {triple_id}",
        "",
        f"Findings: {len(relevant)}",
        "",
    ]
    for f in sorted(relevant, key=_rank):
        lines.extend(
            [
                f"## {f.defect_class.value} ({f.severity.value}/{f.confidence.value})",
                f"{f.summary}",
                "",
                "```",
                (f.detail or "").strip(),
                "```",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Facade
# ---------------------------------------------------------------------------
class ReportBuilder:
    """Write the Phase 4 artefact set to disk."""

    def __init__(self, out_dir: Path):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def write_all(
        self,
        findings: list[Finding],
        previous_findings: Optional[list[Finding]] = None,
        triple_ids: Optional[list[str]] = None,
    ) -> dict[str, Path]:
        paths: dict[str, Path] = {}
        backlog_path = self.out_dir / "backlog.md"
        backlog_path.write_text(render_backlog(findings), encoding="utf-8")
        paths["backlog"] = backlog_path

        heatmap_path = self.out_dir / "heatmap.json"
        heatmap_path.write_text(
            json.dumps(render_heatmap(findings), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        paths["heatmap"] = heatmap_path

        if previous_findings is not None:
            reg_path = self.out_dir / "regression.md"
            reg_path.write_text(
                render_regression_delta(findings, previous_findings),
                encoding="utf-8",
            )
            paths["regression"] = reg_path

        if triple_ids:
            dossier_dir = self.out_dir / "dossier"
            dossier_dir.mkdir(exist_ok=True)
            for tid in triple_ids:
                path = dossier_dir / f"{tid}.md"
                path.write_text(
                    render_triple_dossier(tid, findings), encoding="utf-8"
                )
                paths[f"dossier.{tid}"] = path

        return paths
