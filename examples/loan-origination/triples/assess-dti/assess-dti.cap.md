---
capsule_id: "CAP-LO-DTI-001"
bpmn_task_id: "Task_AssessDTI"
bpmn_task_name: "Assess Debt-to-Income Ratio"
bpmn_task_type: "businessRuleTask"
process_id: "Process_LoanOrigination"
process_name: "Loan Origination"
version: "1.0"
status: "draft"
generated_from: "loan-origination.bpmn"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
last_modified: "2026-04-09T00:00:00Z"
last_modified_by: "MDA Demo"
owner_role: "Automated Systems"
owner_team: "Retail Lending"
domain: "Mortgage Lending"
subdomain: "Credit Decisioning"
regulation_refs:
  - "QM Rule (Ability-to-Repay)"
  - "GSE Selling Guides (Fannie Mae / Freddie Mac)"
policy_refs:
  - "POL-LO-030 DTI Threshold Policy"
  - "POL-LO-031 Income Calculation Standards"
intent_id: "INT-LO-DTI-001"
contract_id: "ICT-LO-DTI-001"
predecessor_ids:
  - "CAP-LO-CRC-001"
successor_ids:
  - "CAP-LO-DEC-001"
gaps:
  - type: "missing_detail"
    description: "Detailed procedure for calculating self-employment income not specified"
    severity: "high"
  - type: "ambiguity"
    description: "Treatment of non-taxable income (e.g., VA disability) grossing-up factor not defined"
    severity: "medium"
---

# Assess Debt-to-Income Ratio

## Purpose

Calculate the borrower's front-end and back-end debt-to-income (DTI) ratios using verified income, existing debts from the credit report, and the proposed mortgage payment to determine initial loan eligibility.

## Procedure

1. **Income Aggregation**: Gather all qualifying income sources from the loan application: base salary, overtime (if consistent for 2+ years), bonuses, commissions, rental income, investment income, alimony/child support received, and other documented income.
2. **Income Verification Check**: Confirm that income documentation is on file (paystubs, W-2s, tax returns). If any required income documentation is missing, set `docs_complete = false` in the output.
3. **Monthly Income Calculation**: Convert all income to gross monthly amounts. Use a 24-month average for variable income sources.
4. **Debt Enumeration**: Extract all recurring monthly obligations from the credit report tradelines: mortgage/rent, auto loans, student loans, credit card minimum payments, personal loans, and other installment debts.
5. **Proposed Housing Expense**: Calculate the proposed monthly housing payment (PITIA): Principal, Interest, Taxes, Insurance, and Association dues based on the requested loan amount, estimated rate, property taxes, and hazard insurance.
6. **Front-End DTI**: Calculate front-end ratio = (proposed PITIA) / (gross monthly income).
7. **Back-End DTI**: Calculate back-end ratio = (proposed PITIA + all recurring debts) / (gross monthly income).
8. **Threshold Evaluation**: Compare both ratios against the applicable product thresholds:
   - Conventional: front-end <= 28%, back-end <= 36% (standard) or <= 45% (with compensating factors)
   - FHA: front-end <= 31%, back-end <= 43%
   - VA: no front-end limit, back-end <= 41%
9. **Result Assembly**: Produce the dti_result object with both ratios, pass/fail status, compensating factors applied (if any), and documentation completeness flag.

## Business Rules

- For Qualified Mortgage (QM) compliance, back-end DTI must not exceed 43% unless the loan meets GSE patch criteria.
- Self-employment income requires 2-year tax return history and a year-to-date profit-and-loss statement.
- Debts with fewer than 10 remaining payments may be excluded if the borrower can document the payoff schedule.
- Child support and alimony obligations must be included in debt calculations regardless of credit report presence.
- Non-taxable income may be grossed up by 25% (subject to policy confirmation).

## Inputs

| Field | Source | Required |
|---|---|---|
| loan_application (income, loan terms) | LOS Database | Yes |
| credit_report (tradelines, debts) | LOS Database / DocVault | Yes |
| borrower_profile | LOS Database | Yes |
| income_documentation_status | DocVault | Yes |

## Outputs

| Field | Destination | Description |
|---|---|---|
| dti_result | LOS Database | Front-end ratio, back-end ratio, pass/fail, docs_complete flag |

## Exception Handling

- **Missing Income Documentation**: Set `dti_result.docs_complete = false` and include a list of missing documents. The process will route to the "Request Additional Documentation" task.
- **Negative Income**: If calculated income is zero or negative, flag for manual review by a senior underwriter.
- **Conflicting Data**: If income on application differs from credit report employer data by more than 20%, flag for manual review.
