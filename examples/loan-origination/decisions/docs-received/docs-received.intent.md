---
intent_id: "INT-LO-DEC-002"
capsule_id: "CAP-LO-DEC-002"
bpmn_task_id: "Gateway_DocsReceived"
version: "1.0"
status: "draft"
goal: "Determine whether the borrower has submitted all requested documentation, routing to DTI re-assessment or application rejection."
goal_type: "decision"
preconditions:
  - "A documentation request has been sent to the borrower."
  - "The documentation request deadline has passed or all documents have been received."
inputs:
  - name: "document_submission_status"
    source: "DocVault"
    schema_ref: "schemas/doc-submission-status.json"
    required: true
  - name: "document_request_record"
    source: "LOS Database"
    schema_ref: "schemas/doc-request-record.json"
    required: true
outputs:
  - name: "routing_decision"
    type: "string"
    sink: "Process Engine"
    invariants:
      - "routing_decision in ['reassess_dti', 'reject_application']"
invariants:
  - "Partial submissions are treated as incomplete unless all critical items are present."
success_criteria:
  - "Exactly one outgoing path is selected."
  - "Decision is logged with document submission details."
failure_modes:
  - mode: "DocVault unavailable"
    detection: "DocVault API returns error or timeout"
    action: "Retry up to 3 times, then hold decision and alert operations"
  - mode: "Ambiguous submission status"
    detection: "Some but not all documents received"
    action: "Evaluate against critical items list; if all critical items present, treat as received"
contract_ref: "ICT-LO-DEC-002"
idempotency: "safe"
timeout_seconds: 10
generated_from: "CAP-LO-DEC-002"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PIM"
execution_hints:
  forbidden_actions:
    - browser_automation
    - screen_scraping
    - ui_click
    - rpa_style_macros
---

# Intent: Docs Received Decision

## Goal

Determine whether the borrower has submitted all requested documentation, routing to DTI re-assessment or application rejection.

## Decision Table

| All requested docs received | Route |
|---|---|
| Yes | Re-assess DTI (loop back to Task_AssessDTI) |
| No | Reject Application (End_Rejected) |
