---
capsule_id: "CAP-IV-W2V-001"
bpmn_task_id: "Task_VerifyW2"
bpmn_task_name: "Verify W-2 Income"
bpmn_task_type: "serviceTask"
process_id: "Process_IncomeVerification"
process_name: "Income Verification"
version: "1.0"
status: "draft"
generated_from: "income-verification.bpmn"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
last_modified: "2026-04-09T00:00:00Z"
last_modified_by: "MDA Demo"
owner_role: "Verification Agent"
owner_team: "Income Verification"
reviewers: []
domain: "Mortgage Lending"
subdomain: "Income Verification"
regulation_refs:
  - "Fannie Mae Selling Guide B3-3.1-01 (Salary and Wage Income)"
  - "FHA 4000.1 II.A.4.c.2.a (W-2 Income Requirements)"
policy_refs:
  - "POL-IV-004 W-2 Income Verification Policy"
intent_id: "INT-IV-W2V-001"
contract_id: "ICT-IV-W2V-001"
parent_capsule_id: null
predecessor_ids:
  - "CAP-IV-DEC-001"
successor_ids:
  - "CAP-IV-QAL-001"
exception_ids: []
gaps:
  - type: "missing_detail"
    description: "OCR extraction confidence threshold for auto-acceptance not yet defined (suggested: 0.95)"
    severity: "low"
---

# Verify W-2 Income

## Purpose

Validates the borrower's W-2 wage income by cross-referencing employer-issued W-2 forms against IRS tax return transcripts (Form 1040). This task ensures that stated income matches documented income within acceptable tolerances per agency guidelines.

## Procedure

1. **Retrieve W-2 Documents**: Fetch the borrower's W-2 documents from DocVault for the most recent two tax years. Extract Box 1 (Wages, tips, other compensation) and Box 5 (Medicare wages) from each W-2.

2. **Retrieve Tax Return Transcripts**: Fetch IRS Form 1040 data for the same tax years. Extract Line 1 (Wages, salaries, tips) from each return.

3. **Cross-Reference W-2 to 1040**: For each tax year, compare the sum of all W-2 Box 1 amounts to the corresponding 1040 Line 1 amount. They should match or the W-2 total should be less than or equal to 1040 Line 1 (since 1040 may include additional wage sources).

4. **Validate Employer Information**: Confirm the employer name and EIN on the W-2 match the employment record in the borrower profile. Flag discrepancies for manual review.

5. **Calculate Year-over-Year Trend**: Compare the two years of W-2 income:
   - If income is stable or increasing, use the most recent year as the base.
   - If income declined by more than 10%, use the lower of the two years or the average, per Fannie Mae B3-3.1-01 guidance.

6. **Identify Additional Compensation**: Review W-2 boxes for overtime (if separately documented), bonuses, commissions, and tips. If these represent more than 25% of base pay, they require a 2-year history of receipt to be included in qualifying income.

7. **Compute Monthly Gross Income**: Calculate the verified monthly gross W-2 income:
   `verifiedMonthlyIncome = verifiedAnnualIncome / 12`

8. **Record Verification Result**: Store the verified income figure, supporting calculations, and any flags in the process context for the downstream qualifying income calculation.

## Business Rules

- Fannie Mae Selling Guide B3-3.1-01: Salary and wage income must be verified with W-2s and pay stubs covering the most recent 30 days plus the most recent two years.
- FHA 4000.1 II.A.4.c.2.a: W-2 income for the most recent two years is required. Declining income requires use of the lower figure.
- Conventional loans may use a 2-year average if income is stable or increasing.
- W-2 documents have been OCR-processed and structured data is available in DocVault.
- IRS transcript data is available through IVES or has been manually obtained and uploaded.

## Inputs

| Field | Source | Required |
|---|---|---|
| borrower_profile | Process Context | Yes |
| w2_documents | DocVault | Yes |
| tax_returns | DocVault | Yes |
| loanProgram | Process Context | Yes |

## Outputs

| Field | Destination | Description |
|---|---|---|
| verifiedAnnualIncome | Process Context | Verified annual W-2 income amount |
| verifiedMonthlyIncome | Process Context | verifiedAnnualIncome / 12 |
| incomeComponents | Process Context | Breakdown: base, overtime, bonus, commission, tips |
| incomeTrend | Process Context | STABLE, INCREASING, or DECLINING |
| w2_1040_matchResult | Process Context | Per-year match status between W-2 totals and 1040 Line 1 |
| verificationFlags | Process Context | Array of flags for manual review items |

## Exception Handling

- **Document Parse Failure**: If W-2 structured data extraction failed, re-queue for manual extraction and flag for underwriter.
- **Missing Tax Year**: If W-2 or 1040 missing for one of the required tax years, request document from borrower; cannot proceed without both years.
- **EIN Mismatch**: If employer EIN on W-2 does not match borrower profile, flag for manual review.
- **Amount Mismatch**: If W-2 total significantly exceeds 1040 Line 1, halt; possible fraudulent W-2 or missing 1040 data.
