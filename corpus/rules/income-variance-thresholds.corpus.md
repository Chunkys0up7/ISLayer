---
corpus_id: "CRP-RUL-IV-002"
title: "Income Variance Threshold Rules"
slug: "income-variance-thresholds"
doc_type: "rule"
domain: "Mortgage Lending"
subdomain: "Income Verification"
tags:
  - "variance"
  - "threshold"
  - "stated-income"
  - "verified-income"
  - "exception"
  - "declining-income"
  - "trending"
  - "tolerance"
applies_to:
  process_ids:
    - "Process_IncomeVerification"
    - "Process_UnderwritingReview"
    - "Process_QualityControl"
  task_types:
    - "businessRuleTask"
    - "userTask"
  task_name_patterns:
    - "variance.*threshold"
    - "check.*variance"
    - "compare.*stated.*verified"
    - "income.*tolerance"
    - "validate.*income.*amount"
    - "declining.*income"
  goal_types:
    - "decision"
  roles:
    - "loan_processor"
    - "underwriter"
    - "quality_control_analyst"
version: "1.3"
status: "current"
effective_date: "2025-02-01"
review_date: "2026-02-01"
supersedes: null
superseded_by: null
author: "Compliance & Standards Team"
last_modified: "2025-01-20"
last_modified_by: "R. Chen"
source: "internal"
source_ref: "BRD-IV-2024-002"
related_corpus_ids:
  - "CRP-PRC-IV-001"
  - "CRP-PRC-IV-002"
  - "CRP-PRC-IV-003"
  - "CRP-REG-IV-001"
  - "CRP-REG-IV-002"
regulation_refs:
  - "Fannie Mae Selling Guide B3-3.1-01"
  - "FHA 4000.1 II.A.4.c"
  - "VA Pamphlet 26-7 Ch. 4"
policy_refs:
  - "POL-IV-004"
  - "POL-QC-001"
---

# Income Variance Threshold Rules

## 1. Purpose

This document defines the business rules governing acceptable variance between stated income (as declared on the loan application) and verified income (as calculated through the income verification process). It also defines the rules for year-over-year income trending and the actions required when thresholds are exceeded.

These rules serve as automated decision points in the income verification process and as quality control checkpoints during pre-close and post-close reviews.

## 2. Variance Calculation Formula

### 2.1. Stated vs. Verified Variance

```
Variance % = |Stated Monthly Income - Verified Monthly Income| / Stated Monthly Income x 100
```

- **Stated Monthly Income:** The gross monthly income declared by the borrower on the Uniform Residential Loan Application (URLA / Form 1003) at the time of initial application.
- **Verified Monthly Income:** The gross monthly qualifying income calculated through the applicable income verification procedure (CRP-PRC-IV-001, CRP-PRC-IV-002, or CRP-PRC-IV-003).
- The absolute value is used because variance in either direction (over-stated or under-stated) triggers review.

### 2.2. Year-Over-Year Trending Variance

```
YoY Variance % = (Year 2 Income - Year 1 Income) / Year 1 Income x 100
```

- A **negative** result indicates declining income.
- A **positive** result indicates increasing income.
- Year 1 = the earlier tax year; Year 2 = the more recent tax year.

### 2.3. YTD Annualized vs. Historical Variance

```
YTD Annualized = (YTD Earnings / Months Elapsed) x 12
Annualized Variance % = (YTD Annualized - Year 2 Income) / Year 2 Income x 100
```

## 3. Stated vs. Verified Variance Decision Table

### 3.1. By Loan Program

| Rule | Loan Program | Variance Range | Result | Required Action |
|------|-------------|----------------|--------|-----------------|
| V-01 | Conventional (Fannie/Freddie) | 0% - 10% | **PASS** | No action required |
| V-02 | Conventional (Fannie/Freddie) | > 10% - 20% | **EXCEPTION** | Document explanation; underwriter sign-off |
| V-03 | Conventional (Fannie/Freddie) | > 20% | **ESCALATION** | Senior underwriter review; re-verify income sources |
| V-04 | FHA | 0% - 15% | **PASS** | No action required |
| V-05 | FHA | > 15% - 25% | **EXCEPTION** | Document explanation; underwriter sign-off |
| V-06 | FHA | > 25% | **ESCALATION** | Senior underwriter review; potential re-disclosure |
| V-07 | VA | 0% - 10% | **PASS** | No action required |
| V-08 | VA | > 10% - 20% | **EXCEPTION** | Document explanation; underwriter sign-off |
| V-09 | VA | > 20% | **ESCALATION** | Senior underwriter review |
| V-10 | USDA | 0% - 10% | **PASS** | No action required |
| V-11 | USDA | > 10% | **EXCEPTION** | Document; USDA has additional income limits to verify |

### 3.2. Direction-Specific Rules

| Rule | Direction | Additional Consideration |
|------|-----------|------------------------|
| V-20 | Verified > Stated (under-stated) | Generally favorable; document but no adverse action. Exception: USDA loans where income limits apply — over-verification may disqualify. |
| V-21 | Verified < Stated (over-stated) | Adverse; may affect DTI qualification. Recalculate DTI with verified figure. If DTI exceeds program limits, escalate. |
| V-22 | Verified < Stated by > 30% | High risk of misrepresentation. Trigger fraud review checklist. Request written explanation from borrower and originating LO. |

