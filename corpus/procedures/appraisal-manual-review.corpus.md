---
corpus_id: "CRP-PRC-PA-005"
title: "Appraisal Manual Review Procedure"
slug: "appraisal-manual-review"
doc_type: "procedure"
domain: "Mortgage Lending"
subdomain: "Property Appraisal"
tags:
  - "manual-review"
  - "senior-underwriter"
  - "ltv-override"
  - "exception-approval"
  - "escalation"
applies_to:
  process_ids:
    - "Process_PropertyAppraisal"
    - "Process_UnderwritingEscalation"
  task_types:
    - "userTask"
  task_name_patterns:
    - "manual.*review"
    - "escalate.*appraisal"
    - "senior.*review"
    - "override.*ltv"
  goal_types:
    - "decision"
    - "exception_handling"
  roles:
    - "senior_underwriter"
    - "chief_appraiser"
    - "credit_committee"
version: "1.0"
status: "current"
effective_date: "2025-06-01"
review_date: "2026-06-01"
supersedes: null
superseded_by: null
author: "Appraisal Operations Committee"
last_modified: "2025-05-18"
last_modified_by: "T. Washington"
source: "internal"
source_ref: "SOP-PA-2025-005"
related_corpus_ids:
  - "CRP-PRC-PA-003"
  - "CRP-PRC-PA-004"
  - "CRP-RUL-PA-002"
regulation_refs:
  - "Fannie Mae Selling Guide B4-1.4-01"
  - "FHA 4000.1 II.D.3"
policy_refs:
  - "POL-PA-001"
  - "POL-UW-003"
---

# Appraisal Manual Review Procedure

## 1. Scope

This procedure governs the escalated manual review of appraisals that cannot be resolved through standard review and revision request processes. It applies when an appraisal presents unresolved value concerns, significant condition issues, or requires LTV override consideration. Manual review is performed by senior underwriters or the chief appraiser and may involve credit committee approval for exceptions.

## 2. Prerequisites

| # | Prerequisite | Source |
|---|---|---|
| 1 | Standard appraisal review completed per CRP-PRC-PA-002 | Appraisal review worksheet |
| 2 | Value assessment completed per CRP-PRC-PA-003 | Underwriting worksheet |
| 3 | Revision request process exhausted or deemed inappropriate per CRP-PRC-PA-004 | Revision request log |
| 4 | Escalation reason documented | Underwriter escalation form |
| 5 | Complete loan file available for holistic review | Loan file |

## 3. Procedure Steps

### Step 1: Senior Underwriter Review

1.1. The escalation is assigned to a senior underwriter (minimum Level III designation) or the chief appraiser based on the escalation reason:

| Escalation Reason | Assigned Reviewer |
|---|---|
| Value dispute (appraised value vs. purchase price) | Senior Underwriter III+ |
| LTV override request | Senior Underwriter IV or Chief Appraiser |
| Property condition C5/C6 | Senior Underwriter III+ with property specialty |
| Comparable adjustment thresholds exceeded | Senior Underwriter III+ |
| Second appraisal conflicts with first | Chief Appraiser |
| Suspected misrepresentation or fraud | Chief Appraiser + Compliance |

1.2. The senior reviewer conducts an independent analysis including:
- Re-examination of all comparable sales used in the appraisal
- Independent comparable search using MLS, public records, and AVM tools
- Review of market trends specific to the subject property's micro-market
- Assessment of the appraisal methodology and any departure from standard practices
- Evaluation of whether the appraiser's conclusions are reasonable given the available data

1.3. The senior reviewer documents their independent value conclusion and compares it to the appraised value. If the values are within 5%, the appraised value is generally considered supportable.

### Step 2: Assess LTV Override Conditions

2.1. If the escalation involves an LTV override request (loan amount exceeds the maximum LTV for the program based on the appraised value), evaluate the following override eligibility criteria:

| Criterion | Requirement | Documentation |
|---|---|---|
| Borrower credit score | Minimum 720 FICO (middle score) | Credit report |
| Debt-to-income ratio | Maximum 36% total DTI | Income/debt documentation |
| Reserves | Minimum 12 months PITIA | Asset verification |
| Payment history | No 30-day lates in 24 months on any mortgage | Credit report |
| LTV excess | Maximum 3% above program limit | Appraisal + loan terms |
| Property type | SFR or condo only (no 2-4 unit or manufactured) | Appraisal |
| Occupancy | Primary residence only | Loan application |

