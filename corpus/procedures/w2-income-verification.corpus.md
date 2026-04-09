---
corpus_id: "CRP-PRC-IV-001"
title: "W-2 Income Verification Procedure"
slug: "w2-income-verification"
doc_type: "procedure"
domain: "Mortgage Lending"
subdomain: "Income Verification"
tags:
  - "w-2"
  - "wage-income"
  - "employment-income"
  - "voe"
  - "income-verification"
  - "base-pay"
  - "overtime"
  - "bonus"
  - "commission"
applies_to:
  process_ids:
    - "Process_IncomeVerification"
    - "Process_UnderwritingReview"
  task_types:
    - "userTask"
    - "businessRuleTask"
  task_name_patterns:
    - "verify.*w-?2"
    - "verify.*wage"
    - "verify.*employment.*income"
    - "review.*w-?2"
    - "calculate.*w-?2.*income"
  goal_types:
    - "data_production"
    - "decision"
  roles:
    - "loan_processor"
    - "underwriter"
    - "income_analyst"
version: "2.1"
status: "current"
effective_date: "2025-03-01"
review_date: "2026-03-01"
supersedes: null
superseded_by: null
author: "Operations Standards Committee"
last_modified: "2025-02-15"
last_modified_by: "J. Whitfield"
source: "internal"
source_ref: "SOP-IV-2025-001"
related_corpus_ids:
  - "CRP-RUL-IV-001"
  - "CRP-RUL-IV-002"
  - "CRP-POL-IV-001"
  - "CRP-REG-IV-001"
  - "CRP-REG-IV-002"
  - "CRP-DAT-IV-001"
regulation_refs:
  - "Fannie Mae Selling Guide B3-3.1-09"
  - "FHA 4000.1 II.A.4.c.2"
  - "VA Pamphlet 26-7 Ch. 4"
policy_refs:
  - "POL-IV-004"
  - "POL-DOC-001"
---

# W-2 Income Verification Procedure

## 1. Scope

This procedure governs the verification and calculation of wage and salary income for borrowers whose primary income source is W-2 employment. It applies to all conventional, FHA, VA, and USDA loan programs unless an agency-specific override is noted. The procedure covers base pay, overtime, bonuses, commissions, and other recurring compensation reported on Form W-2.

This procedure does **not** cover self-employment income (see CRP-PRC-IV-002), rental income, or non-employment income sources such as social security, pensions, or alimony.

## 2. Prerequisites

Before beginning W-2 income verification, ensure the following are available:

| # | Prerequisite | Source |
|---|---|---|
| 1 | Signed and dated Uniform Residential Loan Application (URLA / Form 1003) | Borrower |
| 2 | Most recent 30 days of paystubs covering all employers | Borrower |
| 3 | W-2 forms for the most recent two calendar years | Borrower |
| 4 | Federal tax returns (Form 1040) for the most recent two years, if applicable | Borrower or IVES |
| 5 | IRS Form 4506-C signed by borrower (for transcript ordering) | Borrower |
| 6 | Employer contact information for VOE | Application file |

**Note:** For DU-validated loans where the Findings report waives tax returns, only W-2 forms and paystubs are required. Document the DU waiver in the file.

## 3. Procedure Steps

### Step 1: Collect and Validate Documentation

1.1. Confirm receipt of W-2 forms for the current year (if available) and the two prior calendar years. At minimum, two consecutive years of W-2 history are required.

1.2. Confirm receipt of the most recent 30 consecutive days of paystubs. Paystubs must show:
- Borrower's name and Social Security Number (last 4 digits acceptable)
- Employer name
- Pay period dates and pay date
- Year-to-date (YTD) gross earnings
- Breakdown of earnings by type (regular, overtime, bonus, commission)
- YTD deductions

1.3. Verify that the borrower name on the W-2 matches the name on the loan application. If names differ (e.g., maiden name, legal name change), obtain supporting documentation (marriage certificate, court order).

1.4. Check that the Employer Identification Number (EIN) on the W-2 matches the employer identified on the application and paystubs.

1.5. If tax returns are in the file, confirm that W-2 Box 1 (Wages, tips, other compensation) reconciles to Form 1040 Line 1a within a reasonable tolerance. Discrepancy greater than $500 requires explanation.

