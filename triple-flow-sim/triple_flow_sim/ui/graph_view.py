"""Render a JourneyGraph as an interactive HTML graph via pyvis.

The graph colors each node by:
- Binding status (bound vs unbound)
- Highest-severity finding landing on the node
- Critical path membership (thicker border)

Edges carry their BPMN condition in the tooltip.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from pyvis.network import Network

from triple_flow_sim.contracts import BpmnNodeType, Finding, Severity


_SEVERITY_COLOR = {
    "regulatory": "#b71c1c",   # deep red
    "correctness": "#f57c00",  # orange
    "efficiency": "#fbc02d",   # yellow
    "cosmetic": "#90caf9",     # pale blue
}
_SHAPE_BY_NODE_TYPE = {
    BpmnNodeType.START_EVENT: "dot",
    BpmnNodeType.END_EVENT: "dot",
    BpmnNodeType.EXCLUSIVE_GATEWAY: "diamond",
    BpmnNodeType.PARALLEL_GATEWAY: "diamond",
    BpmnNodeType.INTERMEDIATE_EVENT: "triangle",
    BpmnNodeType.TASK: "box",
}


def _worst_finding(findings: Iterable[Finding]) -> Optional[Finding]:
    order = {"regulatory": 0, "correctness": 1, "efficiency": 2, "cosmetic": 3}
    picks = sorted(findings, key=lambda f: order.get(f.severity.value, 99))
    return picks[0] if picks else None


def render_graph(
    journey_graph,
    findings: list[Finding],
    out_path: Path,
    height: str = "720px",
) -> Path:
    """Write an interactive HTML graph to ``out_path`` and return it."""
    findings_by_node: dict[str, list[Finding]] = {}
    for f in findings:
        if f.bpmn_node_id:
            findings_by_node.setdefault(f.bpmn_node_id, []).append(f)

    net = Network(
        height=height,
        width="100%",
        directed=True,
        bgcolor="#1e1e1e",
        font_color="#eeeeee",
    )
    net.barnes_hut(gravity=-12000, spring_length=150, spring_strength=0.02)

    nxg = journey_graph.networkx
    for node_id, data in nxg.nodes(data=True):
        node_type = data.get("node_type")
        shape = _SHAPE_BY_NODE_TYPE.get(node_type, "ellipse")
        triple = data.get("triple")
        on_critical = data.get("is_on_critical_path", False)
        node_findings = findings_by_node.get(node_id, [])
        worst = _worst_finding(node_findings)
        if worst:
            color = _SEVERITY_COLOR.get(worst.severity.value, "#999999")
        elif triple is None:
            color = "#546e7a"  # muted grey: unbound
        else:
            color = "#2e7d32"  # green: bound + no findings

        title_lines = [
            f"<b>{data.get('name') or node_id}</b>",
            f"Node ID: {node_id}",
            f"Type: {node_type.value if hasattr(node_type, 'value') else node_type}",
        ]
        if triple:
            title_lines.append(f"Triple: {triple.triple_id}")
            intent = (
                triple.cim.intent if triple.cim and triple.cim.intent else ""
            )
            if intent:
                title_lines.append(f"Intent: {intent}")
        if on_critical:
            title_lines.append("★ on critical path")
        if node_findings:
            title_lines.append(f"Findings: {len(node_findings)}")
            for f in node_findings[:5]:
                title_lines.append(
                    f"&nbsp;&nbsp;• {f.severity.value}/{f.defect_class.value}: "
                    f"{(f.summary or '')[:80]}"
                )

        label = data.get("name") or node_id
        net.add_node(
            node_id,
            label=label,
            title="<br>".join(title_lines),
            shape=shape,
            color=color,
            borderWidth=4 if on_critical else 1,
            size=28 if shape in {"box", "ellipse"} else 22,
        )

    for u, v, edata in nxg.edges(data=True):
        cond = edata.get("condition") or ""
        title = f"edge_id: {edata.get('edge_id', '')}"
        if cond:
            title += f"<br>condition: {cond}"
        net.add_edge(
            u,
            v,
            title=title,
            arrows="to",
            dashes=bool(edata.get("is_default")),
            label=(cond[:24] + "…") if cond and len(cond) > 24 else cond,
        )

    net.set_options(
        """
        var options = {
          "physics": { "stabilization": { "iterations": 200 } },
          "interaction": { "hover": true, "tooltipDelay": 120 },
          "edges": { "smooth": { "type": "cubicBezier" }, "color": "#bbbbbb" }
        }
        """
    )
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    net.write_html(str(out_path), notebook=False, open_browser=False)
    return out_path
