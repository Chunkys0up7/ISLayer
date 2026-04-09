---
corpus_id: "CRP-PRC-MTG-007"
title: "Underwriting Submission Procedure"
slug: "underwriting-submission"
doc_type: "procedure"
domain: "Mortgage Lending"
subdomain: "Loan Origination"
tags:
  - "underwriting"
  - "aus"
  - "desktop-underwriter"
  - "loan-prospector"
  - "du-findings"
  - "submission"
  - "conditions"
applies_to:
  process_ids:
    - "Process_LoanOrigination"
  task_types:
    - "userTask"
    - "serviceTask"
    - "businessRuleTask"
  task_name_patterns:
    - "submit.*underwriting"
    - "run.*aus"
    - "run.*du"
    - "run.*lp"
    - "underwriting.*queue"
    - "address.*conditions"
  goal_types:
    - "data_production"
    - "decision"
    - "state_transition"
  roles:
    - "loan_processor"
    - "underwriter"
    - "underwriting_manager"
version: "2.0"
status: "current"
effective_date: "2025-04-01"
review_date: "2026-04-01"
supersedes: null
superseded_by: null
author: "Underwriting Standards Group"
last_modified: "2025-03-28"
last_modified_by: "D. Sullivan"
source: "internal"
source_ref: "SOP-UW-2025-001"
related_corpus_ids:
  - "CRP-PRC-MTG-006"
  - "CRP-RUL-MTG-001"
  - "CRP-RUL-MTG-003"
  - "CRP-DAT-MTG-001"
regulation_refs:
  - "Fannie Mae Selling Guide B3"
  - "Freddie Mac Single-Family Seller/Servicer Guide"
  - "FHA 4000.1"
  - "VA Pamphlet 26-7"
policy_refs:
  - "POL-UW-001"
  - "POL-UW-002"
---

# Underwriting Submission Procedure

## 1. Scope

This procedure governs the preparation, submission, and initial routing of mortgage loan files to the underwriting department. It covers the automated underwriting system (AUS) execution, findings review, pre-submission condition resolution, and queue management for both DU (Desktop Underwriter) and LP (Loan Product Advisor) pathways.

The procedure begins after the loan file has been packaged per CRP-PRC-MTG-006 and ends when the underwriter acknowledges receipt of the submission.

## 2. Prerequisites

| # | Prerequisite | Source |
|---|---|---|
| 1 | Loan file packaged and QC-checked per CRP-PRC-MTG-006 | Processor |
| 2 | Borrower credit report on file within 120-day validity | CRP-PRC-MTG-003 |
| 3 | Verified income and DTI ratios calculated | CRP-PRC-MTG-004 |
| 4 | Property address confirmed and appraisal ordered (or waiver obtained) | LOS |
| 5 | Loan locked or lock-pending (rate lock status documented) | Secondary marketing |
| 6 | LOS data entry complete and validated | Processor |

## 3. Procedure Steps

### Step 1: Run the Automated Underwriting System (AUS)

1.1. Select the appropriate AUS based on the loan program and investor requirements:

| Loan Program | Primary AUS | Secondary AUS |
|-------------|-------------|---------------|
| Conventional (Fannie Mae) | Desktop Underwriter (DU) | N/A |
| Conventional (Freddie Mac) | Loan Product Advisor (LP) | N/A |
| FHA | DU (with FHA TOTAL Scorecard) | Manual underwriting |
| VA | DU or LP (with VA module) | Manual underwriting |
| USDA | GUS (Guaranteed Underwriting System) | Manual underwriting |

1.2. Verify that all required data fields are populated in the LOS before submitting to the AUS. Common fields that cause AUS errors if missing:
- Complete borrower demographics (name, SSN, DOB)
- All liability accounts from credit report
- Property information (address, type, occupancy, estimated value)
- Loan terms (amount, rate, term, program code)
- All income sources

1.3. Submit the loan data to the AUS through the LOS integration. The system will process the data and return findings within minutes.

1.4. Document the AUS submission with:
- Submission date and time
- AUS case/file ID number
- LOS submission reference number

### Step 2: Review AUS Findings

2.1. Upon receipt of AUS findings, review the recommendation:

**DU Recommendations:**
| Recommendation | Meaning | Action |
|---------------|---------|--------|
| Approve/Eligible | Loan meets DU risk assessment standards | Proceed with submission; address DU conditions |
| Approve/Ineligible | Risk assessment passes but loan has an eligibility issue | Resolve eligibility issue (LTV, property type, etc.) and resubmit |
| Refer/Eligible | Requires manual underwriting; loan is eligible for the program | Route to manual underwriting queue |
| Refer with Caution | Significant risk factors identified | Consider restructuring or alternative program |
| Out of Scope | Loan characteristics outside DU parameters | Must be manually underwritten |

**LP Recommendations:**
| Recommendation | Meaning | Action |
|---------------|---------|--------|
| Accept | Loan meets LP risk assessment standards | Proceed with submission; address LP conditions |
| Caution | Additional review warranted | Review risk factors; consider manual UW or restructure |
| Not Accepted | Does not meet LP standards | Restructure loan or route to manual underwriting |

2.2. Review the AUS conditions list. Conditions are categorized as:
- **Prior to Approval (PTA):** Must be cleared before the underwriter can approve
- **Prior to Closing (PTC):** Must be cleared before the loan can close
- **Prior to Funding (PTF):** Must be cleared before disbursement

2.3. For each AUS condition, determine:
- Is the documentation already in the file?
- Can it be obtained from existing sources (credit report, LOS data)?
- Does it require additional borrower documentation?
- Is it a system-generated condition that can be cleared with existing information?

### Step 3: Address Pre-Submission Conditions

