"""Finding store (SQLite). Phase 1 skeleton.

Spec reference: files/12-finding-store.md (~40% scope for Phase 1)

Implemented:
- start_run, complete_run, fail_run
- emit_finding with dedup by (defect_class, primary_triple_id, bpmn_edge_id, signal_context)
- get_findings, findings_by_triple
- findings_by_class, findings_by_run

Deferred to Phase 4 (Task 4.4):
- Blast radius computation
- Lifecycle transitions (triage, accept, suppress, resolve, regress)
- Retention/pruning policy
- Regression detection via trace diff
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from triple_flow_sim.contracts import (
    Confidence,
    DefectClass,
    Evidence,
    Finding,
    FindingStatus,
    Generator,
    Layer,
    Severity,
)


_SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def _canonicalize(value: Any) -> str:
    """Produce a stable JSON canonicalization for dedup hashing."""
    try:
        return json.dumps(value, sort_keys=True, default=str, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(value)


def compute_dedup_key(
    defect_class: str,
    primary_triple_id: Optional[str],
    bpmn_edge_id: Optional[str],
    observed: Any,
) -> str:
    """SHA256 hex of (defect_class, primary_triple_id, bpmn_edge_id, canonicalized_observed)."""
    payload = "|".join(
        [
            str(defect_class),
            primary_triple_id or "",
            bpmn_edge_id or "",
            _canonicalize(observed),
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class FindingStore:
    """SQLite-backed store for runs and findings.

    Phase 1 scope: inventory-signal persistence with dedup. Lifecycle and
    blast-radius computation are deferred (see module docstring).
    """

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()

    # ------------------------------------------------------------------ schema
    def _init_schema(self) -> None:
        schema_sql = _SCHEMA_PATH.read_text(encoding="utf-8")
        self._conn.executescript(schema_sql)
        self._conn.commit()

    # -------------------------------------------------------------------- runs
    def start_run(
        self,
        run_id: str,
        corpus_version_hash: str,
        bpmn_version_hash: str,
        generator: str,
        simulator_version: str,
        taxonomy_version: str,
        config: dict,
    ) -> None:
        now = datetime.utcnow().isoformat()
        self._conn.execute(
            """
            INSERT INTO runs (
                run_id, started_at, corpus_version_hash, bpmn_version_hash,
                generator, simulator_version, taxonomy_version, config_json, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'running')
            """,
            (
                run_id,
                now,
                corpus_version_hash,
                bpmn_version_hash,
                generator,
                simulator_version,
                taxonomy_version,
                json.dumps(config, default=str),
            ),
        )
        self._conn.commit()

    def complete_run(self, run_id: str, metrics: dict) -> None:
        now = datetime.utcnow().isoformat()
        self._conn.execute(
            """
            UPDATE runs
               SET completed_at = ?, status = 'completed', metrics_json = ?
             WHERE run_id = ?
            """,
            (now, json.dumps(metrics, default=str), run_id),
        )
        self._conn.commit()

    def fail_run(self, run_id: str, error: str) -> None:
        now = datetime.utcnow().isoformat()
        self._conn.execute(
            """
            UPDATE runs
               SET completed_at = ?, status = 'failed', metrics_json = ?
             WHERE run_id = ?
            """,
            (now, json.dumps({"error": error}), run_id),
        )
        self._conn.commit()

    # ---------------------------------------------------------------- findings
    def emit_finding(self, finding: Finding, run_id: str) -> str:
        """Insert a finding, deduping by dedup_key.

        On re-emit of the same dedup_key, bump occurrence_count and
        last_seen_run/last_detected_at, and append to finding_occurrences.
        """
        observed = finding.evidence.observed if finding.evidence else None
        dedup_key = compute_dedup_key(
            finding.defect_class.value,
            finding.primary_triple_id or None,
            finding.bpmn_edge_id,
            observed,
        )

        existing = self._conn.execute(
            "SELECT finding_id, occurrence_count FROM findings WHERE dedup_key = ?",
            (dedup_key,),
        ).fetchone()

        detected_at = finding.detected_at.isoformat() if finding.detected_at else datetime.utcnow().isoformat()

        if existing is not None:
            finding_id = existing["finding_id"]
            new_count = (existing["occurrence_count"] or 1) + 1
            self._conn.execute(
                """
                UPDATE findings
                   SET occurrence_count = ?,
                       last_seen_run = ?,
                       last_detected_at = ?
                 WHERE finding_id = ?
                """,
                (new_count, run_id, detected_at, finding_id),
            )
        else:
            finding_id = finding.finding_id
            self._conn.execute(
                """
                INSERT INTO findings (
                    finding_id, dedup_key, taxonomy_version, layer, defect_class,
                    generator, severity, confidence, primary_triple_id,
                    related_triple_ids, bpmn_node_id, bpmn_edge_id, summary, detail,
                    evidence_json, journeys_affected_count, journeys_affected_pct,
                    is_on_critical_path, status, suppression_reason,
                    first_seen_run, last_seen_run, occurrence_count,
                    first_detected_at, last_detected_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    finding_id,
                    dedup_key,
                    finding.taxonomy_version,
                    finding.layer.value,
                    finding.defect_class.value,
                    finding.generator.value,
                    finding.severity.value,
                    finding.confidence.value,
                    finding.primary_triple_id or None,
                    json.dumps(list(finding.related_triple_ids or [])),
                    finding.bpmn_node_id or None,
                    finding.bpmn_edge_id,
                    finding.summary,
                    finding.detail,
                    finding.evidence.model_dump_json() if finding.evidence else None,
                    int(finding.journeys_affected_count or 0),
                    float(finding.journeys_affected_pct or 0.0),
                    1 if finding.is_on_critical_path else 0,
                    finding.status.value,
                    finding.suppression_reason,
                    run_id,
                    run_id,
                    1,
                    detected_at,
                    detected_at,
                ),
            )

        # Always record the occurrence
        self._conn.execute(
            """
            INSERT INTO finding_occurrences (finding_id, run_id, detected_at)
            VALUES (?, ?, ?)
            """,
            (finding_id, run_id, detected_at),
        )
        self._conn.commit()
        return finding_id

    # ----------------------------------------------------------------- queries
    def _row_to_finding(self, row: sqlite3.Row) -> Finding:
        evidence_json = row["evidence_json"]
        evidence = Evidence.model_validate_json(evidence_json) if evidence_json else Evidence()
        related = []
        if row["related_triple_ids"]:
            try:
                related = json.loads(row["related_triple_ids"])
            except (ValueError, TypeError):
                related = []
        return Finding(
            finding_id=row["finding_id"],
            detected_at=datetime.fromisoformat(row["first_detected_at"]),
            taxonomy_version=row["taxonomy_version"],
            layer=Layer(row["layer"]),
            defect_class=DefectClass(row["defect_class"]),
            generator=Generator(row["generator"]),
            severity=Severity(row["severity"]),
            confidence=Confidence(row["confidence"]),
            primary_triple_id=row["primary_triple_id"] or "",
            related_triple_ids=related,
            bpmn_node_id=row["bpmn_node_id"] or "",
            bpmn_edge_id=row["bpmn_edge_id"],
            summary=row["summary"],
            detail=row["detail"] or "",
            evidence=evidence,
            journeys_affected_count=row["journeys_affected_count"] or 0,
            journeys_affected_pct=row["journeys_affected_pct"] or 0.0,
            is_on_critical_path=bool(row["is_on_critical_path"]),
            status=FindingStatus(row["status"]),
            suppression_reason=row["suppression_reason"],
            first_seen_run=row["first_seen_run"],
            last_seen_run=row["last_seen_run"],
            occurrence_count=row["occurrence_count"] or 1,
        )

    def get_findings(self, **filters: Any) -> list[Finding]:
        """Return findings filtered by any supported column.

        Supported filters: defect_class, layer, generator, severity, confidence,
        primary_triple_id, bpmn_node_id, bpmn_edge_id, status.
        """
        allowed = {
            "defect_class",
            "layer",
            "generator",
            "severity",
            "confidence",
            "primary_triple_id",
            "bpmn_node_id",
            "bpmn_edge_id",
            "status",
        }
        where_clauses = []
        params: list[Any] = []
        for key, value in filters.items():
            if key not in allowed:
                raise ValueError(f"Unsupported filter: {key}")
            if hasattr(value, "value"):
                value = value.value
            where_clauses.append(f"{key} = ?")
            params.append(value)

        sql = "SELECT * FROM findings"
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
        sql += " ORDER BY first_detected_at ASC"

        rows = self._conn.execute(sql, params).fetchall()
        return [self._row_to_finding(r) for r in rows]

    def findings_by_triple(self, triple_id: str) -> list[Finding]:
        rows = self._conn.execute(
            "SELECT * FROM findings WHERE primary_triple_id = ? ORDER BY first_detected_at ASC",
            (triple_id,),
        ).fetchall()
        return [self._row_to_finding(r) for r in rows]

    def findings_by_class(self, defect_class: str | DefectClass) -> list[Finding]:
        value = defect_class.value if hasattr(defect_class, "value") else defect_class
        rows = self._conn.execute(
            "SELECT * FROM findings WHERE defect_class = ? ORDER BY first_detected_at ASC",
            (value,),
        ).fetchall()
        return [self._row_to_finding(r) for r in rows]

    def findings_by_run(self, run_id: str) -> list[Finding]:
        """Return distinct findings seen in the given run (via finding_occurrences)."""
        rows = self._conn.execute(
            """
            SELECT f.* FROM findings f
            INNER JOIN (
                SELECT DISTINCT finding_id FROM finding_occurrences WHERE run_id = ?
            ) o ON o.finding_id = f.finding_id
            ORDER BY f.first_detected_at ASC
            """,
            (run_id,),
        ).fetchall()
        return [self._row_to_finding(r) for r in rows]

    # ----------------------------------------------------------------- cleanup
    def close(self) -> None:
        try:
            self._conn.close()
        except sqlite3.Error:
            pass