### Step 2: Determine Employment Classification

2.1. Using the Employment Type Classification Rules (CRP-RUL-IV-001), classify the borrower's employment:

- If borrower owns **25% or more** of the employing entity, treat as self-employed regardless of W-2 issuance. Redirect to CRP-PRC-IV-002.
- If borrower receives both W-2 and 1099 income from the same entity, investigate further; this may indicate misclassification.

2.2. For commissioned borrowers (where commission income exceeds 25% of total compensation), apply the commissioned income rules in Step 5.

2.3. Document the employment classification determination in the income worksheet.

### Step 3: Calculate Base Income

3.1. **Base Salary / Hourly Wage:**
- If salaried: Use the annual salary stated on the VOE or offer letter, divided by 12.
- If hourly: Multiply hourly rate by guaranteed weekly hours, then apply the frequency conversion:
  - Weekly: multiply by 52, divide by 12
  - Bi-weekly: multiply by 26, divide by 12
  - Semi-monthly: multiply by 24, divide by 12

3.2. **Overtime Income:**
- Overtime must have a documented two-year history to be used as qualifying income.
- Calculate the 24-month average of overtime earnings from W-2 and paystub YTD data.
- If overtime is **declining** (current year YTD annualized is more than 20% below the prior year), use the lower of the two-year average or the current year annualized amount.
- If overtime history is less than two years but more than 12 months, use the shorter period average with a written explanation.
- Overtime with less than 12 months of history is generally excluded unless strong compensating factors exist.

3.3. **Bonus Income:**
- Bonus income requires a two-year history.
- Calculate the 24-month average using the two most recent W-2s.
- If current-year YTD bonus annualized is less than the 24-month average by more than 25%, use the lower figure.
- One-time signing bonuses or retention bonuses that are not recurring must be excluded.

3.4. **Commission Income:**
- If commissions represent 25% or more of total compensation, a two-year history and two years of tax returns are required (regardless of DU waivers).
- Calculate the 24-month average from W-2s and/or tax returns.
- Apply declining income analysis per Step 4.
- If commissions are less than 25% of total compensation, they may be treated as supplemental income with a 12-month history.

3.5. **Other Recurring Compensation:**
- Tips: Use the amount reported in W-2 Box 7 (Social Security tips) or Box 1 if tips are included. Two-year average required.
- Shift differential: Verify recurrence through paystubs showing consistent differential pay over 12+ months.
- Housing allowance: Document with employer letter confirming ongoing nature and include in qualifying income.

### Step 4: Perform Trending Analysis

4.1. Compare year-over-year income for each income component:
- Calculate Year 1 total, Year 2 total, and current YTD annualized.
- Formula for annualized YTD: `(YTD earnings / months elapsed in current year) * 12`

4.2. Apply the trending rules:
- **Stable or increasing:** Use the 24-month average (or the higher of the two, per agency guidelines).
- **Declining 1-15%:** Use the 24-month average with a documented explanation for the decline.
- **Declining 16-25%:** Use the lower of the 24-month average or the most recent 12-month earnings. Add a compensating factor narrative.
- **Declining >25%:** Escalate for manual underwriter review. Income may not be usable without strong compensating factors and a reasonable explanation (e.g., one-time medical leave with full recovery documented).

4.3. Document the trending analysis on the Income Calculation Worksheet (Form ICW-100) with specific dollar amounts and percentage calculations.

### Step 5: Verify Employment

5.1. Obtain employment verification through one of the following methods (in order of preference):

| Priority | Method | Acceptable When |
|----------|--------|----------------|
| 1 | The Work Number (TWN) automated VOE | Available for the employer |
| 2 | Written VOE (Form 1005) sent directly to employer | TWN not available |
| 3 | CPA/tax preparer letter + business license | Small employer, borrower is key employee |
| 4 | Direct verbal verification with employer HR | As supplement only, not standalone |

5.2. The VOE must confirm:
- Employment status (active, leave of absence, terminated)
- Hire date and position/title
- Current base pay rate and pay frequency
- Year-to-date overtime, bonus, and commission earnings
- Probability of continued employment

