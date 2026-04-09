---
corpus_id: "CRP-REG-IV-001"
title: "Fannie Mae Selling Guide B3-3.1 (Income Assessment) Summary"
slug: "fannie-mae-income-summary"
doc_type: "regulation"
domain: "Mortgage Lending"
subdomain: "Income Verification"
tags:
  - "fannie-mae"
  - "selling-guide"
  - "b3-3.1"
  - "income-assessment"
  - "du-validation"
  - "w-2"
  - "self-employment"
  - "gse"
applies_to:
  process_ids:
    - "Process_IncomeVerification"
    - "Process_UnderwritingReview"
    - "Process_LoanOrigination"
  task_types:
    - "businessRuleTask"
    - "userTask"
  task_name_patterns:
    - "verify.*income.*conventional"
    - "apply.*fannie.*rule"
    - "check.*selling.*guide"
    - "validate.*fnma"
    - "du.*income"
  goal_types:
    - "decision"
    - "data_production"
  roles:
    - "underwriter"
    - "loan_processor"
    - "compliance_analyst"
version: "4.0"
status: "current"
effective_date: "2025-03-01"
review_date: "2025-09-01"
supersedes: null
superseded_by: null
author: "Compliance Department"
last_modified: "2025-02-28"
last_modified_by: "L. Patel"
source: "regulatory"
source_ref: "Fannie Mae Selling Guide, Effective 2025-03-01"
related_corpus_ids:
  - "CRP-PRC-IV-001"
  - "CRP-PRC-IV-002"
  - "CRP-PRC-IV-003"
  - "CRP-RUL-IV-001"
  - "CRP-RUL-IV-002"
  - "CRP-REG-IV-002"
regulation_refs:
  - "Fannie Mae Selling Guide B3-3.1-01"
  - "Fannie Mae Selling Guide B3-3.1-02"
  - "Fannie Mae Selling Guide B3-3.1-09"
  - "Fannie Mae Selling Guide B3-3.1-10"
  - "Fannie Mae Selling Guide B3-3.1-11"
policy_refs:
  - "POL-IV-004"
  - "POL-CONV-001"
---

# Fannie Mae Selling Guide B3-3.1 -- Income Assessment Summary

## 1. Document Purpose

This corpus document summarizes the key income verification requirements from the Fannie Mae Selling Guide, Chapter B3-3.1 (Income Assessment). It serves as a reference for underwriters and processors when verifying income for conventional loans intended for sale to Fannie Mae.

This is a **summary** of regulatory requirements, not a replacement for the Selling Guide itself. When questions arise, the current Selling Guide must be consulted directly. This summary reflects the Selling Guide as of March 2025.

## 2. B3-3.1-01: General Income Requirements

### Stable Monthly Income Standard

Fannie Mae requires lenders to determine the borrower's stable monthly income -- the amount of income that can be reasonably expected to continue for at least the next three years. Key principles:

- **Continuity:** Income must be verified as likely to continue. A minimum two-year history of receipt is generally required, though shorter periods are acceptable in certain circumstances (e.g., new employment in the same field).
- **Stability:** Income should be stable or increasing. Declining income is evaluated on a case-by-case basis with additional scrutiny.
- **Verification:** All income used for qualifying must be verified through acceptable documentation.

### Income Documentation Standards

The lender must obtain sufficient documentation to support the determination of stable income. The documentation requirements vary based on income type and DU findings:

| Documentation Level | When Applied |
|---------------------|-------------|
| Standard | Manual underwrite or DU with standard documentation |
| Reduced (DU waiver) | DU issues a waiver for tax returns on certain income types |
| Enhanced | Complex income, self-employment, or unusual circumstances |

### Two-Year History Requirement

A two-year history of income receipt is the baseline standard. Exceptions:

- Income from a new employer is acceptable without two-year history if the borrower has a history of similar employment and the income is stable
- Trailing income from a prior employer (e.g., commissions earned but not yet paid) does not establish a two-year history for the new employer
- Gaps in employment exceeding 6 months in the past 2 years require written explanation

## 3. B3-3.1-09: W-2 Employment Income

### Documentation Requirements

For W-2 employees, the following documentation is required unless DU provides a waiver:

| Document | Required | DU May Waive |
|----------|----------|-------------|
| Most recent 30 days of paystubs | Yes | No |
| W-2 forms (most recent 2 years) | Yes | No |
| Federal tax returns (most recent 2 years) | Conditional | Yes, if DU approves |
| Written VOE | If paystubs insufficient | N/A |

### Base Income Calculation

- **Salaried employees:** Use the current salary as documented on the paystub and/or VOE
- **Hourly employees:** Use the hourly rate multiplied by the average hours worked per week (use the lower of guaranteed hours or actual hours if they vary)

### Variable Income (Overtime, Bonus, Commission < 25%)

Variable income components are qualifying if:

1. The borrower has received the income for at least 12 months (24 months preferred)
2. The income is likely to continue
3. The income does not show an unreasonable decline

