---
corpus_id: "CRP-RUL-IV-001"
title: "Employment Type Classification Rules"
slug: "employment-type-classification"
doc_type: "rule"
domain: "Mortgage Lending"
subdomain: "Income Verification"
tags:
  - "employment-classification"
  - "w-2"
  - "self-employed"
  - "commissioned"
  - "part-time"
  - "gig-economy"
  - "1099"
  - "ownership"
applies_to:
  process_ids:
    - "Process_IncomeVerification"
    - "Process_UnderwritingReview"
  task_types:
    - "businessRuleTask"
    - "userTask"
  task_name_patterns:
    - "classify.*employment"
    - "employment.*type"
    - "determine.*employment"
    - "identify.*income.*type"
    - "categorize.*borrower"
  goal_types:
    - "decision"
  roles:
    - "loan_processor"
    - "underwriter"
    - "income_analyst"
    - "loan_officer"
version: "2.0"
status: "current"
effective_date: "2025-01-01"
review_date: "2026-01-01"
supersedes: null
superseded_by: null
author: "Compliance & Standards Team"
last_modified: "2024-12-10"
last_modified_by: "R. Chen"
source: "internal"
source_ref: "BRD-IV-2024-001"
related_corpus_ids:
  - "CRP-PRC-IV-001"
  - "CRP-PRC-IV-002"
  - "CRP-PRC-IV-003"
  - "CRP-REG-IV-001"
  - "CRP-REG-IV-002"
regulation_refs:
  - "Fannie Mae Selling Guide B3-3.1-01"
  - "Fannie Mae Selling Guide B3-3.1-09"
  - "Fannie Mae Selling Guide B3-3.1-10"
  - "FHA 4000.1 II.A.4.c"
policy_refs:
  - "POL-IV-004"
  - "POL-IV-007"
---

# Employment Type Classification Rules

## 1. Purpose

This document defines the decision rules for classifying a borrower's employment type. Correct classification determines which income verification procedure applies, what documentation is required, and how income is calculated for mortgage qualification.

Employment classification must be determined **before** income verification begins. Misclassification results in incorrect documentation requirements and potentially inaccurate income calculations.

## 2. Classification Decision Table

### Primary Classification Matrix

| # | Condition | Classification | Verification Procedure | Key Documentation |
|---|-----------|---------------|----------------------|-------------------|
| R1 | Receives W-2 AND owns < 25% of employing entity (or no ownership) | **W-2 Employee** | CRP-PRC-IV-001 | W-2, paystubs, VOE |
| R2 | Owns >= 25% of any business entity (regardless of W-2 receipt) | **Self-Employed** | CRP-PRC-IV-002 | 2 years personal + business tax returns, Form 1084 |
| R3 | Commission income >= 25% of total compensation | **Commissioned Employee** | CRP-PRC-IV-001 (commission variant) | W-2, paystubs, 2 years tax returns (required regardless of DU waiver) |
| R4 | Receives 1099-NEC/1099-MISC, no W-2, files Schedule C | **Self-Employed (Sole Proprietor)** | CRP-PRC-IV-002 | 2 years personal tax returns with Schedule C |
| R5 | Employed part-time (< 30 hrs/week) or seasonally | **Part-Time / Seasonal** | CRP-PRC-IV-001 (with continuity analysis) | W-2, paystubs, VOE confirming schedule, 2-year history |
| R6 | Multiple 1099 sources, no single employer relationship | **Gig / Contract Worker** | CRP-PRC-IV-002 | 2 years tax returns, Schedule C, evidence of ongoing contracts |
| R7 | Receives W-2 AND 1099 from same entity | **Investigate** | Determine true relationship | Request clarification from employer; possible misclassification |
| R8 | Military active duty or reserve | **Military** | CRP-PRC-IV-001 (military variant) | LES (Leave and Earnings Statement), DD-214 if separated |
| R9 | Employed by family member (parent, spouse, sibling) | **Related-Party Employee** | CRP-PRC-IV-001 + enhanced verification | W-2, paystubs, VOE, 2 years tax returns, proof of arm's-length employment |

### Rule Precedence

When multiple conditions are true simultaneously, apply rules in this priority order:

1. **Self-employment (R2)** takes precedence over all other classifications. A borrower who owns 25%+ of a business is self-employed even if they also receive W-2 wages from that business.
2. **Commissioned (R3)** takes precedence over standard W-2 if the commission threshold is met.
3. **Related-party (R9)** adds enhanced verification requirements on top of the base classification.
4. **Part-time/Seasonal (R5)** modifies the base W-2 or SE classification with additional continuity requirements.

## 3. Detailed Classification Rules

### Rule R1: W-2 Employee

**Criteria (ALL must be true):**
- Borrower receives Form W-2 from the employer
- Borrower does not own 25% or more of the employing entity
- Borrower is not an officer of the company who also owns equity (check application question and W-2 Box 13 "Statutory employee")
- Commission income (if any) is less than 25% of total compensation

**Documentation Required:**
- W-2 forms for the most recent 2 calendar years
- Most recent 30 days of paystubs
- VOE (written or third-party service)
- Verbal VOE within 10 business days of closing

**Income Calculation:** Per CRP-PRC-IV-001.

### Rule R2: Self-Employed

**Criteria (ANY one is sufficient):**
- Borrower owns 25% or more of a business entity (corporation, LLC, partnership, sole proprietorship)
- Borrower is identified as a general partner on a K-1
- Borrower files Schedule C with gross receipts exceeding $10,000/year
- Borrower is the sole proprietor of a business generating income used for qualification

