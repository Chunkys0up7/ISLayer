---
capsule_id: "CAP-IV-SEI-001"
bpmn_task_id: "Task_VerifySelfEmployment"
bpmn_task_name: "Verify Self-Employment Income"
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
  - "Fannie Mae Selling Guide B3-3.2-01 through B3-3.2-03 (Self-Employment Income)"
  - "Fannie Mae Form 1084/1084A (Cash Flow Analysis)"
  - "FHA 4000.1 II.A.4.c.2.b (Self-Employment Income Requirements)"
policy_refs:
  - "POL-IV-005 Self-Employment Income Verification Policy"
intent_id: "INT-IV-SEI-001"
contract_id: "ICT-IV-SEI-001"
parent_capsule_id: null
predecessor_ids:
  - "CAP-IV-DEC-001"
successor_ids:
  - "CAP-IV-QAL-001"
exception_ids: []
gaps:
  - type: "missing_detail"
    description: "Business viability check integration (Secretary of State API or similar) is not yet designed"
    severity: "medium"
---

# Verify Self-Employment Income

## Purpose

Validates self-employment income by analyzing IRS tax returns (Form 1040 with Schedule C, Schedule E, or Form 1065/K-1) for the most recent two years. Self-employment income verification is more complex than W-2 verification because it requires adjusting gross revenue by allowable deductions and add-backs to arrive at qualifying income.

## Procedure

1. **Retrieve Tax Returns**: Fetch IRS Form 1040 transcripts and associated schedules from DocVault for the most recent two tax years.

2. **Identify Business Structure**:
   - **Sole Proprietorship**: Analyze Schedule C (Profit or Loss From Business).
   - **Partnership/S-Corp**: Analyze Schedule K-1 (Form 1065 or 1120-S) for the borrower's share of income/loss.
   - **Corporation (25%+ ownership)**: Analyze Form 1120 or 1120-S corporate returns plus the borrower's W-2 from that business.

3. **Extract Net Business Income**: For each tax year:
   - Schedule C: Line 31 (Net profit or loss)
   - Schedule K-1: Box 1 (Ordinary business income) and relevant distribution boxes
   - Add any applicable K-1 losses or deductions the borrower is personally liable for

4. **Apply Fannie Mae Cash Flow Analysis (Form 1084)**:
   - Start with net income from the tax return
   - Add back non-cash expenses: depreciation (Schedule C Line 13), depletion, amortization
   - Add back meals and entertainment deductions (50% non-deductible portion)
   - Subtract non-recurring income (one-time gains, insurance proceeds)
   - Add/subtract changes in accounts receivable/payable if material

5. **Calculate Two-Year Average or Declining Trend**:
   - If adjusted cash flow is stable or increasing, use the 2-year average.
   - If declining by more than 20%, use the most recent year only.
   - If the most recent year shows a net loss, qualifying income from self-employment is zero (or negative, requiring offset by other income).

6. **Verify Business Viability**: Confirm the business is currently operating by checking:
   - Active business license (if available in DocVault)
   - Most recent quarter's profit/loss statement or bank statements
   - No evidence of business closure or dissolution

7. **Compute Monthly Qualifying Income**:
   `qualifyingSelfEmploymentMonthly = adjustedAnnualCashFlow / 12`

## Business Rules

- Fannie Mae Selling Guide B3-3.2-01 through B3-3.2-03: Requirements for self-employed borrowers, including 2-year history and cash flow analysis.
- Fannie Mae Form 1084/1084A: Cash Flow Analysis worksheets.
- FHA 4000.1 II.A.4.c.2.b: Self-employment income requires 2 years of tax returns and evidence of business viability.
- Tax returns have been OCR-processed and Schedule C / K-1 data is available as structured data in DocVault.
- Corporate returns (1120/1120-S) are provided when the borrower has 25%+ ownership.

## Inputs

| Field | Source | Required |
|---|---|---|
| borrower_profile | Process Context | Yes |
| tax_returns | DocVault | Yes |
| corporate_returns | DocVault | Conditional (25%+ owner) |
| loanProgram | Process Context | Yes |

## Outputs

| Field | Destination | Description |
|---|---|---|
| adjustedCashFlow_year1 | Process Context | Cash-flow-adjusted income for the more recent tax year |
| adjustedCashFlow_year2 | Process Context | Cash-flow-adjusted income for the prior tax year |
| qualifyingSelfEmploymentAnnual | Process Context | Final qualifying annual self-employment income |
| qualifyingSelfEmploymentMonthly | Process Context | qualifyingSelfEmploymentAnnual / 12 |
| cashFlowAnalysis | Process Context | Full Form 1084 analysis with line-by-line detail |
| businessViabilityStatus | Process Context | ACTIVE, DECLINING, CLOSED, UNKNOWN |
| incomeTrend | Process Context | STABLE, INCREASING, DECLINING |

## Exception Handling

- **Missing Schedule**: If tax return lacks Schedule C or K-1, request missing schedules from borrower.
- **Corporate Return Missing**: If borrower owns 25%+ of corp but 1120/1120-S not provided, cannot calculate; request corporate returns.
- **Business Viability Unknown**: If cannot confirm business is currently operating, flag for underwriter and request current bank statements or business license.
- **Low Extraction Confidence**: If structured data extraction confidence below 0.90, re-queue for manual data entry.
