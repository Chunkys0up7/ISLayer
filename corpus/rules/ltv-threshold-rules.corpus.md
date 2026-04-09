---
corpus_id: "CRP-RUL-PA-002"
title: "LTV Threshold Rules by Loan Program"
slug: "ltv-threshold-rules"
doc_type: "rule"
domain: "Mortgage Lending"
subdomain: "Property Appraisal"
tags:
  - "ltv"
  - "loan-to-value"
  - "cltv"
  - "pmi"
  - "conventional"
  - "fha"
  - "va"
  - "usda"
  - "jumbo"
  - "property-type"
applies_to:
  process_ids:
    - "Process_PropertyAppraisal"
    - "Process_UnderwritingReview"
    - "Process_LTVCalculation"
  task_types:
    - "businessRuleTask"
  task_name_patterns:
    - "ltv"
    - "loan.*to.*value"
    - "calculate.*ltv"
    - "check.*ltv"
    - "verify.*ltv"
  goal_types:
    - "validation"
    - "decision"
  roles:
    - "underwriter"
    - "senior_underwriter"
    - "loan_processor"
version: "2.1"
status: "current"
effective_date: "2025-06-01"
review_date: "2026-06-01"
supersedes: null
superseded_by: null
author: "Underwriting Standards Committee"
last_modified: "2025-05-20"
last_modified_by: "L. Fernandez"
source: "internal"
source_ref: "RUL-PA-2025-002"
related_corpus_ids:
  - "CRP-PRC-PA-003"
  - "CRP-PRC-PA-005"
regulation_refs:
  - "Fannie Mae Selling Guide B2-1.3-01"
  - "FHA 4000.1 II.A.1.b"
  - "VA Lenders Handbook Chapter 9"
  - "USDA HB-1-3555 Chapter 12"
policy_refs:
  - "POL-PA-001"
  - "POL-UW-001"
---

# LTV Threshold Rules by Loan Program

## 1. Purpose

This document defines the maximum Loan-to-Value (LTV), Combined Loan-to-Value (CLTV), and Home Equity Combined Loan-to-Value (HCLTV) ratios permitted by loan program and property type. These thresholds are applied during the Property Value Assessment procedure (CRP-PRC-PA-003) and underwriting review. Investor overlays may impose stricter limits than those shown here.

## 2. LTV Calculation Formulas

```
LTV   = Loan Amount / Base Value x 100
CLTV  = (All Mortgage Liens) / Base Value x 100
HCLTV = (All Mortgage Liens + Revolving Credit Lines) / Base Value x 100
```

**Base Value Determination:**

| Transaction Type | Base Value |
|---|---|
| Purchase | Lesser of appraised value or purchase price |
| Rate/Term Refinance | Appraised value |
| Cash-Out Refinance | Appraised value |
| Construction-to-Permanent | Lesser of appraised value (as-completed) or total acquisition cost |

## 3. Maximum LTV by Loan Program

### 3.1 Conventional Loans (Fannie Mae / Freddie Mac)

| Transaction Type | Occupancy | Max LTV | Max CLTV | PMI Required |
|---|---|---|---|---|
| Purchase | Primary Residence | 97% | 97% | Yes, if LTV > 80% |
| Purchase | Second Home | 90% | 90% | Yes, if LTV > 80% |
| Purchase | Investment Property | 85% | 85% | N/A (not available) |
| Rate/Term Refinance | Primary Residence | 97% | 97% | Yes, if LTV > 80% |
| Rate/Term Refinance | Second Home | 90% | 90% | Yes, if LTV > 80% |
| Rate/Term Refinance | Investment Property | 75% | 75% | N/A |
| Cash-Out Refinance | Primary Residence | 80% | 80% | No |
| Cash-Out Refinance | Second Home | 75% | 75% | No |
| Cash-Out Refinance | Investment Property | 75% | 75% | No |

**Notes:**
- 97% LTV requires fixed-rate mortgage, at least 1 borrower is first-time homebuyer (Fannie Mae HomeReady or standard), or meets Freddie Mac Home Possible criteria
- Standard conventional purchase without PMI: maximum 80% LTV
- PMI cancellation available at 80% LTV based on original value; automatic termination at 78%

### 3.2 FHA Loans

| Transaction Type | Max LTV | Max CLTV | MIP Required |
|---|---|---|---|
| Purchase (credit score >= 580) | 96.50% | 96.50% | Yes (upfront + annual) |
| Purchase (credit score 500-579) | 90.00% | 90.00% | Yes (upfront + annual) |
| Rate/Term Refinance | 97.75% | 97.75% | Yes |
| FHA Streamline Refinance | 97.75% | 97.75% | Yes (reduced MIP) |
| Cash-Out Refinance | 80.00% | 80.00% | Yes |
| FHA 203(k) Rehabilitation | 96.50% | 96.50% | Yes; based on as-improved value |

**Notes:**
- FHA requires upfront MIP of 1.75% (financed into loan amount) and annual MIP
- Annual MIP ranges from 0.45% to 1.05% based on LTV, loan term, and loan amount
- MIP for term > 15 years and LTV > 90%: MIP required for life of loan
- FHA floor credit score: 500 (no FHA loan below 500 FICO)

