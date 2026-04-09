---
corpus_id: "CRP-POL-IV-001"
title: "W-2 Income Verification Policy"
slug: "w2-verification-policy"
doc_type: "policy"
domain: "Mortgage Lending"
subdomain: "Income Verification"
tags:
  - "policy"
  - "voe"
  - "verbal-voe"
  - "documentation-age"
  - "the-work-number"
  - "verification-sources"
  - "w-2"
  - "internal-policy"
applies_to:
  process_ids:
    - "Process_IncomeVerification"
    - "Process_UnderwritingReview"
    - "Process_PreClosingQC"
  task_types:
    - "userTask"
    - "manualTask"
  task_name_patterns:
    - "verify.*employment"
    - "obtain.*voe"
    - "verbal.*voe"
    - "check.*documentation.*age"
    - "validate.*verification.*source"
  goal_types:
    - "data_production"
    - "decision"
  roles:
    - "loan_processor"
    - "underwriter"
    - "closing_coordinator"
    - "quality_control_analyst"
version: "3.2"
status: "current"
effective_date: "2025-02-01"
review_date: "2025-08-01"
supersedes: null
superseded_by: null
author: "Policy Committee"
last_modified: "2025-01-25"
last_modified_by: "D. Morrison"
source: "internal"
source_ref: "POL-IV-004 Rev 3.2"
related_corpus_ids:
  - "CRP-PRC-IV-001"
  - "CRP-PRC-IV-003"
  - "CRP-RUL-IV-001"
  - "CRP-REG-IV-001"
  - "CRP-REG-IV-002"
  - "CRP-SYS-IV-002"
regulation_refs:
  - "Fannie Mae Selling Guide B3-3.1-09"
  - "FHA 4000.1 II.A.4.c.2"
  - "VA Pamphlet 26-7 Ch. 4"
policy_refs:
  - "POL-IV-004"
  - "POL-DOC-001"
  - "POL-QC-001"
  - "POL-FRAUD-001"
---

# W-2 Income Verification Policy (POL-IV-004)

## 1. Policy Statement

All W-2 employment income used for mortgage qualification must be independently verified through approved sources and methods. Verification must confirm the borrower's current employment status, income level, and the likelihood of continued employment. This policy establishes the minimum standards for employment and income verification that exceed baseline agency requirements where our risk appetite demands greater rigor.

This policy applies to all loan products originated or brokered by the company, including conventional, FHA, VA, and USDA programs.

## 2. Effective Date and Authority

- **Policy Number:** POL-IV-004
- **Effective Date:** February 1, 2025
- **Approved By:** Chief Credit Officer, VP of Operations
- **Review Cycle:** Semi-annual (next review: August 2025)
- **Compliance:** Mandatory for all origination, processing, underwriting, and closing staff

## 3. Verification Source Hierarchy

Employment and income verification must be obtained from the following sources, listed in order of preference. A higher-preference source should always be attempted before falling back to a lower-preference option.

### 3.1. Acceptable Verification Sources

| Priority | Source | Description | Acceptable Standalone? |
|----------|--------|-------------|----------------------|
| 1 | **The Work Number (TWN)** | Automated verification through Equifax's employer database. Provides employment dates, title, salary, and pay rate. | Yes, if complete data returned |
| 2 | **Written VOE (Form 1005 or equivalent)** | Completed and returned directly by the employer to the lender. Must not pass through the borrower. | Yes |
| 3 | **Third-party payroll provider** | Verification through ADP, Paychex, or similar payroll processors with direct lender access. | Yes, if provider is on the approved list |
| 4 | **CPA / Tax preparer letter** | Acceptable only for small employers (< 20 employees) where TWN and written VOE are unavailable. Must be on CPA letterhead with license number. | Yes, with underwriter approval |
| 5 | **Direct employer contact (phone/email)** | Verbal verification with HR or authorized representative. Acceptable as a supplement only. | No -- must supplement another source |

### 3.2. Unacceptable Verification Sources

The following are **never** acceptable as primary or supplementary verification:

