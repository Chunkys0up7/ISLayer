---
corpus_id: "CRP-PRC-IV-003"
title: "Qualifying Income Calculation Procedure"
slug: "qualifying-income-calculation"
doc_type: "procedure"
domain: "Mortgage Lending"
subdomain: "Income Verification"
tags:
  - "qualifying-income"
  - "income-calculation"
  - "income-aggregation"
  - "frequency-conversion"
  - "variable-income"
  - "dti"
applies_to:
  process_ids:
    - "Process_IncomeVerification"
    - "Process_UnderwritingReview"
    - "Process_DTICalculation"
  task_types:
    - "userTask"
    - "businessRuleTask"
    - "serviceTask"
  task_name_patterns:
    - "calc.*qualifying"
    - "calculate.*income"
    - "aggregate.*income"
    - "sum.*income"
    - "determine.*monthly.*income"
    - "finalize.*income"
  goal_types:
    - "data_production"
  roles:
    - "loan_processor"
    - "underwriter"
    - "income_analyst"
version: "1.4"
status: "current"
effective_date: "2025-04-01"
review_date: "2026-04-01"
supersedes: null
superseded_by: null
author: "Operations Standards Committee"
last_modified: "2025-03-20"
last_modified_by: "J. Whitfield"
source: "internal"
source_ref: "SOP-IV-2025-003"
related_corpus_ids:
  - "CRP-PRC-IV-001"
  - "CRP-PRC-IV-002"
  - "CRP-RUL-IV-002"
  - "CRP-DAT-IV-001"
regulation_refs:
  - "Fannie Mae Selling Guide B3-3.1-01"
  - "FHA 4000.1 II.A.4.c.1"
policy_refs:
  - "POL-IV-004"
---

# Qualifying Income Calculation Procedure

## 1. Scope

This procedure defines how to aggregate all verified income sources into a single qualifying monthly income figure used for debt-to-income (DTI) ratio calculation. It applies after individual income streams have been verified through their respective procedures (W-2 per CRP-PRC-IV-001, self-employment per CRP-PRC-IV-002, and other income-specific procedures).

This is the final step in the income verification process before income is submitted for underwriting DTI analysis.

## 2. Prerequisites

| # | Prerequisite | Source |
|---|---|---|
| 1 | All individual income sources verified per applicable procedures | Income verification files |
| 2 | Income Calculation Worksheets (Form ICW-100) completed for each income source | Processor |
| 3 | Variance analysis completed for each income source | Processor |
| 4 | Employment classifications determined per CRP-RUL-IV-001 | Processor |

## 3. Procedure Steps

### Step 1: Enumerate All Income Sources

1.1. Review the loan application (URLA) and all income documentation to compile a complete list of income sources for each borrower. Common sources include:

| Category | Income Types |
|----------|-------------|
| Employment | Base salary, hourly wages, overtime, bonus, commission, tips |
| Self-Employment | Sole proprietorship, partnership, S-Corp, C-Corp |
| Rental | Net rental income from investment properties |
| Retirement | Social Security, pension, annuity, IRA distributions |
| Government | VA benefits, disability, public assistance |
| Investment | Dividends, interest (if used for qualifying) |
| Other | Alimony, child support, foster care, boarder income, trust income |

1.2. For each income source, confirm that:
- Verification has been completed per the applicable procedure
- The income is documented as likely to continue for at least three years from the mortgage closing date (Fannie Mae) or the foreseeable future (FHA/VA)
- The income is not from an excluded source (e.g., income from illegal activities, unverifiable cash income, income that will terminate within 3 years)

1.3. Flag any income sources on the application that were not verified. These must either be verified or excluded from qualifying income with a documented explanation.

### Step 2: Convert All Income to Monthly Figures

2.1. All income must be expressed as a gross monthly amount. Apply the following frequency conversion factors:

