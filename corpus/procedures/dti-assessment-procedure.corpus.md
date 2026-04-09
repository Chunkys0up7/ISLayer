---
corpus_id: "CRP-PRC-MTG-004"
title: "DTI Ratio Assessment Procedure"
slug: "dti-assessment-procedure"
doc_type: "procedure"
domain: "Mortgage Lending"
subdomain: "Loan Origination"
tags:
  - "dti"
  - "debt-to-income"
  - "front-end-ratio"
  - "back-end-ratio"
  - "housing-ratio"
  - "qualifying-ratios"
  - "compensating-factors"
applies_to:
  process_ids:
    - "Process_LoanOrigination"
  task_types:
    - "userTask"
    - "businessRuleTask"
  task_name_patterns:
    - "assess.*dti"
    - "debt.*income"
    - "calculate.*ratio"
    - "dti.*calculation"
    - "qualify.*income"
  goal_types:
    - "data_production"
    - "decision"
  roles:
    - "loan_processor"
    - "underwriter"
version: "2.1"
status: "current"
effective_date: "2025-04-01"
review_date: "2026-04-01"
supersedes: null
superseded_by: null
author: "Underwriting Standards Group"
last_modified: "2025-03-25"
last_modified_by: "A. Mendez"
source: "internal"
source_ref: "SOP-UW-2025-004"
related_corpus_ids:
  - "CRP-PRC-MTG-003"
  - "CRP-RUL-MTG-001"
  - "CRP-RUL-MTG-003"
  - "CRP-DAT-MTG-001"
regulation_refs:
  - "Fannie Mae Selling Guide B3-6"
  - "FHA 4000.1 II.A.5.d"
  - "VA Pamphlet 26-7 Ch. 4 Section 9"
  - "USDA HB-1-3555 Ch. 9"
policy_refs:
  - "POL-UW-003"
---

# DTI Ratio Assessment Procedure

## 1. Scope

This procedure details the calculation and assessment of debt-to-income (DTI) ratios for residential mortgage qualification. It covers both the front-end (housing) ratio and back-end (total) ratio, including income and liability determination, program-specific thresholds, and the documentation of compensating factors when ratios exceed standard limits.

The procedure applies to all loan programs and is used by processors during file preparation and by underwriters during credit decisioning.

## 2. Prerequisites

| # | Prerequisite | Source |
|---|---|---|
| 1 | Verified qualifying income calculated and documented | Income verification procedures |
| 2 | Tri-merge credit report received with tradeline analysis complete | CRP-PRC-MTG-003 |
| 3 | Proposed loan terms (amount, rate, term, MI if applicable) | LOS |
| 4 | Property tax and insurance estimates | Appraiser / Insurance agent |
| 5 | HOA dues amount (if applicable) | HOA documentation |

## 3. Procedure Steps

### Step 1: Determine Total Qualifying Monthly Income

1.1. Gather the verified monthly income from all sources for all borrowers whose income is being used to qualify:
- Base employment income (salary or hourly, annualized and divided by 12)
- Overtime, bonus, and commission income (per averaging methodology)
- Self-employment net income (if applicable)
- Rental income (per net rental income calculation, typically 75% of gross rent less PITIA)
- Other income (Social Security, pensions, disability, alimony/child support received, interest/dividend income)
- Non-borrower household income (FHA only, under specific circumstances)

1.2. Use only income that has been verified and documented per the applicable income verification procedure. Stated income is not acceptable for any agency loan program.

1.3. Record the total qualifying monthly income figure on the loan analysis worksheet.

### Step 2: Calculate the Proposed Monthly Housing Expense (Front-End)

2.1. Calculate the total proposed monthly housing expense (PITIA):

| Component | Description | Source |
|-----------|-------------|--------|
| P - Principal & Interest | Monthly P&I payment on the proposed mortgage | Amortization schedule based on loan amount, rate, and term |
| T - Property Taxes | Monthly property tax estimate | Annual tax bill / 12, or tax service estimate |
| I - Homeowner's Insurance | Monthly hazard insurance premium | Insurance quote / 12 |
| A - HOA/Condo Fees | Monthly homeowner's association dues | HOA documentation |
| MI - Mortgage Insurance | Monthly mortgage insurance premium (if LTV > 80% for Conv, or MIP for FHA) | MI rate table or FHA MIP schedule |

