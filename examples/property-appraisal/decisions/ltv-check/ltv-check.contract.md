---
contract_id: "ICT-PA-DEC-002"
contract_name: "LTV Decision Binding"
bpmn_task_id: "Gateway_LTV"
bpmn_task_name: "Value Within LTV?"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"

version: "1.0.0"
status: "draft"
mda_layer: "PSM"

generated_from: "CAP-PA-DEC-002 + INT-PA-DEC-002"
generated_date: "2026-04-09"
generated_by: "mda-pipeline"
last_modified: "2026-04-09"
last_modified_by: "mda-pipeline"

owner_role: "Integration Architect"
owner_team: "Mortgage Technology"
reviewers:
  - "Underwriting Manager"
  - "Risk Officer"

domain: "Mortgage"
subdomain: "Property Appraisal"

capsule_id: "CAP-PA-DEC-002"
intent_id: "INT-PA-DEC-002"

binding_status: "unbound"

input_schema:
  - name: "ltv_ratio"
    type: "float"
    required: true
    description: "Calculated LTV ratio."
    source: "Task_AssessValue"
    constraints: "min: 0, max: 200"
  - name: "ltv_determination"
    type: "string"
    required: true
    description: "LTV threshold comparison result."
    source: "Task_AssessValue"
    constraints: "enum: [Within_LTV, Exceeds_LTV]"

output_schema:
  - name: "routing_target"
    type: "string"
    required: true
    description: "The downstream task to activate."
    destination: "Process Engine"
    constraints: "enum: [Task_EmitComplete, Task_ManualReview]"

error_codes:
  - code: "ERR-PA-DEC-002"
    name: "Unknown LTV Determination"
    severity: "critical"
    description: "The LTV determination is not a recognized value."
    resolution: "Halt processing and escalate to underwriting manager."

max_latency_ms: 1000
throughput: "1000 decisions/hour"
availability: "99.9%"

min_capsule_version: "1.0.0"
min_intent_version: "1.0.0"
breaking_changes: []

gaps: []
---

# LTV Decision Binding

## Binding Rationale

This contract binds **LTV Decision Gateway** (`CAP-PA-DEC-002`) to **Route Based on LTV Threshold** (`INT-PA-DEC-002`).

The binding ensures the gateway receives a well-typed LTV determination and produces a deterministic routing output. Without this contract, the gateway could receive malformed determination values, leading to process deadlocks or misrouting.

**Key guarantees:**

- The input determination is constrained to exactly two valid values.
- The output target maps deterministically to one of two downstream tasks.
- Unknown determination values trigger an error rather than silent failure.

## Change Protocol

1. **Non-breaking changes** (MINOR/PATCH): Documentation updates only.
2. **Breaking changes** (MAJOR): Adding new determination values or routing targets.

## Decommissioning

This contract may be decommissioned when the gateway is removed. **Data retention:** 7 years per mortgage regulatory requirements.