- Borrower-provided verbal confirmation of their own employment
- Letters or emails authored by the borrower claiming to represent the employer
- Social media profiles (LinkedIn, etc.) as employment verification
- Phone numbers or email addresses provided solely by the borrower without independent verification
- Business cards or personal websites
- Unsigned or undated VOE forms

### 3.3. Independent Phone Number Verification

For any verbal or telephone-based verification, the employer's phone number must be independently confirmed through at least one of:

- Company website (official "Contact Us" page)
- Published business directory (Yellow Pages, Dun & Bradstreet)
- State licensing board or professional registry
- Previous file history (same employer verified in a prior transaction within 12 months)
- TWN or third-party verification service employer records

A phone number provided solely by the borrower or found only in the borrower's submitted documents is **not independently verified** and must not be used.

## 4. Documentation Age Requirements

### 4.1. Maximum Document Age

| Document | Maximum Age | Measured From |
|----------|------------|---------------|
| Paystubs | 30 calendar days | Date of initial loan application |
| W-2 forms | Current + 1 prior year required; additional years as needed | Tax year |
| Written VOE | 120 calendar days | Note date (closing) |
| Verbal VOE | 10 business days | Note date (closing) |
| Tax returns | Most recent 2 filing years | Calendar year |
| IRS transcripts | Same tax years as returns in file | Calendar year |

### 4.2. Stale Document Procedures

When documents approach or exceed their maximum age:

1. **Paystubs beyond 30 days:** Request updated paystubs. If the borrower has changed pay rates, overtime patterns, or employment status, the updated paystub may trigger re-verification.

2. **VOE beyond 90 days (approaching 120-day limit):** Proactively order an updated VOE. Do not wait until the document expires.

3. **Application-to-closing exceeds 120 days:** All income documentation must be refreshed:
   - New 30-day paystubs
   - Updated VOE (or new TWN pull)
   - Verbal VOE re-confirmed
   - If a new tax year has been filed, the new year's returns and W-2 must be obtained

4. **Year-end transition:** If the loan application was taken in Q4 but closing occurs after January 31 of the following year, the new year's W-2 must be obtained if it has been issued by the employer.

### 4.3. Company Overlay: 90-Day Documentation Policy

As an internal overlay stricter than agency minimums:
- Written VOE or TWN report should be **no more than 90 days old** at the time of underwriting submission (agency allows 120 days to closing)
- If VOE is between 90-120 days old at closing, an additional verbal VOE is required confirming no change in employment status or compensation

## 5. Verbal VOE Requirements

### 5.1. Timing

A verbal VOE must be completed within **10 business days** of the scheduled closing date. This is a hard requirement with no exceptions.

### 5.2. Verbal VOE Content

The verbal verification must confirm:

| Item | Required |
|------|----------|
| Borrower currently employed | Yes |
| Current position/title | Yes |
| Employment start date | Yes |
| Current pay rate (if available) | Preferred |
| Any pending termination, layoff, or leave | Yes |
| Expected continuation of employment | Yes |

### 5.3. Documentation of Verbal VOE

Each verbal VOE must be documented with:

- Date and time of the call
- Full name and title of the person contacted at the employer
- Phone number used for the contact (must be independently verified per Section 3.3)
- All information obtained during the call
- Name and title of the company representative who conducted the verification
- Notation in the LOS and the physical/electronic file

### 5.4. Failed Verbal VOE

If a verbal VOE cannot be completed (employer unresponsive, number disconnected, HR unavailable):

1. Attempt contact on at least **3 separate business days** at different times
2. Document each attempt with date, time, and result
3. Escalate to underwriter for alternative verification strategy
4. Acceptable alternatives if verbal VOE cannot be completed:
   - Fresh TWN pull dated within 5 business days of closing
   - Email confirmation from a verified employer HR email address
   - Signed employer letter on company letterhead dated within 10 business days of closing
5. None of the above alternatives are acceptable if the employer has a published phone number that simply goes unanswered -- in that case, continue attempting contact

## 6. Special Situations

