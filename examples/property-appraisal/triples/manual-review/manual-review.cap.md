---
capsule_id: "CAP-PA-MRV-001"
bpmn_task_id: "Task_ManualReview"
bpmn_task_name: "Flag for Manual Review"
bpmn_task_type: "userTask"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"

version: "1.0.0"
status: "draft"

generated_from: "bpmn/property-appraisal.bpmn"
generated_date: "2026-04-09"
generated_by: "mda-pipeline"
last_modified: "2026-04-09"
last_modified_by: "mda-pipeline"

owner_role: "Underwriting Manager"
owner_team: "Underwriting Review"
reviewers:
  - "Chief Appraiser"
  - "Risk Officer"

domain: "Mortgage"
subdomain: "Property Appraisal"
regulation_refs:
  - "USPAP-SR3: Standards Rule 3 - Appraisal Review"
  - "FNMA-B4-1.4: Fannie Mae Appraisal Review Requirements"
policy_refs:
  - "POL-MTG-UW-011: Manual Appraisal Review Escalation Policy"

intent_id: "INT-PA-MRV-001"
contract_id: "ICT-PA-MRV-001"
parent_capsule_id: ""
predecessor_ids:
  - "CAP-PA-ASV-001"
successor_ids: []
exception_ids: []

gaps: []
---

# Flag for Manual Review

## Purpose

When the LTV ratio exceeds program limits or the value assessment identifies risk indicators (excessive adjustments, declining market, value inflation), this task routes the appraisal to a senior underwriter for manual review. Manual review ensures that high-risk collateral situations receive human judgment before the loan proceeds, protecting the lender from potential loss due to overvaluation.

## Procedure

1. Receive the value assessment results including LTV ratio, adjustment flags, and market condition flags.
2. Compile a review package containing the appraisal report PDF, UAD data, comparable sales analysis, LTV calculation, and all risk flags.
3. Assign the review to the next available senior underwriter based on workload and property type expertise.
4. Create a manual review task in the underwriting work queue with priority based on the severity of risk indicators.
5. The underwriter evaluates whether the appraisal supports the loan, requests additional information (e.g., a second appraisal, field review, or desk review), or recommends denial.
6. Record the underwriter's decision, supporting rationale, and any conditions imposed.
7. Route the loan based on the underwriter's decision: approve with conditions, request additional appraisal work, or deny.

## Business Rules

- All loans with LTV exceeding program maximums must receive manual review before proceeding.
- Loans with appraised values more than 15% above the AVM estimate require a second appraisal or field review.
- The underwriter must document the basis for accepting or rejecting the appraised value.
- Manual review must be completed within 2 business days of assignment per underwriting SLA.
- Underwriters reviewing the appraisal must hold a state appraisal reviewer credential or equivalent qualification per USPAP Standards Rule 3.

## Inputs Required

| Input | Source | Description |
|-------|--------|-------------|
| Value Assessment Summary | Task_AssessValue | LTV ratio, determination, adjustment flags, market flags |
| Appraisal Report PDF | Document Management System | Full appraisal report for underwriter review |
| UAD Data | LOS | Structured appraisal data |
| Loan File Summary | LOS | Borrower, property, and loan program details |

## Outputs Produced

| Output | Destination | Description |
|--------|-------------|-------------|
| Review Decision | LOS | Accept, Conditional Accept, Request Additional Work, or Deny |
| Decision Rationale | LOS | Underwriter's written explanation of the decision |
| Conditions List | LOS | Any conditions imposed (e.g., PMI required, reduced loan amount) |
| Review Completion Record | Audit Trail | Timestamp, reviewer identity, and decision for compliance records |

## Exception Handling

- **No Qualified Reviewer Available** -- If no underwriter with the required credentials is available within 4 hours, escalate to the Underwriting Manager for assignment.
- **Underwriter Requests Second Appraisal** -- Initiate a new appraisal order as a separate engagement, following the same ordering process.
- **SLA Breach** -- If the review is not completed within 2 business days, auto-escalate to the Underwriting Manager.

## Regulatory Context

USPAP Standards Rule 3 governs the appraisal review function, requiring that reviewers have competency in the property type and market area. The review must be documented with sufficient detail to support the reviewer's conclusions. Fannie Mae Selling Guide B4-1.4 specifies the lender's responsibility to review appraisals for credibility, accuracy, and adequacy.

## Notes

- Manual review may result in a counteroffer to the borrower (reduced loan amount, higher down payment, PMI requirement).
- Reconsideration of value (ROV) initiated by the borrower with additional comparable sales data may be submitted during the review period.
- The manual review outcome feeds back into the broader loan underwriting decision.
