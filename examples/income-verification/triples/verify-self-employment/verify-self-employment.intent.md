---
intent_id: "INT-IV-SEI-001"
capsule_id: "CAP-IV-SEI-001"
bpmn_task_id: "Task_VerifySelfEmployment"
version: "1.0"
status: "draft"
goal: "Verify self-employment income through IRS tax return analysis and Fannie Mae cash flow methodology to produce a reliable monthly qualifying income figure."
goal_type: "computation"
preconditions:
  - "The borrower has been classified as SELF_EMPLOYED or HYBRID."
  - "IRS Form 1040 returns with applicable schedules (C, E, K-1) for the most recent 2 tax years are in DocVault."
  - "If the borrower owns 25%+ of a corporation, corporate tax returns (1120/1120-S) are available."
  - "Structured data extraction from tax documents has completed with confidence >= 0.90."
inputs:
  - name: "borrower_profile"
    source: "Process Context"
    schema_ref: "schemas/borrower-profile.json"
    required: true
  - name: "tax_returns"
    source: "DocVault"
    schema_ref: "schemas/tax-return-schedules.json"
    required: true
  - name: "corporate_returns"
    source: "DocVault"
    schema_ref: "schemas/corporate-return.json"
    required: false
  - name: "loanProgram"
    source: "Process Context"
    schema_ref: "schemas/loan-program.json"
    required: true
outputs:
  - name: "adjustedCashFlow_year1"
    type: "decimal"
    sink: "Process Context"
    invariants:
      - "Cash flow adjusted using Form 1084 methodology, not raw Schedule C net income"
  - name: "adjustedCashFlow_year2"
    type: "decimal"
    sink: "Process Context"
  - name: "qualifyingSelfEmploymentAnnual"
    type: "decimal"
    sink: "Process Context"
  - name: "qualifyingSelfEmploymentMonthly"
    type: "decimal"
    sink: "Process Context"
    invariants:
      - "qualifyingSelfEmploymentMonthly equals qualifyingSelfEmploymentAnnual / 12"
  - name: "cashFlowAnalysis"
    type: "object"
    sink: "Process Context"
  - name: "businessViabilityStatus"
    type: "string"
    sink: "Process Context"
    invariants:
      - "businessViabilityStatus is one of ACTIVE, DECLINING, CLOSED, UNKNOWN"
  - name: "incomeTrend"
    type: "string"
    sink: "Process Context"
    invariants:
      - "incomeTrend is one of STABLE, INCREASING, DECLINING"
invariants:
  - "Self-employment income MUST be calculated using cash flow analysis (Form 1084), not raw Schedule C net income alone."
  - "Depreciation, depletion, and amortization MUST be added back as non-cash expenses."
  - "If the 2-year trend is declining by more than 20%, the qualifying income MUST use the most recent year only, not the 2-year average."
  - "A net loss in the most recent year MUST result in zero or negative qualifying self-employment income."
  - "Business viability MUST be confirmed; income from a closed business is not qualifying."
success_criteria:
  - "A qualifying monthly self-employment income figure is computed and stored in the process context."
  - "Cash flow analysis is completed per Form 1084 methodology."
  - "Business viability status is determined."
failure_modes:
  - mode: "Missing schedule"
    detection: "Tax return lacks Schedule C or K-1 for self-employment"
    action: "Request missing schedules from borrower"
  - mode: "Corporate return missing"
    detection: "Borrower owns 25%+ of corp but 1120/1120-S not provided"
    action: "Cannot calculate; request corporate returns"
  - mode: "Business viability unknown"
    detection: "Cannot confirm business is currently operating"
    action: "Flag for underwriter; request current bank statements or business license"
  - mode: "Low extraction confidence"
    detection: "Structured data extraction confidence below 0.90"
    action: "Re-queue for manual data entry; do not use low-confidence figures"
contract_ref: "ICT-IV-SEI-001"
idempotency: "safe"
retry_policy: "exponential_backoff, max_retries=3, base_delay=5s"
timeout_seconds: 300
side_effects:
  - "Stores verified self-employment income figures in process context"
execution_hints:
  preferred_agent: "income-verification-service"
  tool_access:
    - "docvault_api"
    - "rule_engine_api"
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"
generated_from: "CAP-IV-SEI-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PIM"
gaps:
  - type: "missing_detail"
    description: "Business viability check integration not yet designed"
    severity: "medium"
---

# Intent: Verify Self-Employment Income

## Goal

Verify self-employment income through IRS tax return analysis and Fannie Mae cash flow methodology to produce a reliable monthly qualifying income figure.

## Preconditions

- The borrower has been classified as SELF_EMPLOYED or HYBRID.
- IRS Form 1040 returns with applicable schedules (C, E, K-1) for the most recent 2 tax years are in DocVault.
- If the borrower owns 25%+ of a corporation, corporate tax returns (1120/1120-S) are available.
- Structured data extraction from tax documents has completed with confidence >= 0.90.

## Execution Notes

This intent performs self-employment income verification using Fannie Mae Form 1084 cash flow analysis methodology. The executing agent must not use gross revenue (Schedule C Line 1) as qualifying income, must not include one-time or non-recurring income items, must not skip the cash flow add-back analysis, must not qualify income from a business that has ceased operations, and must not accept verbal assertions of business income without documentary support.
