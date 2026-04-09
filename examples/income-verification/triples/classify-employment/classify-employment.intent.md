---
intent_id: "INT-IV-CLS-001"
capsule_id: "CAP-IV-CLS-001"
bpmn_task_id: "Task_ClassifyEmployment"
version: "1.0"
status: "draft"
goal: "Classify the borrower's employment type to determine the correct income verification path, ensuring the appropriate documentation requirements and calculation methods are applied."
goal_type: "decision"
preconditions:
  - "The borrower_profile data object is populated with at least one employment history record."
  - "Employment records include employmentType, startDate, and statedMonthlyIncome."
  - "The RuleEngine service is accessible for executing classification decision tables."
inputs:
  - name: "borrower_profile"
    source: "Process Context"
    schema_ref: "schemas/borrower-profile.json"
    required: true
  - name: "borrower_profile.employmentHistory"
    source: "Process Context"
    schema_ref: "schemas/employment-history.json"
    required: true
  - name: "loanProgram"
    source: "Process Context"
    schema_ref: "schemas/loan-program.json"
    required: true
outputs:
  - name: "employmentType"
    type: "string"
    sink: "Process Variable"
    invariants:
      - "employmentType is exactly W2 or SELF_EMPLOYED"
  - name: "employmentClassification"
    type: "string"
    sink: "Process Context"
    invariants:
      - "employmentClassification is one of W2_STABLE, W2_NEW, SELF_EMPLOYED_ESTABLISHED, HYBRID"
  - name: "primaryIncomeSource"
    type: "object"
    sink: "Process Context"
  - name: "manualReviewRequired"
    type: "boolean"
    sink: "Process Context"
invariants:
  - "Every borrower MUST be classified into exactly one employment type for gateway routing."
  - "Borrowers with 25%+ ownership in a business MUST be classified as SELF_EMPLOYED regardless of whether they also receive W-2 wages from that business."
  - "The classification MUST consider the most recent 24 months of employment history."
  - "If no employment records exist, classification MUST fail with an error rather than defaulting."
success_criteria:
  - "The employmentType process variable is set to W2 or SELF_EMPLOYED."
  - "The employmentClassification detail is recorded in the process context."
  - "Edge cases are flagged for manual review."
failure_modes:
  - mode: "No employment records"
    detection: "borrower_profile has zero employment records"
    action: "Halt process; return to LOS for borrower data correction"
  - mode: "Ambiguous classification"
    detection: "Employment records conflict (e.g., overlapping full-time W-2 positions)"
    action: "Flag for manual review; do not auto-classify"
  - mode: "RuleEngine service unavailable"
    detection: "RuleEngine API returns 503 or connection timeout"
    action: "Retry with exponential backoff (max 3 attempts); escalate to underwriter if still down"
contract_ref: "ICT-IV-CLS-001"
idempotency: "safe"
retry_policy: "exponential_backoff, max_retries=3, base_delay=5s"
timeout_seconds: 60
side_effects:
  - "Sets employmentType process variable for gateway routing"
execution_hints:
  preferred_agent: "income-verification-service"
  tool_access:
    - "rule_engine_api"
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"
generated_from: "CAP-IV-CLS-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PIM"
gaps:
  - type: "missing_detail"
    description: "HYBRID borrowers require parallel gateway for dual verification paths"
    severity: "medium"
---

# Intent: Classify Employment Type

## Goal

Classify the borrower's employment type to determine the correct income verification path, ensuring the appropriate documentation requirements and calculation methods are applied.

## Preconditions

- The `borrower_profile` data object is populated with at least one employment history record.
- Employment records include `employmentType`, `startDate`, and `statedMonthlyIncome`.
- The RuleEngine service is accessible for executing classification decision tables.

## Execution Notes

This intent evaluates the borrower's employment history against agency-specific classification rules. The executing agent must not default to W2 if classification is ambiguous, must not skip ownership percentage evaluation when available, and must not classify borrowers with only pension/retirement income as W2 or SELF_EMPLOYED (those require a retirement income path out of scope for this process).
