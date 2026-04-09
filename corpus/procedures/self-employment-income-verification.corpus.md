---
corpus_id: "CRP-PRC-IV-002"
title: "Self-Employment Income Verification Procedure"
slug: "self-employment-income-verification"
doc_type: "procedure"
domain: "Mortgage Lending"
subdomain: "Income Verification"
tags:
  - "self-employment"
  - "schedule-c"
  - "schedule-k1"
  - "1120s"
  - "form-1084"
  - "cash-flow-analysis"
  - "sole-proprietor"
  - "partnership"
  - "s-corp"
  - "tax-returns"
applies_to:
  process_ids:
    - "Process_IncomeVerification"
    - "Process_UnderwritingReview"
  task_types:
    - "userTask"
    - "businessRuleTask"
  task_name_patterns:
    - "verify.*self-?employ"
    - "verify.*se.*income"
    - "review.*business.*income"
    - "calculate.*self-?employ"
    - "analyze.*schedule.*[ck]"
    - "complete.*1084"
  goal_types:
    - "data_production"
    - "decision"
  roles:
    - "loan_processor"
    - "underwriter"
    - "income_analyst"
version: "3.0"
status: "current"
effective_date: "2025-01-15"
review_date: "2026-01-15"
supersedes: null
superseded_by: null
author: "Operations Standards Committee"
last_modified: "2025-01-10"
last_modified_by: "A. Kapoor"
source: "internal"
source_ref: "SOP-IV-2025-002"
related_corpus_ids:
  - "CRP-RUL-IV-001"
  - "CRP-RUL-IV-002"
  - "CRP-PRC-IV-003"
  - "CRP-REG-IV-001"
  - "CRP-REG-IV-002"
  - "CRP-DAT-IV-001"
  - "CRP-SYS-IV-002"
regulation_refs:
  - "Fannie Mae Selling Guide B3-3.1-10"
  - "Fannie Mae Form 1084"
  - "Fannie Mae Form 1088"
  - "FHA 4000.1 II.A.4.c.3"
  - "VA Pamphlet 26-7 Ch. 4 Sec. 6"
policy_refs:
  - "POL-IV-004"
  - "POL-IV-007"
  - "POL-DOC-001"
---

# Self-Employment Income Verification Procedure

## 1. Scope

This procedure governs the verification and calculation of income for borrowers who are self-employed, defined as individuals who have 25% or greater ownership interest in a business. It covers sole proprietorships (Schedule C), partnerships (Schedule E / Form 1065 / K-1), S-corporations (Form 1120S / K-1), and C-corporations (Form 1120) where the borrower is both an owner and employee.

This procedure applies to all loan programs (conventional, FHA, VA, USDA). Agency-specific variations are called out where applicable.

## 2. Prerequisites

| # | Prerequisite | Source |
|---|---|---|
| 1 | Signed URLA (Form 1003) with self-employment disclosed | Borrower |
| 2 | Complete personal federal tax returns (Form 1040 with all schedules) for the most recent 2 years | Borrower or IVES |
| 3 | Complete business tax returns for the most recent 2 years (Form 1065, 1120S, or 1120 as applicable) | Borrower |
| 4 | IRS Form 4506-C signed by borrower | Borrower |
| 5 | Year-to-date Profit & Loss statement (if more than 3 months into the current fiscal year) | Borrower / CPA |
| 6 | Business license or registration (if available) | Borrower |
| 7 | Most recent 2-3 months of business bank statements (if required by overlay or DU) | Borrower |

**Note:** A two-year history of self-employment is required for all agency programs. Borrowers with 12-24 months of self-employment history may qualify only if they have prior experience in the same line of work (Fannie Mae) or meet specific FHA exceptions.

## 3. Procedure Steps

### Step 1: Confirm Self-Employment Status

1.1. Review the loan application to determine if the borrower has indicated self-employment or business ownership.

1.2. Apply the Employment Type Classification Rules (CRP-RUL-IV-001):
- Ownership of 25% or more in any business entity = self-employed
- If the borrower receives a W-2 from a company they own 25%+ of, they are still classified as self-employed and the business returns must be analyzed

1.3. Determine the business entity type:

| Entity Type | Personal Returns Needed | Business Returns Needed | IRS Forms |
|-------------|------------------------|------------------------|-----------|
| Sole Proprietorship | 1040 + Schedule C | None (included in personal) | Schedule C, Schedule SE |
| Partnership | 1040 + Schedule E + K-1 | Form 1065 | K-1 (Form 1065) |
| S-Corporation | 1040 + Schedule E + K-1 + W-2 | Form 1120S | K-1 (Form 1120S), W-2 |
| C-Corporation | 1040 + W-2 | Form 1120 | W-2, Form 1120 |

1.4. For borrowers with multiple businesses, each business must be analyzed separately.

### Step 2: Obtain and Validate Tax Returns

