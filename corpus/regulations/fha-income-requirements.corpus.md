---
corpus_id: "CRP-REG-IV-002"
title: "FHA 4000.1 Income Requirements Summary"
slug: "fha-income-requirements"
doc_type: "regulation"
domain: "Mortgage Lending"
subdomain: "Income Verification"
tags:
  - "fha"
  - "hud"
  - "4000.1"
  - "effective-income"
  - "income-requirements"
  - "government-loan"
  - "voe"
  - "tax-transcripts"
  - "self-employment"
applies_to:
  process_ids:
    - "Process_IncomeVerification"
    - "Process_UnderwritingReview"
    - "Process_FHALoanOrigination"
  task_types:
    - "businessRuleTask"
    - "userTask"
  task_name_patterns:
    - "verify.*income.*fha"
    - "apply.*fha.*rule"
    - "check.*4000\\.1"
    - "validate.*fha"
    - "fha.*income"
  goal_types:
    - "decision"
    - "data_production"
  roles:
    - "underwriter"
    - "loan_processor"
    - "compliance_analyst"
    - "de_underwriter"
version: "3.0"
status: "current"
effective_date: "2025-01-01"
review_date: "2025-07-01"
supersedes: null
superseded_by: null
author: "Compliance Department"
last_modified: "2024-12-20"
last_modified_by: "L. Patel"
source: "regulatory"
source_ref: "HUD Handbook 4000.1, Effective 2024-09-01"
related_corpus_ids:
  - "CRP-PRC-IV-001"
  - "CRP-PRC-IV-002"
  - "CRP-PRC-IV-003"
  - "CRP-RUL-IV-001"
  - "CRP-RUL-IV-002"
  - "CRP-REG-IV-001"
regulation_refs:
  - "HUD 4000.1 II.A.4.c"
  - "HUD 4000.1 II.A.4.c.2"
  - "HUD 4000.1 II.A.4.c.3"
  - "HUD 4000.1 II.A.4.c.4"
  - "HUD 4000.1 II.A.4.c.5"
policy_refs:
  - "POL-IV-004"
  - "POL-FHA-001"
---

# FHA 4000.1 Income Requirements Summary

## 1. Document Purpose

This corpus document summarizes the income verification requirements from HUD Handbook 4000.1 (the FHA Single Family Housing Policy Handbook), specifically Section II.A.4.c covering income requirements. It serves as a reference for DE (Direct Endorsement) underwriters and processors when verifying income for FHA-insured mortgages.

This is a summary of regulatory requirements. The full HUD 4000.1 handbook must be consulted for detailed guidance. This summary reflects the handbook as of September 2024 with updates through December 2024.

## 2. Section II.A.4.c.1: General Income Requirements

### Effective Income Definition

FHA defines "Effective Income" as income that is:

1. **Verifiable:** The income can be confirmed through documentation and/or third-party sources
2. **Stable:** The income has been received consistently and is expected to continue
3. **Continuing:** The income is expected to continue for at least three years from the date of mortgage closing

All three criteria must be satisfied for income to be counted toward qualification.

### Verification Standards

FHA requires the following general verification approach:

- **Direct verification** is preferred (written VOE sent directly to the employer by the lender)
- **Third-party verification services** are acceptable (e.g., The Work Number) provided the data is current
- **Verbal VOE** is required for all employment income to confirm current employment status
- **IRS transcripts** (Form 4506-C) must be obtained and compared to borrower-provided tax returns

### Documentation Freshness

| Document Type | Maximum Age |
|--------------|-------------|
| Paystubs | 30 calendar days prior to initial case assignment date |
| W-2 forms | Most recent tax year; if new year W-2 not yet issued, prior year acceptable with current paystub |
| VOE (written) | 120 calendar days prior to case assignment or closing, whichever is earlier |
| Tax returns | Most recent 2 tax years; if recently filed year's transcript not available, prior 2 years with extension documentation |
| IRS transcripts | Must cover same years as tax returns in file |

