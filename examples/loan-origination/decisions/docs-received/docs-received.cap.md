---
capsule_id: "CAP-LO-DEC-002"
bpmn_task_id: "Gateway_DocsReceived"
bpmn_task_name: "Docs Received?"
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
owner_role: "Loan Officer"
owner_team: "Retail Lending"
domain: "Mortgage Lending"
subdomain: "Document Collection"
policy_refs:
  - "POL-LO-040 Document Request Policy"
intent_id: "INT-LO-DEC-002"
contract_id: "ICT-LO-DEC-002"
predecessor_ids:
  - "CAP-LO-DOC-001"
successor_ids:
  - "CAP-LO-DTI-001"
---

# Docs Received Decision (Gateway: Docs Received?)

## Purpose

Evaluate whether the borrower has submitted the requested additional documentation within the allowed timeframe, determining whether to loop back to DTI assessment or reject the application.

## Decision Logic

This exclusive gateway checks the document submission status after the documentation request was sent.

### Path 1: Documents Received (loop back to Assess DTI)
**Condition**: `docs_received == true`

The borrower has submitted all requested documents within the deadline. The documents have been uploaded to DocVault and the checklist has been updated. Route back to the "Assess Debt-to-Income Ratio" task for re-evaluation with the new documentation.

### Path 2: Documents Not Received (to Application Rejected)
**Condition**: `docs_received == false`

The borrower has not submitted the required documents, and the documentation request has expired or been explicitly declined by the borrower. Route to the "Application Rejected" end event.

## Business Rules

- Partial document submission is treated as `docs_received == false` unless all critical items are present.
- The loan officer may grant a one-time extension of 7 calendar days if the borrower requests it (this resets the timer but does not change the gateway logic).
- If the borrower explicitly withdraws the application, set `docs_received == false` and proceed to rejection.
- The rejection path triggers an adverse action notice if required by ECOA.
