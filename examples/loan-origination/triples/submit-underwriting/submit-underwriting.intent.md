---
intent_id: "INT-LO-SUB-001"
capsule_id: "CAP-LO-SUB-001"
bpmn_task_id: "Task_SubmitUW"
version: "1.0"
status: "draft"
goal: "Submit the completed loan file package to the appropriate underwriting queue, establishing the formal handoff from origination to underwriting."
goal_type: "notification"
preconditions:
  - "Loan file package exists with qc_status == 'pass'."
  - "All required documents are present and current."
  - "Processor cover memo is attached."
inputs:
  - name: "packaged_loan_file"
    source: "LOS Database"
    schema_ref: "schemas/loan-package.json"
    required: true
  - name: "qc_checklist_result"
    source: "LOS Database"
    schema_ref: "schemas/qc-result.json"
    required: true
  - name: "rate_lock_info"
    source: "LOS Database"
    schema_ref: "schemas/rate-lock.json"
    required: false
outputs:
  - name: "underwriting_submission"
    type: "object"
    sink: "Underwriting Queue"
    invariants:
      - "underwriting_submission.queue is assigned based on product type and complexity"
      - "underwriting_submission.priority reflects lock expiration and contract deadlines"
  - name: "submission_confirmation"
    type: "object"
    sink: "LOS Database"
    invariants:
      - "submission_confirmation.expected_turnaround_hours > 0"
invariants:
  - "Only QC-passed files may be submitted."
  - "Loan status transitions to 'Submitted to Underwriting'."
success_criteria:
  - "Loan file is placed in the correct underwriting queue."
  - "Loan officer receives submission confirmation with expected turnaround."
  - "Loan status is updated to 'Submitted to Underwriting'."
failure_modes:
  - mode: "QC failure at final validation"
    detection: "QC status is not 'pass' at submission time"
    action: "Reject submission, return to processor with deficiency details"
  - mode: "Underwriting queue unavailable"
    detection: "Queue service returns error or all queues at capacity"
    action: "Hold in pre-submission buffer, alert underwriting management"
  - mode: "Rate lock expiring within 5 days"
    detection: "rate_lock_info.expiration_date - today < 5 days"
    action: "Escalate priority, notify underwriting manager"
contract_ref: "ICT-LO-SUB-001"
idempotency: "safe"
timeout_seconds: 60
side_effects:
  - "Enqueues loan file in underwriting queue"
  - "Sends notification to loan officer and optionally borrower"
  - "Publishes loan.submitted.underwriting event"
execution_hints:
  preferred_agent: "uw-submission-service"
  tool_access:
    - "los_api"
    - "uw_queue_api"
    - "email_service"
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"
generated_from: "CAP-LO-SUB-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PIM"
---

# Intent: Submit to Underwriting

## Goal

Submit the completed loan file package to the appropriate underwriting queue, establishing the formal handoff from origination to underwriting.

## Execution Notes

This is the terminal task of the loan origination process. After this task, the loan enters the underwriting process (a separate BPMN process). The send task places the file into the underwriting queue and triggers notifications.
