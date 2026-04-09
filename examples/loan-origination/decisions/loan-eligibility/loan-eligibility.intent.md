---
intent_id: "INT-LO-DEC-001"
capsule_id: "CAP-LO-DEC-001"
bpmn_task_id: "Gateway_Eligible"
version: "1.0"
status: "draft"
goal: "Determine the processing path based on DTI eligibility and documentation completeness, routing to either loan packaging or documentation request."
goal_type: "decision"
preconditions:
  - "DTI assessment has been completed (dti_result exists in loan file)."
  - "dti_result contains eligible and docs_complete boolean fields."
inputs:
  - name: "dti_result"
    source: "LOS Database"
    schema_ref: "schemas/dti-result.json"
    required: true
outputs:
  - name: "routing_decision"
    type: "string"
    sink: "Process Engine"
    invariants:
      - "routing_decision in ['package_loan', 'request_docs']"
invariants:
  - "Decision is deterministic and based solely on dti_result data."
  - "No manual override path exists at this gateway."
success_criteria:
  - "Exactly one outgoing path is selected."
  - "Decision is logged with conditions evaluated."
failure_modes:
  - mode: "Missing dti_result data"
    detection: "dti_result record not found in loan file"
    action: "Halt processing, escalate to operations as data integrity issue"
  - mode: "Ambiguous dti_result values"
    detection: "eligible or docs_complete fields are null or undefined"
    action: "Route to manual review by senior processor"
contract_ref: "ICT-LO-DEC-001"
idempotency: "safe"
timeout_seconds: 5
generated_from: "CAP-LO-DEC-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PIM"
---

# Intent: Loan Eligibility Decision

## Goal

Determine the processing path based on DTI eligibility and documentation completeness.

## Decision Table

| dti_result.eligible | dti_result.docs_complete | Route |
|---|---|---|
| true | true | Package Loan File |
| true | false | Request Additional Documentation |
| false | true | Request Additional Documentation |
| false | false | Request Additional Documentation |
