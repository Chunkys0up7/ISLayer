---
intent_id: "INT-LO-DTI-001"
capsule_id: "CAP-LO-DTI-001"
bpmn_task_id: "Task_AssessDTI"
version: "1.0"
status: "draft"
goal: "Calculate front-end and back-end DTI ratios using verified income and credit data, producing an eligibility determination with documentation completeness status."
goal_type: "decision"
preconditions:
  - "A credit report has been obtained and parsed (credit_report record exists)."
  - "Borrower income data is available in the loan application."
  - "Representative credit score has been calculated."
inputs:
  - name: "loan_application"
    source: "LOS Database"
    schema_ref: "schemas/loan-application.json"
    required: true
  - name: "credit_report"
    source: "LOS Database"
    schema_ref: "schemas/credit-summary.json"
    required: true
  - name: "borrower_profile"
    source: "LOS Database"
    schema_ref: "schemas/borrower-profile.json"
    required: true
  - name: "income_documentation_status"
    source: "DocVault"
    schema_ref: "schemas/doc-checklist-status.json"
    required: true
outputs:
  - name: "dti_result"
    type: "object"
    sink: "LOS Database"
    invariants:
      - "dti_result.front_end_ratio is a decimal between 0.0 and 1.0"
      - "dti_result.back_end_ratio is a decimal between 0.0 and 1.0"
      - "dti_result.eligible is a boolean"
      - "dti_result.docs_complete is a boolean"
      - "dti_result.qm_compliant is a boolean"
invariants:
  - "DTI calculations follow GSE selling guide methodology."
  - "QM compliance check is always performed regardless of loan type."
success_criteria:
  - "Both front-end and back-end DTI ratios are calculated and persisted."
  - "Eligibility determination is made based on applicable product thresholds."
  - "Documentation completeness is assessed and flagged."
failure_modes:
  - mode: "Missing income documentation"
    detection: "DocVault checklist shows required income docs not uploaded"
    action: "Set docs_complete=false, include missing_documents list in dti_result"
  - mode: "Zero or negative calculated income"
    detection: "Gross monthly income calculation returns <= 0"
    action: "Flag for manual underwriter review, set eligible=false"
  - mode: "Rule engine unavailable"
    detection: "DTI rule engine returns error or timeout"
    action: "Retry up to 3 times, then escalate to operations"
contract_ref: "ICT-LO-DTI-001"
idempotency: "safe"
retry_policy: "exponential_backoff, max_retries=3, base_delay=5s"
timeout_seconds: 30
side_effects:
  - "Persists DTI results to loan file"
  - "Publishes loan.dti.assessed event"
execution_hints:
  preferred_agent: "dti-calculation-engine"
  tool_access:
    - "los_api"
    - "docvault_api"
    - "dti_rule_engine"
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"
generated_from: "CAP-LO-DTI-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PIM"
gaps:
  - type: "missing_detail"
    description: "Self-employment income calculation procedure not fully specified"
    severity: "high"
---

# Intent: Assess Debt-to-Income Ratio

## Goal

Calculate front-end and back-end DTI ratios using verified income and credit data, producing an eligibility determination with documentation completeness status.

## Execution Notes

This is a business rule task. The DTI calculation engine applies product-specific thresholds (conventional, FHA, VA) and QM compliance rules. The output `docs_complete` flag drives the downstream gateway decision on whether to request additional documentation or proceed to packaging.
