---
corpus_id: "CRP-PRC-MTG-003"
title: "Credit Report Ordering and Review Procedure"
slug: "credit-report-procedure"
doc_type: "procedure"
domain: "Mortgage Lending"
subdomain: "Credit"
tags:
  - "credit-report"
  - "tri-merge"
  - "credit-score"
  - "tradeline"
  - "derogatory"
  - "representative-score"
  - "credit-depth"
applies_to:
  process_ids:
    - "Process_LoanOrigination"
  task_types:
    - "userTask"
    - "serviceTask"
  task_name_patterns:
    - "pull.*credit"
    - "credit.*report"
    - "order.*credit"
    - "review.*credit"
    - "credit.*score"
  goal_types:
    - "data_production"
    - "decision"
  roles:
    - "loan_processor"
    - "underwriter"
    - "loan_officer"
version: "2.3"
status: "current"
effective_date: "2025-05-01"
review_date: "2026-05-01"
supersedes: null
superseded_by: null
author: "Credit Operations Team"
last_modified: "2025-04-22"
last_modified_by: "L. Patel"
source: "internal"
source_ref: "SOP-CR-2025-001"
related_corpus_ids:
  - "CRP-PRC-MTG-002"
  - "CRP-PRC-MTG-004"
  - "CRP-RUL-MTG-001"
  - "CRP-POL-MTG-001"
  - "CRP-POL-MTG-002"
  - "CRP-DAT-MTG-002"
regulation_refs:
  - "FCRA 15 U.S.C. 1681"
  - "ECOA Regulation B 12 CFR 1002"
  - "Fannie Mae Selling Guide B3-5"
  - "FHA 4000.1 II.A.5"
policy_refs:
  - "POL-CR-001"
  - "POL-CR-002"
---

# Credit Report Ordering and Review Procedure

## 1. Scope

This procedure governs the ordering, receipt, and analysis of residential mortgage credit reports (tri-merge reports) for all borrowers and co-borrowers. It applies to all loan programs (Conventional, FHA, VA, USDA) and covers the full credit evaluation workflow from initial order through representative score selection and tradeline analysis.

This procedure must be followed in conjunction with CRP-POL-MTG-001 (Credit Report Ordering Policy) and CRP-POL-MTG-002 (Permissible Purpose Policy).

## 2. Prerequisites

| # | Prerequisite | Source |
|---|---|---|
| 1 | Identity verification completed (CRP-PRC-MTG-002) | Compliance |
| 2 | Signed credit authorization from borrower | Borrower |
| 3 | Permissible purpose documented per FCRA | Compliance |
| 4 | Borrower SSN verified against SSA | CIP Process |
| 5 | Access to approved credit report vendor | System |

## 3. Procedure Steps

### Step 1: Order the Tri-Merge Credit Report

1.1. Verify that a valid permissible purpose exists under FCRA before ordering the credit report. For mortgage lending, the permissible purpose is established when the borrower has submitted a loan application and signed a credit authorization form.

1.2. Access the approved credit report vendor through the LOS integration or the vendor's direct portal. The company's approved vendor is [Credit Vendor Name], and all orders must flow through the designated account.

1.3. Enter the borrower information for the credit request:
- Full legal name (first, middle, last, suffix)
- Social Security Number
- Current residential address
- Date of birth
- Prior address (if at current address less than two years)

1.4. Select the report type:
- **Tri-merge residential mortgage credit report (RMCR):** Standard for all mortgage applications. Pulls data from all three bureaus (Experian, Equifax, TransUnion).
- **Joint report:** For applications with co-borrowers. Each borrower gets a separate tri-merge report.
- **Supplemental report:** When updating an existing report within the 120-day validity window.

1.5. Submit the order and record the following in the LOS:
- Order date and time
- Report reference number
- Cost charged (per POL-CR-001 cost controls)
- Ordering user ID

1.6. For joint applications, order separate tri-merge reports for each borrower/co-borrower. Do not use a combined report format, as it can complicate score selection.

### Step 2: Review Credit Scores and Select Representative Score

2.1. Upon receipt of the tri-merge report, extract the credit scores from each bureau:

