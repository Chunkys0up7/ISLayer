---
capsule_id: "CAP-LO-APP-001"
bpmn_task_id: "Task_ReceiveApplication"
bpmn_task_name: "Receive Loan Application"
bpmn_task_type: "receiveTask"
process_id: "Process_LoanOrigination"
process_name: "Loan Origination"
version: "1.0"
status: "draft"
generated_from: "loan-origination.bpmn"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
last_modified: "2026-04-09T00:00:00Z"
last_modified_by: "MDA Demo"
owner_role: "Loan Officer"
owner_team: "Retail Lending"
domain: "Mortgage Lending"
subdomain: "Application Intake"
regulation_refs:
  - "TILA (Truth in Lending Act)"
  - "ECOA (Equal Credit Opportunity Act)"
  - "HMDA (Home Mortgage Disclosure Act)"
policy_refs:
  - "POL-LO-001 Application Acceptance Policy"
  - "POL-LO-002 Borrower Data Handling Policy"
intent_id: "INT-LO-APP-001"
contract_id: "ICT-LO-APP-001"
predecessor_ids: []
successor_ids:
  - "CAP-LO-IDV-001"
gaps:
  - type: "missing_detail"
    description: "Co-borrower handling not specified in BPMN"
    severity: "medium"
---

# Receive Loan Application

## Purpose

Capture and validate an incoming residential mortgage loan application from a borrower, creating the initial loan file and borrower profile record in the Loan Origination System (LOS).

## Procedure

1. **Application Receipt**: Accept the loan application via one of the approved channels (online portal, branch walk-in, broker submission, or telephone).
2. **Preliminary Validation**: Confirm that all mandatory fields are populated: borrower name, SSN, property address, loan amount requested, loan purpose (purchase/refinance), and employment information.
3. **Duplicate Check**: Query the LOS for existing applications from the same borrower (SSN match) within the past 90 days to prevent duplicate submissions.
4. **Loan File Creation**: Generate a unique Loan Number and create the initial loan record in the LOS with status "Application Received."
5. **Borrower Profile Assembly**: Extract borrower demographics, employment, income, and asset declarations into a structured borrower profile object.
6. **Document Checklist Generation**: Based on the loan type (conventional, FHA, VA, USDA) and borrower profile, produce the required document checklist.
7. **Acknowledgment**: Send the borrower a receipt confirmation with the Loan Number and next-steps summary within 3 business days per TILA requirements.

## Business Rules

- Applications must be accepted regardless of borrower race, color, religion, national origin, sex, marital status, or age (ECOA compliance).
- Loan Number format: `LN-YYYY-NNNNNNN` (year + 7-digit sequence).
- Applications older than 120 days without progression must be automatically withdrawn.
- HMDA data fields must be captured at intake for reportable applications.

## Inputs

| Field | Source | Required |
|---|---|---|
| Loan application form (1003/URLA) | Borrower / Broker | Yes |
| Borrower identification documents | Borrower | Yes |
| Property address and estimated value | Borrower | Yes |

## Outputs

| Field | Destination | Description |
|---|---|---|
| loan_application | LOS Database | Structured loan application record |
| borrower_profile | LOS Database | Borrower demographic and financial profile |
| document_checklist | LOS Database | Required documents list based on loan type |
| application_receipt | Borrower (email/mail) | Confirmation of receipt |

## Exception Handling

- **Incomplete Application**: If mandatory fields are missing, place the application in "Pending - Incomplete" status and notify the borrower of required fields within 24 hours.
- **Duplicate Detected**: Flag the application and route to a senior loan officer for manual review before proceeding.
- **System Unavailable**: Queue the application in the intake buffer and process within the next batch window (max 4-hour delay).
