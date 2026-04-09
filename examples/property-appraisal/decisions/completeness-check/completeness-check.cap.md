---
capsule_id: "CAP-PA-DEC-001"
bpmn_task_id: "Gateway_Complete"
bpmn_task_name: "Complete?"
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

owner_role: "Chief Appraiser"
owner_team: "Appraisal Management"
reviewers:
  - "Compliance Officer"
  - "Underwriting Manager"

domain: "Mortgage"
subdomain: "Property Appraisal"
regulation_refs:
  - "USPAP-SR2: Standards Rule 2 - Appraisal Reporting"
  - "FNMA-B4-1.2: Fannie Mae Appraisal Report Requirements"
policy_refs:
  - "POL-MTG-APR-004: Appraisal Completeness Checklist Policy"

intent_id: "INT-PA-DEC-001"
contract_id: "ICT-PA-DEC-001"
parent_capsule_id: ""
predecessor_ids:
  - "CAP-PA-VAL-001"
successor_ids:
  - "CAP-PA-ASV-001"
  - "CAP-PA-REV-001"
exception_ids: []

gaps: []
---

# Completeness Decision Gateway

## Purpose

This decision gateway evaluates the completeness status produced by the Validate Appraisal Completeness task and routes the process flow accordingly. If the report is complete, processing continues to value assessment. If incomplete, the flow routes to request a revision from the appraiser. This binary routing decision prevents incomplete reports from entering the value assessment pipeline, where missing data would cause calculation errors or unreliable results.

## Procedure

1. Read the completeness_status field from the validation task output.
2. If completeness_status equals "Complete," route to the Assess Property Value task.
3. If completeness_status equals "Incomplete," route to the Request Appraisal Revision task.
4. No other routing outcomes are possible; the decision is strictly binary.

## Business Rules

- A completeness status of "Complete" means every required checklist item passed. No exceptions or overrides are permitted at the gateway level.
- A completeness status of "Incomplete" triggers the revision path regardless of the severity of the deficiencies.
- The gateway does not evaluate the content quality or value reasonableness of the report; it only checks whether all required sections and data are present.

## Inputs Required

| Input | Source | Description |
|-------|--------|-------------|
| Completeness Status | Task_ValidateCompleteness | "Complete" or "Incomplete" determination |
| Deficiency Codes | Task_ValidateCompleteness | List of failed checklist items (for the incomplete path) |

## Outputs Produced

| Output | Destination | Description |
|--------|-------------|-------------|
| Routing Decision | Process Engine | Directs flow to Task_AssessValue or Task_RequestRevision |

## Exception Handling

- **Unknown Completeness Status** -- If the status is neither "Complete" nor "Incomplete," halt the process and escalate to the appraisal desk. This indicates a validation system error.

## Regulatory Context

The completeness decision enforces USPAP Standards Rule 2 reporting requirements at the process level. Fannie Mae and FHA have additional minimum content requirements that must be satisfied before a report can be used for lending decisions.

## Notes

- This gateway does not perform its own validation; it merely routes based on the upstream task's output.
- Future enhancements may add a "Partially Complete" status with conditional routing, but this is not currently supported.
