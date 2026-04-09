---
capsule_id: "CAP-PA-RCV-001"
bpmn_task_id: "Task_ReceiveReport"
bpmn_task_name: "Receive Appraisal Report"
bpmn_task_type: "receiveTask"
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
  - "Loan Processing Manager"
  - "Compliance Officer"

domain: "Mortgage"
subdomain: "Property Appraisal"
regulation_refs:
  - "USPAP-SR2: Standards Rule 2 - Real Property Appraisal Reporting"
  - "UCDP: Uniform Collateral Data Portal Submission Requirements"
policy_refs:
  - "POL-MTG-APR-003: Appraisal Report Receipt and Logging Policy"

intent_id: "INT-PA-RCV-001"
contract_id: "ICT-PA-RCV-001"
parent_capsule_id: ""
predecessor_ids:
  - "CAP-PA-ORD-001"
  - "CAP-PA-REV-001"
successor_ids:
  - "CAP-PA-VAL-001"
exception_ids: []

gaps: []
---

# Receive Appraisal Report

## Purpose

This task captures the completed appraisal report delivered by the AMC or appraiser and logs it into the loan file. Timely receipt and proper indexing of the appraisal report is essential to maintaining the loan timeline and ensuring the report is available for completeness validation and value assessment downstream.

## Procedure

1. Monitor the Appraisal Portal for inbound report deliveries matching open order confirmation IDs.
2. Upon receipt, extract the report PDF and the MISMO UAD (Uniform Appraisal Dataset) XML payload.
3. Validate the file integrity (non-corrupt PDF, well-formed XML) and confirm the order confirmation ID matches an active loan.
4. Parse key header fields from the UAD XML: appraised value, effective date, appraiser license number, and property address.
5. Store the appraisal report PDF and UAD XML in the document management system, indexed to the loan number.
6. Update the LOS appraisal status from "Ordered" to "Report Received" with the receipt timestamp.
7. If this is a revised report (responding to a revision request), link it to the prior report version and the revision request record.
8. Notify the appraisal desk that the report is ready for completeness validation.

## Business Rules

- Reports must be received in both PDF and UAD XML format; PDF-only deliveries are flagged as incomplete.
- The appraiser license number in the report must be validated against the state licensing board registry.
- Reports received after the estimated completion date trigger an SLA breach notification.
- Revised reports must reference the original order confirmation ID and prior report version.
- The report effective date must be within 120 days of the loan closing date for conventional loans, 180 days for FHA.

## Inputs Required

| Input | Source | Description |
|-------|--------|-------------|
| Appraisal Report PDF | AMC / Appraisal Portal | The completed USPAP-compliant appraisal report |
| UAD XML Payload | AMC / Appraisal Portal | MISMO-formatted Uniform Appraisal Dataset |
| Order Confirmation ID | AMC / Appraisal Portal | Reference ID linking the report to the original order |
| Active Order Records | LOS | Open appraisal orders awaiting report delivery |

## Outputs Produced

| Output | Destination | Description |
|--------|-------------|-------------|
| Indexed Report PDF | Document Management System | Appraisal report stored and linked to the loan file |
| Parsed Report Header | LOS | Appraised value, effective date, appraiser info extracted from UAD XML |
| Status Update | LOS | Appraisal status changed to "Report Received" |
| Receipt Notification | Appraisal Desk | Alert that the report is ready for validation |

## Exception Handling

- **Corrupt or Unreadable PDF** -- Reject the delivery, log the error, and send an automated re-delivery request to the AMC.
- **UAD XML Schema Validation Failure** -- Flag the report for manual data entry of header fields and notify the AMC of the XML defect.
- **Orphaned Report** -- If the order confirmation ID does not match any active loan, quarantine the report and alert the appraisal desk.
- **SLA Breach** -- If the report arrives past the estimated completion date, automatically escalate to the AMC relationship manager.

## Regulatory Context

USPAP Standards Rule 2 governs the content and format of appraisal reports. The UCDP submission requirement mandates that all GSE-eligible loans have appraisal data submitted in UAD XML format. The receipt logging must maintain an audit trail showing when the report was received and by whom, supporting examiner review of turnaround times and appraiser independence.

## Notes

- Some AMCs deliver reports via email with PDF attachments rather than through the portal API; these must be manually uploaded.
- Hybrid appraisals and desktop appraisals may have different XML schemas than traditional URAR reports.
