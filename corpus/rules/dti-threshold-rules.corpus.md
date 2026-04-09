---
corpus_id: "CRP-RUL-MTG-003"
title: "DTI Threshold Rules by Loan Program"
slug: "dti-threshold-rules"
doc_type: "rule"
domain: "Mortgage Lending"
subdomain: "Loan Origination"
tags:
  - "dti"
  - "debt-to-income"
  - "threshold"
  - "decision-table"
  - "compensating-factors"
  - "front-end-ratio"
  - "back-end-ratio"
applies_to:
  process_ids:
    - "Process_LoanOrigination"
  task_types:
    - "businessRuleTask"
  task_name_patterns:
    - "dti.*threshold"
    - "dti.*limit"
    - "dti.*exceed"
    - "ratio.*check"
    - "qualify.*dti"
  goal_types:
    - "decision"
  roles:
    - "loan_processor"
    - "underwriter"
version: "3.0"
status: "current"
effective_date: "2025-04-01"
review_date: "2026-04-01"
supersedes: null
superseded_by: null
author: "Underwriting Standards Group"
last_modified: "2025-03-25"
last_modified_by: "A. Mendez"
source: "internal"
source_ref: "RULE-DTI-2025-001"
related_corpus_ids:
  - "CRP-PRC-MTG-004"
  - "CRP-RUL-MTG-001"
  - "CRP-DAT-MTG-001"
regulation_refs:
  - "Fannie Mae Selling Guide B3-6"
  - "FHA 4000.1 II.A.5.d"
  - "VA Pamphlet 26-7 Ch. 4"
  - "USDA HB-1-3555 Ch. 9"
policy_refs:
  - "POL-UW-003"
---

# DTI Threshold Rules by Loan Program

## 1. Purpose

This document provides the definitive decision tables for debt-to-income ratio thresholds across all residential mortgage loan programs. It specifies standard limits, extended limits, required compensating factors, and hard caps. Underwriters and processors must reference these rules when evaluating DTI compliance.

## 2. Conventional Loans (Fannie Mae / Freddie Mac)

### 2.1 AUS-Approved Loans (DU Approve/Eligible or LP Accept)

| Ratio | Standard Limit | Extended Limit | Hard Cap |
|-------|---------------|----------------|----------|
| Front-End (Housing) | No specific limit | No specific limit | No front-end cap for AUS-approved |
| Back-End (Total) | 45% | 50% | 50% (DU will not approve above 50%) |

**Rules:**
- DU evaluates DTI as one of many risk factors; there is no standalone front-end limit
- DU may approve loans up to 50% back-end DTI when compensated by strong residual factors (high credit score, significant reserves, low LTV)
- If DU returns Approve/Eligible at a DTI above 45%, no additional compensating factor documentation is required (the DU approval itself is the justification)
- At DTI above 50%, DU will return Refer/Eligible or Refer with Caution, requiring manual underwriting

### 2.2 Manually Underwritten Conventional Loans

| Ratio | Standard Limit | Maximum with Compensating Factors | Hard Cap |
|-------|---------------|----------------------------------|----------|
| Front-End | 36% | 36% | 36% (no extension for manual UW) |
| Back-End | 36% (credit score >= 720) | 45% | 45% |
| Back-End | 36% (credit score 680-719) | 43% | 43% |
| Back-End | 36% (credit score 620-679) | 36% | 36% (no extension at lower scores) |

**Rules:**
- For manually underwritten conventional loans, front-end ratio is capped at 36% with no exceptions
- Back-end ratio extensions depend on credit score tier
- At least two compensating factors are required for any back-end ratio exceeding 36%

## 3. FHA Loans

### 3.1 AUS-Approved FHA Loans (DU with TOTAL Scorecard Approve)

| Ratio | Standard Limit | Extended Limit | Hard Cap |
|-------|---------------|----------------|----------|
| Front-End | 31% (guideline, not a hard limit under TOTAL) | 46.99% | 46.99% |
| Back-End | 43% (guideline) | 56.99% | 56.99% |

**Rules:**
- FHA TOTAL Scorecard within DU evaluates risk holistically and may approve DTI ratios above standard guidelines
- Company overlay: Maximum back-end DTI of 50% even with TOTAL approval (stricter than FHA allows)
- When TOTAL approves DTI above 43%, the approval recommendation itself serves as documentation
- Loans with DTI above 50% per company overlay require VP-level exception

### 3.2 Manually Underwritten FHA Loans

| DTI Range (Back-End) | Front-End Max | Required Compensating Factors | Additional Requirements |
|----------------------|---------------|------------------------------|------------------------|
| Up to 31% / 43% | 31% | None required | Standard documentation |
| 31.01-37% / 43.01-47% | 37% | At least ONE of the listed factors | Document in loan file |
| 37.01-40% / 47.01-50% | 40% | At least TWO of the listed factors | Narrative explanation required |
| Above 40% / Above 50% | N/A | Not eligible | Manual UW hard cap |

