"""Finding Classifier -- converts RawDetection -> Finding.

Reads rules.yaml, matches signal_type, populates a Finding with
defect_class / layer / severity / confidence, and renders summary and detail
via Jinja2 templates. The dedup_key is computed here so the store can dedup
identical findings across runs.

Spec reference: files/11-finding-classifier.md
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml

from triple_flow_sim import TAXONOMY_VERSION
from triple_flow_sim.components.c11_classifier.templates import render
from triple_flow_sim.contracts import (
    Confidence,
    DefectClass,
    Evidence,
    Finding,
    FindingStatus,
    Generator,
    Layer,
    RawDetection,
    Severity,
)


_DEFAULT_RULES = Path(__file__).parent / "rules.yaml"


def _canonicalize(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, default=str, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(value)


class FindingClassifier:
    """Map RawDetection -> Finding using rules.yaml."""

    def __init__(self, rules_path: Optional[Path] = None, strict: bool = True):
        self.rules_path = Path(rules_path) if rules_path else _DEFAULT_RULES
        self.strict = strict
        data = yaml.safe_load(self.rules_path.read_text(encoding="utf-8")) or {}
        self.taxonomy_version = data.get("taxonomy_version", TAXONOMY_VERSION)
        self.rules: dict[str, dict] = data.get("rules", {}) or {}

    # ------------------------------------------------------------------ public
    def classify(self, detection: RawDetection, run_id: str) -> Finding:
        rule = self.rules.get(detection.signal_type)
        if rule is None:
            return self._fallback(detection, run_id)

        context = self._build_context(detection)

        # Layer may be templated (e.g. "{layer_name}"); resolve then enum-cast.
        layer_raw = str(rule.get("layer", "N/A"))
        layer_rendered = render(layer_raw, context) if "{" in layer_raw else layer_raw
        try:
            layer = Layer(layer_rendered)
        except ValueError:
            layer = Layer.NA

        defect_class = DefectClass(rule["defect_class"])
        severity = Severity(rule.get("severity", "correctness"))
        confidence = Confidence(rule.get("confidence", "high"))

        summary = render(rule.get("summary_template", ""), context)
        detail = render(rule.get("detail_template", ""), context)

        evidence = detection.evidence or Evidence()

        finding = Finding(
            detected_at=datetime.utcnow(),
            taxonomy_version=self.taxonomy_version,
            layer=layer,
            defect_class=defect_class,
            generator=detection.generator,
            severity=severity,
            confidence=confidence,
            primary_triple_id=detection.primary_triple_id or "",
            related_triple_ids=list(detection.related_triple_ids or []),
            bpmn_node_id=detection.bpmn_node_id or "",
            bpmn_edge_id=detection.bpmn_edge_id,
            summary=summary,
            detail=detail,
            evidence=evidence,
            status=FindingStatus.NEW,
            first_seen_run=run_id,
            last_seen_run=run_id,
            occurrence_count=1,
        )
        return finding

    def dedup_key(self, finding: Finding) -> str:
        """SHA256 hex of (defect_class, primary_triple_id, bpmn_edge_id, observed)."""
        observed = finding.evidence.observed if finding.evidence else None
        payload = "|".join(
            [
                finding.defect_class.value,
                finding.primary_triple_id or "",
                finding.bpmn_edge_id or "",
                _canonicalize(observed),
            ]
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    # --------------------------------------------------------------- internals
    def _build_context(self, detection: RawDetection) -> dict:
        context: dict[str, Any] = {
            "primary_triple_id": detection.primary_triple_id or "",
            "bpmn_node_id": detection.bpmn_node_id or "",
            "bpmn_edge_id": detection.bpmn_edge_id or "",
            "signal_type": detection.signal_type,
            "generator": detection.generator.value if hasattr(detection.generator, "value") else str(detection.generator),
        }
        # detector_context wins for overlapping keys.
        context.update(detection.detector_context or {})
        return context

    def _fallback(self, detection: RawDetection, run_id: str) -> Finding:
        if self.strict:
            raise ValueError(
                f"Unknown signal_type {detection.signal_type!r}; no rule in {self.rules_path.name}"
            )
        # Non-strict: try to derive defect_class from detector_context, else
        # fall back to CONTENT_MISSING as a conservative default.
        ctx = detection.detector_context or {}
        defect_value = ctx.get("defect_class") or DefectClass.CONTENT_MISSING.value
        try:
            defect_class = DefectClass(defect_value)
        except ValueError:
            defect_class = DefectClass.CONTENT_MISSING
        layer_value = ctx.get("layer") or Layer.NA.value
        try:
            layer = Layer(layer_value)
        except ValueError:
            layer = Layer.NA
        return Finding(
            detected_at=datetime.utcnow(),
            taxonomy_version=self.taxonomy_version,
            layer=layer,
            defect_class=defect_class,
            generator=detection.generator,
            severity=Severity.CORRECTNESS,
            confidence=Confidence.LOW,
            primary_triple_id=detection.primary_triple_id or "",
            related_triple_ids=list(detection.related_triple_ids or []),
            bpmn_node_id=detection.bpmn_node_id or "",
            bpmn_edge_id=detection.bpmn_edge_id,
            summary=f"Unclassified signal: {detection.signal_type}",
            detail=f"No rule matched signal_type={detection.signal_type!r}. Context: {ctx}",
            evidence=detection.evidence or Evidence(),
            status=FindingStatus.NEW,
            first_seen_run=run_id,
            last_seen_run=run_id,
            occurrence_count=1,
        )
