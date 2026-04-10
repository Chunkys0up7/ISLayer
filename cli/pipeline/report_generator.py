"""Report generator — produces XML, JSON, YAML output from ProcessReport."""

import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from typing import Optional
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib.util
def _load_io(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mda_io", f"{name}.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
yaml_io = _load_io("yaml_io")

from models.report import ProcessReport


def generate_xml(report: ProcessReport) -> str:
    """Generate XML report string from ProcessReport."""
    root = ET.Element("mda-report", version="1.0", generated=report.generated)

    proc = ET.SubElement(root, "process", id=report.process_id, name=report.process_name)

    # Health score
    hs = ET.SubElement(proc, "health-score", value=str(round(report.health_score, 1)), grade=report.grade.value, label=report.grade_label)

    # Summary
    summary = ET.SubElement(proc, "summary")
    ET.SubElement(summary, "total-triples").text = str(len(report.triple_scores))
    gaps_el = ET.SubElement(summary, "gaps",
        total=str(report.gap_summary.total),
        critical=str(report.gap_summary.critical),
        high=str(report.gap_summary.high),
        medium=str(report.gap_summary.medium),
        low=str(report.gap_summary.low),
    )
    ET.SubElement(summary, "schema-violations").text = str(report.schema_violations)
    ET.SubElement(summary, "cross-ref-errors").text = str(report.cross_ref_errors)

    # Triples
    triples_el = ET.SubElement(proc, "triples")
    for ts in report.triple_scores:
        triple_el = ET.SubElement(triples_el, "triple", id=ts.triple_id, name=ts.triple_name, type=ts.bpmn_task_type)
        ET.SubElement(triple_el, "health-score", value=str(round(ts.health_score, 1)), grade=ts.grade.value)

        dims_el = ET.SubElement(triple_el, "dimensions")
        for d in ts.dimensions:
            dim_el = ET.SubElement(dims_el, d.name.replace("_", "-"), score=str(round(d.score, 1)))
            if d.details:
                for det in d.details[:3]:
                    ET.SubElement(dim_el, "detail").text = det

        if ts.gaps:
            gaps_el = ET.SubElement(triple_el, "gaps")
            for g in ts.gaps:
                gap_el = ET.SubElement(gaps_el, "gap", type=g.gap_type, severity=g.severity)
                gap_el.text = g.description

        files_el = ET.SubElement(triple_el, "files")
        for f in ts.files:
            attrs = {"id": f.artifact_id, "status": f.status}
            if f.binding_status: attrs["binding"] = f.binding_status
            ET.SubElement(files_el, f.artifact_type, **attrs)

    # Corpus coverage
    cc = ET.SubElement(proc, "corpus-coverage")
    ET.SubElement(cc, "matched-docs").text = str(report.corpus_coverage.matched_docs)
    ET.SubElement(cc, "total-corpus-docs").text = str(report.corpus_coverage.total_corpus_docs)
    ET.SubElement(cc, "triples-with-corpus-refs").text = str(report.corpus_coverage.triples_with_corpus_refs)

    # Graph integrity
    gi = ET.SubElement(proc, "graph-integrity")
    ET.SubElement(gi, "connected").text = str(report.graph_integrity.connected).lower()
    ET.SubElement(gi, "cycles").text = str(report.graph_integrity.cycles).lower()
    ET.SubElement(gi, "start-events").text = str(report.graph_integrity.start_events)
    ET.SubElement(gi, "end-events").text = str(report.graph_integrity.end_events)

    # Pretty-print
    xml_str = ET.tostring(root, encoding="unicode", xml_declaration=False)
    pretty = minidom.parseString(xml_str).toprettyxml(indent="  ", encoding=None)
    # Remove extra XML declaration from minidom
    lines = pretty.split("\n")
    if lines[0].startswith("<?xml"):
        lines[0] = '<?xml version="1.0" encoding="UTF-8"?>'
    return "\n".join(lines)


def generate_json(report: ProcessReport, indent: int = 2) -> str:
    """Generate JSON report string."""
    return json.dumps(report.to_dict(), indent=indent, default=str)


def generate_yaml(report: ProcessReport) -> str:
    """Generate YAML report string."""
    return yaml_io.dump_yaml_string(report.to_dict())


def write_report(report: ProcessReport, output_path: Path, fmt: str = "xml") -> None:
    """Write report to file in specified format."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "xml":
        content = generate_xml(report)
    elif fmt == "json":
        content = generate_json(report)
    elif fmt == "yaml":
        content = generate_yaml(report)
    else:
        raise ValueError(f"Unknown format: {fmt}")
    output_path.write_text(content, encoding="utf-8")
