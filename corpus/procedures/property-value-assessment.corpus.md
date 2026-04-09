---
corpus_id: "CRP-PRC-PA-003"
title: "Property Value Assessment Procedure"
slug: "property-value-assessment"
doc_type: "procedure"
domain: "Mortgage Lending"
subdomain: "Property Appraisal"
tags:
  - "value-assessment"
  - "ltv-calculation"
  - "comparable-adjustments"
  - "market-conditions"
  - "property-condition"
applies_to:
  process_ids:
    - "Process_PropertyAppraisal"
    - "Process_UnderwritingReview"
    - "Process_LTVCalculation"
  task_types:
    - "userTask"
    - "businessRuleTask"
  task_name_patterns:
    - "assess.*value"
    - "calculate.*ltv"
    - "review.*appraised.*value"
    - "evaluate.*property.*value"
  goal_types:
    - "validation"
    - "data_production"
  roles:
    - "underwriter"
    - "senior_underwriter"
    - "appraisal_reviewer"
version: "1.1"
status: "current"
effective_date: "2025-06-01"
review_date: "2026-06-01"
supersedes: null
superseded_by: null
author: "Appraisal Operations Committee"
last_modified: "2025-05-12"
last_modified_by: "R. Chatterjee"
source: "internal"
source_ref: "SOP-PA-2025-003"
related_corpus_ids:
  - "CRP-PRC-PA-002"
  - "CRP-RUL-PA-002"
  - "CRP-PRC-PA-005"
  - "CRP-DAT-PA-001"
regulation_refs:
  - "Fannie Mae Selling Guide B4-1.3-01"
  - "FHA 4000.1 II.D.3.d"
  - "VA Lenders Handbook Chapter 10"
policy_refs:
  - "POL-PA-001"
---

# Property Value Assessment Procedure

## 1. Scope

This procedure defines how to assess the appraised value of a property for mortgage lending purposes. It covers value reasonableness analysis, LTV ratio calculation, comparable adjustment review, market condition assessment, and property condition evaluation. This procedure follows the Appraisal Report Review (CRP-PRC-PA-002) and feeds into the underwriting decision.

## 2. Prerequisites

| # | Prerequisite | Source |
|---|---|---|
| 1 | Appraisal report reviewed and completeness verified per CRP-PRC-PA-002 | Appraisal review worksheet |
| 2 | Loan amount and loan program determined | Loan file |
| 3 | Purchase price and contract date (if purchase transaction) | Purchase agreement |
| 4 | LTV threshold rules available (CRP-RUL-PA-002) | Reference library |
| 5 | MLS access and market data sources available | System credentials |

## 3. Procedure Steps

### Step 1: Review Appraised Value

1.1. Record the appraised value from the appraisal report. For reports with multiple approaches to value, confirm the final reconciled value is clearly stated and supported by the reconciliation narrative.

1.2. Compare the appraised value against available benchmarks:

| Benchmark | Acceptable Range |
|---|---|
| Purchase price (if purchase transaction) | Appraised value >= purchase price (no negative equity at origination) |
| Automated Valuation Model (AVM) estimate | Within +/- 10% of AVM median value |
| Prior appraisal (if within 12 months) | Variance explainable by market trends or property improvements |
| Tax assessed value | Informational only; large discrepancies should be investigated |

1.3. If the appraised value is below the purchase price on a purchase transaction, document the shortfall and its impact on LTV. Options include:
- Borrower increases down payment to maintain target LTV
- Parties renegotiate purchase price
- Reconsideration of value is requested per CRP-PRC-PA-004 (only with new comparable data)
- Loan is denied if LTV exceeds program maximum

1.4. If the appraised value significantly exceeds the purchase price (>15% above), investigate for potential concerns such as inflated improvements, seller concessions not reflected, or data errors.

### Step 2: Calculate Loan-to-Value (LTV) Ratio

2.1. Determine the base value for LTV calculation:

| Transaction Type | Base Value |
|---|---|
| Purchase | Lesser of appraised value or purchase price |
| Rate/term refinance | Appraised value |
| Cash-out refinance | Appraised value |
| Construction-to-permanent | Lesser of appraised value (as-completed) or total acquisition cost |

2.2. Calculate the LTV ratio:

```
LTV = (Loan Amount / Base Value) x 100
```

2.3. For transactions involving subordinate financing, also calculate Combined LTV (CLTV):

```
CLTV = (Total of All Mortgage Liens / Base Value) x 100
```

2.4. For HELOCs or other revolving credit, calculate Home Equity CLTV (HCLTV):

```
HCLTV = (First Mortgage + Drawn Balance + Total Credit Line / Base Value) x 100
```

2.5. Compare the calculated LTV, CLTV, and HCLTV against program-specific thresholds per CRP-RUL-PA-002. If any ratio exceeds the maximum for the loan program, the loan requires:
- Restructuring (increased down payment, reduced loan amount)
- Program change (to a program with higher LTV allowance)
- Private mortgage insurance (PMI) for conventional loans exceeding 80% LTV
- Denial if no viable option exists

### Step 3: Check Comparable Adjustments

3.1. Review the adjustment grid in the sales comparison approach. Evaluate each adjustment category:

| Adjustment Category | Typical Range | Red Flag Threshold |
|---|---|---|
| Location | +/- $5,000 - $50,000 | Adjustment > 15% of comp sale price |
| Site/View | +/- $2,000 - $25,000 | Subjective; verify narrative support |
| Design/Appeal | +/- $2,000 - $15,000 | Large adjustments suggest poor comp selection |
| Quality of Construction | +/- $5,000 - $30,000 | Adjusting across more than one quality tier |
| Age/Condition | +/- $3,000 - $20,000 | Adjusting across more than two condition ratings |
| GLA (per sq ft) | +/- $30 - $150 per sq ft | GLA difference > 25% of subject |
| Basement/Finished Area | +/- $5,000 - $25,000 | Adjustment for full basement vs. none |
| Garage/Carport | +/- $3,000 - $15,000 | Verify market support |

