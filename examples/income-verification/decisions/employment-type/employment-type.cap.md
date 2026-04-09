---
capsule_id: "CAP-IV-DEC-001"
bpmn_task_id: "Gateway_EmploymentType"
bpmn_task_name: "Employment Type Decision"
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
owner_role: "Verification Agent"
owner_team: "Income Verification"
reviewers: []
domain: "Mortgage Lending"
subdomain: "Income Verification"
regulation_refs:
  - "Fannie Mae Selling Guide B3-3.1 (Salary/Wage Income)"
  - "Fannie Mae Selling Guide B3-3.2 (Self-Employment Income)"
policy_refs:
  - "POL-IV-003 Employment Classification Policy"
intent_id: "INT-IV-DEC-001"
contract_id: "ICT-IV-DEC-001"
parent_capsule_id: null
predecessor_ids:
  - "CAP-IV-CLS-001"
successor_ids:
  - "CAP-IV-W2V-001"
  - "CAP-IV-SEI-001"
exception_ids: []
gaps:
  - type: "missing_detail"
    description: "HYBRID classification requires parallel gateway for dual verification paths, not modeled in current BPMN"
    severity: "medium"
---

# Employment Type Decision

## Purpose

Routes the verification workflow to the appropriate income verification path based on the borrower's classified employment type. This decision point ensures the correct documentation requirements and calculation methods are applied.

## Decision Logic

The gateway evaluates the `employmentType` process variable set by the preceding Classify Employment Type task (Task_ClassifyEmployment).

### Decision Table

| # | Condition | Route | Target Task |
|---|---|---|---|
| 1 | employmentType == 'W2' | W-2 Employee | Task_VerifyW2 |
| 2 | employmentType == 'SELF_EMPLOYED' | Self-Employed | Task_VerifySelfEmployment |

### Edge Cases

- **HYBRID Classification**: When the borrower has both W-2 and self-employment income, the classification task should set employmentType to the primary source. Both verification paths would need to run, which requires a parallel gateway (not modeled in this version; see GAP-001).
- **Default**: If employmentType is neither W2 nor SELF_EMPLOYED, the gateway has no matching outbound flow and the process engine will raise an unmatched gateway exception.

## Business Rules

- The employment classification directly determines which sections of the Fannie Mae Selling Guide apply:
  - W2 path: B3-3.1 (Salary/Wage Income)
  - Self-Employment path: B3-3.2 (Self-Employment Income)
- Requires Task_ClassifyEmployment to have completed and set the `employmentType` variable.
- The variable must be exactly 'W2' or 'SELF_EMPLOYED' (case-sensitive).
