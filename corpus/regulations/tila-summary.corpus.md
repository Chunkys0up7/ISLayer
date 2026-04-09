---
corpus_id: "CRP-REG-MTG-002"
title: "Truth in Lending Act (TILA) / Regulation Z Summary"
slug: "tila-summary"
doc_type: "regulation"
domain: "Mortgage Lending"
subdomain: "Compliance"
tags:
  - regulation
  - TILA
  - RegZ
  - disclosures
  - APR
  - compliance
  - TRID
applies_to:
  process_ids:
    - "PRC-MTG-ORIG-001"
  task_types:
    - origination
    - disclosures
    - closing
    - compliance
  task_name_patterns:
    - "*_disclosure_*"
    - "*_origination_*"
    - "*_closing_*"
    - "*_apr_*"
  goal_types:
    - compliance
    - consumer_protection
    - disclosure
  roles:
    - loan_officer
    - loan_processor
    - closer
    - compliance_officer
version: "1.0"
status: "current"
effective_date: "2026-01-01"
review_date: "2026-07-01"
supersedes: null
superseded_by: null
author: "MDA Demo"
last_modified: "2026-04-09"
last_modified_by: "MDA Demo"
source: "regulatory"
source_ref: "12 CFR Part 1026"
related_corpus_ids:
  - "CRP-REG-MTG-003"
  - "CRP-GLO-MTG-001"
regulation_refs: []
policy_refs:
  - "CRP-POL-MTG-010"
---

# Truth in Lending Act (TILA) / Regulation Z Summary

## Overview

The Truth in Lending Act (TILA), enacted in 1968 and implemented by Regulation Z (12 CFR Part 1026), requires creditors to provide consumers with clear and standardized disclosures of credit terms and costs. For mortgage lending, TILA's primary objectives are to ensure borrowers can compare the costs of different loan offers, understand the true cost of credit through the APR, and exercise their right of rescission when applicable.

TILA is enforced by the Consumer Financial Protection Bureau (CFPB). Violations can result in statutory damages, actual damages, class action liability, and regulatory enforcement actions.

## Key Requirements for Mortgage Lending

### 1. TRID Integrated Disclosures

The TILA-RESPA Integrated Disclosure (TRID) rule, effective October 2015, consolidated mortgage disclosures into two forms:

**Loan Estimate (LE)**
- Must be provided within 3 business days of receiving a loan application
- Application is defined as the receipt of six pieces of information: borrower name, income, SSN, property address, estimated property value, and loan amount sought
- Contains estimated loan terms, projected monthly payments, estimated closing costs, and comparisons
- Valid for 10 business days from issuance (for rate and fee purposes)

**Closing Disclosure (CD)**
- Must be provided at least 3 business days before consummation (closing)
- Contains final loan terms, actual closing costs, and cash to close
- Must be compared to the LE for tolerance compliance

### 2. Timing Requirements

| Event | Timing Rule |
|-------|-------------|
| LE delivery after application | Within 3 business days |
| Borrower intent to proceed | Within 10 business days of LE receipt |
| CD delivery before closing | At least 3 business days before consummation |
| Revised LE (changed circumstances) | Within 3 business days of the changed circumstance |
| Revised CD (post-closing corrections) | Within 30 calendar days of closing |

**Three-Day Waiting Period Resets**: A new 3-business-day waiting period is required if the CD is revised and any of the following changes occur:
- The APR increases by more than 1/8% for fixed-rate loans or 1/4% for adjustable-rate loans
- The loan product changes (e.g., fixed to ARM)
- A prepayment penalty is added

### 3. Fee Tolerance Limits

TRID establishes three tolerance categories that limit how much actual fees can exceed estimated fees from the LE:

| Tolerance Category | Variance Allowed | Fee Types |
|--------------------|-----------------|-----------|
| **Zero Tolerance** | 0% increase allowed | Fees paid to the creditor, mortgage broker fees, transfer taxes, fees for required services where the creditor selected the provider |
| **10% Cumulative Tolerance** | Aggregate increase of up to 10% | Recording fees, fees for required services where the borrower selects from the creditor's written list |
| **Unlimited Tolerance** | No limit on increase | Fees for services the borrower shops for and selects the provider, prepaid interest, property insurance premiums |