3.2. Calculate net and gross adjustment percentages for each comparable:

```
Net Adjustment % = |Sum of Positive Adjustments + Sum of Negative Adjustments| / Comparable Sale Price x 100
Gross Adjustment % = (Sum of |Each Individual Adjustment|) / Comparable Sale Price x 100
```

3.3. Apply the following thresholds per Fannie Mae guidelines:

| Metric | Maximum | Action if Exceeded |
|---|---|---|
| Net adjustment per comparable | 15% of comparable sale price | Flag for additional review; may still be acceptable with strong narrative support |
| Gross adjustment per comparable | 25% of comparable sale price | Flag for additional review; consider requesting additional comparables |
| Both net and gross exceeded | N/A | Strongly consider revision request or additional appraisal |

3.4. Verify that adjustments are consistent across all comparables (e.g., the same feature receives a similar adjustment amount for each comparable where it applies).

3.5. Confirm that the reconciled value falls within the adjusted range of the comparable sales and is adequately supported by the appraiser's narrative.

### Step 4: Verify Market Conditions

4.1. Review the neighborhood analysis section of the appraisal for market condition indicators:

| Indicator | Stable Market | Declining Market | Increasing Market |
|---|---|---|---|
| Property values trend | Stable | Declining | Increasing |
| Demand/Supply | In balance | Over supply | Under supply |
| Marketing time | 3-6 months | Over 6 months | Under 3 months |
| Seller concessions | 0-3% | >3% or increasing | Minimal |

4.2. If the appraiser indicates a declining market:
- Verify with independent market data (MLS statistics, local market reports)
- Consider whether a market conditions addendum is required
- Assess whether additional LTV restrictions apply per investor guidelines
- Some programs require reduced maximum LTV in declining markets (typically 5% reduction)

4.3. Review the time adjustment analysis. If sales more than 3 months old are used, the appraiser should address whether a time adjustment is warranted based on market trends.

4.4. Check for environmental or economic factors that may affect marketability:
- Proximity to environmental hazards (landfill, industrial sites, flood zones)
- Local economic conditions (major employer closures, new development)
- Zoning changes or pending assessments
- Natural disaster history or risk

### Step 5: Assess Property Condition

5.1. Review the condition rating assigned by the appraiser (UAD C1-C6 scale):

| Rating | Description | Lending Impact |
|---|---|---|
| C1 | New construction, no deferred maintenance | No restrictions |
| C2 | No deferred maintenance, limited physical depreciation | No restrictions |
| C3 | Well-maintained, minor deferred maintenance | No restrictions |
| C4 | Adequate maintenance, some deferred maintenance | Acceptable; verify deferred items are cosmetic |
| C5 | Obvious deferred maintenance, some structural issues | Requires additional review; may need repair escrow |
| C6 | Substantial damage or deferred maintenance | Generally ineligible; requires rehabilitation program |

5.2. For condition ratings C5 or C6, evaluate:
- Whether the property meets minimum property standards for the loan program
- FHA requires property to meet HUD Minimum Property Requirements (MPR)
- VA requires property to meet VA Minimum Property Requirements
- Conventional loans follow Fannie Mae property eligibility guidelines
- Whether a repair escrow, completion certificate, or re-inspection is required

5.3. Review the quality rating (UAD Q1-Q6 scale) and verify it is consistent with the neighborhood, comparable sales, and supporting photographs.

5.4. Identify any health and safety concerns noted in the appraisal:
- Lead-based paint (pre-1978 construction)
- Asbestos
- Structural deficiencies
- Non-functional systems (HVAC, plumbing, electrical)
- Missing safety features (handrails, smoke detectors)

5.5. Document all value assessment findings in the underwriting worksheet. Record the final determination:
- **Accept**: Value is supported, LTV within limits, condition acceptable
- **Conditional Accept**: Value supported but conditions required (repairs, re-inspection, additional documentation)
- **Revision Required**: Deficiencies identified requiring appraiser response (proceed to CRP-PRC-PA-004)
- **Reject / Manual Review**: Value not supported or significant concerns (proceed to CRP-PRC-PA-005)

## 4. Exception Handling

| Exception | Action |
|---|---|
| Appraised value significantly below purchase price (>10%) | Notify loan officer; provide borrower options; do not pressure for value |
| AVM variance exceeds 20% from appraised value | Order CDA (Collateral Desktop Analysis) or second appraisal |
| Comparable sales older than 12 months used | Require appraiser to address lack of recent sales in reconciliation |
| Property in FEMA Special Flood Hazard Area | Confirm flood insurance requirement is communicated |

## 5. Quality Controls

- LTV calculations are independently verified by a second reviewer for loans exceeding $500,000
- Value assessment findings are documented on the standardized underwriting worksheet
- Monthly sample audit of 5% of value assessments for consistency and accuracy
- Variance between appraised values and AVMs tracked as a quality metric

## 6. References

- CRP-PRC-PA-002: Appraisal Report Review Procedure
- CRP-RUL-PA-002: LTV Threshold Rules by Loan Program
- CRP-PRC-PA-004: Appraisal Revision Request Procedure
- CRP-PRC-PA-005: Appraisal Manual Review Procedure
- Fannie Mae Selling Guide B4-1.3-01
- FHA 4000.1 II.D.3.d