| Bureau | Score Model | Typical Range |
|--------|------------|---------------|
| Experian | FICO Score 2 (Experian/Fair Isaac Risk Model v2) | 300-850 |
| Equifax | FICO Score 5 (Equifax Beacon 5.0) | 300-850 |
| TransUnion | FICO Score 4 (TransUnion FICO Risk Score 04) | 300-850 |

2.2. Determine the **representative credit score** for each borrower using the following rules:

- **Three scores available:** Use the **middle score** (not the average). Example: Scores of 720, 695, 740 yield a representative score of 720.
- **Two scores available:** Use the **lower of the two scores**. Example: Scores of 720 and 695 yield a representative score of 695.
- **One score available:** Use that score. Document why only one bureau reported. Consider ordering a non-traditional credit report if needed for program eligibility.
- **No scores available:** The borrower is considered a "thin file." Refer to the non-traditional credit evaluation procedure. FHA allows alternative credit assessment; Conventional typically requires a minimum of two tradelines.

2.3. For loans with multiple borrowers, determine the **qualifying credit score** for the loan:
- Use the **lowest representative score** among all borrowers whose income is used to qualify.
- Example: Borrower A has a representative score of 720; Co-Borrower B has a representative score of 680. The qualifying score for the loan is 680.

2.4. Record the representative score and qualifying score in the LOS credit module.

### Step 3: Identify and Analyze Tradelines

3.1. Review all tradelines (credit accounts) reported on the credit report. For each tradeline, note:
- Creditor name and account type (revolving, installment, mortgage, student loan)
- Current balance and credit limit (for revolving accounts)
- Monthly payment amount
- Account status (open, closed, paid, charged off, collection)
- Payment history (30/60/90/120+ day late indicators)
- Date opened and date of last activity
- Responsibility (individual, joint, authorized user)

3.2. **Authorized User Accounts:** Identify any tradelines where the borrower is listed as an authorized user. Per Fannie Mae guidelines:
- Authorized user accounts **may** be included in the credit evaluation if the borrower can demonstrate a history of making payments on the account.
- If the authorized user account represents a significant portion of the borrower's credit history and there is no evidence the borrower has been making payments, the account should be excluded from the credit assessment, and the underwriter should evaluate whether the remaining credit profile is sufficient.

3.3. **Installment Debt with Fewer Than 10 Payments Remaining:** Installment debts (e.g., auto loans, student loans) with fewer than 10 monthly payments remaining may be excluded from DTI calculations for Conventional loans. FHA requires all debts to be included regardless of remaining term.

3.4. Assess **credit depth** using the following criteria:

| Credit Depth Rating | Criteria |
|---------------------|----------|
| Strong | 3+ tradelines open 24+ months, no derogatory history, mix of revolving and installment |
| Acceptable | 2-3 tradelines open 12+ months, minimal derogatory items (0-1 late payments > 12 months ago) |
| Limited | 1-2 tradelines with less than 12 months history or thin file |
| Insufficient | No traditional tradelines or all tradelines are authorized user accounts |

### Step 4: Check for Derogatory Items

4.1. Review the credit report for the following derogatory items and their impact:

| Derogatory Item | Conventional Seasoning | FHA Seasoning | VA Seasoning | USDA Seasoning |
|----------------|----------------------|---------------|--------------|----------------|
| Bankruptcy (Ch. 7) | 4 years from discharge | 2 years from discharge | 2 years from discharge | 3 years from discharge |
| Bankruptcy (Ch. 13) | 2 years from discharge, 4 from filing if not discharged | 1 year of payout with court approval | 1 year of payout | 1 year of payout |
| Foreclosure | 7 years from completion | 3 years from completion | 2 years from completion | 3 years from completion |
| Short sale / Deed-in-lieu | 4 years (2 with extenuating circumstances) | 3 years from completion | 2 years from completion | 3 years from completion |
| Collections (medical) | Excluded from DTI; do not require payoff | Excluded from DTI | Excluded from DTI | Excluded from DTI |
| Collections (non-medical) | May require payoff per DU findings | Debts > $1,000 cumulative: must pay off or include 5% of balance in DTI | No payoff required per VA | Must be paid or included in DTI |
| Judgments | Must be paid prior to or at closing | Must be paid prior to or at closing | Must be paid or in payment plan | Must be paid prior to closing |
| Tax liens | Must be paid or in IRS payment plan (3 months seasoning) | Must be paid or in payment plan (3 months) | Must be paid or in payment plan | Must be paid |

