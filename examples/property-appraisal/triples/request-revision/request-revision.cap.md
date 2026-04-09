---
capsule_id: "CAP-PA-REV-001"
bpmn_task_id: "Task_RequestRevision"
bpmn_task_name: "Request Appraisal Revision"
bpmn_task_type: "sendTask"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"

version: "1.0.0"
status: "draft"

generated_from: "bpmn/property-appraisal.bpmn"
generated_date: "2026-04-09"
generated_by: "mda-pipeline"
last_modified: "2026-04-09"
last_modified_by: "mda-pipeline"

owner_role: "Appraisal Desk Supervisor"
owner_team: "Appraisal Management"
reviewers:
  - "Chief Appraiser"
  - "Compliance Officer"

domain: "Mortgage"
subdomain: "Property Appraisal"
regulation_refs:
  - "USPAP-Ethics: USPAP Ethics Rule - Communication with Appraiser"
  - "AIR: Appraiser Independence Requirements"
policy_refs:
  - "POL-MTG-APR-005: Appraisal Revision Request Policy"

intent_id: "INT-PA-REV-001"
contract_id: "ICT-PA-REV-001"
parent_capsule_id: ""
predecessor_ids:
  - "CAP-PA-VAL-001"
successor_ids:
  - "CAP-PA-RCV-001"
exception_ids: []

gaps: []
---

# Request Appraisal Revision

## Purpose

When the completeness validation identifies deficiencies in the appraisal report, this task composes and transmits a structured revision request to the AMC or appraiser. Proper revision requests must clearly state the specific deficiencies without attempting to influence the appraiser's value opinion, maintaining compliance with appraiser independence requirements.

## Procedure

1. Retrieve the deficiency codes produced by the completeness validation task.
2. Map each deficiency code to a standardized revision request narrative describing the missing or deficient item.
3. Compose the revision request message, including the order confirmation ID, deficiency list, and requested turnaround date.
4. Verify that the revision request does not contain any language that could be construed as attempting to influence the appraised value.
5. Transmit the revision request to the AMC via the Appraisal Portal.
6. Update the LOS appraisal status to "Revision Requested" with the revision request details and timestamp.
7. Reset the turnaround tracking timer for the revised report.

## Business Rules

- Revision requests must be limited to factual deficiencies (missing sections, photos, data fields) and must not suggest or require a specific value conclusion.
- A maximum of two revision requests are permitted per appraisal engagement; a third deficiency triggers a new appraisal order.
- The revision turnaround period is 5 business days from the request date.
- All revision requests must be logged in the communication audit trail for examiner review.
- Only the appraisal desk (not the loan officer or borrower) may communicate with the appraiser regarding revisions.

## Inputs Required

| Input | Source | Description |
|-------|--------|-------------|
| Deficiency Codes | Task_ValidateCompleteness | Specific checklist items that failed |
| Order Confirmation ID | LOS | AMC order reference for the revision |
| Revision Count | LOS | Number of prior revision requests for this engagement |

## Outputs Produced

| Output | Destination | Description |
|--------|-------------|-------------|
| Revision Request | Appraisal Portal / AMC | Structured request identifying deficiencies |
| Status Update | LOS | Appraisal status changed to "Revision Requested" |
| Communication Log Entry | Audit Trail | Record of the revision request for compliance |

## Exception Handling

- **Maximum Revisions Exceeded** -- If this would be the third revision request, block the request and escalate to the Chief Appraiser for a new appraisal order.
- **AMC Communication Failure** -- If the portal is unavailable, queue the revision request and retry per the exponential backoff policy.
- **Value Influence Detected** -- If the composed message is flagged by the compliance filter for value-influencing language, block transmission and route to the appraisal desk for manual review.

## Regulatory Context

Appraiser Independence Requirements prohibit any communication that could be perceived as pressuring the appraiser to reach a predetermined value. The USPAP Ethics Rule further governs communication standards. All revision requests must be factual, specific to report deficiencies, and free of value-related suggestions. The audit trail must capture the exact content of each communication.

## Notes

- Reconsideration of value (ROV) requests are a separate process from completeness-based revision requests and follow different compliance rules.
- Some investors have specific revision request templates that must be used.
