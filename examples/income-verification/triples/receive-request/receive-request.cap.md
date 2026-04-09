---
capsule_id: "CAP-IV-REQ-001"
bpmn_task_id: "Task_ReceiveRequest"
bpmn_task_name: "Receive Verification Request"
bpmn_task_type: "receiveTask"
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
  - "Fannie Mae Selling Guide B3-3.1 (Employment and Other Sources of Income)"
  - "FHA Handbook 4000.1 Section II.A.4.c"
  - "GLBA (Gramm-Leach-Bliley Act)"
  - "ECOA (Equal Credit Opportunity Act)"
policy_refs:
  - "POL-IV-001 Income Verification Request Acceptance Policy"
  - "POL-IV-002 Borrower PII Handling Policy"
intent_id: "INT-IV-REQ-001"
contract_id: "ICT-IV-REQ-001"
parent_capsule_id: null
predecessor_ids: []
successor_ids:
  - "CAP-IV-CLS-001"
exception_ids: []
gaps:
  - type: "missing_detail"
    description: "Co-borrower income verification request handling not specified in BPMN"
    severity: "medium"
---

# Receive Verification Request

## Purpose

Receives and validates an inbound income verification request originating from the Loan Origination System (LOS). This task acts as the entry point for the verification workflow, ensuring all required borrower data and document references are present before downstream processing begins.

## Procedure

1. **Accept Inbound Message**: Listen for a `VerificationRequest` message on the configured message channel (queue or topic). The message contains the loan application ID, borrower identifier, and a list of document references.

2. **Validate Request Payload**: Confirm the presence of required fields:
   - `loanApplicationId` (string, non-empty)
   - `borrowerId` (string, non-empty)
   - `requestedBy` (string, the underwriter or system principal)
   - `documentRefs` (array, at least one reference to a tax return or W-2)
   - `loanProgram` (enum: FHA, CONV, VA, USDA)

3. **Retrieve Borrower Profile**: Call the LOS Borrower API to fetch the full borrower profile, including employment history, stated income, and SSN (masked). Store the result in the `borrower_profile` data object.

4. **Verify Document Availability**: For each document reference in the request, confirm the document exists in the Document Vault (DocVault) and has a status of `AVAILABLE` or `VERIFIED`. Flag any documents with status `PENDING_UPLOAD` as incomplete.

5. **Emit Acknowledgement**: Publish a `VerificationRequestAcknowledged` event back to the LOS with a correlation ID and estimated processing time.

6. **Reject if Invalid**: If validation fails (missing fields, unavailable documents), reject the request with error code `ERR_REQ_INVALID` and do not proceed to classification.

## Business Rules

- Verification must comply with Fannie Mae Selling Guide B3-3.1 (Employment and Other Sources of Income) and FHA Handbook 4000.1 Section II.A.4.c.
- All PII access must be logged per GLBA and ECOA requirements.
- The LOS has already performed preliminary borrower identity verification (KYC).
- Document references in the request correspond to objects already uploaded to DocVault.
- The message broker guarantees at-least-once delivery.

## Inputs

| Field | Source | Required |
|---|---|---|
| loanApplicationId | LOS | Yes |
| borrowerId | LOS | Yes |
| requestedBy | LOS | Yes |
| documentRefs | LOS | Yes |
| loanProgram | LOS | Yes |

## Outputs

| Field | Destination | Description |
|---|---|---|
| borrower_profile | Process Context | Full borrower profile including employment history and stated income |
| acknowledgement | LOS | Confirmation that the request was received with correlation ID |
| validation_errors | LOS | (Conditional) List of validation failures if request is rejected |

## Exception Handling

- **Invalid Request**: If required fields are missing or malformed, reject with `ERR_REQ_INVALID` and return field-level errors.
- **Documents Unavailable**: If all document references have status other than AVAILABLE/VERIFIED, reject with `ERR_REQ_DOC_UNAVAILABLE`.
- **Borrower Not Found**: If borrowerId does not exist in LOS, reject with `ERR_REQ_BORROWER_NOT_FOUND`.
- **Unauthorized Request**: If requesting principal lacks required role, reject with `ERR_REQ_UNAUTHORIZED`.
