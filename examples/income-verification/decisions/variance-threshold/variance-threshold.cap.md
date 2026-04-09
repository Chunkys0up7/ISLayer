---
capsule_id: "CAP-IV-DEC-002"
bpmn_task_id: "Gateway_Variance"
bpmn_task_name: "Variance Threshold Decision"
bpmn_task_type: "exclusiveGateway"
process_id: "Process_IncomeVerification"
process_name: "Income Verification"
version: "1.0"
status: "draft"
generated_from: "income-verification.bpmn"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
last_modified: "2026-04-09T00:00:00Z"
last_modified_by: "MDA Demo"
owner_role: "Underwriter"
owner_team: "Income Verification"
reviewers: []
domain: "Mortgage Lending"
subdomain: "Income Verification"
regulation_refs:
  - "TILA-RESPA Integrated Disclosure (TRID) Rule (Ability-to-Repay)"
  - "Bank Secrecy Act (Suspicious Activity Report obligations)"
policy_refs:
  - "POL-IV-008 Income Variance Exception Policy"
intent_id: "INT-IV-DEC-002"
contract_id: "ICT-IV-DEC-002"
parent_capsule_id: null
predecessor_ids:
  - "CAP-IV-QAL-001"
successor_ids:
  - "CAP-IV-NTF-001"
exception_ids:
  - "End_VarianceException"
gaps: []
---

# Variance Threshold Decision

## Purpose

Evaluates whether the variance between the borrower's stated income and verified income falls within acceptable limits for the loan program. This decision determines whether the verification result can be automatically accepted or must be routed to an exception path for manual underwriter review.

## Decision Logic

The gateway evaluates two process variables:
- `variancePercent`: The absolute percentage difference between stated and verified income
- `varianceThreshold`: The program-specific acceptable limit

### Decision Table

| # | Condition | Route | Target |
|---|---|---|---|
| 1 | variancePercent <= varianceThreshold | Within Threshold | Task_EmitVerified |
| 2 | variancePercent > varianceThreshold | Exceeds Threshold | End_VarianceException |

### Program-Specific Thresholds

| Loan Program | Variance Threshold | Rationale |
|---|---|---|
| Conventional (CONV) | 10% | Fannie Mae standard tolerance |
| FHA | 15% | HUD allows slightly wider tolerance for FHA borrowers |
| VA | 10% | VA follows conventional standards |
| USDA | 10% | USDA follows conventional standards |

### Interpretation

- A variance of 0% means stated income exactly matches verified income.
- A positive variance means the borrower stated more income than was verified (over-stated).
- A negative variance means the borrower stated less income than verified (under-stated). Both directions trigger the threshold check.
- When variance exceeds the threshold, the process terminates with a Variance Exception error event, which signals the underwriting system to queue the application for manual review.

## Business Rules

- Income variance is a key risk indicator for ability-to-repay (ATR) under the TILA-RESPA Integrated Disclosure (TRID) rule.
- Material income discrepancies may trigger Suspicious Activity Report (SAR) obligations under the Bank Secrecy Act if fraud is suspected.
- Requires Task_CalcQualifying to have completed and set both `variancePercent` and `varianceThreshold` process variables.
