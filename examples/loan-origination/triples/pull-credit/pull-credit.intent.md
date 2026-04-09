---
intent_id: "INT-LO-CRC-001"
capsule_id: "CAP-LO-CRC-001"
bpmn_task_id: "Task_PullCredit"
version: "1.0"
status: "draft"
goal: "Obtain and parse a tri-merge credit report for the borrower, extracting representative credit scores and tradeline data for DTI assessment."
goal_type: "data_production"
preconditions:
  - "Borrower identity has been verified (identity_verification_result.status == 'verified')."
  - "A signed credit authorization form is on file in DocVault."
  - "Credit authorization is dated within 120 days."
inputs:
  - name: "borrower_profile"
    source: "LOS Database"
    schema_ref: "schemas/borrower-profile.json"
    required: true
  - name: "credit_authorization"
    source: "DocVault"
    schema_ref: "schemas/credit-auth.json"
    required: true
outputs:
  - name: "credit_report"
    type: "object"
    sink: "DocVault"
    invariants:
      - "credit_report contains data from at least 2 of 3 bureaus"
      - "credit_report.format == 'MISMO_XML'"
  - name: "representative_score"
    type: "integer"
    sink: "LOS Database"
    invariants:
      - "representative_score is between 300 and 850"
      - "representative_score follows GSE middle-score selection rules"
  - name: "tradeline_summary"
    type: "object"
    sink: "LOS Database"
invariants:
  - "Credit pull has a documented permissible purpose under FCRA."
  - "Borrower SSN is transmitted only over encrypted channels."
success_criteria:
  - "A tri-merge (or bi-merge with flag) credit report is stored in DocVault."
  - "Representative credit score is calculated and persisted to the loan file."
  - "Tradeline summary is available for DTI calculation."
failure_modes:
  - mode: "Credit freeze at one or more bureaus"
    detection: "CRA returns freeze indicator"
    action: "Notify loan officer, pause credit pull, request borrower to lift freeze"
  - mode: "All bureaus unavailable"
    detection: "All three CRA requests return error/timeout"
    action: "Retry after 30 minutes, escalate to operations if still unavailable"
  - mode: "Fraud alert on file"
    detection: "CRA response includes fraud_alert flag"
    action: "Route to fraud investigation team, halt loan processing"
contract_ref: "ICT-LO-CRC-001"
idempotency: "unsafe"
retry_policy: "fixed_delay, max_retries=2, delay=1800s"
timeout_seconds: 90
side_effects:
  - "Hard credit inquiry recorded on borrower's credit file"
  - "Credit report stored in DocVault"
  - "Publishes credit.report.received event"
execution_hints:
  preferred_agent: "credit-pull-service"
  tool_access:
    - "cra_integration_api"
    - "docvault_api"
    - "los_api"
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"
generated_from: "CAP-LO-CRC-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PIM"
---

# Intent: Pull Credit Report

## Goal

Obtain and parse a tri-merge credit report for the borrower, extracting representative credit scores and tradeline data for DTI assessment.

## Execution Notes

This is a service task with an external side effect (hard credit inquiry). It is NOT idempotent -- each invocation creates a new hard inquiry on the borrower's credit file. The agent must check for recent existing reports before initiating a new pull.