## 3. Section II.A.4.c.2: Employment Income (Salary/Wage)

### Standard Employment Income

For borrowers employed on a salary or hourly basis:

**Required Documentation:**
- Most recent 30 days of paystubs
- W-2s for the most recent 2 years
- Written VOE or third-party employment verification
- Verbal VOE within 10 business days prior to closing

**Income Calculation:**
- Base pay: Use the current rate from paystub or VOE
- If the borrower has been employed for less than 2 years, a written explanation of employment history is required along with evidence of income stability (education, training, or prior related employment)

### Overtime and Bonus

FHA requirements for overtime and bonus income:

- Must have been received for at least **2 years** to be considered stable
- Calculate using the **2-year average**
- If overtime or bonus has been received for **12 to 24 months**, it may be used with documented evidence of likely continuance, but a reduced average or the actual period average must be used
- If the current year earnings show a decline from prior years, use the lower of the 2-year average or the current year annualized amount
- Employer must confirm on the VOE that overtime/bonus is expected to continue

### Commission Income

FHA treats commission income with additional requirements:

- Must demonstrate a **2-year history** of commission receipt
- Two years of **complete tax returns** are required (no waiver permitted)
- Unreimbursed business expenses must be deducted (review prior Schedule A or current standard deduction comparison)
- Commission income that represents the primary source of compensation requires the 2-year average; if secondary, the same averaging rules apply
- Declining commission income must use the lower of the 2-year average or the most recent year

### Part-Time and Second Job Income

- Part-time and secondary employment income is acceptable with a **2-year verified history** of uninterrupted receipt
- The borrower must demonstrate intent and ability to continue the secondary employment
- If the second job is seasonal, average over the full 24-month period (including months when not working)
- Income from a job held for less than 2 years may be considered if there is a prior history of similar work and the income is stable

## 4. Section II.A.4.c.3: Self-Employment Income

### Self-Employment Determination

FHA defines self-employment as having 25% or greater ownership interest in a business. This aligns with the Fannie Mae definition.

### Documentation Requirements (No Exceptions)

| Document | Required | Can Be Waived |
|----------|----------|--------------|
| Personal federal tax returns (1040) - 2 years | Yes | **No** |
| Business federal tax returns - 2 years | Yes | **No** |
| All K-1 forms | Yes | **No** |
| Year-to-date Profit & Loss statement | Conditional | No |
| Balance sheet (if corporation) | Recommended | N/A |
| Business verification | Yes | **No** |

**Critical difference from Fannie Mae:** FHA does **not** permit any waiver of tax return requirements for self-employed borrowers. Two full years of personal and business tax returns are always required.

### Income Calculation

FHA requires the following approach to self-employment income:

1. Complete a cash flow analysis using Form 1084 or equivalent
2. Start with the net income from the business (after taxes for the business entity)
3. Add back non-cash charges: depreciation, depletion, amortization
4. Add back any non-recurring losses
5. Subtract any non-recurring gains
6. Calculate the 24-month average as the qualifying income

### Declining Self-Employment Income

FHA's treatment of declining self-employment income:

- If income declined by **more than 20%** from Year 1 to Year 2, the underwriter must determine whether the business is viable and the income is stable
- A decline of more than 20% requires a **written analysis** explaining the cause and prognosis
- If the most recent year shows a **net loss**, the loss must be deducted from the borrower's other qualifying income
- A net loss in the most recent year combined with a decline trend may result in the self-employment income being excluded entirely

### Business Viability

FHA requires the underwriter to assess whether the business will continue to generate sufficient income:

- Review the trend of gross receipts (not just net income)
- Evaluate industry conditions
- Consider the age and history of the business
- If the business has been in operation for less than 2 years, self-employment income is generally **not eligible** for FHA qualification

### Year-to-Date Requirements