2.2. For specific loan types, include additional items:
- **FHA loans:** Include the monthly MIP (upfront MIP is financed into the loan amount; annual MIP is divided by 12)
- **VA loans:** VA funding fee is financed into the loan amount; no monthly MI
- **USDA loans:** Include the annual guarantee fee divided by 12
- **Subordinate financing:** Include the monthly payment on any second mortgage or HELOC

2.3. For adjustable-rate mortgages (ARMs), use the **qualifying rate:**
- Conventional ARMs: The greater of the fully indexed rate (index + margin) or the note rate + 2%
- FHA/VA ARMs: Use the note rate for the initial fixed period if 5+ years; otherwise use note rate + 1% per adjustment cap up to the lifetime cap

2.4. Document each component of the housing expense with its source on the loan analysis worksheet.

### Step 3: Calculate Monthly Recurring Liabilities (Back-End Component)

3.1. From the tri-merge credit report, identify all monthly obligations that must be included in the DTI calculation:

| Liability Type | Monthly Payment Used | Notes |
|----------------|---------------------|-------|
| Revolving credit (credit cards) | Minimum payment shown on credit report (or 5% of balance if no payment reported) | Use actual minimum payment, not required payment |
| Installment loans (auto, personal, student) | Monthly payment per credit report | Conv: may exclude if < 10 payments remaining; FHA: always include |
| Student loans (income-driven repayment) | Actual IBR payment if documented; otherwise 1% of outstanding balance (Conv) or 0.5% (FHA) | Must use documented IBR payment amount from servicer |
| Student loans (deferred) | 1% of outstanding balance (Conv) or 0.5% (FHA/VA) | Cannot use $0 even if in deferment |
| Mortgage on other property | Full PITIA on other owned properties | Offset by rental income per program rules |
| Alimony / child support | Monthly obligation per court order | Must include if > 10 months remaining |
| Court-ordered obligations | Monthly payment per judgment or order | Include regardless of remaining term |
| Contingent liabilities (co-signed loans) | Full monthly payment | Exclude only if primary obligor can document 12 months of payments without borrower contribution |

3.2. **Non-medical collections and charge-offs (Conventional):** Generally do not require payoff and are not included in DTI unless DU findings require it.

3.3. **Non-medical collections (FHA):** If cumulative non-medical collections exceed $1,000, either pay them off or include 5% of the outstanding balance as a monthly liability.

3.4. **Debts paid by business:** If the borrower is self-employed and a debt is paid by the business, it may be excluded from DTI if:
- The debt is documented on the business tax returns as a business expense
- The business has made 12 consecutive months of timely payments
- The business income has not already been reduced by this debt payment

3.5. Sum all monthly recurring liabilities to determine total monthly obligations.

### Step 4: Calculate DTI Ratios

4.1. **Front-End Ratio (Housing Ratio):**
```
Front-End DTI = Total Proposed Housing Expense (PITIA + MI) / Total Qualifying Monthly Income x 100
```

4.2. **Back-End Ratio (Total DTI):**
```
Back-End DTI = (Total Proposed Housing Expense + Total Monthly Recurring Liabilities) / Total Qualifying Monthly Income x 100
```

4.3. Round both ratios to two decimal places.

4.4. Example calculation:
```
Monthly Income:          $8,500
Housing Expense (PITIA): $2,125
Monthly Liabilities:     $1,350

Front-End DTI: $2,125 / $8,500 = 25.00%
Back-End DTI:  ($2,125 + $1,350) / $8,500 = 40.88%
```

### Step 5: Compare Against Program Limits

5.1. Compare the calculated DTI ratios against the applicable program limits (see CRP-RUL-MTG-003 for the full decision table):

| Program | Front-End Max | Back-End Max | Notes |
|---------|--------------|--------------|-------|
| Conventional (DU Approve/Eligible) | N/A (no front-end limit) | 45% standard; up to 50% with DU approval | DU may approve up to 50% with strong compensating factors |
| Conventional (manually underwritten) | 36% | 45% | Hard limits for manual UW |
| FHA (standard) | 31% | 43% | Standard limits |
| FHA (with compensating factors) | 40% | 50% | Requires at least two compensating factors documented |
| FHA (Energy Efficient Mortgage) | 33% | 45% | Stretch ratios for EEM |
| VA | N/A (no front-end limit) | 41% guideline | VA has no hard DTI cap; 41% is a guideline. Residual income must be met. |
| USDA | 29% | 41% | Waiver available up to 32%/44% with strong compensating factors via GUS |

