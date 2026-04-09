---
intent_id: "INT-IV-W2V-001"
capsule_id: "CAP-IV-W2V-001"
bpmn_task_id: "Task_VerifyW2"
version: "1.0"
status: "draft"
goal: "Verify the borrower's W-2 wage income by cross-referencing W-2 forms against IRS tax return transcripts and computing a reliable monthly income figure for qualifying income calculation."
goal_type: "computation"
preconditions:
  - "The borrower has been classified as a W-2 employee (employmentType = W2)."
  - "W-2 documents for the most recent 2 tax years are available in DocVault with status AVAILABLE or VERIFIED."
  - "IRS Form 1040 transcripts for the corresponding years are available."
  - "The DocVault extraction service has parsed structured data from the W-2 images/PDFs."
inputs:
  - name: "borrower_profile"
    source: "Process Context"
    schema_ref: "schemas/borrower-profile.json"
    required: true
  - name: "w2_documents"
    source: "DocVault"
    schema_ref: "schemas/w2-document.json"
    required: true
  - name: "tax_returns"
    source: "DocVault"
    schema_ref: "schemas/tax-return-1040.json"
    required: true
  - name: "loanProgram"
    source: "Process Context"
    schema_ref: "schemas/loan-program.json"
    required: true
outputs:
  - name: "verifiedAnnualIncome"
    type: "decimal"
    sink: "Process Context"
    invariants:
      - "verifiedAnnualIncome is derived from W-2 and 1040 cross-reference, never from stated income"
  - name: "verifiedMonthlyIncome"
    type: "decimal"
    sink: "Process Context"
    invariants:
      - "verifiedMonthlyIncome equals verifiedAnnualIncome / 12"
  - name: "incomeComponents"
    type: "object"
    sink: "Process Context"
  - name: "incomeTrend"
    type: "string"
    sink: "Process Context"
    invariants:
      - "incomeTrend is one of STABLE, INCREASING, DECLINING"
  - name: "w2_1040_matchResult"
    type: "object"
    sink: "Process Context"
  - name: "verificationFlags"
    type: "array"
    sink: "Process Context"
invariants:
  - "W-2 Box 1 totals MUST NOT exceed 1040 Line 1 for the same tax year (unless additional W-2s from other employers are missing)."
  - "If income declined year-over-year by more than 10%, the verified income MUST use the lower year or the 2-year average, whichever is less."
  - "Variable income (overtime, bonus, commission) exceeding 25% of base MUST have a 2-year receipt history to be included."
  - "Employer EIN on W-2 MUST match the employment record in borrower_profile or be flagged for review."
success_criteria:
  - "A verified monthly W-2 income figure is computed and stored in the process context."
  - "W-2 to 1040 cross-reference passes for both tax years."
  - "Income trend is determined and applied correctly."
failure_modes:
  - mode: "W-2 document parse failure"
    detection: "Structured data extraction failed or confidence below threshold"
    action: "Re-queue for manual extraction; flag for underwriter"
  - mode: "Missing tax year"
    detection: "W-2 or 1040 missing for one of the required tax years"
    action: "Request document from borrower; cannot proceed without both years"
  - mode: "EIN mismatch"
    detection: "Employer EIN on W-2 does not match borrower profile"
    action: "Flag for manual review; may indicate unreported employer change"
  - mode: "Amount mismatch"
    detection: "W-2 total significantly exceeds 1040 Line 1"
    action: "Halt; possible fraudulent W-2 or missing 1040 data"
contract_ref: "ICT-IV-W2V-001"
idempotency: "safe"
retry_policy: "exponential_backoff, max_retries=3, base_delay=5s"
timeout_seconds: 180
side_effects:
  - "Stores verified income figures in process context"
execution_hints:
  preferred_agent: "income-verification-service"
  tool_access:
    - "docvault_api"
    - "irs_ives_api"
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"
generated_from: "CAP-IV-W2V-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PIM"
gaps: []
---

# Intent: Verify W-2 Income

## Goal

Verify the borrower's W-2 wage income by cross-referencing W-2 forms against IRS tax return transcripts and computing a reliable monthly income figure for qualifying income calculation.

## Preconditions

- The borrower has been classified as a W-2 employee (employmentType = W2).
- W-2 documents for the most recent 2 tax years are available in DocVault with status AVAILABLE or VERIFIED.
- IRS Form 1040 transcripts for the corresponding years are available.
- The DocVault extraction service has parsed structured data from the W-2 images/PDFs.

## Execution Notes

This intent performs the core W-2 income verification. The executing agent must not use stated income from the loan application as verified income, must not include variable compensation without a 2-year history, and must not average income when a declining trend exceeds the program threshold and the program requires use of the lower figure. The agent must not proceed if W-2 documents cannot be parsed into structured data.
