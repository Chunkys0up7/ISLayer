---
intent_id: "INT-IV-REQ-001"
capsule_id: "CAP-IV-REQ-001"
bpmn_task_id: "Task_ReceiveRequest"
version: "1.0"
status: "draft"
goal: "Accept and validate an income verification request from the Loan Origination System so that only well-formed, actionable requests enter the verification pipeline."
goal_type: "state_transition"
preconditions:
  - "The message broker channel income.verification.requests is active and accessible."
  - "The LOS has submitted a verification request containing a valid loanApplicationId."
  - "At least one income document (W-2 or tax return) has been uploaded to DocVault for the borrower."
  - "The requesting principal has the ROLE_UNDERWRITER or ROLE_SYSTEM authorization."
inputs:
  - name: "loanApplicationId"
    source: "LOS"
    schema_ref: "schemas/verification-request.json"
    required: true
  - name: "borrowerId"
    source: "LOS"
    schema_ref: "schemas/verification-request.json"
    required: true
  - name: "requestedBy"
    source: "LOS"
    schema_ref: "schemas/verification-request.json"
    required: true
  - name: "documentRefs"
    source: "LOS"
    schema_ref: "schemas/verification-request.json"
    required: true
  - name: "loanProgram"
    source: "LOS"
    schema_ref: "schemas/verification-request.json"
    required: true
outputs:
  - name: "borrower_profile"
    type: "object"
    sink: "Process Context"
    invariants:
      - "borrower_profile contains employment history and stated income"
      - "borrower_profile.ssnMasked is present and masked in all non-secure contexts"
  - name: "acknowledgement"
    type: "object"
    sink: "LOS"
    invariants:
      - "acknowledgement contains correlationId and estimatedCompletionSeconds"
  - name: "validation_errors"
    type: "array"
    sink: "LOS"
invariants:
  - "Every accepted request MUST have a non-empty loanApplicationId and borrowerId."
  - "At least one document reference MUST resolve to an existing DocVault object with status AVAILABLE or VERIFIED."
  - "The loanProgram field MUST be one of the supported enum values. Unknown programs are rejected."
  - "All PII field access MUST generate an audit log entry."
success_criteria:
  - "A valid verification request is accepted and borrower_profile is populated in the process context."
  - "An acknowledgement event is published back to the LOS with correlation ID."
  - "Invalid requests are rejected with appropriate error codes."
failure_modes:
  - mode: "Required fields missing or malformed"
    detection: "Request payload validation fails"
    action: "Return ERR_REQ_INVALID with field-level errors; do not proceed"
  - mode: "All documents unavailable"
    detection: "All document references have status other than AVAILABLE/VERIFIED"
    action: "Return ERR_REQ_DOC_UNAVAILABLE; notify originator to upload documents"
  - mode: "Borrower not found"
    detection: "borrowerId does not exist in LOS"
    action: "Return ERR_REQ_BORROWER_NOT_FOUND; log discrepancy for reconciliation"
  - mode: "Unauthorized request"
    detection: "Requesting principal lacks required role"
    action: "Return ERR_REQ_UNAUTHORIZED; log unauthorized access attempt"
contract_ref: "ICT-IV-REQ-001"
idempotency: "safe"
retry_policy: "exponential_backoff, max_retries=3, base_delay=5s"
timeout_seconds: 120
side_effects:
  - "Publishes VerificationRequestAcknowledged event to LOS"
  - "Fetches borrower profile from LOS Borrower API"
  - "Checks document status in DocVault"
execution_hints:
  preferred_agent: "income-verification-service"
  tool_access:
    - "los_borrower_api"
    - "docvault_api"
    - "message_broker"
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"
generated_from: "CAP-IV-REQ-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PIM"
gaps: []
---

# Intent: Receive Verification Request

## Goal

Accept and validate an income verification request from the Loan Origination System so that only well-formed, actionable requests enter the verification pipeline.

## Preconditions

- The message broker channel `income.verification.requests` is active and accessible.
- The LOS has submitted a verification request containing a valid `loanApplicationId`.
- At least one income document (W-2 or tax return) has been uploaded to DocVault for the borrower.
- The requesting principal has the `ROLE_UNDERWRITER` or `ROLE_SYSTEM` authorization.

## Execution Notes

This intent represents the entry point of the income verification process. The executing agent must validate mandatory fields, confirm document availability in DocVault, and retrieve the borrower profile from the LOS. The agent must not make any income calculations or classification decisions at this stage. All PII access must be logged per GLBA requirements.
