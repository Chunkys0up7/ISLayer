---
capsule_id: "CAP-LO-SUB-001"
bpmn_task_id: "Task_SubmitUW"
bpmn_task_name: "Submit to Underwriting"
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
owner_role: "Processing Team"
owner_team: "Retail Lending"
domain: "Mortgage Lending"
subdomain: "Underwriting Submission"
regulation_refs:
  - "TRID (TILA-RESPA Integrated Disclosure)"
  - "Fannie Mae Selling Guide"
  - "Freddie Mac Seller/Servicer Guide"
policy_refs:
  - "POL-LO-060 Underwriting Submission Policy"
  - "POL-LO-061 SLA Management Policy"
intent_id: "INT-LO-SUB-001"
contract_id: "ICT-LO-SUB-001"
predecessor_ids:
  - "CAP-LO-PKG-001"
successor_ids: []
---

# Submit to Underwriting

## Purpose

Formally submit the completed, quality-checked loan file package to the underwriting queue for credit decision, routing to the appropriate underwriter based on loan type, amount, and complexity.

## Procedure

1. **Final File Validation**: Perform a final check that the loan package QC status is "pass" and all required documents are present.
2. **Underwriter Assignment**: Route the loan file to the appropriate underwriting queue based on:
   - Loan product type (conventional, FHA, VA, USDA, jumbo)
   - Loan amount (standard vs. high-balance thresholds)
   - Complexity flags (self-employment, multiple properties, non-QM)
3. **Priority Determination**: Assign queue priority based on:
   - Lock expiration date (loans with expiring rate locks get higher priority)
   - Contract deadlines (purchase loans with approaching closing dates)
   - Standard processing order (FIFO within priority tier)
4. **Submission Record**: Create a formal underwriting submission record with:
   - Submission timestamp
   - Assigned queue/underwriter
   - Expected turnaround time based on current queue depth
   - Processor ID and cover memo reference
5. **Status Update**: Update loan status from "Processing" to "Submitted to Underwriting" in LOS.
6. **Stakeholder Notification**: Notify the loan officer and borrower (if configured) that the file has been submitted to underwriting with the expected turnaround time.

## Business Rules

- Only loan files with QC status "pass" may be submitted to underwriting.
- Jumbo loans (above conforming loan limits) must be routed to senior underwriters.
- FHA and VA loans require underwriters with the appropriate DE (Direct Endorsement) or SAR (Staff Appraisal Reviewer) credentials.
- Rate lock expiration within 15 days triggers priority escalation.
- The expected turnaround SLA is 48 hours for standard files, 72 hours for complex files.

## Inputs

| Field | Source | Required |
|---|---|---|
| packaged_loan_file | LOS Database | Yes |
| qc_checklist_result | LOS Database | Yes |
| rate_lock_info | LOS Database | No |

## Outputs

| Field | Destination | Description |
|---|---|---|
| underwriting_submission | Underwriting Queue | Formal submission with assigned queue |
| submission_confirmation | Loan Officer / Borrower | Notification of submission and ETA |

## Exception Handling

- **QC Failure Detected at Submission**: Reject the submission, return to processor with specific deficiencies noted.
- **No Available Underwriter Queue**: Hold in pre-submission buffer, alert underwriting management for capacity planning.
- **Rate Lock Expiring Imminently**: Escalate to underwriting manager for expedited handling.
