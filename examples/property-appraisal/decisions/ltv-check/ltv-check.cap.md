---
capsule_id: "CAP-PA-DEC-002"
bpmn_task_id: "Gateway_LTV"
bpmn_task_name: "Value Within LTV?"
bpmn_task_type: "businessRuleTask"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"

version: "1.0.0"
status: "draft"

generated_from: "bpmn/property-appraisal.bpmn"
generated_date: "2026-04-09"
generated_by: "mda-pipeline"
last_modified: "2026-04-09"
last_modified_by: "mda-pipeline"

owner_role: "Underwriting Manager"
owner_team: "Underwriting Review"
reviewers:
  - "Chief Appraiser"
  - "Risk Officer"

domain: "Mortgage"
subdomain: "Property Appraisal"
regulation_refs:
  - "FNMA-B2-1.5: Fannie Mae LTV/CLTV/HCLTV Ratio Requirements"
  - "FHA-4000.1-II.A.2: FHA Maximum LTV Ratios"
policy_refs:
  - "POL-MTG-UW-010: Collateral Risk Assessment Policy"
  - "POL-MTG-APR-006: LTV Calculation and Threshold Policy"

intent_id: "INT-PA-DEC-002"
contract_id: "ICT-PA-DEC-002"
parent_capsule_id: ""
predecessor_ids:
  - "CAP-PA-ASV-001"
successor_ids:
  - "CAP-PA-NTF-001"
  - "CAP-PA-MRV-001"
exception_ids: []

gaps: []
---

# LTV Decision Gateway

## Purpose

This decision gateway compares the calculated LTV ratio against the maximum LTV permitted by the loan program and routes the process accordingly. Loans within the LTV threshold proceed to completion; those exceeding the threshold are routed to manual underwriting review. This routing decision is the primary collateral risk gate in the appraisal subprocess.

## Procedure

1. Read the ltv_ratio and ltv_determination fields from the value assessment task output.
2. If ltv_determination equals "Within_LTV," route to the Emit Appraisal Complete Event task.
3. If ltv_determination equals "Exceeds_LTV," route to the Flag for Manual Review task.
4. No other routing outcomes are possible.

## Business Rules

- Maximum LTV thresholds by program: Conventional 97%, FHA 96.5%, VA 100%, USDA 100%, Jumbo 80% (typical).
- The determination is made by the upstream Assess Property Value task; the gateway only routes based on the result.
- No LTV exceptions or overrides are permitted at the gateway level; exceptions must flow through manual review.
- PMI (Private Mortgage Insurance) eligibility is determined downstream and does not affect this routing decision.

## Inputs Required

| Input | Source | Description |
|-------|--------|-------------|
| LTV Ratio | Task_AssessValue | Calculated loan-to-value percentage |
| LTV Determination | Task_AssessValue | "Within_LTV" or "Exceeds_LTV" |

## Outputs Produced

| Output | Destination | Description |
|--------|-------------|-------------|
| Routing Decision | Process Engine | Directs flow to Task_EmitComplete or Task_ManualReview |

## Exception Handling

- **Unknown LTV Determination** -- If the determination is neither "Within_LTV" nor "Exceeds_LTV," halt the process and escalate to the underwriting manager.

## Regulatory Context

Fannie Mae Selling Guide B2-1.5 and FHA Handbook 4000.1 Section II.A.2 define maximum LTV ratios by loan program. Exceeding these limits requires additional risk mitigation (PMI, reduced loan amount) or denial. The gateway enforces these limits at the process level.

## Notes

- The gateway does not consider CLTV (Combined LTV) or HCLTV, which are evaluated separately in the underwriting process.
- Some investors may have LTV overlays more restrictive than GSE guidelines.