3.1. Resolve as many AUS conditions as possible before submitting to the underwriter. Common pre-submission resolutions:

| Condition | Resolution |
|-----------|-----------|
| "Verify employment" | Attach completed VOE or TWN verification |
| "Verify deposits in excess of X" | Attach bank statements with large deposit explanations |
| "Provide evidence of mortgage payments" | Attach mortgage statement or VOM |
| "Verify rent payments" | Attach cancelled checks or landlord VOR |
| "Provide explanation for credit inquiries" | Attach borrower's letter of explanation |
| "Verify source of funds for down payment" | Attach asset statements tracing funds |

3.2. If a condition requires additional borrower documentation that is not currently available, note it in the transmittal summary as an outstanding condition. Do not hold submission solely for non-critical conditions, as this delays the underwriting pipeline.

3.3. For conditions that require AUS resubmission (e.g., corrected loan data, updated credit report), run the AUS again and verify the findings before proceeding. Each AUS resubmission should result in equal or better findings.

3.4. If the AUS recommendation is "Refer" or "Not Accepted" and the processor believes the loan is viable, escalate to the underwriting manager to determine if manual underwriting is appropriate. Document the rationale for the manual UW request.

### Step 4: Prepare the Underwriting Submission Summary

4.1. Finalize the processor transmittal summary (initially drafted in CRP-PRC-MTG-006, Step 4). Add the following underwriting-specific items:

- AUS recommendation and case ID
- Summary of AUS conditions and their resolution status
- Outstanding conditions that require underwriter attention
- Any compensating factors for DTI or credit exceptions (per CRP-PRC-MTG-004)
- Rate lock expiration date (if applicable)
- Contract closing date (if purchase transaction)
- Any time-sensitive items requiring priority handling

4.2. Assign a submission priority based on the following criteria:

| Priority | Criteria | Target UW Turn Time |
|----------|----------|-------------------|
| Rush | Rate lock expiring within 5 days or contract closing within 7 days | 24 hours |
| High | Rate lock expiring within 10 days or contract closing within 14 days | 48 hours |
| Standard | No imminent deadlines | 72 hours |
| Low | Pre-approval or early-stage file | 5 business days |

### Step 5: Route to Underwriter Queue

5.1. Submit the completed loan file to the underwriting queue through the LOS workflow. The system will:
- Validate that required sections of the LOS are complete
- Check that the AUS findings are on file
- Assign a queue position based on priority and submission time
- Route to the appropriate underwriter queue based on:
  - Loan program (Conventional, FHA, VA, USDA)
  - Loan amount (jumbo loans may require senior underwriters)
  - Complexity level (self-employment, non-traditional credit, etc.)
  - Underwriter specialization and current workload

5.2. For delegated underwriting (where the company has DE authority for FHA or SAR authority for VA), route to an underwriter with the appropriate designation:
- FHA loans: Must be reviewed by a DE (Direct Endorsement) underwriter
- VA loans: Must be reviewed by a SAR (Staff Appraisal Reviewer) or VA-certified underwriter
- Conventional: Any certified underwriter

5.3. If the file requires a specific underwriter due to resubmission (returning from a prior suspension or condition clearing), route directly to the original underwriter.

### Step 6: Acknowledge Receipt

6.1. The underwriting queue manager (or automated system) will acknowledge receipt of the submission by:
- Updating the loan status in the LOS to "In Underwriting"
- Assigning a specific underwriter to the file
- Setting the expected decision date based on the priority and queue position
- Sending a receipt notification to the submitting processor

6.2. The processor should verify receipt acknowledgment within one business day of submission. If no acknowledgment is received, follow up with the underwriting queue manager.

6.3. Document the following in the loan file:
- Underwriting submission date and time
- Assigned underwriter name
- Expected decision date
- Any special instructions or escalation notes

## 4. Quality Checks

| Check | Criteria | Action if Failed |
|-------|----------|-----------------|
| AUS recommendation | DU Approve/Eligible or LP Accept | Investigate findings; resubmit or route to manual UW |
| AUS data accuracy | Loan data in AUS matches loan file | Correct data and resubmit AUS |
| Condition pre-clearing | All resolvable conditions addressed | Clear conditions before submission |
| File completeness | Packaged per CRP-PRC-MTG-006 | Complete packaging before submission |
| Priority accuracy | Correct priority assigned per criteria | Adjust priority level |
| Routing accuracy | Correct queue/underwriter assignment | Reroute to appropriate queue |

## 5. Common Pitfalls

1. **Submitting with outdated AUS findings.** If the loan data has changed since the last AUS run (income, liabilities, loan amount, property value), the findings are no longer valid. Always rerun AUS after material changes.

2. **Not resolving conditions that are easily clearable.** Submitting a file with 15 AUS conditions when 10 of them could be cleared with existing documentation wastes underwriter time and increases turn times.

3. **Incorrect priority assignment.** Over-prioritizing files disrupts the queue for everyone. Only use Rush or High priority when rate lock or contract deadlines genuinely warrant it.

4. **Submitting refer/caution files without manager approval.** Files that receive a Refer or Caution finding from the AUS should not be submitted to the standard queue without underwriting manager review and approval for manual underwriting.

5. **Missing the resubmission context.** When a file is being resubmitted after a prior suspension or conditions return, always route to the original underwriter and clearly document what has changed since the prior review.

## 6. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.0 | 2025-03-28 | D. Sullivan | Added LP pathway; updated priority matrix; revised routing criteria |
| 1.5 | 2024-10-01 | D. Sullivan | Added pre-submission condition clearing requirements |
| 1.0 | 2023-05-01 | Underwriting Standards Group | Initial release |
