---
contract_id: "ICT-PA-DEC-001"
contract_name: "Completeness Decision Binding"
bpmn_task_id: "Gateway_Complete"
bpmn_task_name: "Complete?"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"

version: "1.0.0"
status: "draft"

generated_from: "CAP-PA-DEC-001 + INT-PA-DEC-001"
generated_date: "2026-04-09"
generated_by: "mda-pipeline"
last_modified: "2026-04-09"
last_modified_by: "mda-pipeline"

owner_role: "Integration Architect"
owner_team: "Mortgage Technology"
reviewers:
  - "Chief Appraiser"
  - "API Platform Lead"

domain: "Mortgage"
subdomain: "Property Appraisal"

capsule_id: "CAP-PA-DEC-001"
intent_id: "INT-PA-DEC-001"

binding_status: "unbound"

input_schema:
  - name: "completeness_status"
    type: "string"
    required: true
    description: "Result of the completeness validation."
    source: "Task_ValidateCompleteness"
    constraints: "enum: [Complete, Incomplete]"
  - name: "deficiency_codes"
    type: "array"
    required: false
    description: "List of deficiency codes if status is Incomplete."
    source: "Task_ValidateCompleteness"
    constraints: ""

output_schema:
  - name: "routing_target"
    type: "string"
    required: true
    description: "The downstream task to activate."
    destination: "Process Engine"
    constraints: "enum: [Task_AssessValue, Task_RequestRevision]"

error_codes:
  - code: "ERR-PA-DEC-001"
    name: "Unknown Completeness Status"
    severity: "critical"
    description: "The completeness status is not a recognized value."
    resolution: "Halt processing and escalate to appraisal desk."

max_latency_ms: 1000
throughput: "1000 decisions/hour"
availability: "99.9%"

min_capsule_version: "1.0.0"
min_intent_version: "1.0.0"
breaking_changes: []

gaps: []
---

# Completeness Decision Binding

## Binding Rationale

This contract binds **Completeness Decision Gateway** (`CAP-PA-DEC-001`) to **Route Based on Appraisal Completeness** (`INT-PA-DEC-001`).

The binding ensures the gateway receives a well-typed completeness status and produces a deterministic routing output. Without this contract, the gateway could receive malformed status values, leading to process deadlocks.

**Key guarantees:**

- The input status is constrained to exactly two valid values.
- The output target maps deterministically to one of two downstream tasks.
- Unknown status values trigger an error rather than silent failure.

## Change Protocol

1. **Non-breaking changes** (MINOR/PATCH): Documentation updates only.
2. **Breaking changes** (MAJOR): Adding new status values or routing targets. Must coordinate with all upstream and downstream triples.

## Decommissioning

This contract may be decommissioned when the gateway is removed. **Data retention:** 7 years per mortgage regulatory requirements.
