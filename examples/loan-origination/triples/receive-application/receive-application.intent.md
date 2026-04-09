---
intent_id: "INT-LO-APP-001"
capsule_id: "CAP-LO-APP-001"
bpmn_task_id: "Task_ReceiveApplication"
version: "1.0"
status: "draft"
goal: "Capture and persist a validated residential mortgage loan application, producing a structured loan_application record and borrower_profile ready for identity verification."
goal_type: "state_transition"
preconditions:
  - "Borrower has submitted a completed or partially completed Uniform Residential Loan Application (URLA/1003)."
  - "The Loan Origination System (LOS) is available and accepting new applications."
  - "The intake channel (portal, branch, broker, phone) has been authenticated."
inputs:
  - name: "urla_form_data"
    source: "LOS Intake API"
    schema_ref: "schemas/urla-1003.json"
    required: true
  - name: "borrower_id_documents"
    source: "DocVault"
    schema_ref: "schemas/id-document.json"
    required: true
  - name: "property_info"
    source: "LOS Intake API"
    schema_ref: "schemas/property-info.json"
    required: true
outputs:
  - name: "loan_application"
    type: "object"
    sink: "LOS Database"
    invariants:
      - "loan_application.loan_number matches pattern LN-YYYY-NNNNNNN"
      - "loan_application.status == 'Application Received'"
      - "loan_application.hmda_fields are populated for reportable loans"
  - name: "borrower_profile"
    type: "object"
    sink: "LOS Database"
    invariants:
      - "borrower_profile.ssn is present and masked in all non-secure contexts"
      - "borrower_profile.ecoa_demographic_fields are captured"
  - name: "document_checklist"
    type: "array"
    sink: "LOS Database"
invariants:
  - "No application shall be rejected based on protected class characteristics."
  - "All PII is encrypted at rest and in transit."
success_criteria:
  - "A valid loan_application record exists in LOS with status 'Application Received'."
  - "A borrower_profile record is created and linked to the loan_application."
  - "The borrower receives an acknowledgment within 3 business days."
failure_modes:
  - mode: "Incomplete application data"
    detection: "Mandatory field validation fails on URLA form"
    action: "Set status to 'Pending - Incomplete', notify borrower of missing fields"
  - mode: "Duplicate application detected"
    detection: "SSN match found in LOS within 90-day window"
    action: "Flag for senior loan officer review, do not create new record"
  - mode: "LOS system unavailable"
    detection: "API returns 503 or connection timeout > 30s"
    action: "Queue in intake buffer, retry with exponential backoff, alert ops if > 4 hours"
contract_ref: "ICT-LO-APP-001"
idempotency: "safe"
retry_policy: "exponential_backoff, max_retries=3, base_delay=5s"
timeout_seconds: 120
side_effects:
  - "Creates a new loan record in LOS"
  - "Sends acknowledgment email/letter to borrower"
  - "Publishes application.received event to event bus"
execution_hints:
  preferred_agent: "loan-intake-service"
  tool_access:
    - "los_api"
    - "docvault_api"
    - "email_service"
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"
generated_from: "CAP-LO-APP-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PIM"
---

# Intent: Receive Loan Application

## Goal

Capture and persist a validated residential mortgage loan application, producing a structured `loan_application` record and `borrower_profile` ready for identity verification.

## Preconditions

- Borrower has submitted a completed or partially completed URLA (1003).
- The LOS is available and accepting new applications.
- The intake channel has been authenticated.

## Execution Notes

This intent represents the entry point of the loan origination process. The executing agent must validate mandatory fields per the URLA specification, check for duplicates, and generate the initial loan file. All HMDA-reportable fields must be captured at this stage. The agent must not make any credit decisions or eligibility assessments at this stage.
