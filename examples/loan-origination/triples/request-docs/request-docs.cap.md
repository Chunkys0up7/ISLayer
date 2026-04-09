---
capsule_id: "CAP-LO-DOC-001"
bpmn_task_id: "Task_RequestDocs"
bpmn_task_name: "Request Additional Documentation"
bpmn_task_type: "sendTask"
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
regulation_refs:
  - "TILA (Regulation Z) - Timing Requirements"
  - "RESPA (Regulation X)"
policy_refs:
  - "POL-LO-040 Document Request Policy"
  - "POL-LO-041 Borrower Communication Standards"
intent_id: "INT-LO-DOC-001"
contract_id: "ICT-LO-DOC-001"
predecessor_ids:
  - "CAP-LO-DEC-001"
successor_ids:
  - "CAP-LO-DEC-002"
exception_ids:
  - "CAP-LO-TMO-001"
---

# Request Additional Documentation

## Purpose

Send a formal request to the borrower for specific missing or insufficient documents identified during the DTI assessment, providing clear instructions and deadlines for submission.

## Procedure

1. **Compile Missing Items**: Review the `dti_result.missing_documents` list to identify all outstanding documentation needs (e.g., paystubs, W-2s, tax returns, bank statements, gift letters, explanation letters).
2. **Generate Request Letter**: Create a formal document request letter using the approved template, listing each missing item with:
   - Document name and description
   - Acceptable formats (original, copy, digital scan)
   - Specific requirements (date ranges, completeness criteria)
   - Submission deadline (14 calendar days from request date)
3. **Multi-Channel Delivery**: Send the request via the borrower's preferred communication channel (email, secure portal message, or physical mail). Email and portal are primary; physical mail is backup if no electronic contact.
4. **Portal Upload Link**: Generate a secure, time-limited upload link to the borrower portal where documents can be submitted directly to DocVault.
5. **LOS Status Update**: Update the loan status to "Pending Documentation" and log the request details in the loan timeline.
6. **Follow-Up Schedule**: Set automated reminders at day 7 and day 12 if documents have not been received.

## Business Rules

- The borrower must be given at least 14 calendar days to respond to documentation requests.
- A maximum of 3 documentation requests may be sent for the same loan before escalating to a supervisor.
- All communication must include the loan number and loan officer contact information.
- Requests must not disclose the reason for the documentation need (e.g., do not state "your DTI is too high").
- The 14-day timeout boundary event (Boundary_Timeout) will trigger if no response is received.

## Inputs

| Field | Source | Required |
|---|---|---|
| dti_result.missing_documents | LOS Database | Yes |
| borrower contact information | LOS Database | Yes |
| document request template | Template Library | Yes |

## Outputs

| Field | Destination | Description |
|---|---|---|
| document_request_record | LOS Database | Log of request sent, items requested, deadline |
| secure_upload_link | Borrower (via email/portal) | Time-limited upload URL |

## Exception Handling

- **Invalid Borrower Contact Info**: Attempt all available channels. If all fail, notify loan officer for manual follow-up within 1 business day.
- **Template Rendering Error**: Use a plain-text fallback template and alert the template service team.
- **Borrower Opts Out of Electronic Communication**: Send via physical mail and extend the deadline to 21 calendar days to account for postal delays.
