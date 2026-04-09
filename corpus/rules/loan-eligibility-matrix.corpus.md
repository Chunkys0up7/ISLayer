---
corpus_id: "CRP-RUL-MTG-001"
title: "Loan Eligibility Decision Matrix"
slug: "loan-eligibility-matrix"
doc_type: "rule"
domain: "Mortgage Lending"
subdomain: "Loan Origination"
tags:
  - "eligibility"
  - "credit-score"
  - "ltv"
  - "dti"
  - "loan-program"
  - "property-type"
  - "occupancy"
  - "decision-matrix"
applies_to:
  process_ids:
    - "Process_LoanOrigination"
  task_types:
    - "businessRuleTask"
    - "userTask"
  task_name_patterns:
    - "eligible"
    - "eligibility"
    - "program.*select"
    - "qualify.*loan"
    - "check.*eligibility"
  goal_types:
    - "decision"
  roles:
    - "loan_officer"
    - "loan_processor"
    - "underwriter"
version: "4.0"
status: "current"
effective_date: "2025-05-01"
review_date: "2026-05-01"
supersedes: null
superseded_by: null
author: "Product and Pricing Team"
last_modified: "2025-04-15"
last_modified_by: "M. Chen"
source: "internal"
source_ref: "RULE-ELIG-2025-001"
related_corpus_ids:
  - "CRP-PRC-MTG-003"
  - "CRP-PRC-MTG-004"
  - "CRP-RUL-MTG-003"
  - "CRP-DAT-MTG-001"
regulation_refs:
  - "Fannie Mae Selling Guide B2, B3, B5"
  - "FHA 4000.1"
  - "VA Pamphlet 26-7"
  - "USDA HB-1-3555"
policy_refs:
  - "POL-PROD-001"
---

# Loan Eligibility Decision Matrix

## 1. Purpose

This document defines the eligibility criteria for residential mortgage loan programs offered by the company. It provides decision tables for minimum credit scores, maximum DTI ratios, maximum LTV/CLTV ratios, eligible property types, and occupancy requirements by loan program. Processors and underwriters must consult this matrix when determining program eligibility.

## 2. Credit Score Requirements by Program

### 2.1 Minimum Qualifying Credit Score

The qualifying credit score is the lowest representative score among all borrowers whose income is used to qualify for the loan.

| Loan Program | Minimum Credit Score | Notes |
|-------------|---------------------|-------|
| Conventional (Fannie Mae / Freddie Mac) | 620 | DU/LP may approve with limited exceptions at 620 |
| Conventional - Manually Underwritten | 620 | No exceptions below 620 |
| Conventional - High Balance | 640 | Higher minimum for loan amounts above conforming limit |
| FHA - Standard (3.5% down) | 580 | Minimum for 96.5% LTV |
| FHA - Reduced LTV (10% down) | 500 | 500-579 requires 90% max LTV |
| FHA - Manually Underwritten | 580 | Manual UW not available below 580 |
| FHA - Streamline Refinance | No minimum* | *No credit qualifying for streamline; company overlay: 580 |
| VA - Purchase/Cash-Out | No VA minimum | Company overlay: 580 minimum |
| VA - IRRRL (Streamline Refi) | No VA minimum | Company overlay: 560 minimum |
| USDA - Purchase | 640 | GUS automated approval requires 640; manual UW below 640 |
| Jumbo (Portfolio) | 700 | Per portfolio investor requirements |
| Non-QM | 600 | Varies by sub-program; some allow 580 |

### 2.2 Credit Score Impact on Pricing

Credit scores also affect loan-level price adjustments (LLPAs). The following tiers determine pricing adjustments applied to the base rate:

| Score Range | LLPA Tier | Typical Adjustment (Conventional) |
|-------------|-----------|----------------------------------|
| 780+ | Best pricing | 0.000% |
| 760-779 | Excellent | 0.000% - 0.250% |
| 740-759 | Very Good | 0.250% - 0.500% |
| 720-739 | Good | 0.500% - 0.750% |
| 700-719 | Acceptable | 0.750% - 1.250% |
| 680-699 | Fair | 1.250% - 1.750% |
| 660-679 | Below Average | 1.750% - 2.500% |
| 640-659 | Minimum | 2.500% - 3.250% |
| 620-639 | Floor | 3.250% + |

## 3. Maximum DTI Ratios by Program

| Program | Front-End (Housing) Max | Back-End (Total) Max | Extended Max (with AUS approval / compensating factors) |
|---------|------------------------|---------------------|------------------------------------------------------|
| Conventional (DU Approve/Eligible) | No limit | 45% | Up to 50% with DU approval |
| Conventional (Manually Underwritten) | 36% | 45% | No extension |
| FHA (Standard) | 31% | 43% | Up to 40%/50% with two compensating factors |
| FHA (Manually Underwritten) | 31% | 43% | Up to 37%/47% with one compensating factor; up to 40%/50% with two |
| VA | No limit | 41% (guideline only) | No hard cap; residual income must be met |
| USDA (GUS Approve) | 29% | 41% | Up to 32%/44% with GUS approval |
| USDA (Manually Underwritten) | 29% | 41% | No extension |
| Jumbo (Portfolio) | 35% | 43% | Per investor; typically no extension |

## 4. Maximum LTV/CLTV Ratios

### 4.1 Purchase Transactions