### 3.3 VA Loans

| Transaction Type | Max LTV | Max CLTV | Funding Fee |
|---|---|---|---|
| Purchase | 100% | 100% | Yes (varies by service, down payment, usage) |
| Rate/Term Refinance (IRRRL) | 100% | 100% | Yes (0.50% for IRRRL) |
| Cash-Out Refinance | 100% | 100% | Yes |

**Notes:**
- No maximum LTV for VA purchase; 100% financing available for eligible veterans
- VA funding fee ranges from 1.25% to 3.30% based on down payment, service type, and prior VA loan usage
- Funding fee exempt for veterans with service-connected disability (10%+ rating)
- No private mortgage insurance required
- VA appraisal must be performed by VA-assigned appraiser from the VA fee panel

### 3.4 USDA Loans

| Transaction Type | Max LTV | Max CLTV | Guarantee Fee |
|---|---|---|---|
| Purchase | 100% | 100% | Yes (1.00% upfront + 0.35% annual) |
| Streamline Refinance | 100% | N/A | Yes |
| Non-Streamline Refinance | 100% | 100% | Yes |

**Notes:**
- Property must be in USDA-eligible rural area
- Income limits apply (115% of area median income)
- No cash-out refinance option
- Guarantee fee may be financed into loan amount

### 3.5 Jumbo Loans (Non-Agency)

| Transaction Type | Occupancy | Max LTV | Max CLTV |
|---|---|---|---|
| Purchase | Primary Residence | 80% | 80% |
| Purchase | Second Home | 75% | 75% |
| Purchase | Investment Property | 70% | 70% |
| Rate/Term Refinance | Primary Residence | 80% | 80% |
| Rate/Term Refinance | Second Home | 75% | 75% |
| Cash-Out Refinance | Primary Residence | 70% | 70% |
| Cash-Out Refinance | Second Home | 65% | 65% |
| Cash-Out Refinance | Investment Property | 60% | 60% |

**Notes:**
- Jumbo thresholds vary by investor; these represent the most common guidelines
- Some investors offer up to 89.99% LTV with enhanced PMI for jumbo purchases
- Minimum credit score typically 700+ for jumbo loans
- Enhanced documentation requirements (larger reserve requirements, additional income verification)

## 4. Maximum LTV by Property Type

Property type adjustments apply as overlays on top of program-specific limits. The effective maximum LTV is the lower of the program limit and the property type limit.

| Property Type | Conv. Purchase Max LTV | FHA Purchase Max LTV | VA Purchase Max LTV | USDA Purchase Max LTV | Jumbo Purchase Max LTV |
|---|---|---|---|---|---|
| Single-Family Residence (SFR) | 97% | 96.50% | 100% | 100% | 80% |
| Condominium (warrantable) | 97% | 96.50% | 100% | 100% | 75% |
| Condominium (non-warrantable) | 75% | N/A | N/A | N/A | 70% |
| 2-Unit Property | 85% | 96.50% | 100% | N/A | 75% |
| 3-4 Unit Property | 75% | 96.50% | 100% | N/A | N/A |
| Manufactured Housing (permanent foundation) | 95% | 96.50% | 100% | 100% | N/A |
| Manufactured Housing (chattel) | N/A | 96.50% | N/A | N/A | N/A |
| Co-op | 80% | N/A | N/A | N/A | 70% |
| PUD | 97% | 96.50% | 100% | 100% | 80% |

## 5. Declining Market Adjustments

When the appraisal indicates a declining market for the subject property's neighborhood, the following LTV reductions apply:

| Program | Standard Max LTV | Declining Market Max LTV | Reduction |
|---|---|---|---|
| Conventional (purchase, primary) | 97% | 92% | 5% |
| Conventional (purchase, second home) | 90% | 85% | 5% |
| Conventional (purchase, investment) | 85% | 80% | 5% |
| FHA | No reduction | No reduction | 0% |
| VA | No reduction | No reduction | 0% |
| Jumbo | Per investor | Typically 5-10% reduction | Varies |

## 6. Decision Logic

```
IF calculated_LTV > program_max_LTV THEN
    IF (calculated_LTV - program_max_LTV) <= 3% AND loan is eligible for override THEN
        Route to manual review (CRP-PRC-PA-005)
    ELSE
        DENY or require restructure
    END IF
END IF

IF market_condition = "declining" AND program has declining_market_adjustment THEN
    effective_max_LTV = program_max_LTV - declining_market_reduction
    Re-evaluate against effective_max_LTV
END IF

IF property_type_max_LTV < program_max_LTV THEN
    effective_max_LTV = property_type_max_LTV
END IF
```

## 7. References

- CRP-PRC-PA-003: Property Value Assessment Procedure
- CRP-PRC-PA-005: Appraisal Manual Review Procedure
- Fannie Mae Selling Guide B2-1.3-01
- FHA 4000.1 II.A.1.b
- VA Lenders Handbook Chapter 9
- USDA HB-1-3555 Chapter 12