**Acceptable Compensating Factors for FHA Manual UW:**
1. Verified and documented cash reserves equal to at least three months of PITIA after closing
2. New total housing payment is not more than $100 or 5% greater than the previous housing payment (whichever is less), and there is a documented 12-month satisfactory payment history
3. Residual income meets or exceeds the VA residual income guidelines by at least 20%
4. No discretionary debt (no open revolving accounts with balances; proposed housing is the only significant monthly obligation)
5. Demonstrated conservative use of credit: credit utilization below 30% on all revolving accounts, no late payments in the past 24 months
6. Additional income not used for qualification (non-borrower spouse income, anticipated raise with documentation, part-time income with < 2-year history)

### 3.3 FHA Energy Efficient Mortgage (EEM)

| Ratio | Standard Limit | Extended Limit |
|-------|---------------|----------------|
| Front-End | 33% | 45% (with energy improvement financing) |
| Back-End | 45% | 50% (with compensating factors) |

## 4. VA Loans

| Ratio | Guideline | Hard Cap | Notes |
|-------|-----------|----------|-------|
| Front-End | No limit | No hard cap | VA does not use a front-end ratio |
| Back-End | 41% | No hard cap | 41% is a guideline, not a requirement |

**Rules:**
- VA does not impose a hard DTI cap; 41% is a guideline used to flag loans for additional scrutiny
- When back-end DTI exceeds 41%, the underwriter must verify that the borrower meets **residual income** requirements
- Residual income is the amount of net income remaining after all monthly obligations and taxes are deducted
- Residual income minimums vary by region and family size:

| Region | 1 Family Member | 2 Members | 3 Members | 4 Members | 5 Members | Over 5 (add per member) |
|--------|----------------|-----------|-----------|-----------|-----------|------------------------|
| Northeast | $450 | $755 | $909 | $1,025 | $1,062 | $80 |
| Midwest | $441 | $738 | $889 | $1,003 | $1,039 | $75 |
| South | $441 | $738 | $889 | $1,003 | $1,039 | $75 |
| West | $491 | $823 | $990 | $1,117 | $1,158 | $80 |

- For loans above $79,999: Residual income requirements are the table amounts above
- For loans $79,999 and below: Multiply the table amounts by 0.95
- Company overlay: DTI above 60% requires regional manager approval regardless of residual income

## 5. USDA Loans

### 5.1 GUS-Approved USDA Loans

| Ratio | Standard Limit | Extended Limit | Hard Cap |
|-------|---------------|----------------|----------|
| Front-End | 29% | 32% | 32% (GUS may approve up to 32%) |
| Back-End | 41% | 44% | 44% (GUS may approve up to 44%) |

**Rules:**
- GUS (Guaranteed Underwriting System) may approve ratios up to 32%/44% when compensated by strong credit profile
- When GUS approves above standard limits, no additional compensating factor documentation is required
- Company overlay: Back-end DTI above 41% requires at least one compensating factor documented even with GUS approval

### 5.2 Manually Underwritten USDA Loans

| Ratio | Standard Limit | Hard Cap |
|-------|---------------|----------|
| Front-End | 29% | 29% (no extension for manual UW) |
| Back-End | 41% | 41% (no extension for manual UW) |

**Rules:**
- Manually underwritten USDA loans have firm DTI caps with no exceptions
- If DTI exceeds 29%/41%, the borrower must restructure the loan, add income, or reduce debt

## 6. Decision Flow for DTI Evaluation

```
1. Calculate front-end and back-end DTI ratios

2. Is this an AUS-approved loan?
   YES -> Does AUS show Approve/Accept?
          YES -> DTI is acceptable per AUS findings (document the finding)
          NO  -> Proceed to manual UW thresholds
   NO  -> Proceed to manual UW thresholds

3. Compare DTI to program-specific manual UW thresholds:
   a. Both ratios within standard limits?
      YES -> Approved (no compensating factors needed)
      NO  -> Continue

   b. Ratios within extended limits?
      YES -> Document required number of compensating factors
      NO  -> Continue

   c. Ratios exceed hard cap?
      YES -> Ineligible under this program (restructure, change program, or deny)
      NO  -> Should not reach this point; re-evaluate
```

## 7. DTI Rounding and Precision Rules

- All DTI calculations must be carried to two decimal places
- Rounding is performed at the final ratio, not at intermediate steps
- Use standard rounding rules (0.005 rounds up)
- Example: 43.004% rounds to 43.00% (within limit); 43.005% rounds to 43.01% (exceeds limit)
- Income and liabilities should be calculated to the nearest cent before ratio computation

## 8. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 3.0 | 2025-03-25 | A. Mendez | Updated FHA TOTAL scorecard limits; added company overlays; revised VA residual income table |
| 2.0 | 2024-06-01 | A. Mendez | Added USDA thresholds; expanded compensating factors list |
| 1.0 | 2023-03-01 | Underwriting Standards Group | Initial release |