5.3. If the VOE shows discrepancies with paystubs or W-2s exceeding $200/month, investigate and resolve before proceeding.

5.4. A verbal VOE is required within **10 business days** of the closing date (per POL-IV-004). Document the verbal VOE with:
- Date and time of call
- Name and title of contact at employer
- Phone number used (must be independently verified, not borrower-provided)
- Employment status confirmed

### Step 6: Reconcile and Calculate Final Monthly Income

6.1. Sum all verified income components:
```
Qualifying Monthly Income =
    Base Monthly Income
  + Monthly Overtime (averaged)
  + Monthly Bonus (averaged)
  + Monthly Commission (averaged)
  + Other Recurring Monthly Income
```

6.2. Compare the calculated qualifying income against the income stated on the loan application. Calculate variance:
```
Variance % = |Stated Income - Verified Income| / Stated Income * 100
```

6.3. Apply variance threshold rules per CRP-RUL-IV-002:
- Conventional: variance > 10% requires exception documentation
- FHA: variance > 15% requires exception documentation
- VA: variance > 10% requires exception documentation

6.4. Record the final qualifying monthly income in the Loan Origination System (LOS) income tab.

### Step 7: Document Findings

7.1. Complete the Income Calculation Worksheet (Form ICW-100) with all calculated values.

7.2. Upload all supporting documents to the Document Management System (DMS) with correct indexing:
- Category: Income
- Subcategory: W-2 / Paystub / VOE / Tax Return
- Borrower association: Primary / Co-Borrower

7.3. Add processor notes summarizing:
- Income sources verified and amounts
- Any trending concerns and mitigating factors
- Variance from stated income (if any)
- Any conditions or follow-up items needed

## 4. Quality Checks

| Check | Criteria | Action if Failed |
|-------|----------|-----------------|
| Name consistency | Borrower name matches across all documents | Obtain name-change documentation |
| EIN match | Employer EIN consistent across W-2, VOE, paystubs | Investigate; possible fraud indicator |
| W-2 / 1040 reconciliation | Box 1 within $500 of 1040 Line 1a | Request explanation from borrower |
| Math verification | Income calculation independently reproducible | Re-calculate and correct |
| Documentation age | Paystubs within 30 days, VOE within 120 days | Obtain updated documents |
| Verbal VOE timing | Completed within 10 business days of closing | Reconfirm if outside window |
| Trending consistency | YTD annualized aligns with 2-year trend | Apply declining income rules |

## 5. Common Pitfalls

1. **Mixing gross and net income.** Always use gross income (pre-tax, pre-deduction) for qualification. Net income is never used for W-2 borrowers.

2. **Using outdated paystubs.** Paystubs must cover the most recent 30 consecutive days. A paystub from 45 days ago with a recent date stamp is not acceptable.

3. **Ignoring employer ownership.** A borrower who owns 26% of their employer must be treated as self-employed even if they receive a W-2. Always check the ownership question on the application.

4. **Double-counting income.** When a borrower has overtime reflected in both the W-2 total and the paystub YTD, ensure the same dollars are not counted twice. Use W-2 for historical averaging and paystubs for current validation.

5. **Failing to annualize YTD correctly.** Use the actual number of months elapsed, not pay periods. If the borrower's most recent paystub is dated March 15, use 2.5 months (not 3) for annualization: `YTD / 2.5 * 12`.

6. **Accepting borrower-provided employer phone numbers for verbal VOE.** The phone number must be independently verified through a directory, company website, or third-party database. Never accept a number provided solely by the borrower.

7. **Overlooking gaps in employment.** If the W-2 history shows a gap (e.g., no W-2 for one of the two years from the current employer), investigate and document. A gap greater than 6 months requires a written letter of explanation from the borrower.

## 6. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.1 | 2025-02-15 | J. Whitfield | Updated trending thresholds to align with 2025 Fannie Mae guidance |
| 2.0 | 2024-06-01 | J. Whitfield | Major revision; added commission sub-procedure, updated VOE hierarchy |
| 1.3 | 2023-11-15 | M. Torres | Added verbal VOE timing requirement per POL-IV-004 |
| 1.0 | 2022-01-10 | Operations Standards Committee | Initial release |