| Pay Frequency | Conversion Formula | Multiplier |
|--------------|-------------------|------------|
| Weekly | Amount x 52 / 12 | 4.333 |
| Bi-weekly (every 2 weeks) | Amount x 26 / 12 | 2.167 |
| Semi-monthly (twice per month) | Amount x 24 / 12 | 2.000 |
| Monthly | Amount x 1 | 1.000 |
| Quarterly | Amount x 4 / 12 | 0.333 |
| Annual | Amount / 12 | 0.083 |

2.2. **Important distinctions:**
- **Bi-weekly** (every 2 weeks, 26 pay periods/year) is different from **semi-monthly** (twice per month, 24 pay periods/year). Verify the pay frequency from the paystub, not the borrower's verbal statement.
- When the paystub does not clearly indicate frequency, count the number of pay periods from the YTD earnings and the current pay period.

2.3. For variable income (overtime, bonus, commission), use the averaged monthly figure from the applicable verification procedure. Do not convert a single paycheck amount using frequency multipliers.

### Step 3: Handle Variable and Averaged Income

3.1. Income components that vary from period to period must be averaged:

| Income Type | Averaging Period | Method |
|-------------|-----------------|--------|
| Overtime | 24 months (preferred) or 12 months minimum | Total overtime from W-2s / number of months |
| Bonus | 24 months | Total bonus from W-2s / 24 |
| Commission | 24 months | Total commission from W-2s or tax returns / 24 |
| Self-employment | 24 months (or 12 if declining) | Per CRP-PRC-IV-002 |
| Seasonal employment | 24 months | Annualize full-year earnings / 12 |
| Rental income | Per Schedule E | Net rental per most recent tax year / 12 |

3.2. When the current year annualized amount differs from the historical average:
- Use the **lower** of the two figures if income is declining
- Use the **average** if income is stable or increasing
- Document the rationale for the figure selected

3.3. For income that has been received for less than 24 months but more than 12 months, average over the actual period received. Income received for less than 12 months is generally not eligible for qualifying unless:
- It is base salary from a new job with a reasonable expectation of continuance
- The borrower has a documented history in the same field
- The income is guaranteed by contract

### Step 4: Apply Income-Specific Adjustments

4.1. **Rental Income Adjustments:**
- Start with gross rent from the lease agreement or Schedule E
- Subtract PITIA (principal, interest, taxes, insurance, association dues) for the rental property if not already deducted
- Apply the applicable vacancy factor:
  - Fannie Mae: 25% vacancy factor for properties with no history of rental income
  - FHA: 25% vacancy factor on gross rental income; use Schedule E net if two-year history exists
  - If Schedule E shows a net loss, the loss must be added to the borrower's monthly obligations, not deducted from income

4.2. **Non-Taxable Income Gross-Up:**
- Income that is not subject to federal income tax may be "grossed up" to reflect the tax-equivalent value
- Gross-up factor: multiply by 1.25 (25% gross-up) unless the borrower's actual tax rate can be documented to support a higher factor (maximum gross-up factor is typically 1.25 for conventional, 1.15 for FHA)
- Common non-taxable income types: Social Security benefits (non-taxable portion), VA disability benefits, certain municipal bond interest, child support
- Document the gross-up calculation and the basis for non-taxable status

4.3. **Temporary Income Exclusions:**
- If a borrower is on temporary leave (medical, parental, sabbatical), determine:
  - Is the borrower currently receiving any income (disability, PTO)?
  - What is the documented return-to-work date?
  - Does the employer confirm the borrower's position will be available upon return?
- If return is within 60 days of closing and employer confirms position, use the pre-leave income
- If return is uncertain or beyond 60 days, use only the income currently being received

### Step 5: Aggregate and Calculate Total Qualifying Income

5.1. Sum all verified, converted, and adjusted monthly income amounts:

```
Total Qualifying Monthly Income =
    Σ (Employment income components)
  + Σ (Self-employment income)
  + Σ (Rental income, net)
  + Σ (Retirement / government income, grossed up if applicable)
  + Σ (Other qualifying income)
  - Σ (Business losses from self-employment)
  - Σ (Rental losses)
```

5.2. For co-borrowers, calculate each borrower's income independently, then sum for the total household qualifying income. Maintain separate income calculations in the file for each borrower.