2.1. Obtain complete federal tax returns for the two most recent tax years. "Complete" means:
- All pages including all schedules, attachments, and K-1s
- Signed and dated (or e-filed confirmation)
- Consistent with IRS transcripts (order via IVES per CRP-SYS-IV-002)

2.2. Compare key figures between the tax return and the IRS transcript:
- 1040 Line 1 (Wages) must match within $100
- 1040 Line 8 (Schedule 1 total) must match within $100
- Schedule C Line 31 (Net Profit) must match within $100
- Adjusted Gross Income (AGI) must match within $200

2.3. If transcripts are not yet available for the most recent tax year (e.g., returns just filed), obtain a signed copy of the return with a CPA-prepared cover letter or IRS e-file acceptance confirmation (Form 8879). Flag the file for transcript follow-up.

2.4. Verify that the business tax return EIN matches the K-1 EIN and the business entity name matches across all documents.

### Step 3: Complete the Cash Flow Analysis (Form 1084)

3.1. Use the Fannie Mae Form 1084 (Cash Flow Analysis) as the standard calculation worksheet for all loan programs. For FHA loans, the FHA self-employment worksheet may be used as a supplement.

3.2. **Sole Proprietorship (Schedule C):**

| Line | Source | Description |
|------|--------|-------------|
| Net Profit/Loss | Schedule C, Line 31 | Starting point for income |
| + Depreciation | Schedule C, Line 13 | Non-cash expense, add back |
| + Depletion | Schedule C, Line 12 | Non-cash expense, add back |
| + Amortization | From attached statements | Identify in Other Expenses |
| + Business Use of Home | Schedule C, Line 30 | Add back (not a true cash expense to the business) |
| - Non-recurring income | As identified | Exclude one-time gains |
| + Non-recurring losses | As identified | Add back one-time losses |
| = Adjusted Business Income | Calculated | Annual business cash flow |

3.3. **Partnership / S-Corporation (K-1 + Business Return):**

For K-1 income, begin with the borrower's share of ordinary income:

| Line | Source | Description |
|------|--------|-------------|
| Ordinary Income | K-1 Line 1 (1065) or K-1 Line 1 (1120S) | Borrower's distributive share |
| + Net Rental Income | K-1 Line 2 | If applicable |
| + Guaranteed Payments | K-1 Line 4 (1065 only) | Payments to partner for services |
| + Depreciation | Form 1065/1120S, Schedule M-1 or K-1 supplemental | Borrower's share |
| + Depletion | K-1 Line 15c or Line 17c | Borrower's share |
| + Amortization | Form 1065/1120S, attached statement | Borrower's share |
| - Distributions exceeding income | Compare K-1 income to actual distributions | If distributions consistently exceed income, assess sustainability |

For S-Corps, also add the W-2 wages paid to the borrower by the S-Corp. Do not double-count: the W-2 wages are separate from the K-1 ordinary income.

3.4. **C-Corporation (Form 1120):**

C-Corporation income is only used when the borrower owns 100% of the corporation. For borrowers owning less than 100%, only the W-2 wages from the corporation are used.

For 100% owners:
- Start with the W-2 wages from the corporation
- Analyze the business return for viability (Step 5) but do not add corporate retained earnings to personal qualifying income unless the borrower can demonstrate access through consistent distributions
- If distributions are made, document with corporate minutes and bank statements

### Step 4: Calculate the Qualifying Income

4.1. Calculate the monthly income using the method that produces the most conservative result:

**24-Month Average:**
```
Monthly Income = (Year 1 Adjusted Business Income + Year 2 Adjusted Business Income) / 24
```

**12-Month Average (most recent year only):**
```
Monthly Income = Year 2 Adjusted Business Income / 12
```

4.2. Income selection rules:
- If Year 2 income >= Year 1 income (stable or increasing): use the **24-month average**
- If Year 2 income < Year 1 income but decline is <=15%: use the **24-month average** with explanation
- If Year 2 income < Year 1 income with decline >15% but <=25%: use the **12-month average** (lower figure)
- If Year 2 income < Year 1 income with decline >25%: **escalate to senior underwriter**; income may not be usable

4.3. For borrowers with multiple businesses, calculate each business separately, then sum the positive results. If any business shows a loss, the loss must be deducted from total qualifying income.

4.4. **Agency-Specific Rules:**
- **Fannie Mae:** If DU issues an "Approve/Eligible" with one year of tax returns, the 12-month figure may be used alone if the borrower has a 5+ year history of self-employment in the same field.
- **FHA:** Always requires two full years of tax returns; no exceptions for seasoned self-employment.
- **VA:** Follows general two-year requirement but allows for flexibility with a clear upward trend and strong compensating factors.

### Step 5: Assess Business Viability

5.1. Business viability analysis is required to determine the likelihood that the self-employment income will continue. Evaluate:

