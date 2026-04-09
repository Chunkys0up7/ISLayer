---
intent_id: "INT-LO-DOC-001"
capsule_id: "CAP-LO-DOC-001"
bpmn_task_id: "Task_RequestDocs"
version: "1.0"
status: "draft"
goal: "Send a formal documentation request to the borrower listing all missing items with a secure upload link and a 14-day response deadline."
goal_type: "notification"
preconditions:
  - "DTI assessment has been completed with dti_result.docs_complete == false."
  - "The missing_documents list in dti_result is non-empty."
  - "Borrower contact information is available in the loan file."
inputs:
  - name: "dti_result"
    source: "LOS Database"
    schema_ref: "schemas/dti-result.json"
    required: true
  - name: "borrower_contact"
    source: "LOS Database"
    schema_ref: "schemas/borrower-contact.json"
    required: true
  - name: "document_request_template"
    source: "Template Library"
    schema_ref: "schemas/doc-request-template.json"
    required: true
outputs:
  - name: "document_request_record"
    type: "object"
    sink: "LOS Database"
    invariants:
      - "document_request_record.items_requested is non-empty"
      - "document_request_record.deadline is 14 calendar days from request_date"
      - "document_request_record.request_count <= 3"
  - name: "secure_upload_link"
    type: "string"
    sink: "Borrower (email/portal)"
    invariants:
      - "secure_upload_link expires within 30 days"
      - "secure_upload_link is single-use per document"
invariants:
  - "Communication must not disclose internal eligibility reasoning."
  - "Maximum 3 documentation requests per loan."
success_criteria:
  - "Document request is delivered to borrower via at least one channel."
  - "Secure upload link is generated and included in the request."
  - "Loan status is updated to 'Pending Documentation'."
failure_modes:
  - mode: "All delivery channels fail"
    detection: "Email bounces, portal delivery fails, no physical address on file"
    action: "Notify loan officer for manual follow-up within 1 business day"
  - mode: "Maximum request count exceeded"
    detection: "document_request_record.request_count > 3"
    action: "Escalate to supervisor for loan disposition decision"
contract_ref: "ICT-LO-DOC-001"
idempotency: "unsafe"
timeout_seconds: 60
side_effects:
  - "Sends notification to borrower"
  - "Updates loan status to 'Pending Documentation'"
  - "Publishes loan.docs.requested event"
  - "Starts 14-day timeout timer (Boundary_Timeout)"
execution_hints:
  preferred_agent: "notification-service"
  tool_access:
    - "los_api"
    - "email_service"
    - "portal_api"
    - "template_engine"
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"
generated_from: "CAP-LO-DOC-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PIM"
---

# Intent: Request Additional Documentation

## Goal

Send a formal documentation request to the borrower listing all missing items with a secure upload link and a 14-day response deadline.

## Execution Notes

This is a send task that triggers borrower-facing communication. The 14-day timer boundary event (Boundary_Timeout) is attached to this task. If the borrower does not respond within 14 days, the timeout fires and the application is rejected.
