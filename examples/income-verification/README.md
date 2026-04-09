# Income Verification -- MDA Demo

This example demonstrates the MDA Intent Layer framework applied to a residential mortgage income verification process.

## Process Overview

The Income Verification process validates a borrower's reported income against IRS documentation as part of mortgage underwriting. It supports two verification paths:

- **W-2 Employee Path**: Cross-references W-2 wage statements against IRS Form 1040 transcripts
- **Self-Employment Path**: Applies Fannie Mae Form 1084 cash flow analysis to Schedule C/K-1 data

The process terminates with either a verified income event (published to the underwriting event bus) or a variance exception when stated income deviates from verified income beyond program-specific thresholds.

## Directory Structure

```
income-verification/
  bpmn/
    income-verification.bpmn    # BPMN 2.0 process definition
    bpmn-metadata.yaml          # Extracted process metadata
  triples/
    _manifest.json              # Process-level triple registry
    receive-request/            # ICT-IV-REQ-001
    classify-employment/        # ICT-IV-CLS-001
    verify-w2/                  # ICT-IV-W2V-001
    verify-self-employment/     # ICT-IV-SEI-001
    calc-qualifying/            # ICT-IV-QAL-001
    emit-verified/              # ICT-IV-NTF-001
  decisions/
    employment-type/            # ICT-IV-DEC-001
    variance-threshold/         # ICT-IV-DEC-002
  graph/
    process-graph.yaml          # Machine-readable process graph
    graph-visual.md             # Mermaid visualization
  gaps/
    GAP-001.md                  # Identified process gaps
  audit/
    ingestion-log.yaml          # Ingestion audit trail
    change-log.yaml             # Version history
  mda.config.yaml               # MDA Intent Layer project configuration
```

## Triple Structure

Each task and decision point has a triple consisting of:

| File | Purpose |
|---|---|
| `.cap.md` | **Capability** -- What the task does and how (procedure, regulatory context) |
| `.intent.md` | **Intent** -- Why the task exists (goal, preconditions, invariants, failure modes) |
| `.contract.md` | **Integration Contract** -- How the task connects to external systems (APIs, schemas) |

## Capability IDs

| ID | Element | Type |
|---|---|---|
| ICT-IV-REQ-001 | Receive Verification Request | receiveTask |
| ICT-IV-CLS-001 | Classify Employment Type | businessRuleTask |
| ICT-IV-W2V-001 | Verify W-2 Income | serviceTask |
| ICT-IV-SEI-001 | Verify Self-Employment Income | serviceTask |
| ICT-IV-QAL-001 | Calculate Qualifying Income | businessRuleTask |
| ICT-IV-NTF-001 | Emit Income Verified Event | sendTask |
| ICT-IV-DEC-001 | Employment Type Gateway | exclusiveGateway |
| ICT-IV-DEC-002 | Variance Threshold Gateway | exclusiveGateway |

## Integrated Systems

| System | Role |
|---|---|
| LOS | Loan Origination System -- source of borrower data and loan applications |
| DocVault | Document storage with OCR extraction for W-2s, tax returns, schedules |
| RuleEngine | DMN-compatible engine for classification, cash flow analysis, and aggregation |
| Event Bus | Kafka-based event streaming for underwriting domain events |
| IVES | IRS Income Verification Express Service for transcript retrieval |

## Binding Status

All 8 triples are currently **unbound** -- integration contracts define the expected API shapes but are not yet connected to running services.

## Known Gaps

- **GAP-001**: Missing VOE fallback procedure for gig economy workers