| Factor | Favorable Indicator | Unfavorable Indicator |
|--------|--------------------|-----------------------|
| Revenue trend | Stable or growing revenue over 2 years | Declining revenue year-over-year |
| Profit margin | Consistent positive margins | Narrowing margins or losses |
| Industry outlook | Growing or stable industry | Contracting industry, regulatory risk |
| Business age | 5+ years of operation | Less than 2 years |
| Liquidity | 3+ months of business expenses in cash reserves | Minimal cash reserves |
| Debt levels | Manageable business debt | High leverage, maxed credit lines |

5.2. If the business shows a net loss in the most recent year:
- The loss must be deducted from the borrower's total qualifying income
- If the loss eliminates all qualifying income, the loan cannot proceed without alternative income sources
- Exception: a one-time documented event (e.g., lawsuit settlement, natural disaster) may allow the prior year income to be used with compensating factors

5.3. Review the YTD Profit & Loss statement (if applicable):
- Must be prepared by the borrower or their CPA
- If more than 3 months have elapsed since the end of the most recent tax year, a YTD P&L is required
- The P&L should confirm that the business is still operating and revenue is consistent with historical patterns
- If YTD revenue is down more than 20% compared to the same period in the prior year, additional analysis and explanation are required

### Step 6: Verify Business Existence

6.1. Confirm the business exists and is operational through at least two of the following:

- Business license or registration with state/county
- Third-party verification (e.g., Dun & Bradstreet, Secretary of State website)
- CPA letter confirming the business is active and the borrower is the owner
- Business website, professional directory listing, or industry association membership
- Recent business bank statements showing ongoing transactions

6.2. A phone call to the business is acceptable as supplemental verification but not as standalone proof.

6.3. For newly established businesses (less than 2 years), additional documentation may include:
- Business plan
- Contracts or invoices demonstrating revenue
- Evidence of prior experience in the same field

### Step 7: Document and Finalize

7.1. Complete Form 1084 in its entirety. Every line must be filled in; use zero where a deduction does not apply. Do not leave lines blank.

7.2. Prepare a written income analysis narrative that includes:
- Business entity type and borrower's ownership percentage
- Summary of 2-year income trend (dollars and percentages)
- Business viability assessment conclusion
- Any compensating factors relied upon
- Final qualifying monthly income determination

7.3. Upload all documents to the DMS:
- Personal tax returns (both years)
- Business tax returns (both years)
- K-1s
- Form 1084 (completed)
- Business verification evidence
- YTD P&L (if applicable)
- Income analysis narrative

## 4. Quality Checks

| Check | Criteria | Action if Failed |
|-------|----------|-----------------|
| Tax return completeness | All schedules, K-1s, and attachments present | Request missing pages |
| Transcript match | Key figures match IRS transcripts within tolerances | Investigate discrepancy; possible amended return |
| EIN consistency | Business EIN matches across K-1, business return, and VOE | Verify correct entity |
| Ownership verification | 25%+ ownership confirmed on K-1 and application | Reclassify if needed |
| Form 1084 math | All calculations independently verified | Recalculate |
| Trend analysis | Year-over-year changes documented with explanations | Add narrative |
| Business viability | Viability assessment completed and documented | Complete assessment |

## 5. Common Pitfalls

1. **Ignoring depreciation add-backs.** Depreciation is the most commonly missed add-back. It appears on Schedule C Line 13, Form 1065 and 1120S in the depreciation section, and sometimes in "Other Deductions" as amortization. Always check attached depreciation schedules.

2. **Using gross receipts instead of net profit.** Schedule C Line 7 (gross income) is not the starting point. Always begin with Line 31 (net profit or loss).

3. **Forgetting to deduct business losses.** If a borrower has two businesses and one shows a loss, the loss must reduce total qualifying income. You cannot ignore the losing business.

4. **Misidentifying the ownership percentage.** The K-1 shows the ownership percentage. If the borrower claims 20% ownership but the K-1 shows 30%, use the K-1 figure. Investigate any discrepancy.

5. **Not requesting business returns for S-Corps.** Even though S-Corp income passes through to the personal return via K-1, the full Form 1120S is needed to assess depreciation, officer compensation, and business viability.

6. **Double-counting W-2 and K-1 income for S-Corp owners.** The W-2 wages paid by the S-Corp to the borrower and the K-1 ordinary income are separate line items. Both should be included, but verify they are not double-counted by checking that the W-2 wages appear as officer compensation on the 1120S.

7. **Overlooking distributions vs. income mismatch.** If a partner's distributions significantly exceed their K-1 income year after year, this may indicate the business is distributing capital, not earnings. This can signal declining business health.

## 6. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 3.0 | 2025-01-10 | A. Kapoor | Added C-Corp handling, expanded viability section, updated Form 1084 references |
| 2.2 | 2024-04-01 | A. Kapoor | Added YTD P&L requirements, clarified transcript matching tolerances |
| 2.0 | 2023-06-15 | M. Torres | Major revision for Fannie Mae 2023 Selling Guide updates |
| 1.0 | 2022-01-10 | Operations Standards Committee | Initial release |