5.3. For non-occupant co-borrowers or co-signers, include their income only when permitted by the loan program:
- Fannie Mae: non-occupant co-borrower income can be included in DTI
- FHA: non-occupant co-signer income cannot be combined for DTI; they only help with credit qualification

### Step 6: Calculate Stated vs. Verified Variance

6.1. Compare the total qualifying monthly income to the income stated on the original loan application:

```
Variance % = |Stated Monthly Income - Verified Monthly Income| / Stated Monthly Income x 100
```

6.2. Apply the variance threshold rules from CRP-RUL-IV-002:

| Loan Program | Acceptable Variance | Action if Exceeded |
|-------------|--------------------|--------------------|
| Conventional | ≤ 10% | Pass |
| Conventional | > 10% | Generate exception; document reason |
| FHA | ≤ 15% | Pass |
| FHA | > 15% | Generate exception; document reason |
| VA | ≤ 10% | Pass |
| VA | > 10% | Generate exception; document reason |

6.3. Common reasons for variance:
- Bonus or overtime that was estimated vs. actual
- Application taken mid-year with partial-year data
- Borrower changed jobs between application and verification
- Self-employment income calculated differently by borrower vs. procedure

6.4. If the verified income is **lower** than stated and causes the DTI to exceed program limits, the loan may require:
- Restructuring (reduced loan amount, increased down payment)
- Program change (to a program with higher DTI limits)
- Addition of a co-borrower
- Denial if no viable alternative exists

### Step 7: Finalize and Record

7.1. Enter the final qualifying monthly income into the Loan Origination System (LOS):
- Total qualifying income per borrower
- Breakdown by income type
- Verification status for each component

7.2. Complete the Income Summary section of the Income Calculation Worksheet with:
- All income sources listed with monthly amounts
- Frequency conversion factors applied
- Gross-up factors applied (if any)
- Final total

7.3. Submit the completed income package for underwriting review, including:
- All verification documentation
- Income Calculation Worksheets
- Form 1084 (if self-employment is present)
- Variance analysis
- Processor narrative for any exceptions or unusual circumstances

## 4. Quality Checks

| Check | Criteria | Action if Failed |
|-------|----------|-----------------|
| Completeness | All application-listed income sources addressed | Verify or document exclusion |
| Frequency accuracy | Pay frequency matches paystub evidence | Correct calculation |
| Math verification | All conversions and sums independently verified | Recalculate |
| Variance threshold | Variance within program limits or exception documented | Document exception |
| Non-taxable gross-up | Gross-up applied correctly and documented | Correct factor |
| Rental income | Vacancy factor and PITIA offset correctly applied | Recalculate |
| LOS entry | LOS income matches worksheet total | Correct LOS entry |

## 5. Common Pitfalls

1. **Confusing bi-weekly and semi-monthly.** This is the single most common calculation error. Bi-weekly (26 periods) yields a higher monthly figure than semi-monthly (24 periods). Always verify from the paystub.

2. **Grossing up taxable income.** Only non-taxable income may be grossed up. Grossing up a W-2 salary is never permitted.

3. **Omitting rental losses.** When Schedule E shows a net rental loss, that loss must be added to the borrower's monthly obligations. It cannot be ignored.

4. **Using net income instead of gross.** For W-2 employees, always use gross income. The only context where net income is relevant is self-employment (net profit from Schedule C).

5. **Not reconciling co-borrower income.** Each borrower's income must be independently calculated and verified. Simply splitting a household total by two borrowers is not acceptable.

6. **Forgetting the 3-year continuance test.** All qualifying income must have a reasonable expectation of continuing for at least three years. Income from a contract ending in 18 months does not qualify unless there is documented evidence of renewal likelihood.

## 6. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.4 | 2025-03-20 | J. Whitfield | Added non-occupant co-borrower rules, updated gross-up limits |
| 1.3 | 2024-09-01 | J. Whitfield | Added temporary leave handling |
| 1.2 | 2024-01-15 | M. Torres | Clarified bi-weekly vs semi-monthly conversion |
| 1.0 | 2022-01-10 | Operations Standards Committee | Initial release |
