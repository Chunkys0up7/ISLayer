"""Report builder (component 13).

Spec reference: files/13-report-builder.md.

Phase 4 scope: backlog markdown, heatmap JSON (defect_class × layer),
regression delta vs a previous run, and per-triple dossier text.
"""
from triple_flow_sim.components.c13_reports.builder import (
    ReportBuilder,
    render_backlog,
    render_heatmap,
    render_regression_delta,
    render_triple_dossier,
)

__all__ = [
    "ReportBuilder",
    "render_backlog",
    "render_heatmap",
    "render_regression_delta",
    "render_triple_dossier",
]