### 6.1. Borrower on Leave of Absence

If the verbal VOE or any verification reveals the borrower is on leave:

- Determine the type of leave (medical, parental, military, personal)
- Obtain a written statement from the employer confirming:
  - The borrower's position will be available upon return
  - The expected return date
  - Whether the borrower is receiving any compensation during leave
- If return date is within 60 days of closing: use pre-leave income with employer confirmation
- If return date is beyond 60 days or uncertain: use only current income being received during leave
- Document the leave status prominently in the underwriting notes

### 6.2. Job Change Between Application and Closing

If the borrower changes jobs between application and closing:

1. Obtain new employment documentation (offer letter, first paystub, updated VOE)
2. Verify that the new income supports the loan qualification
3. If new income is lower than prior income:
   - Recalculate DTI
   - Determine if the loan still qualifies
   - Re-disclose if terms change
4. If in the same line of work: a reasonable transition is generally acceptable
5. If in a different field: assess stability with additional scrutiny (probationary period, guaranteed vs. variable compensation)

### 6.3. Multiple Employers

For borrowers with more than one employer:

- Each employer must be independently verified
- Each income stream must be separately calculated
- If combining primary and secondary employment, verify that the schedule is sustainable (no overlap that would suggest inability to maintain both)
- Secondary employment income requires a 2-year history for variable components

### 6.4. Foreign Employment Income

For borrowers employed by foreign entities or earning income from foreign sources:

- Income must be documented with equivalent foreign tax documents translated to English by a certified translator
- Currency conversion must use the exchange rate as of the most recent month-end prior to application
- Verification of foreign employment may require embassy or consulate confirmation
- Foreign income used for qualifying requires senior underwriter approval

## 7. Fraud Prevention

### 7.1. Red Flags in Employment Verification

The following indicators should trigger enhanced scrutiny:

| Red Flag | Action |
|----------|--------|
| Employer phone number traces to a residence | Investigate; verify business registration |
| VOE completed and returned same day it was sent | Verify the employer contact is legitimate |
| Employer has no web presence and was recently established | Enhanced business verification required |
| Borrower's stated income significantly exceeds industry norms for their position | Request detailed compensation breakdown |
| W-2 EIN does not match IRS records for the employer | Do not proceed; potential fabricated W-2 |
| Paystub formatting inconsistencies (fonts, alignment, math errors) | Request additional paystubs; consider direct employer verification |
| VOE signature matches borrower's signature | Do not accept; potential fraud |

### 7.2. Suspicious Activity Reporting

If fraud is suspected, follow the company's SAR (Suspicious Activity Report) procedures per POL-FRAUD-001. Do not alert the borrower of the suspicion. Escalate to the Fraud Prevention team immediately.

## 8. Compliance and Audit

### 8.1. File Review Checklist

Every closed loan file must contain:

- [ ] Paystubs covering most recent 30 days
- [ ] W-2 forms for 2 most recent years
- [ ] Tax returns (if not waived by DU for conventional)
- [ ] Written VOE or TWN report
- [ ] Verbal VOE documentation (within 10 business days of closing)
- [ ] Income Calculation Worksheet
- [ ] Variance analysis (if applicable)
- [ ] All required explanations and conditions satisfied

### 8.2. Audit Trail

All verification activities must create an audit trail in the LOS:
- Timestamp of each verification attempt
- Source used for verification
- Results obtained
- Reviewer who performed the verification
- Any exceptions or overrides (with supervisor approval)

## 9. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 3.2 | 2025-01-25 | D. Morrison | Added 90-day overlay, expanded fraud indicators, foreign income section |
| 3.1 | 2024-08-15 | D. Morrison | Updated verbal VOE alternatives, added failed VOE procedure |
| 3.0 | 2024-02-01 | D. Morrison | Major revision: restructured verification hierarchy, added TWN as primary |
| 2.0 | 2023-06-01 | Policy Committee | Added leave of absence and job change procedures |
| 1.0 | 2022-01-10 | Policy Committee | Initial release |
