---
capsule_id: "CAP-PA-VAL-001"
bpmn_task_id: "Task_ValidateCompleteness"
bpmn_task_name: "Validate Appraisal Completeness"
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

owner_role: "Appraisal Desk Supervisor"
owner_team: "Appraisal Management"
reviewers:
  - "Chief Appraiser"
  - "Compliance Officer"

domain: "Mortgage"
subdomain: "Property Appraisal"
regulation_refs:
  - "USPAP-SR2: Standards Rule 2 - Appraisal Reporting Requirements"
  - "FHA-4000.1-D4: FHA Appraisal Report Requirements"
  - "FNMA-B4-1.2: Fannie Mae Appraisal Report Forms and Exhibits"
policy_refs:
  - "POL-MTG-APR-004: Appraisal Completeness Checklist Policy"

intent_id: "INT-PA-VAL-001"
contract_id: "ICT-PA-VAL-001"
parent_capsule_id: ""
predecessor_ids:
  - "CAP-PA-RCV-001"
successor_ids:
  - "CAP-PA-ASV-001"
  - "CAP-PA-REV-001"
exception_ids: []

gaps:
  - "FHA-specific completeness checklist items not yet enumerated -- Chief Appraiser to provide"
---

# Validate Appraisal Completeness

## Purpose

This task applies a structured completeness checklist to the received appraisal report, ensuring that all required sections, signatures, exhibits, and data fields are present before the report proceeds to value assessment. Incomplete reports sent to underwriting cause rework loops and delays. This validation catches deficiencies early, enabling a timely revision request to the appraiser.

## Procedure

1. Load the appraisal report PDF and the parsed UAD XML from the document management system.
2. Execute the completeness checklist against the report, verifying the presence of each required section.
3. Check that the appraiser's certification and signature page is present and signed.
4. Verify that all required photographs are included: front, rear, street scene, and each comparable sale.
5. Confirm that the sketch or floor plan is present and that the gross living area (GLA) calculation is populated.
6. Validate that at least three comparable sales are included with complete data (address, sale price, sale date, adjustments).
7. For FHA loans, verify additional requirements: photographs of deficiencies, well/septic documentation if applicable, and FHA case number on each page.
8. For condominiums, verify that Form 1073 addendum and HOA questionnaire are attached.
9. Record the completeness status (Complete or Incomplete) and, if incomplete, enumerate the specific deficiency codes.
10. Route the report to the appropriate downstream path based on the completeness determination.

## Business Rules

- A report is deemed "Complete" only if every item on the applicable checklist passes.
- Any single missing required section renders the report "Incomplete."
- The appraiser's license must be active and in good standing at the time of the appraisal effective date.
- Comparable sales must have sale dates within 12 months of the appraisal effective date (6 months preferred).
- The reconciled value must be explicitly stated, not merely implied from the comparable grid.
- Photographs must be clear, in color, and taken at the time of inspection (no stock or archival images).

## Inputs Required

| Input | Source | Description |
|-------|--------|-------------|
| Appraisal Report PDF | Document Management System | The stored appraisal report |
| UAD XML Data | LOS | Parsed structured data from the UAD payload |
| Completeness Checklist | Rules Engine | Checklist template for the applicable loan program |
| Loan Program Type | LOS | Determines which checklist variant to apply (Conventional, FHA, VA) |

## Outputs Produced

| Output | Destination | Description |
|--------|-------------|-------------|
| Completeness Status | LOS | "Complete" or "Incomplete" |
| Deficiency Codes | LOS | List of specific checklist items that failed, if any |
| Validation Timestamp | LOS | Date and time the completeness check was executed |
| Routing Decision | Process Engine | Determines whether the report flows to value assessment or revision request |

## Exception Handling

- **Missing Signature Page** -- Mark as incomplete with deficiency code SIGN-001 and route to revision.
- **Insufficient Comparables** -- If fewer than three comparable sales are present, mark as incomplete with code COMP-001.
- **Expired Appraiser License** -- Reject the report entirely and escalate to the Chief Appraiser for a new assignment.
- **Checklist Template Not Found** -- If no checklist exists for the loan program, escalate to the compliance team.

## Regulatory Context

USPAP Standards Rule 2 establishes minimum content requirements for appraisal reports. Fannie Mae Selling Guide B4-1.2 and FHA Handbook 4000.1 Section D4 add investor-specific requirements. The completeness validation must be auditable, showing which checklist was applied, the result of each item, and the identity of the validator (human or system).

## Notes

- Desktop appraisals (Form 1004 Desktop) have a reduced checklist that omits interior photographs and physical inspection items.
- Exterior-only appraisals (Form 2055) also have a modified checklist.
- The checklist should be version-controlled and updated when GSE or FHA guidance changes.