If zero-tolerance or 10%-tolerance fees exceed limits, the creditor must refund the excess to the borrower within 60 calendar days of consummation.

### 4. APR Calculation

The Annual Percentage Rate represents the total cost of credit to the borrower, expressed as an annualized rate. The APR calculation must include:

**Included in APR**:
- Interest charges
- Mortgage insurance premiums (PMI/MIP)
- Discount points and origination fees
- Prepaid finance charges
- Mortgage broker fees paid by the consumer

**Excluded from APR**:
- Appraisal fees (if reasonable)
- Credit report fees
- Title examination and insurance fees
- Property survey fees
- Recording fees
- Transfer taxes
- Notary fees

### 5. Right of Rescission

Applies to refinance transactions and home equity loans secured by the borrower's principal dwelling (does not apply to purchase money mortgages).

- Borrower has 3 business days after closing to rescind the transaction
- The rescission period begins on the latest of: (a) consummation, (b) delivery of the notice of right to rescind, or (c) delivery of material TILA disclosures
- If proper notice is not given, the right extends up to 3 years from consummation
- Upon rescission, the creditor must return all fees and the security interest is voided within 20 calendar days

### 6. Higher-Priced Mortgage Loans (HPML)

A mortgage loan is classified as higher-priced if the APR exceeds the Average Prime Offer Rate (APOR) by:
- 1.5 percentage points for first-lien conforming loans
- 2.5 percentage points for first-lien jumbo loans
- 3.5 percentage points for subordinate-lien loans

HPMLs trigger additional requirements:
- Interior appraisal required (no drive-by or desktop)
- Second appraisal required for "flipped" properties (seller owned less than 180 days with significant price increase)
- Mandatory escrow account for property taxes and insurance (minimum 5 years)

### 7. Ability to Repay (ATR) / Qualified Mortgage (QM)

Under TILA Section 129C, creditors must make a reasonable, good-faith determination that a consumer has the ability to repay a mortgage loan. The ATR rule requires consideration of at least eight underwriting factors:

1. Current or reasonably expected income or assets
2. Current employment status
3. Monthly mortgage payment (using fully indexed rate for ARMs)
4. Monthly payments on simultaneous loans secured by the same property
5. Monthly payments for mortgage-related obligations (taxes, insurance, HOA)
6. Current debt obligations, alimony, and child support
7. Monthly DTI ratio or residual income
8. Credit history

**Qualified Mortgage (QM) Safe Harbor**: Loans meeting QM criteria receive a legal safe harbor or rebuttable presumption of ATR compliance:
- No negative amortization, interest-only, or balloon features
- Loan term does not exceed 30 years
- Points and fees do not exceed 3% of the loan amount (for loans over $100,000)
- DTI ratio does not exceed 43% (or loan eligible for GSE purchase under the GSE patch)
- Income and debt verified using specified documentation

## Compliance Monitoring

### Key Controls

| Control | Frequency | Responsible Party |
|---------|-----------|------------------|
| LE timing audit (application to LE delivery) | Monthly random sample | Compliance |
| CD timing audit (CD delivery to closing) | Monthly random sample | Compliance |
| Fee tolerance comparison (LE vs. CD) | Every loan at closing | Processing/Closing |
| APR accuracy verification | Quarterly random sample | Compliance |
| HPML identification and escrow setup | Every loan at underwriting | Underwriting |
| ATR/QM documentation review | Quarterly random sample | Compliance |
| Rescission notice delivery verification | Every refinance at closing | Closing |

### Common Violations

1. **Late LE delivery**: LE not provided within 3 business days of application
2. **Fee tolerance breach**: Zero-tolerance fees exceeded without valid changed circumstance
3. **CD timing violation**: CD delivered fewer than 3 business days before closing
4. **Inaccurate APR**: APR calculation error exceeding tolerance (1/8% fixed, 1/4% ARM)
5. **Missing rescission notice**: Failure to provide right of rescission notice on refinance transactions
6. **Changed circumstance abuse**: Issuing revised LE without a valid changed circumstance