Calculation method: Average the variable income over the applicable period (12 or 24 months). If income is declining, use the lower of the period average or the most recent 12-month figure.

### Commission Income (>= 25% of Total Compensation)

When commission income represents 25% or more of the borrower's total annual earnings:

- Two years of complete tax returns are **always** required (DU cannot waive)
- Use the 24-month average of commission income
- Apply trending analysis; declining commissions require use of the lower figure
- Unreimbursed business expenses (Form 2106, if applicable) must be deducted

## 4. B3-3.1-10: Self-Employment Income

### Qualification Requirements

Fannie Mae defines a self-employed borrower as one who has 25% or greater ownership interest in a business. Requirements:

- **Two years of tax returns:** Both personal (1040) and business returns are required for the most recent two years
- **Form 1084:** The Cash Flow Analysis (Form 1084) or equivalent worksheet must be completed to determine qualifying income
- **Business viability:** The lender must evaluate whether the business provides a stable and sufficient income stream

### Income Calculation

For each business entity type, Fannie Mae specifies the starting point and allowable adjustments:

**Sole Proprietorship (Schedule C):**
- Begin with Schedule C, Line 31 (Net Profit or Loss)
- Add back: depreciation (Line 13), depletion (Line 12), amortization, business use of home (Line 30)
- Subtract: non-recurring income items

**Partnership (Form 1065 / K-1):**
- Begin with K-1 ordinary income (Line 1)
- Add: guaranteed payments to partner (Line 4), depreciation, depletion, amortization (borrower's share)
- Verify distributions against income for sustainability

**S-Corporation (Form 1120S / K-1):**
- Include W-2 wages from the S-Corp
- Add K-1 ordinary income (Line 1), depreciation, depletion, amortization (borrower's share)
- Officer compensation on 1120S should reconcile to the borrower's W-2

**C-Corporation (Form 1120):**
- Only W-2 wages from the corporation are used for qualifying income
- Corporate earnings may be considered only if the borrower owns 100% and can document access through distributions

### Trending Requirements

- If the most recent year's income is less than the prior year (declining trend), the lender must use the lower of the 24-month average or the most recent 12-month figure
- Significant decline (>25%) may render the income unstable and unusable
- If a business reported a net loss in the most recent year, that loss must reduce the borrower's qualifying income

### DU Considerations for Self-Employment

- DU may offer reduced documentation (one year of tax returns) for borrowers with strong credit and established businesses (5+ years in same field)
- Even with DU waivers, the lender retains responsibility for assessing income stability
- Business returns cannot be waived by DU; they are always required when the borrower is self-employed

## 5. B3-3.1-11: DU Validation Service

### Overview

Desktop Underwriter (DU) Validation Service allows certain income and employment data to be validated through third-party services, potentially reducing documentation requirements. Key features:

- **Income validation:** DU can validate income through payroll providers and The Work Number
- **Employment validation:** DU can confirm current employment status
- **Impact on documentation:** When DU validates income, certain documents (e.g., tax returns, VOE) may be waived per the DU Findings report

### Lender Responsibilities with DU Validation

Even when DU validates income:
- The lender must still review the validated data for reasonableness
- If the validated income differs significantly from application data, investigation is required
- DU validation does not override the lender's obligation to assess income stability
- Fraud indicators must still be investigated regardless of DU validation status

### What DU Validation Cannot Waive

- Self-employment documentation (business returns are always required)
- Commission documentation when commissions are >= 25% of income
- Tax returns when there are indicators of self-employment
- Verbal VOE within 10 business days of closing (per investor overlay)

## 6. Additional Key Requirements

### Age of Documents

- Paystubs: Must be dated within 30 days of the initial loan application date; updated paystubs may be needed if closing is significantly delayed
- Tax returns: Must be for the most recent filing year; if a new tax year has passed and the borrower has filed, the new return is required
- VOE: Must be dated within 120 days of the note date
- IRS transcripts: Must cover the same tax years as the returns in the file

### Income Not Used for Qualifying

If a borrower has an income source listed on the application that is not being used for qualifying, the lender must still consider that income for other purposes:
- USDA: All household income must be assessed against income limits even if not used for DTI
- Fannie Mae does not require unused income to be verified, but any income source must be free of negative indicators (e.g., a borrower's undisclosed self-employment loss)

### Non-Taxable Income

Non-taxable income may be grossed up by 25% (multiply by 1.25) if the income is verified as non-taxable and is expected to continue. The lender must document the basis for non-taxable treatment.

## 7. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 4.0 | 2025-02-28 | L. Patel | Updated for 2025 Selling Guide changes; added DU Validation Service section |
| 3.0 | 2024-03-15 | L. Patel | Revised for 2024 Selling Guide updates |
| 2.0 | 2023-04-01 | Compliance Department | Major update for redesigned Form 1084 |
| 1.0 | 2022-01-10 | Compliance Department | Initial release |
