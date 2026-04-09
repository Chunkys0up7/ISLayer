---
capsule_id: "CAP-LO-TMO-001"
bpmn_task_id: "Boundary_Timeout"
bpmn_task_name: "Timeout - No Response"
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
subdomain: "Application Management"
regulation_refs:
  - "ECOA (Adverse Action Notice Requirements)"
  - "Regulation B"
policy_refs:
  - "POL-LO-040 Document Request Policy"
  - "POL-LO-080 Application Withdrawal Policy"
intent_id: "INT-LO-TMO-001"
contract_id: "ICT-LO-TMO-001"
predecessor_ids:
  - "CAP-LO-DOC-001"
successor_ids: []
---

# Timeout - No Response (Boundary Event)

## Purpose

Handle the expiration of the 14-day documentation response deadline attached to the "Request Additional Documentation" task. When the timer fires, the borrower has not submitted the requested documents within the allowed timeframe, and the application is moved toward rejection.

## Procedure

1. **Timer Expiration Detection**: The boundary timer event fires after 14 calendar days (P14D) from the documentation request date.
2. **Cancel Active Request**: Cancel the active documentation request task (cancelActivity=true on the boundary event).
3. **Status Update**: Update the loan status to "Withdrawn - Documentation Timeout" in the LOS.
4. **Adverse Action Determination**: Evaluate whether an adverse action notice is required under ECOA/Regulation B:
   - If the application was a completed application (all initial required info was present), an adverse action notice is required within 30 days.
   - If the application was incomplete, a notice of incompleteness is required instead.
5. **Notification**: Send the borrower a notification that the application has been withdrawn due to non-receipt of requested documentation, with instructions on how to reapply.
6. **Record Closure**: Close the loan file with the reason "Documentation Timeout" and archive per retention policy.

## Business Rules

- The 14-day timer is non-negotiable once it fires; however, the loan officer may extend the deadline before it expires by resetting the timer.
- Applications withdrawn due to timeout must still comply with HMDA reporting requirements if they were reportable.
- The borrower may reapply at any time; the withdrawn application does not create a cooling-off period.
- All timeout events must be logged for fair lending monitoring to ensure no disparate impact in documentation request patterns.

## Inputs

| Field | Source | Required |
|---|---|---|
| document_request_record | LOS Database | Yes |
| loan_application | LOS Database | Yes |
| borrower contact information | LOS Database | Yes |

## Outputs

| Field | Destination | Description |
|---|---|---|
| withdrawal_record | LOS Database | Reason, timestamp, and disposition |
| adverse_action_notice (if applicable) | Borrower (mail) | ECOA-required notice |
| borrower_notification | Borrower (email/mail) | Withdrawal notification with reapply instructions |

## Exception Handling

- **Adverse Action Notice Failure**: If the notice cannot be generated or delivered, escalate to compliance for manual handling within 24 hours.
- **Concurrent Document Upload**: If the borrower uploads documents at nearly the same time the timer fires, check for a race condition. If documents were received before the timer event was processed, cancel the timeout and proceed normally.