If more than one calendar quarter has elapsed since the end of the most recent tax year:
- A YTD Profit & Loss statement is required
- The P&L may be borrower-prepared but must be signed and dated
- Audited or CPA-prepared P&L is preferred but not required
- If the YTD P&L shows a significant decline from the prior year's performance (>20%), additional analysis is required

## 5. Section II.A.4.c.4: Other Income Sources

### Rental Income

FHA rental income requirements:

- Net rental income from Schedule E of the most recent tax year
- Apply a **25% vacancy factor** to gross rental income for properties without a documented rental history
- If Schedule E shows a net loss, the loss is added to the borrower's monthly obligations
- For properties being vacated by the borrower (departure residence), rental income may be used only if:
  - A fully executed lease agreement is provided
  - The borrower has documented reserves equal to 3 months PITIA
  - 75% of the gross rental income exceeds the PITIA

### Non-Taxable Income

FHA permits a gross-up of non-taxable income:
- Maximum gross-up factor: **15%** (multiply by 1.15)
- This is more conservative than Fannie Mae's 25% gross-up
- Documentation must confirm the non-taxable status of the income
- Common non-taxable sources: VA disability, Social Security (if non-taxable), child support

### Alimony, Child Support, and Maintenance

- May be used as qualifying income only if the borrower **elects** to disclose and use it
- Must be documented as court-ordered or formally agreed upon
- Must demonstrate a **minimum 6-month history** of consistent receipt
- Must be expected to continue for at least **3 years** from closing

### Asset-Based Income (Asset Depletion)

FHA does **not** permit asset depletion as an income source. This is a key difference from Fannie Mae conventional guidelines.

## 6. Section II.A.4.c.5: IRS Transcript Requirements

### 4506-C Processing

FHA requires the lender to obtain IRS tax transcripts to validate borrower-provided tax returns:

- Borrower must sign IRS Form 4506-C authorizing the lender to request transcripts
- Transcripts must be ordered for all tax years for which returns are required
- Both personal (Individual) and business transcripts may be needed

### Transcript Comparison

The lender must compare the tax transcripts to the borrower-provided tax returns:

| Field | Tolerance |
|-------|-----------|
| Adjusted Gross Income (AGI) | Must match within $500 |
| Filing status | Must match exactly |
| W-2 wages (Line 1) | Must match within $200 |
| Self-employment income | Must match within $500 |

### Transcript Unavailability

If transcripts are unavailable (e.g., returns recently filed, IRS backlog):

- Document the reason for unavailability with IRS response
- Obtain alternative evidence: IRS e-file acceptance, cancelled checks for taxes owed, direct IRS confirmation
- Proceed with closing if alternative evidence is sufficient and no fraud indicators exist
- Follow up with transcript retrieval post-closing within 120 days

## 7. Key Differences: FHA vs. Fannie Mae

| Topic | FHA (4000.1) | Fannie Mae (Selling Guide) |
|-------|-------------|--------------------------|
| Tax return waiver | Not permitted for SE | DU may waive for established SE |
| Non-taxable gross-up | 15% maximum | 25% maximum |
| Asset depletion income | Not permitted | Permitted with conditions |
| Transcript tolerance | $500 AGI | No explicit tolerance stated |
| Declining SE income | 20% decline triggers analysis | 25% decline triggers escalation |
| YTD P&L requirement | After 1 quarter post-tax year | After 3 months post-tax year |
| Business history minimum | 2 years required (no exceptions) | 2 years standard; 1 year with DU and 5+ year field experience |
| Verbal VOE timing | 10 business days before closing | 10 business days before closing |

## 8. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 3.0 | 2024-12-20 | L. Patel | Updated for HUD 4000.1 September 2024 revisions; added transcript comparison table |
| 2.0 | 2024-01-15 | L. Patel | Updated for 2023 HUD revisions |
| 1.0 | 2022-01-10 | Compliance Department | Initial release |