5.2. If DTI ratios are within program limits, document the ratios and proceed with the file.

5.3. If DTI ratios exceed program limits, proceed to Step 6 to evaluate compensating factors.

### Step 6: Document Compensating Factors (When DTI Exceeds Limits)

6.1. When the DTI ratio exceeds the standard program limit but may be eligible with compensating factors, document the applicable factors from the following:

| Compensating Factor | Description | Applicable Programs |
|---------------------|-------------|-------------------|
| Reserves | Borrower has 3+ months of PITIA in liquid reserves after closing | Conv, FHA, VA, USDA |
| Minimal housing payment increase | New PITIA is within 5% of current housing payment | FHA |
| Residual income | Borrower meets VA residual income guidelines (even if not a VA loan) | FHA, VA |
| No discretionary debt | Proposed housing expense is the borrower's only major obligation | FHA |
| Conservative use of credit | Low revolving utilization (< 30%), no late payments in 12+ months | Conv, FHA |
| Down payment | 10% or greater down payment (equity position reduces default risk) | Conv, FHA |
| Employment stability | 5+ years with the same employer or in the same field | FHA |
| High credit score | Representative score 680+ (for FHA high-DTI exceptions) | FHA |
| Non-taxable income gross-up | Income was not grossed up, creating a conservative DTI | Conv, FHA |

6.2. For FHA loans exceeding 43% DTI, at least **two** compensating factors must be documented. For DTI exceeding 50%, manual downgrade is required regardless of AUS findings.

6.3. Write a narrative compensating factor statement in the loan file explaining why the higher DTI is acceptable. The narrative must reference specific dollar amounts, percentages, and documented evidence.

6.4. If compensating factors are insufficient to justify the DTI exception, evaluate options:
- Reduce the loan amount
- Add a co-borrower with additional income
- Pay off liabilities to reduce obligations
- Select an alternative program with higher DTI allowances
- Decline the loan with proper adverse action notice

### Step 7: Record DTI Analysis

7.1. Enter the final DTI ratios into the LOS underwriting module:
- Front-end ratio
- Back-end ratio
- Income total used
- Housing expense total used
- Recurring liability total used
- Compensating factors (if applicable)
- Program DTI limit applied

7.2. Attach the DTI calculation worksheet to the loan file.

7.3. Flag any DTI-related conditions or exceptions for underwriter attention.

## 4. Quality Checks

| Check | Criteria | Action if Failed |
|-------|----------|-----------------|
| Income accuracy | Qualifying income matches verified income documentation | Recalculate from source documents |
| Liability completeness | All credit report liabilities accounted for | Add missing liabilities to calculation |
| Student loan treatment | Correct payment amount used per program rules | Recalculate with correct payment |
| Housing expense completeness | All PITIA components included | Add missing components |
| Math verification | DTI ratios independently recalculated correctly | Correct calculation errors |
| Program limit compliance | Ratios within limits or compensating factors documented | Document compensating factors or restructure |

## 5. Common Pitfalls

1. **Using net income instead of gross income.** DTI ratios always use gross (pre-tax) monthly income. Using net income overstates the DTI ratio.

2. **Excluding student loan payments in deferment.** Even if the current payment is $0, a calculated monthly payment (1% of balance for Conventional, 0.5% for FHA) must be included in the DTI calculation.

3. **Forgetting to include HOA dues.** HOA dues are part of the proposed housing expense and must be included in both the front-end and back-end ratios.

4. **Using the stated credit card minimum instead of the reported minimum.** The monthly payment used for revolving accounts must be the amount reported on the credit report, not the amount stated by the borrower.

5. **Double-counting mortgage payments.** When a borrower owns other properties, include the PITIA on those properties as a liability, but do not double-count the proposed property's PITIA.

6. **Omitting mortgage insurance from the housing expense.** PMI (for Conventional) or MIP (for FHA) is part of the housing expense and affects both ratios.

## 6. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.1 | 2025-03-25 | A. Mendez | Updated FHA collection threshold to $1,000; revised student loan handling per 2025 guidance |
| 2.0 | 2024-08-01 | A. Mendez | Major revision; added USDA thresholds, expanded compensating factors |
| 1.0 | 2023-03-01 | Underwriting Standards Group | Initial release |
