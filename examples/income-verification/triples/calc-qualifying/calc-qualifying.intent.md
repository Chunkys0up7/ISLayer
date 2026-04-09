---
intent_id: "INT-IV-QAL-001"
capsule_id: "CAP-IV-QAL-001"
bpmn_task_id: "Task_CalcQualifying"
version: "1.0"
status: "draft"
goal: "Aggregate verified income streams and compute total qualifying monthly income with a stated-vs-verified variance analysis to determine whether the result passes or requires exception handling."
goal_type: "computation"
preconditions:
  - "At least one upstream verification task (Task_VerifyW2 or Task_VerifySelfEmployment) has completed successfully."
  - "Verified income figures are available in the process context."
  - "The borrower's stated monthly income is available in borrower_profile."
  - "The RuleEngine income aggregation rules are accessible."
inputs:
  - name: "verifiedMonthlyIncome"
    source: "Process Context"
    schema_ref: "schemas/verified-income.json"
    required: false
  - name: "qualifyingSelfEmploymentMonthly"
    source: "Process Context"
    schema_ref: "schemas/self-employment-income.json"
    required: false
  - name: "incomeComponents"
    source: "Process Context"
    schema_ref: "schemas/income-components.json"
    required: true
  - name: "borrower_profile.statedMonthlyIncome"
    source: "Process Context"
    schema_ref: "schemas/borrower-profile.json"
    required: true
  - name: "loanProgram"
    source: "Process Context"
    schema_ref: "schemas/loan-program.json"
    required: true
outputs:
  - name: "income_result"
    type: "object"
    sink: "Process Context"
    invariants:
      - "income_result contains all verified income streams and variance analysis"
  - name: "totalQualifyingMonthlyIncome"
    type: "decimal"
    sink: "Process Context"
    invariants:
      - "totalQualifyingMonthlyIncome is the sum of individually verified income streams only"
  - name: "variancePercent"
    type: "decimal"
    sink: "Process Variable"
    invariants:
      - "variancePercent is calculated as absolute percentage of stated income"
  - name: "varianceThreshold"
    type: "decimal"
    sink: "Process Variable"
    invariants:
      - "varianceThreshold is set per loan program rules (10% CONV/VA, 15% FHA)"
  - name: "varianceStatus"
    type: "string"
    sink: "Process Context"
    invariants:
      - "varianceStatus is WITHIN_THRESHOLD or EXCEEDS_THRESHOLD"
invariants:
  - "Total qualifying income MUST be the sum of individually verified income streams only; no unverified sources may be included."
  - "Variance MUST be calculated as an absolute percentage of stated income."
  - "The variance threshold MUST be set per the loan program rules (10% for CONV/VA, 15% for FHA)."
  - "If no income streams were verified (all upstream tasks failed), qualifying income MUST be zero and the variance MUST exceed threshold."
  - "Self-employment losses MUST reduce total qualifying income (they are not ignored)."
success_criteria:
  - "Total qualifying monthly income is computed and stored in the process context."
  - "Variance analysis is completed with correct program-specific threshold."
  - "Gateway variables (variancePercent, varianceThreshold) are set for downstream routing."
failure_modes:
  - mode: "No verified income"
    detection: "No upstream verification completed successfully"
    action: "Set qualifying income to zero; route to variance exception"
  - mode: "Stated income missing"
    detection: "Stated monthly income is null or zero in borrower profile"
    action: "Cannot compute variance; flag for underwriter to obtain stated income"
  - mode: "RuleEngine service unavailable"
    detection: "RuleEngine API returns 503 or connection timeout"
    action: "Retry with backoff; escalate after 3 failures"
contract_ref: "ICT-IV-QAL-001"
idempotency: "safe"
retry_policy: "exponential_backoff, max_retries=3, base_delay=5s"
timeout_seconds: 60
side_effects:
  - "Sets variancePercent and varianceThreshold process variables for gateway routing"
  - "Stores income_result in process context"
execution_hints:
  preferred_agent: "income-verification-service"
  tool_access:
    - "rule_engine_api"
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"
generated_from: "CAP-IV-QAL-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PIM"
gaps: []
---

# Intent: Calculate Qualifying Income

## Goal

Aggregate verified income streams and compute total qualifying monthly income with a stated-vs-verified variance analysis to determine whether the result passes or requires exception handling.

## Preconditions

- At least one upstream verification task (Task_VerifyW2 or Task_VerifySelfEmployment) has completed successfully.
- Verified income figures are available in the process context.
- The borrower's stated monthly income is available in `borrower_profile`.
- The RuleEngine income aggregation rules are accessible.

## Execution Notes

This intent aggregates verified income and performs variance analysis. The executing agent must not use stated income as qualifying income, must not ignore self-employment losses when computing total qualifying income, must not apply a variance threshold that is more lenient than the program's published limit, and must not round variance percentages in a direction that would change the pass/fail outcome.
