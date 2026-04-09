---
intent_id: "INT-LO-TMO-001"
capsule_id: "CAP-LO-TMO-001"
bpmn_task_id: "Boundary_Timeout"
version: "1.0"
status: "draft"
goal: "Handle the documentation request timeout by withdrawing the application, issuing required notices, and closing the loan file."
goal_type: "state_transition"
preconditions:
  - "The 14-day documentation request timer has expired."
  - "The borrower has not submitted all requested documents."
  - "The Task_RequestDocs task is still active (will be cancelled by this boundary event)."
inputs:
  - name: "document_request_record"
    source: "LOS Database"
    schema_ref: "schemas/doc-request-record.json"
    required: true
  - name: "loan_application"
    source: "LOS Database"
    schema_ref: "schemas/loan-application.json"
    required: true
  - name: "borrower_contact"
    source: "LOS Database"
    schema_ref: "schemas/borrower-contact.json"
    required: true
outputs:
  - name: "withdrawal_record"
    type: "object"
    sink: "LOS Database"
    invariants:
      - "withdrawal_record.reason == 'Documentation Timeout'"
      - "withdrawal_record.timestamp is set to timeout fire time"
  - name: "adverse_action_notice"
    type: "object"
    sink: "Borrower (mail)"
    invariants:
      - "adverse_action_notice issued within 30 days if application was complete"
  - name: "borrower_notification"
    type: "object"
    sink: "Borrower (email/mail)"
invariants:
  - "HMDA reporting fields are preserved for reportable applications."
  - "Fair lending monitoring data is logged."
success_criteria:
  - "Loan status is updated to 'Withdrawn - Documentation Timeout'."
  - "Borrower receives withdrawal notification."
  - "Adverse action notice is generated if applicable."
  - "Loan file is closed and archived."
failure_modes:
  - mode: "Race condition with document upload"
    detection: "Documents received after timer fired but before event processed"
    action: "Check document timestamps; if received before timer processing, cancel withdrawal"
  - mode: "Adverse action notice generation failure"
    detection: "Notice template rendering or delivery fails"
    action: "Escalate to compliance for manual notice within 24 hours"
contract_ref: "ICT-LO-TMO-001"
idempotency: "unsafe"
timeout_seconds: 120
side_effects:
  - "Cancels the active documentation request task"
  - "Updates loan status to withdrawn"
  - "May trigger adverse action notice"
  - "Publishes loan.application.withdrawn event"
execution_hints:
  preferred_agent: "loan-lifecycle-service"
  tool_access:
    - "los_api"
    - "email_service"
    - "compliance_api"
    - "notice_generator"
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"
generated_from: "CAP-LO-TMO-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PIM"
---

# Intent: Timeout - No Response

## Goal

Handle the documentation request timeout by withdrawing the application, issuing required notices, and closing the loan file.

## Execution Notes

This is a boundary timer event (cancelActivity=true) attached to Task_RequestDocs. When it fires, the documentation request task is cancelled and this exception path executes. The agent must check for race conditions where documents arrived just before the timer fired.
