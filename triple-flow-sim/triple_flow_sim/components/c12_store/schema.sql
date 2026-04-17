-- Finding store schema (SQLite).
-- Spec reference: files/12-finding-store.md

CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    corpus_version_hash TEXT,
    bpmn_version_hash TEXT,
    generator TEXT,
    simulator_version TEXT,
    taxonomy_version TEXT,
    config_json TEXT,
    status TEXT DEFAULT 'running',  -- running/completed/failed
    metrics_json TEXT
);

CREATE TABLE IF NOT EXISTS findings (
    finding_id TEXT PRIMARY KEY,
    dedup_key TEXT NOT NULL,
    taxonomy_version TEXT NOT NULL,
    layer TEXT NOT NULL,
    defect_class TEXT NOT NULL,
    generator TEXT NOT NULL,
    severity TEXT NOT NULL,
    confidence TEXT NOT NULL,
    primary_triple_id TEXT,
    related_triple_ids TEXT,  -- JSON array
    bpmn_node_id TEXT,
    bpmn_edge_id TEXT,
    summary TEXT NOT NULL,
    detail TEXT,
    evidence_json TEXT,
    journeys_affected_count INTEGER DEFAULT 0,
    journeys_affected_pct REAL DEFAULT 0.0,
    is_on_critical_path INTEGER DEFAULT 0,
    status TEXT DEFAULT 'new',
    suppression_reason TEXT,
    first_seen_run TEXT NOT NULL,
    last_seen_run TEXT NOT NULL,
    occurrence_count INTEGER DEFAULT 1,
    first_detected_at TEXT NOT NULL,
    last_detected_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_findings_dedup ON findings(dedup_key);
CREATE INDEX IF NOT EXISTS idx_findings_triple ON findings(primary_triple_id);
CREATE INDEX IF NOT EXISTS idx_findings_class ON findings(defect_class);
CREATE INDEX IF NOT EXISTS idx_findings_generator ON findings(generator);

CREATE TABLE IF NOT EXISTS finding_occurrences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    finding_id TEXT NOT NULL REFERENCES findings(finding_id),
    run_id TEXT NOT NULL REFERENCES runs(run_id),
    detected_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_occurrences_finding ON finding_occurrences(finding_id);
CREATE INDEX IF NOT EXISTS idx_occurrences_run ON finding_occurrences(run_id);
