---
capsule_id: "CAP-IV-QAL-001"
bpmn_task_id: "Task_CalcQualifying"
bpmn_task_name: "Calculate Qualifying Income"
bpmn_task_type: "businessRuleTask"
process_id: "Process_IncomeVerification"
process_name: "Income Verification"
version: "1.0"
status: "draft"
generated_from: "income-verification.bpmn"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
last_modified: "2026-04-09T00:00:00Z"
last_modified_by: "MDA Demo"
owner_role: "Verification Agent"
owner_team: "Income Verification"
reviewers: []
domain: "Mortgage Lending"
subdomain: "Income Verification"
regulation_refs:
  - "Fannie Mae Selling Guide B3-3.1-01 (Total Qualifying Income)"
  - "FHA 4000.1 II.A.4.c.1 (Effective Income)"
  - "Regulation B / ECOA (Income Nondiscrimination)"
policy_refs:
  - "POL-IV-006 Qualifying Income Calculation Policy"
intent_id: "INT-IV-QAL-001"
contract_id: "ICT-IV-QAL-001"
parent_capsule_id: null
predecessor_ids:
  - "CAP-IV-W2V-001"
  - "CAP-IV-SEI-001"
successor_ids:
  - "CAP-IV-DEC-002"
exception_ids: []
gaps:
  - type: "missing_detail"
    description: "USDA program requires additional household income check against area median income limits (integration not yet designed)"
    severity: "medium"
---

# Calculate Qualifying Income

## Purpose

Aggregates all verified income streams and calculates the total qualifying monthly income for the borrower. This figure is used by the underwriting engine to compute debt-to-income (DTI) ratios and determine loan eligibility.

## Procedure

1. **Collect Verified Income Streams**: Gather all verified income figures from upstream tasks:
   - W-2 verified monthly income (from Task_VerifyW2)
   - Self-employment qualifying monthly income (from Task_VerifySelfEmployment)
   - For HYBRID borrowers, both streams will be present

2. **Apply Program-Specific Rules**:
   - **Conventional (Fannie Mae/Freddie Mac)**: Use the sum of all stable qualifying income sources. Variable income (bonus, overtime, commission) requires 2-year history.
   - **FHA**: Per HUD 4000.1, effective income is the borrower's gross income from all sources that can be expected to continue for at least 3 years.
   - **VA**: Per VA Pamphlet 26-7, effective income includes all reliable income sources.
   - **USDA**: Total annual household income must not exceed program area limits.

3. **Calculate Stated vs. Verified Variance**:
   - Compare the total verified monthly income against the borrower's stated monthly income from the loan application.
   - Compute variance percentage: `variancePercent = abs(stated - verified) / stated * 100`

4. **Determine Variance Threshold**:
   - Standard threshold: 10% for Conventional and VA loans
   - FHA threshold: 15% (more lenient for FHA programs)
   - If variance exceeds threshold, the result triggers the variance exception path.

5. **Build Income Result Object**: Construct the `income_result` data object containing:
   - Total qualifying monthly income
   - Income breakdown by source
   - Stated vs. verified comparison
   - Variance percentage and threshold
   - Pass/fail indicator

6. **Set Gateway Variable**: Write `variancePercent` and `varianceThreshold` to process variables for the Variance gateway evaluation.

## Business Rules

- Fannie Mae Selling Guide B3-3.1-01: Total qualifying income is the sum of all eligible income sources.
- FHA 4000.1 II.A.4.c.1: Effective income must be verified and reasonably expected to continue.
- Regulation B (ECOA): Income from public assistance, alimony, or part-time work cannot be discounted if the borrower chooses to disclose it.
- At least one income verification path (W-2 or Self-Employment) has completed successfully before this task runs.
- Stated income is available in the borrower profile from the loan application.

## Inputs

| Field | Source | Required |
|---|---|---|
| verifiedMonthlyIncome | Process Context | Conditional (W-2 path) |
| qualifyingSelfEmploymentMonthly | Process Context | Conditional (Self-Employment path) |
| incomeComponents | Process Context | Yes |
| borrower_profile.statedMonthlyIncome | Process Context | Yes |
| loanProgram | Process Context | Yes |

## Outputs

| Field | Destination | Description |
|---|---|---|
| income_result | Process Context | Complete income verification result object |
| totalQualifyingMonthlyIncome | Process Context | Sum of all verified qualifying income streams |
| variancePercent | Process Variable | Percentage difference between stated and verified income |
| varianceThreshold | Process Variable | Program-specific acceptable variance limit |
| varianceStatus | Process Context | WITHIN_THRESHOLD or EXCEEDS_THRESHOLD |

## Exception Handling

- **No Verified Income**: If no upstream verification completed successfully, set qualifying income to zero and route to variance exception.
- **Stated Income Missing**: If stated monthly income is null or zero in borrower profile, cannot compute variance; flag for underwriter to obtain stated income.
- **RuleEngine Unavailable**: If RuleEngine service unavailable, retry with backoff; escalate after 3 failures.
