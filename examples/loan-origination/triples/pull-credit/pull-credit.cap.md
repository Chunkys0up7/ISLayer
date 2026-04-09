---
capsule_id: "CAP-LO-CRC-001"
bpmn_task_id: "Task_PullCredit"
bpmn_task_name: "Pull Credit Report"
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
subdomain: "Credit Analysis"
regulation_refs:
  - "FCRA (Fair Credit Reporting Act)"
  - "Regulation V"
policy_refs:
  - "POL-LO-020 Credit Report Ordering Policy"
  - "POL-LO-021 Permissible Purpose Policy"
intent_id: "INT-LO-CRC-001"
contract_id: "ICT-LO-CRC-001"
predecessor_ids:
  - "CAP-LO-IDV-001"
successor_ids:
  - "CAP-LO-DTI-001"
---

# Pull Credit Report

## Purpose

Obtain a tri-merge credit report from the three major credit bureaus (Equifax, Experian, TransUnion) for the borrower, producing a consolidated credit profile with scores, tradelines, and public records.

## Procedure

1. **Permissible Purpose Confirmation**: Verify that a valid permissible purpose exists (signed loan application with credit authorization).
2. **Credit Authorization Check**: Confirm borrower has signed the credit authorization form and it is on file in DocVault.
3. **Tri-Merge Request**: Submit a tri-merge credit report request to the credit reporting agency (CRA) integration service using borrower SSN, name, DOB, and current address.
4. **Report Receipt and Parsing**: Receive the merged credit report in MISMO XML format and parse into structured data: FICO scores (per bureau), tradeline history, public records, inquiries, and collections.
5. **Representative Score Selection**: Select the representative credit score per GSE guidelines: for a single borrower, use the middle of three scores (or lower of two); for multiple borrowers, use the lower of the representative scores.
6. **Fraud Alert Check**: Check if any bureau returned a fraud alert or active duty alert. If so, flag for manual handling.
7. **Report Storage**: Store the full credit report in DocVault with appropriate access controls and link to the loan file.

## Business Rules

- Credit reports may only be pulled with a valid permissible purpose under FCRA.
- The credit authorization form must be dated within 120 days of the credit pull.
- If the borrower has a credit freeze at any bureau, the loan officer must be notified to coordinate a temporary lift.
- Credit reports are valid for 120 days from the date of pull for conventional loans; 90 days for FHA/VA.
- Duplicate credit pulls for the same borrower within 10 days should reuse the existing report.

## Inputs

| Field | Source | Required |
|---|---|---|
| borrower_profile (SSN, name, DOB, address) | LOS Database | Yes |
| credit_authorization | DocVault | Yes |

## Outputs

| Field | Destination | Description |
|---|---|---|
| credit_report | DocVault / LOS Database | Full tri-merge credit report |
| credit_scores | LOS Database | FICO scores from each bureau |
| representative_score | LOS Database | Selected representative score per GSE rules |
| tradeline_summary | LOS Database | Summary of open/closed tradelines |

## Exception Handling

- **Credit Freeze**: Notify loan officer. Provide instructions for borrower to temporarily lift freeze. Pause until resolved.
- **Bureau Unavailable**: If one bureau is unavailable, proceed with a bi-merge and flag the file for follow-up within 48 hours.
- **Fraud Alert on File**: Route to fraud investigation team. Do not proceed with loan processing until cleared.