## 4. Year-Over-Year Income Trending Decision Table

### 4.1. Income Trend Analysis

| Rule | Trend | YoY Change | Result | Income Calculation Impact |
|------|-------|-----------|--------|--------------------------|
| T-01 | Increasing | > 0% | **PASS** | Use 24-month average |
| T-02 | Stable | 0% (exact) | **PASS** | Use 24-month average |
| T-03 | Slight decline | -1% to -15% | **CAUTION** | Use 24-month average; document explanation |
| T-04 | Moderate decline | -16% to -25% | **EXCEPTION** | Use lower of 24-month or 12-month average; underwriter review required |
| T-05 | Significant decline | > -25% | **ESCALATION** | Senior underwriter review; income may be unusable |
| T-06 | Loss in most recent year | Net loss | **CRITICAL** | Business loss must reduce qualifying income; assess viability |

### 4.2. Trending by Income Type

| Rule | Income Component | Specific Trending Rule |
|------|-----------------|----------------------|
| T-10 | Base salary | Declining base salary is rare and must be explained (demotion, industry downturn, hour reduction) |
| T-11 | Overtime | Decline up to 20% acceptable with employer confirmation of continued availability |
| T-12 | Bonus | Decline up to 25% acceptable if employer confirms bonus program continues |
| T-13 | Commission | Strictly trending-sensitive; any decline requires explanation and lower figure |
| T-14 | Self-employment | Most trending-sensitive; declining SE income questions business viability |
| T-15 | Rental income | Evaluate separately; vacancy or rent reduction may be temporary and explainable |

### 4.3. YTD Annualized Trending

| Rule | YTD vs. Prior Year | Action |
|------|-------------------|--------|
| T-20 | YTD annualized >= Year 2 | Supports income stability; no concern |
| T-21 | YTD annualized 5-15% below Year 2 | Note in file; may indicate seasonal variation if early in year |
| T-22 | YTD annualized > 15% below Year 2 | Investigate cause; request employer or borrower explanation |
| T-23 | YTD annualized > 25% below Year 2 | Red flag; potential change in employment terms, reduced hours, or business decline |
| T-24 | YTD data covers < 3 months | YTD annualization unreliable; do not use for trending comparison; rely on W-2 history |

## 5. Exception Handling Procedures

### 5.1. Exception Documentation Requirements

When a variance threshold is exceeded and the result is EXCEPTION, the following documentation is required:

1. **Variance Calculation Worksheet** showing the exact figures and percentage
2. **Written Explanation** from the borrower (if variance exceeds 15% in any direction)
3. **Processor Narrative** explaining:
   - Root cause of the variance (timing, income change, calculation method)
   - Whether the variance affects loan qualification (DTI impact)
   - Compensating factors (reserves, low LTV, strong credit)
4. **Underwriter Sign-Off** with a determination of:
   - Acceptable with compensating factors
   - Acceptable with additional conditions
   - Not acceptable; loan must be restructured

### 5.2. Escalation Procedures

When a variance result is ESCALATION:

1. All EXCEPTION documentation requirements apply, PLUS:
2. **Senior Underwriter Review** (minimum Level 3 underwriter)
3. **Re-verification** of at least one independent source (e.g., IRS transcript if not already obtained, direct employer contact)
4. **Fraud Indicators Checklist** must be completed if variance exceeds 30%
5. **Management Notification** if variance exceeds 40% or if fraud indicators are present

### 5.3. Re-Disclosure Requirements

If verified income differs from stated income to the extent that the loan terms change (rate, fees, or qualification), the following re-disclosures may be triggered:

- Revised Loan Estimate (within 3 business days of the changed circumstance)
- Updated URLA reflecting accurate income
- New pre-qualification or pre-approval letter (if previously issued)

## 6. Quality Control Application

### 6.1. Pre-Close QC Sampling

During pre-close quality control review, the income variance check is mandatory. QC analysts must:

1. Independently recalculate qualifying income from source documents
2. Compare QC-calculated income to the processor/underwriter-calculated income
3. If the QC calculation differs by more than 5% from the file calculation, flag as a finding
4. Verify that any exceptions were properly documented and approved

### 6.2. Post-Close QC Sampling

For post-close QC reviews, income variance is recalculated with the benefit of complete documentation. Additional checks include:

1. Verify that IRS transcripts (received post-close) match the tax returns in the file
2. If transcript data changes the income calculation by more than 10%, flag as a material finding
3. Material findings require a corrective action plan and may trigger repurchase risk assessment

## 7. System Implementation Notes

These rules are implemented in the Loan Origination System (LOS) as automated checks:

- **V-01 through V-11:** Automated comparison at income finalization; system generates pass/exception/escalation flag
- **T-01 through T-06:** Semi-automated; processor enters historical income figures, system calculates trend
- The LOS will prevent loan submission to underwriting if an ESCALATION flag is unresolved
- Override of automated flags requires supervisor credentials and creates an audit trail

## 8. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.3 | 2025-01-20 | R. Chen | Added USDA variance rules, YTD annualization rules, fraud checklist trigger |
| 1.2 | 2024-06-15 | R. Chen | Updated FHA threshold from 10% to 15% per HUD guidance |
| 1.1 | 2023-09-01 | M. Torres | Added direction-specific rules and re-disclosure triggers |
| 1.0 | 2022-01-10 | Compliance & Standards Team | Initial release |
