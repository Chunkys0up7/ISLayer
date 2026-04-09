---
capsule_id: "CAP-LO-DEC-001"
bpmn_task_id: "Gateway_Eligible"
bpmn_task_name: "Eligible?"
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
subdomain: "Eligibility Decisioning"
regulation_refs:
  - "ECOA (Equal Credit Opportunity Act)"
  - "QM Rule (Ability-to-Repay)"
policy_refs:
  - "POL-LO-030 DTI Threshold Policy"
  - "POL-LO-070 Eligibility Decision Matrix"
intent_id: "INT-LO-DEC-001"
contract_id: "ICT-LO-DEC-001"
predecessor_ids:
  - "CAP-LO-DTI-001"
successor_ids:
  - "CAP-LO-PKG-001"
  - "CAP-LO-DOC-001"
---

# Loan Eligibility Decision (Gateway: Eligible?)

## Purpose

Evaluate the DTI assessment results and documentation completeness to determine whether the loan application is eligible to proceed to packaging or requires additional documentation.

## Decision Logic

This exclusive gateway evaluates two conditions from the `dti_result` output:

### Path 1: Eligible (to Package Loan)
**Condition**: `dti_result.eligible == true AND dti_result.docs_complete == true`

The loan meets all DTI thresholds for the selected product type and all required documentation is on file. Route to the "Package Loan File" task.

### Path 2: Needs Additional Documentation (to Request Docs)
**Condition**: `dti_result.docs_complete == false`

The DTI assessment identified missing documentation that prevents a definitive eligibility determination, or additional documentation is needed to support compensating factors. Route to the "Request Additional Documentation" task.

## Business Rules

- This gateway does not make a final underwriting decision; it determines processing path eligibility.
- If DTI exceeds standard thresholds but compensating factors exist, additional documentation may be requested to support those factors.
- The gateway must log the decision path taken and the conditions evaluated for audit purposes.
- No manual override is available at this gateway; all routing is based on the dti_result data.