**How to Determine Ownership Percentage:**
1. Review the URLA: Borrower must disclose ownership interests
2. Review K-1 forms: Box J (Partner's share of profit) or Box F (Shareholder's percentage of stock owned)
3. Review corporate documents if available (operating agreement, articles of incorporation)
4. Cross-reference with business tax return schedules

**Documentation Required:**
- 2 years of complete personal federal tax returns
- 2 years of complete business federal tax returns (1065, 1120S, or 1120)
- All K-1 forms
- Form 1084 (Cash Flow Analysis)
- Business verification (license, third-party confirmation)
- YTD Profit & Loss (if applicable)

**Income Calculation:** Per CRP-PRC-IV-002.

### Rule R3: Commissioned Employee

**Criteria:**
- Commission income represents 25% or more of the borrower's total annual compensation
- Determination based on the most recent 12 months of earnings data

**Commission Percentage Calculation:**
```
Commission % = (Total Commission Earned in 12 months / Total Compensation in 12 months) x 100
```

**Where to find commission data:**
- Paystub YTD earnings breakdown (look for "commission" or "incentive" line items)
- W-2 (total Box 1 vs. base salary from VOE; the difference may include commissions)
- VOE (should break down base vs. commission)

**Key Difference from Standard W-2:**
- Tax returns are **always required** for commissioned borrowers (cannot be waived by DU)
- Two-year commission history is required
- Declining commission trend requires the lower of 12-month or 24-month average

### Rule R4: Self-Employed Sole Proprietor (1099 Income)

**Criteria:**
- Borrower receives Form 1099-NEC or 1099-MISC for services performed
- No W-2 is issued for this income
- Borrower files Schedule C on their personal tax return

**Critical Distinction:**
- A borrower who receives a single 1099 from one client is still self-employed, not a "contract employee"
- The IRS classification (not the borrower's self-description) determines the category
- Borrowers who say they are "contractors" or "freelancers" are self-employed for mortgage purposes

### Rule R5: Part-Time / Seasonal Employee

**Criteria:**
- Borrower works fewer than 30 hours per week, OR
- Employment is seasonal (e.g., tax preparation, landscaping, retail holiday work)
- Borrower receives W-2 from this employment

**Continuity Requirements:**
- Two-year history of part-time/seasonal employment in the same position or field
- Employer confirms the borrower's intent and ability to continue
- If seasonal, income must be averaged over the full 24-month period (including non-working months)

**When Part-Time Income Cannot Be Used:**
- Less than 12 months in the position
- Employer cannot confirm ongoing availability
- Hours are not guaranteed and have varied significantly

### Rule R6: Gig / Contract Worker

**Criteria:**
- Income derived from multiple sources with no single traditional employer
- Examples: rideshare drivers, delivery services, freelance platforms, independent consulting
- Typically multiple 1099s or direct deposits from platform companies

**Treated As:** Self-employed (sole proprietor). Must follow CRP-PRC-IV-002.

**Additional Considerations:**
- Mileage and vehicle expenses on Schedule C may significantly reduce net income
- Platform-reported income (1099-K) may differ from Schedule C gross receipts; reconcile
- If the borrower uses multiple platforms, all must be accounted for on Schedule C

### Rule R7: W-2 and 1099 from Same Entity

**Action Required:** Investigate before classifying.

**Possible Explanations:**
- Employee changed status mid-year (W-2 for part of year, 1099 for remainder)
- Misclassification by employer (IRS may consider them an employee)
- Borrower performs different functions under different arrangements

**Resolution:**
1. Request a written explanation from the borrower
2. Contact the employer to clarify the relationship
3. Review the IRS guidelines for worker classification
4. Classify based on the current and expected future arrangement

### Rule R8: Military Employment

**Criteria:**
- Active duty, reserve, or National Guard member
- Income documented via Leave and Earnings Statement (LES)

**Special Considerations:**
- Base pay, BAH (Basic Allowance for Housing), and BAS (Basic Allowance for Subsistence) are qualifying income
- BAH and BAS are non-taxable and may be grossed up per CRP-PRC-IV-003
- Flight pay, hazard pay, and combat pay that are expected to continue may qualify
- Short remaining service time (< 12 months) requires re-enlistment confirmation or evidence of civilian employment plans

### Rule R9: Related-Party Employment

**Criteria:**
- Borrower is employed by a family member (parent, child, sibling, spouse, in-law)
- Borrower is employed by a company owned by a family member

**Enhanced Verification:**
- Standard W-2 verification applies, PLUS:
- Two years of personal tax returns are required (even if DU waives them)
- VOE must confirm arm's-length employment (same compensation as non-related employees in similar roles)
- If the borrower is the only employee or the primary employee, consider treating as self-employed

## 4. Edge Cases and Escalation

| Scenario | Action |
|----------|--------|
| Borrower recently transitioned from W-2 to self-employed (< 2 years) | May use prior W-2 income if in the same field; requires senior underwriter approval |
| Borrower has both W-2 and SE income from different sources | Classify and verify each income source separately under its applicable procedure |
| Borrower's ownership percentage is exactly 25% | Treated as self-employed (the threshold is "25% or more," not "more than 25%") |
| Borrower sold their business within the past 12 months | Prior SE income cannot be used; only current W-2 income (if any) qualifies |
| Borrower is a real estate agent receiving W-2 from brokerage | Generally self-employed due to the nature of the work, even with W-2; verify with brokerage |
| Borrower is a statutory employee (W-2 Box 13 checked) | Treated as self-employed; file Schedule C |

## 5. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.0 | 2024-12-10 | R. Chen | Added gig worker and military classifications, expanded edge cases |
| 1.5 | 2024-03-01 | R. Chen | Added related-party employment rules |
| 1.0 | 2022-01-10 | Compliance & Standards Team | Initial release |
