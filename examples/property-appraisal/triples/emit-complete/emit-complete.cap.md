---
capsule_id: "CAP-PA-NTF-001"
bpmn_task_id: "Task_EmitComplete"
bpmn_task_name: "Emit Appraisal Complete Event"
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

owner_role: "Loan Processing Manager"
owner_team: "Mortgage Origination"
reviewers:
  - "Integration Architect"
  - "Underwriting Manager"

domain: "Mortgage"
subdomain: "Property Appraisal"
regulation_refs:
  - "TRID: TILA-RESPA Integrated Disclosure - Timing Requirements"
policy_refs:
  - "POL-MTG-APR-007: Appraisal Completion Notification Policy"
  - "POL-MTG-DISC-002: Appraisal Delivery to Borrower Policy"

intent_id: "INT-PA-NTF-001"
contract_id: "ICT-PA-NTF-001"
parent_capsule_id: ""
predecessor_ids:
  - "CAP-PA-ASV-001"
successor_ids: []
exception_ids: []

gaps: []
---

# Emit Appraisal Complete Event

## Purpose

This task publishes the appraisal completion event to downstream systems and stakeholders, signaling that the property valuation is finalized and the loan can proceed to the next stage of origination. The event also triggers the regulatory requirement to deliver a copy of the appraisal report to the borrower. Without this notification, the loan underwriting pipeline stalls waiting for appraisal clearance.

## Procedure

1. Compile the appraisal completion summary including the appraised value, LTV ratio, and effective date.
2. Publish an "Appraisal Complete" event to the enterprise event bus with the loan number and completion details.
3. Update the LOS appraisal status to "Complete" with the final appraised value and LTV.
4. Trigger the borrower appraisal delivery workflow to send a copy of the report per ECOA/TRID requirements.
5. Notify the loan officer and underwriter that the appraisal milestone is cleared.
6. If the loan is on a rate lock, check the lock expiration against the appraisal completion date and flag any lock extension needs.
7. Record the completion event in the audit trail with timestamp and event payload.

## Business Rules

- The borrower must receive a copy of the appraisal report at least 3 business days before closing (ECOA requirement).
- The appraisal completion event must include the appraised value, LTV ratio, and any conditions or flags.
- The event must be published within 1 hour of the value assessment completing successfully.
- Rate lock expiration alerts must be generated if the lock expires within 7 business days of completion.

## Inputs Required

| Input | Source | Description |
|-------|--------|-------------|
| Appraised Value | LOS | Final market value from the appraisal |
| LTV Ratio | Task_AssessValue | Calculated loan-to-value ratio |
| LTV Determination | Task_AssessValue | Confirmation that LTV is within program limits |
| Loan Number | LOS | Loan identifier for event correlation |
| Rate Lock Details | LOS | Lock expiration date for alert check |

## Outputs Produced

| Output | Destination | Description |
|--------|-------------|-------------|
| Appraisal Complete Event | Event Bus | Domain event signaling appraisal clearance |
| Borrower Delivery Trigger | Disclosure System | Triggers appraisal report delivery to borrower |
| Status Update | LOS | Appraisal status set to "Complete" |
| Lock Alert | LOS / Loan Officer | Rate lock expiration warning if applicable |
| Completion Audit Record | Audit Trail | Timestamped event record |

## Exception Handling

- **Event Bus Unavailable** -- Queue the event for retry with exponential backoff. The loan status update should still proceed.
- **Borrower Delivery Failure** -- If the disclosure system cannot be reached, flag the loan for manual delivery and alert the loan officer.
- **Rate Lock Expired** -- If the rate lock has already expired, flag the loan for lock extension or re-pricing.

## Regulatory Context

Under ECOA (Equal Credit Opportunity Act) and TRID (TILA-RESPA Integrated Disclosure) rules, the borrower must receive a copy of the appraisal report promptly after completion, and no later than 3 business days before closing. The completion event triggers this delivery workflow. The lender must maintain evidence of timely delivery.

## Notes

- The completion event is consumed by the underwriting pipeline, the closing team, and potentially the investor commitment system.
- For correspondent lending, the appraisal completion may also trigger UCDP submission to Fannie Mae or FHA EAD.