2.2. LTV overrides are NOT permitted for:
- Investment properties
- Cash-out refinance transactions
- Manufactured housing
- Properties in declining markets
- Loans with layered risk factors (low credit score + high DTI + limited reserves)
- LTV excess greater than 3% above program maximum

2.3. If override criteria are met, proceed to Step 3 for borrower qualification review.

### Step 3: Review Borrower Qualifications for Exception

3.1. Perform a holistic assessment of the borrower's profile to determine whether compensating factors justify the exception:

| Compensating Factor | Weight | Evidence |
|---|---|---|
| High credit score (740+) | Strong | Credit report |
| Substantial reserves (24+ months) | Strong | Asset verification |
| Low DTI (<30%) | Strong | Income documentation |
| Long employment tenure (5+ years same employer) | Moderate | Employment verification |
| Significant equity in other properties | Moderate | Real estate owned schedule |
| Prior homeownership with clean mortgage history | Moderate | Credit report |
| Down payment from own funds (not gift) | Moderate | Source of funds documentation |
| Stable or increasing income trend | Moderate | Tax returns / pay stubs |

3.2. The exception requires a minimum of 3 compensating factors, including at least 1 rated "Strong."

3.3. Assess the combined risk profile. Even with compensating factors, the exception may be denied if:
- Multiple risk layers are present (even if each individually qualifies)
- Market conditions in the subject area are deteriorating
- The property type has limited marketability
- The borrower's income stability is uncertain

### Step 4: Document Rationale

4.1. Complete the Appraisal Exception Request Form (Form AER-200) with:
- Executive summary of the escalation reason
- Senior reviewer's independent value analysis and conclusion
- Comparison of appraised value to independent findings
- LTV override calculation (if applicable)
- Compensating factors analysis with supporting documentation
- Risk assessment narrative
- Recommendation (approve, approve with conditions, or deny)

4.2. The rationale must be sufficient for regulatory audit. It must demonstrate:
- Objective analysis based on market data
- No influence from loan production staff on the value conclusion
- Compliance with appraiser independence requirements
- Sound credit judgment supported by documented compensating factors

### Step 5: Approve or Deny with Conditions

5.1. Approval authority matrix:

| Exception Type | Approval Authority | Additional Requirements |
|---|---|---|
| Value accepted within 5% of independent analysis | Senior Underwriter III+ | Documented rationale |
| LTV override (1-2% above program max) | Senior Underwriter IV | Documented rationale + 2nd level review |
| LTV override (2-3% above program max) | Chief Appraiser | Credit committee notification |
| Property condition exception (C5) | Senior Underwriter IV | Repair escrow required |
| Second appraisal reconciliation | Chief Appraiser | Use lower of two values unless justified |
| Suspected fraud or misrepresentation | Chief Appraiser + Compliance | SAR filing assessment |

5.2. Approval conditions may include:
- Additional mortgage insurance coverage
- Repair escrow with defined completion timeline and re-inspection requirement
- Reduced loan amount to achieve acceptable LTV
- Additional reserves required at closing
- Post-closing property inspection

5.3. Denials must include:
- Clear statement of the reason for denial
- Specific criteria not met
- Any alternative paths the borrower may pursue (restructure, additional down payment, different program)
- Adverse action notice requirements (if applicable)

5.4. Record the final decision, conditions (if any), and approving authority in the loan file and appraisal tracking system.

5.5. Notify the underwriter of record, loan officer, and appraisal coordinator of the decision within 1 business day.

## 4. Exception Handling

| Exception | Action |
|---|---|
| Senior underwriter and chief appraiser disagree | Escalate to credit committee for final determination |
| Borrower provides new information after denial | May reopen review if information is material and documented |
| Investor declines to purchase loan with exception | Loan must be restructured or placed with alternative investor |
| Regulatory examiner questions exception | All documentation must support the decision independently |

## 5. Quality Controls

- All manual review decisions are subject to post-closing quality control sampling (100% for first 6 months of new reviewer authority)
- Exception approval rates tracked by reviewer, property type, and geography
- Exception performance monitored (delinquency rates on exception loans vs. standard loans)
- Annual recertification required for exception approval authority
- Credit committee reviews aggregate exception data quarterly

## 6. References

- CRP-PRC-PA-003: Property Value Assessment Procedure
- CRP-PRC-PA-004: Appraisal Revision Request Procedure
- CRP-RUL-PA-002: LTV Threshold Rules by Loan Program
- Fannie Mae Selling Guide B4-1.4-01
- FHA 4000.1 II.D.3
