---
capsule_id: "CAP-PA-ASV-001"
bpmn_task_id: "Task_AssessValue"
bpmn_task_name: "Assess Property Value"
bpmn_task_type: "serviceTask"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"

version: "1.0.0"
status: "draft"

generated_from: "bpmn/property-appraisal.bpmn"
generated_date: "2026-04-09"
generated_by: "mda-pipeline"
last_modified: "2026-04-09"
last_modified_by: "mda-pipeline"

owner_role: "Chief Appraiser"
owner_team: "Appraisal Management"
reviewers:
  - "Underwriting Manager"
  - "Risk Officer"

domain: "Mortgage"
subdomain: "Property Appraisal"
regulation_refs:
  - "USPAP-SR1: Standards Rule 1 - Scope of Work and Approaches to Value"
  - "FNMA-B4-1.3: Fannie Mae Property Valuation and Comparable Sales"
  - "FHA-4000.1-D5: FHA Property Valuation Analysis"
policy_refs:
  - "POL-MTG-APR-006: LTV Calculation and Threshold Policy"
  - "POL-MTG-UW-010: Collateral Risk Assessment Policy"

intent_id: "INT-PA-ASV-001"
contract_id: "ICT-PA-ASV-001"
parent_capsule_id: ""
predecessor_ids:
  - "CAP-PA-VAL-001"
successor_ids:
  - "CAP-PA-NTF-001"
  - "CAP-PA-MRV-001"
exception_ids: []

gaps:
  - "Automated comparable sales validation against MLS data not yet implemented -- see GAP-001"
---

# Assess Property Value

## Purpose

This task evaluates the appraised value from the completed report against the loan parameters to calculate the Loan-to-Value (LTV) ratio and determine whether the property valuation supports the requested financing. The LTV ratio is the primary collateral risk metric in mortgage lending. A value assessment that fails to catch inflated appraisals or insufficient collateral exposes the lender to loss in the event of default.

## Procedure

1. Retrieve the appraised value and supporting data from the UAD XML and the validated appraisal report.
2. Extract comparable sales data including sale prices, adjustment grids, and the appraiser's reconciled value.
3. Cross-reference the comparable sales against available MLS or public records data to verify sale prices and dates.
4. Evaluate the adjustment grid for reasonableness: net adjustments should not exceed 15% and gross adjustments should not exceed 25% of each comparable's sale price per GSE guidelines.
5. Calculate the LTV ratio: LTV = (Loan Amount / Lesser of Appraised Value or Purchase Price) x 100.
6. For refinances, use the appraised value as the denominator (no purchase price comparison).
7. Compare the calculated LTV against the maximum LTV permitted by the loan program.
8. Flag any property condition issues noted in the appraisal that could affect value (deferred maintenance, environmental hazards, functional obsolescence).
9. Record the LTV calculation result and the value assessment determination (Within LTV / Exceeds LTV).
10. Route to the appropriate downstream path based on the LTV determination.

## Business Rules

- LTV is calculated using the lesser of the appraised value or the purchase price for purchase transactions.
- Maximum LTV thresholds vary by loan program: Conventional (97%), FHA (96.5%), VA (100%), Jumbo (80% typical).
- Net adjustments exceeding 15% of a comparable's sale price require a narrative explanation from the appraiser.
- Gross adjustments exceeding 25% of a comparable's sale price trigger a review flag.
- If the appraised value is more than 10% above the contract price, the assessment must flag for potential value inflation.
- Declining market conditions noted in the appraisal require a 5% LTV reduction for risk adjustment.
- Comparable sales older than 6 months carry reduced weight in the reconciliation.

## Inputs Required

| Input | Source | Description |
|-------|--------|-------------|
| Appraised Value | UAD XML / LOS | The reconciled market value opinion from the appraisal |
| Comparable Sales Grid | UAD XML | Sale prices, dates, adjustments for each comparable |
| Loan Amount | LOS | Requested loan amount |
| Purchase Price | LOS | Contract purchase price (for purchase transactions) |
| Transaction Type | LOS | Purchase or refinance indicator |
| Loan Program | LOS | Program type determining maximum LTV threshold |
| MLS/Public Records Data | Data Provider API | Market data for comparable sales verification |

## Outputs Produced

| Output | Destination | Description |
|--------|-------------|-------------|
| LTV Ratio | LOS | Calculated loan-to-value percentage |
| LTV Determination | Gateway_LTV | "Within LTV" or "Exceeds LTV" |
| Adjustment Reasonableness Flags | LOS | Flags for comparable adjustments exceeding thresholds |
| Value Assessment Summary | LOS | Summary of value assessment findings |
| Market Condition Flags | LOS | Declining market or value inflation indicators |

## Exception Handling

- **Comparable Sales Data Unavailable** -- If MLS data cannot be retrieved, proceed with the appraiser's reported comparables only and flag the assessment as "Unverified Comparables."
- **Appraised Value Significantly Above Market** -- If the appraised value exceeds the AVM (Automated Valuation Model) estimate by more than 15%, flag for mandatory manual review.
- **Missing Purchase Price** -- For purchase transactions where the purchase price is not in the LOS, block the assessment and request the loan officer to update the file.
- **Zero or Negative LTV** -- If the calculation produces an impossible result, log a data integrity error and halt processing.

## Regulatory Context

USPAP Standards Rule 1 governs the scope of work and approaches to value used by the appraiser. The lender's value assessment is a secondary review to ensure the appraisal supports the lending decision. Fannie Mae Selling Guide B4-1.3 provides guidelines for evaluating comparable sales and adjustment reasonableness. FHA Handbook 4000.1 Section D5 adds FHA-specific valuation requirements.

## Notes

- Automated Valuation Models (AVMs) may supplement but never replace the USPAP-compliant appraisal for GSE loans.
- The value assessment does not override the appraiser's opinion of value; it evaluates whether that opinion supports the loan terms.
- CLTV (Combined LTV) and HCLTV (Home Equity CLTV) may also be calculated but are outside the scope of this task.
