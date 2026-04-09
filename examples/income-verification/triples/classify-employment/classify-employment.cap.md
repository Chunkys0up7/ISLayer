---
capsule_id: "CAP-IV-CLS-001"
bpmn_task_id: "Task_ClassifyEmployment"
bpmn_task_name: "Classify Employment Type"
bpmn_task_type: "businessRuleTask"
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
  - "Fannie Mae Selling Guide B3-3.1-01 (General Income Information)"
  - "Fannie Mae Selling Guide B3-3.2-01 (Self-Employment Income)"
  - "FHA 4000.1 II.A.4.c.2 (Employment Less Than Two Years)"
policy_refs:
  - "POL-IV-003 Employment Classification Policy"
intent_id: "INT-IV-CLS-001"
contract_id: "ICT-IV-CLS-001"
parent_capsule_id: null
predecessor_ids:
  - "CAP-IV-REQ-001"
successor_ids:
  - "CAP-IV-DEC-001"
exception_ids: []
gaps:
  - type: "missing_detail"
    description: "HYBRID classification requires parallel gateway not modeled in current BPMN"
    severity: "medium"
---

# Classify Employment Type

## Purpose

Determines the borrower's employment classification based on their employment history and submitted documentation. The classification drives the downstream verification path -- W-2 salaried verification or self-employment income analysis.

## Procedure

1. **Load Borrower Employment History**: Retrieve the `borrower_profile` data object from the process context. Extract the most recent employment record (or all current concurrent employments).

2. **Apply Classification Rules**:
   - If the borrower's most recent employment record has `employmentType` = `W2` and the position has been held for at least 24 months continuously, classify as **W2_STABLE**.
   - If `employmentType` = `W2` but tenure is less than 24 months, classify as **W2_NEW** (still routes to W-2 path but triggers additional VOE requirements).
   - If `employmentType` = `SELF_EMPLOYED` and tax returns show Schedule C or Schedule K-1 income for 2+ years, classify as **SELF_EMPLOYED_ESTABLISHED**.
   - If `employmentType` = `1099`, classify as **SELF_EMPLOYED** (treated as self-employment per Fannie Mae B3-3.2).
   - If the borrower has both W-2 and self-employment income, classify as **HYBRID** and route to both verification paths.

3. **Determine Primary Income Source**: When multiple income sources exist, identify the primary source as the one contributing the highest stated monthly income.

4. **Set Gateway Variable**: Write the `employmentType` process variable (W2 or SELF_EMPLOYED) for the downstream exclusive gateway.

5. **Flag Edge Cases**: If the borrower has fewer than 2 years of employment history, or has gaps exceeding 6 months in the last 24 months, flag for manual underwriter review.

## Business Rules

- Fannie Mae Selling Guide B3-3.1-01: General Income Information.
- FHA 4000.1 II.A.4.c.2: Employment less than two years requires documentation of training or education.
- Self-employment classification per Fannie Mae B3-3.2-01: a borrower with 25% or greater ownership interest is self-employed.
- The borrower profile contains accurate employment history as reported by the borrower and validated by the LOS intake process.
- Employment records include start/end dates sufficient to calculate tenure.

## Inputs

| Field | Source | Required |
|---|---|---|
| borrower_profile | Process Context | Yes |
| borrower_profile.employmentHistory | Process Context | Yes |
| loanProgram | Process Context | Yes |

## Outputs

| Field | Destination | Description |
|---|---|---|
| employmentType | Process Variable | Gateway routing variable: W2 or SELF_EMPLOYED |
| employmentClassification | Process Context | Detailed classification: W2_STABLE, W2_NEW, SELF_EMPLOYED_ESTABLISHED, HYBRID |
| primaryIncomeSource | Process Context | The employment record contributing the highest income |
| manualReviewRequired | Process Context | Boolean flag for edge cases requiring underwriter review |

## Exception Handling

- **No Employment Records**: If borrower_profile has zero employment records, halt process and return to LOS for borrower data correction.
- **Ambiguous Classification**: If employment records conflict (e.g., overlapping full-time W-2 positions), flag for manual review and do not auto-classify.
- **RuleEngine Unavailable**: If RuleEngine service is unavailable, retry with exponential backoff (max 3 attempts); escalate to underwriter if still down.
