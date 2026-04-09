---
intent_id: "INT-LO-IDV-001"
capsule_id: "CAP-LO-IDV-001"
bpmn_task_id: "Task_VerifyIdentity"
version: "1.0"
status: "draft"
goal: "Verify the borrower's identity against government records and sanctions lists, producing a verified or flagged identity status for the loan file."
goal_type: "data_production"
preconditions:
  - "A loan_application record exists in LOS with status 'Application Received'."
  - "A borrower_profile record is available with SSN, name, DOB, and address."
  - "Government-issued ID document has been uploaded to DocVault."
inputs:
  - name: "borrower_profile"
    source: "LOS Database"
    schema_ref: "schemas/borrower-profile.json"
    required: true
  - name: "government_id_image"
    source: "DocVault"
    schema_ref: "schemas/id-document.json"
    required: true
outputs:
  - name: "identity_verification_result"
    type: "object"
    sink: "LOS Database"
    invariants:
      - "identity_verification_result.status in ['verified', 'manual_review', 'failed', 'ofac_match']"
      - "identity_verification_result.confidence_score is between 0 and 1000"
      - "identity_verification_result.data_sources_count >= 2"
  - name: "ofac_screening_result"
    type: "object"
    sink: "LOS Database"
    invariants:
      - "ofac_screening_result.status in ['clear', 'match', 'potential_match']"
  - name: "cip_compliance_record"
    type: "object"
    sink: "Compliance Database"
invariants:
  - "Borrower SSN is never logged in plaintext."
  - "OFAC match results in immediate process halt."
success_criteria:
  - "Identity verification result is persisted to the loan file."
  - "OFAC screening is completed and recorded."
  - "CIP compliance record is created with all required fields."
failure_modes:
  - mode: "OFAC SDN list match"
    detection: "Sanctions screening returns status 'match'"
    action: "Halt all loan processing, escalate to BSA/AML officer, create SAR referral"
  - mode: "Identity verification service timeout"
    detection: "Service does not respond within 30 seconds"
    action: "Retry up to 3 times with exponential backoff, then queue for manual processing"
  - mode: "Document authentication failure"
    detection: "ID document fails forgery detection checks"
    action: "Flag for manual review, notify loan officer"
contract_ref: "ICT-LO-IDV-001"
idempotency: "safe"
retry_policy: "exponential_backoff, max_retries=3, base_delay=10s"
timeout_seconds: 60
side_effects:
  - "Creates CIP compliance record"
  - "May trigger SAR referral on OFAC match"
  - "Publishes identity.verified or identity.flagged event"
execution_hints:
  preferred_agent: "identity-verification-service"
  tool_access:
    - "idv_api"
    - "ofac_screening_api"
    - "docvault_api"
    - "los_api"
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"
generated_from: "CAP-LO-IDV-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PIM"
---

# Intent: Verify Borrower Identity

## Goal

Verify the borrower's identity against government records and sanctions lists, producing a verified or flagged identity status for the loan file.

## Preconditions

- A loan application has been received and a borrower profile exists.
- Government-issued identification has been uploaded.

## Execution Notes

This is an automated service task. The executing agent must call external identity verification and sanctions screening APIs. OFAC matches are treated as critical exceptions that halt all processing. The agent must ensure at least two independent data sources confirm the identity before marking as verified.