4.2. For each derogatory item found, calculate the seasoning period from the applicable date (discharge date, completion date, or satisfaction date) to the present.

4.3. If a derogatory item falls within the required seasoning period, document the borrower's explanation and any extenuating circumstances. Extenuating circumstances that may reduce seasoning requirements include:
- Job loss due to employer downsizing (not voluntary resignation)
- Serious medical event affecting ability to work
- Death of a primary wage earner
- Natural disaster affecting the property

4.4. Record all derogatory items, seasoning calculations, and borrower explanations in the credit analysis section of the loan file.

### Step 5: Assess Overall Credit Profile

5.1. Compile the credit analysis summary:
- Representative score and qualifying score
- Credit depth rating
- Total number of open tradelines
- Total revolving utilization ratio (aggregate balances / aggregate limits)
- Derogatory item summary and seasoning status
- Any fraud alerts, security freezes, or consumer statements

5.2. Determine if the credit profile meets the minimum requirements for the requested loan program per CRP-RUL-MTG-001 (Loan Eligibility Decision Matrix).

5.3. If the credit profile does not meet minimum standards, evaluate the following options:
- Alternative loan program with lower credit requirements
- Credit improvement plan with re-evaluation after remediation
- Addition of a co-borrower with stronger credit
- Denial with adverse action notice per ECOA requirements

5.4. Document the credit analysis determination in the processor notes and update the loan file status accordingly.

## 4. Credit Report Validity and Reissue

| Scenario | Action |
|----------|--------|
| Report is less than 120 days old | Valid for use; no reissue needed |
| Report is 120+ days old | Must order a new report or supplemental update |
| Borrower reports significant credit change | Order supplemental update regardless of age |
| Loan program change | Evaluate whether existing report is sufficient for new program |
| Closing delayed beyond 120 days | Reissue or update required before closing |

## 5. Quality Checks

| Check | Criteria | Action if Failed |
|-------|----------|-----------------|
| Permissible purpose documented | FCRA authorization on file before order | Do not order; obtain authorization first |
| SSN match | Credit report SSN matches application SSN | Investigate discrepancy; possible identity issue |
| Score selection accuracy | Representative score correctly selected per rules | Recalculate and correct in LOS |
| Tradeline completeness | All tradelines reviewed and categorized | Complete tradeline analysis |
| Derogatory seasoning | All derogatories assessed for program compliance | Document seasoning or escalate ineligibility |
| Report currency | Report within 120-day validity window | Order supplemental or new report |

## 6. Common Pitfalls

1. **Averaging credit scores instead of selecting the middle.** The representative score is the middle of three scores, not the average. This is a frequent data entry error that can affect pricing and eligibility.

2. **Failing to use the lowest representative score for multiple borrowers.** When two borrowers apply jointly, the qualifying score for the loan is the lower of the two representative scores, not the higher.

3. **Ignoring authorized user tradelines without proper analysis.** Authorized user accounts cannot be automatically excluded. Evaluate whether the borrower has been making payments; if so, the tradeline may be beneficial to the credit profile.

4. **Ordering credit before identity verification.** Pulling credit without completing CIP/KYC verification creates compliance risk and may result in pulling credit on a fraudulent identity.

5. **Not checking for credit report disputes.** Active disputes on tradelines can affect DU/LP findings and may need to be resolved before underwriting submission.

## 7. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.3 | 2025-04-22 | L. Patel | Updated FICO score models to current versions; revised collection handling for FHA |
| 2.0 | 2024-07-01 | L. Patel | Added authorized user analysis requirements; expanded derogatory seasoning table |
| 1.0 | 2023-02-01 | Credit Operations Team | Initial release |
