---
capsule_id: "CAP-LO-IDV-001"
bpmn_task_id: "Task_VerifyIdentity"
bpmn_task_name: "Verify Borrower Identity"
bpmn_task_type: "serviceTask"
process_id: "Process_LoanOrigination"
process_name: "Loan Origination"
version: "1.0"
status: "draft"
generated_from: "loan-origination.bpmn"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
last_modified: "2026-04-09T00:00:00Z"
last_modified_by: "MDA Demo"
owner_role: "Automated Systems"
owner_team: "Retail Lending"
domain: "Mortgage Lending"
subdomain: "Identity Verification"
regulation_refs:
  - "USA PATRIOT Act Section 326 (CIP)"
  - "BSA/AML Regulations"
  - "Red Flags Rule (FACTA)"
policy_refs:
  - "POL-LO-010 Customer Identification Program"
  - "POL-LO-011 Anti-Money Laundering Policy"
intent_id: "INT-LO-IDV-001"
contract_id: "ICT-LO-IDV-001"
predecessor_ids:
  - "CAP-LO-APP-001"
successor_ids:
  - "CAP-LO-CRC-001"
---

# Verify Borrower Identity

## Purpose

Perform automated identity verification of the loan applicant to satisfy Customer Identification Program (CIP) requirements under the USA PATRIOT Act and to screen against OFAC sanctions lists.

## Procedure

1. **Extract Identity Data**: Retrieve borrower name, date of birth, SSN, and address from the borrower_profile record.
2. **Government ID Validation**: Submit the borrower's government-issued identification (driver's license, passport, state ID) to the document authentication service for forgery detection and data extraction.
3. **Identity Cross-Reference**: Call the identity verification service to cross-reference borrower-provided data against public records, credit header data, and government databases.
4. **OFAC/Sanctions Screening**: Screen the borrower's name and aliases against the OFAC Specially Designated Nationals (SDN) list and other sanctions databases.
5. **Watchlist Check**: Check the borrower against FinCEN's 314(a) list and internal suspicious activity watchlists.
6. **Score and Decide**: Evaluate the identity verification score. If the score is above the threshold (e.g., 700 out of 1000), mark identity as "Verified." If below threshold, flag for manual review.
7. **Record Results**: Persist the verification results, timestamps, and data sources used to the loan file for audit purposes.

## Business Rules

- All borrowers and co-borrowers must pass CIP verification before the loan can proceed to credit pull.
- OFAC matches result in an immediate hard stop and escalation to the BSA/AML officer.
- Identity verification results are valid for 90 days; after that, re-verification is required.
- A minimum of two independent data sources must confirm the borrower's identity.
- If automated verification fails, manual review by a trained compliance analyst is required within 2 business days.

## Inputs

| Field | Source | Required |
|---|---|---|
| borrower_profile | LOS Database | Yes |
| government_id_image | DocVault | Yes |
| borrower SSN | LOS Database (encrypted) | Yes |

## Outputs

| Field | Destination | Description |
|---|---|---|
| identity_verification_result | LOS Database | Pass/fail/manual-review with confidence score |
| ofac_screening_result | LOS Database | Clear/match/potential-match |
| cip_compliance_record | Compliance Database | Audit record of CIP checks performed |

## Exception Handling

- **OFAC Match**: Immediately halt all processing. Escalate to BSA/AML officer. Do not notify borrower of the match.
- **Low Confidence Score**: Route to compliance analyst for manual identity verification within 2 business days.
- **Service Unavailable**: Retry identity verification service up to 3 times. If still unavailable, queue for next available window and notify loan officer of delay.