| Program | Max LTV | Max CLTV | Min Down Payment |
|---------|---------|----------|-----------------|
| Conventional (1-unit, primary) | 97% | 97% | 3% |
| Conventional (2-unit, primary) | 85% | 85% | 15% |
| Conventional (3-4 unit, primary) | 75% | 75% | 25% |
| Conventional (1-unit, second home) | 90% | 90% | 10% |
| Conventional (1-unit, investment) | 85% | 85% | 15% |
| Conventional (2-4 unit, investment) | 75% | 75% | 25% |
| FHA (1-4 unit, primary, score >= 580) | 96.5% | 96.5% | 3.5% |
| FHA (1-4 unit, primary, score 500-579) | 90% | 90% | 10% |
| VA (primary residence) | 100% | 100% | 0% |
| USDA (primary residence, eligible area) | 100% | 100% | 0% |
| Jumbo (1-unit, primary) | 80% | 80% | 20% |

### 4.2 Rate-Term Refinance Transactions

| Program | Max LTV | Max CLTV |
|---------|---------|----------|
| Conventional (1-unit, primary) | 97% | 97% |
| Conventional (1-unit, second home) | 90% | 90% |
| Conventional (1-unit, investment) | 75% | 75% |
| FHA (Streamline, non-credit qualifying) | N/A (no appraisal) | N/A |
| FHA (Standard refinance) | 97.75% | 97.75% |
| VA (IRRRL) | N/A (no appraisal) | N/A |
| VA (Standard refinance) | 100% | 100% |
| USDA (Streamline) | N/A (no appraisal) | N/A |

### 4.3 Cash-Out Refinance Transactions

| Program | Max LTV | Max CLTV |
|---------|---------|----------|
| Conventional (1-unit, primary) | 80% | 80% |
| Conventional (2-4 unit, primary) | 75% | 75% |
| Conventional (1-unit, second home) | 75% | 75% |
| Conventional (1-unit, investment) | 75% | 75% |
| FHA (primary, 1-4 unit) | 80% | 80% |
| VA (primary residence) | 100% | 100% |
| USDA | Not available | Not available |

## 5. Eligible Property Types

| Property Type | Conventional | FHA | VA | USDA |
|---------------|-------------|-----|-----|------|
| Single-family detached | Yes | Yes | Yes | Yes |
| PUD (Planned Unit Development) | Yes | Yes | Yes | Yes |
| Condo (warrantable) | Yes | Yes (FHA-approved project) | Yes (VA-approved project) | Yes |
| Condo (non-warrantable) | Limited (Freddie Mac only, specific programs) | No | No | No |
| 2-unit | Yes (primary only for high LTV) | Yes | Yes | No |
| 3-unit | Yes (primary only) | Yes | Yes | No |
| 4-unit | Yes (primary only) | Yes | Yes | No |
| Manufactured (permanent foundation) | Yes (limited programs) | Yes (with FHA foundation cert) | Yes | Yes (new only, permanent foundation) |
| Manufactured (not on permanent foundation) | No | No | No | No |
| Co-op | Yes (limited markets) | No | No | No |
| Mixed-use (primary + commercial) | No | Yes (if residential use >= 51%) | No | No |
| Vacant land | No | No | No | No |
| Condotel / hotel-condo | No | No | No | No |

## 6. Occupancy Requirements

| Occupancy Type | Conventional | FHA | VA | USDA |
|---------------|-------------|-----|-----|------|
| Primary residence | Yes | Yes (required) | Yes (required) | Yes (required) |
| Second home | Yes | No | No | No |
| Investment property | Yes | No | No | No |
| Non-occupant co-borrower allowed | Yes (limited) | Yes (with restrictions) | No | No |

### 6.1 Occupancy Certification Requirements

- **Primary residence:** Borrower must certify intent to occupy within 60 days of closing and maintain occupancy for at least 12 months.
- **Second home:** Property must be in a location that is a reasonable distance from the borrower's primary residence, suitable for year-round use, and the borrower must have exclusive control (no rental pool or management agreement).
- **Investment property:** No occupancy requirement; subject to higher LTV restrictions and pricing adjustments.

## 7. Loan Amount Limits (2025)

| Program | 1-Unit | 2-Unit | 3-Unit | 4-Unit |
|---------|--------|--------|--------|--------|
| Conventional (standard) | $806,500 | $1,032,650 | $1,248,150 | $1,551,250 |
| Conventional (high-cost areas) | Up to $1,209,750 | Up to $1,548,975 | Up to $1,872,225 | Up to $2,326,875 |
| FHA (floor) | $498,257 | $637,950 | $771,125 | $958,350 |
| FHA (ceiling / high-cost) | $1,209,750 | $1,548,975 | $1,872,225 | $2,326,875 |
| VA | No limit | No limit | No limit | No limit |
| USDA | No limit (income limits apply) | N/A | N/A | N/A |

## 8. Quick Eligibility Decision Flow

```
1. Is the qualifying credit score >= program minimum?
   NO  -> Ineligible for this program (consider alternative)
   YES -> Continue

2. Is the LTV/CLTV within program maximum?
   NO  -> Ineligible (consider higher down payment or different program)
   YES -> Continue

3. Is the DTI within program limits (or extended limits with AUS/compensating factors)?
   NO  -> Restructure (reduce loan, add income, pay off debt) or deny
   YES -> Continue

4. Is the property type eligible for the program?
   NO  -> Select alternative program
   YES -> Continue

5. Does the occupancy type meet program requirements?
   NO  -> Select alternative program
   YES -> Eligible - proceed with underwriting
```

## 9. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 4.0 | 2025-04-15 | M. Chen | Updated 2025 conforming loan limits; revised LLPA tiers |
| 3.0 | 2024-11-01 | M. Chen | Added Non-QM program; updated FHA loan limits |
| 2.0 | 2024-01-15 | Product and Pricing Team | Added cash-out refi LTV table; expanded property type matrix |
| 1.0 | 2023-01-01 | Product and Pricing Team | Initial release |
