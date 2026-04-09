---
corpus_id: "CRP-RUL-MTG-002"
title: "Document Completeness Checklist"
slug: "document-completeness-checklist"
doc_type: "rule"
domain: "Mortgage Lending"
subdomain: "Loan Origination"
tags:
  - "document-checklist"
  - "completeness"
  - "required-documents"
  - "loan-program"
  - "income-docs"
  - "asset-docs"
  - "property-docs"
applies_to:
  process_ids:
    - "Process_LoanOrigination"
  task_types:
    - "businessRuleTask"
    - "userTask"
  task_name_patterns:
    - "doc.*received"
    - "completeness"
    - "check.*document"
    - "verify.*complete"
    - "missing.*doc"
  goal_types:
    - "decision"
    - "data_production"
  roles:
    - "loan_processor"
    - "document_specialist"
    - "quality_control_analyst"
version: "3.1"
status: "current"
effective_date: "2025-04-01"
review_date: "2026-04-01"
supersedes: null
superseded_by: null
author: "Processing Operations"
last_modified: "2025-03-20"
last_modified_by: "K. Washington"
source: "internal"
source_ref: "RULE-DOC-2025-001"
related_corpus_ids:
  - "CRP-PRC-MTG-005"
  - "CRP-PRC-MTG-006"
  - "CRP-RUL-MTG-001"
policy_refs:
  - "POL-DOC-001"
---

# Document Completeness Checklist

## 1. Purpose

This checklist defines the required documentation for residential mortgage loan files by loan program and transaction type. It is used by processors to identify missing documents, by QC analysts to verify file completeness, and by the document request procedure (CRP-PRC-MTG-005) to generate borrower requests.

Documents marked as "Required" must be present in every file of that program type. Documents marked as "Conditional" are required only when specific circumstances apply. Documents marked as "If Applicable" should be included when the situation is present but may not apply to every file.

## 2. Application and Disclosure Documents

| Document | Conv | FHA | VA | USDA | Notes |
|----------|------|-----|-----|------|-------|
| URLA (Form 1003) - signed and dated | Required | Required | Required | Required | All borrowers must sign |
| Loan Estimate (initial) | Required | Required | Required | Required | Must be delivered within 3 business days |
| Loan Estimate (revised, if applicable) | If Applicable | If Applicable | If Applicable | If Applicable | When changed circumstance triggers revision |
| Intent to Proceed | Required | Required | Required | Required | Must be received before fees charged |
| Borrower Authorization (credit pull) | Required | Required | Required | Required | Signed by all borrowers |
| IRS Form 4506-C (transcript request) | Required | Required | Required | Required | Signed by all borrowers |
| State-specific disclosures | Required | Required | Required | Required | Varies by property state |
| ECOA / Appraisal notice | Required | Required | Required | Required | |
| Servicing Disclosure | Required | Required | Required | Required | |
| Anti-Steering Disclosure | Required | Required | Required | Required | |
| Affiliated Business Arrangement disclosure | If Applicable | If Applicable | If Applicable | If Applicable | When affiliated services used |
| HMDA data collection form | Required | Required | Required | Required | |

## 3. Identity and Compliance Documents

| Document | Conv | FHA | VA | USDA | Notes |
|----------|------|-----|-----|------|-------|
| Government-issued photo ID (unexpired) | Required | Required | Required | Required | All borrowers; CIP requirement |
| SSN verification result | Required | Required | Required | Required | SSA match documented |
| OFAC screening result | Required | Required | Required | Required | Must be current at submission and closing |
| Certificate of Eligibility (COE) | N/A | N/A | Required | N/A | VA entitlement verification |
| DD-214 (or equivalent) | N/A | N/A | If Applicable | N/A | For veterans not on active duty |
| USDA income eligibility determination | N/A | N/A | N/A | Required | Household income within area limits |

## 4. Income Documents

### 4.1 W-2 Employment Income

| Document | Conv | FHA | VA | USDA | Notes |
|----------|------|-----|-----|------|-------|
| Pay stubs (most recent 30 days) | Required | Required | Required | Required | Consecutive, covering all employers |
| W-2 forms (most recent 2 years) | Required | Required | Required | Required | From all employers |
| Federal tax returns (1040, 2 years) | Conditional | Required | Required | Required | Conv: may be waived by DU |
| IRS W-2 transcripts | Conditional | Required | Required | Required | Conv: per DU findings |
| IRS 1040 transcripts | Conditional | Required | Required | Required | Conv: per DU findings |
| Written VOE (Form 1005) or TWN | Required | Required | Required | Required | One method required |
| Verbal VOE | Required | Required | Required | Required | Within 10 business days of closing |
| Income Calculation Worksheet | Required | Required | Required | Required | Processor-completed |

### 4.2 Self-Employment Income

| Document | Conv | FHA | VA | USDA | Notes |
|----------|------|-----|-----|------|-------|
| Personal tax returns (2 years) with all schedules | Required | Required | Required | Required | |
| Business tax returns (2 years) with all schedules | Required | Required | Required | Required | All business entities |
| Year-to-date profit and loss statement | Conditional | Required | Required | Required | Conv: per DU; signed by borrower or CPA |
| Business license or registration | If Applicable | If Applicable | If Applicable | If Applicable | Verification of business existence |
| CPA or tax preparer letter | If Applicable | If Applicable | If Applicable | If Applicable | When VOE not feasible |
| IRS 1040 transcripts (2 years) | Required | Required | Required | Required | |
| IRS business return transcripts | Required | Required | Required | Required | 1120S, 1065, or 1120 as applicable |

### 4.3 Other Income Sources

| Document | Conv | FHA | VA | USDA | Notes |
|----------|------|-----|-----|------|-------|
| Social Security award letter | If Applicable | If Applicable | If Applicable | If Applicable | When using SS income |
| Pension/retirement award letter | If Applicable | If Applicable | If Applicable | If Applicable | When using pension income |
| Disability income documentation | If Applicable | If Applicable | If Applicable | If Applicable | Must document continuance (3+ years) |
| Child support / alimony court order | If Applicable | If Applicable | If Applicable | If Applicable | Plus 12 months receipt documentation |
| Rental income documentation (lease, tax returns) | If Applicable | If Applicable | If Applicable | If Applicable | For investment property income |
| Interest / dividend income (statements) | If Applicable | If Applicable | If Applicable | If Applicable | Must show 2-year history |

## 5. Asset Documents

| Document | Conv | FHA | VA | USDA | Notes |
|----------|------|-----|-----|------|-------|
| Bank statements (2 most recent months, all pages) | Required | Required | Required | Required | All accounts being used for qualification |
| Retirement account statements | If Applicable | If Applicable | If Applicable | If Applicable | When used for reserves or down payment |
| Gift letter (signed by donor and borrower) | If Applicable | If Applicable | If Applicable | If Applicable | When gift funds used |
| Gift donor bank statements (showing withdrawal) | If Applicable | If Applicable | If Applicable | If Applicable | Conv: required; FHA: required for > $1,000 |
| Gift transfer documentation | If Applicable | If Applicable | If Applicable | If Applicable | Evidence of transfer to borrower |
| Earnest money deposit receipt | Required (purchase) | Required (purchase) | Required (purchase) | Required (purchase) | Must show on bank statement |
| Large deposit explanation and documentation | Conditional | Conditional | Conditional | Conditional | Deposits > 50% of monthly income (Conv) or > 1% of purchase price (FHA) |
| Sale of asset documentation | If Applicable | If Applicable | If Applicable | If Applicable | When down payment from asset sale |
| Stock/bond account statements | If Applicable | If Applicable | If Applicable | If Applicable | When using liquidated securities |

## 6. Property Documents

| Document | Conv | FHA | VA | USDA | Notes |
|----------|------|-----|-----|------|-------|
| Purchase contract (fully executed) | Required (purchase) | Required (purchase) | Required (purchase) | Required (purchase) | With all addenda and amendments |
| Appraisal report | Required | Required | Required | Required | Unless waiver obtained (Conv only) |
| Title commitment / preliminary report | Required | Required | Required | Required | |
| Survey | Conditional | Conditional | Conditional | Conditional | Per state or lender requirements |
| Flood certification | Required | Required | Required | Required | |
| Flood insurance (if in flood zone) | If Applicable | If Applicable | If Applicable | If Applicable | Required if in SFHA Zone A or V |
| Homeowner's insurance binder | Required | Required | Required | Required | Coverage >= loan amount or replacement cost |
| HOA documentation (dues, budget, questionnaire) | If Applicable | If Applicable | If Applicable | If Applicable | For condo and PUD properties |
| Condo project approval / certification | If Applicable | If Applicable (FHA project approval) | If Applicable (VA project approval) | If Applicable | Program-specific project requirements |
| Termite / pest inspection | Conditional | Required (some states) | Required | Conditional | VA always requires; others per state |
| Well / septic inspection | Conditional | Required (if applicable) | If Applicable | Required (if applicable) | When property has private water/sewer |
| Property tax bill or estimate | Required | Required | Required | Required | For PITIA calculation |
| Payoff statement (refinance) | Required (refi) | Required (refi) | Required (refi) | Required (refi) | Current mortgage payoff |

## 7. Transaction-Specific Documents

| Document | When Required | Programs |
|----------|--------------|----------|
| Divorce decree / separation agreement | When borrower is divorced and income/liability affected | All |
| Bankruptcy discharge papers | When borrower has bankruptcy history | All |
| Letter of explanation (LOE) | For credit events, employment gaps, large deposits, address discrepancies | All |
| Power of Attorney | When borrower cannot sign in person | All (must be program-compliant POA) |
| Trust documents (trust agreement, certification) | When property held in trust or borrower is trustee | All |
| Non-occupant co-borrower documentation | When co-borrower will not occupy | Conv, FHA |
| Down payment assistance program documents | When using DPA program | FHA, Conv (per program) |
| Construction documents (plans, specs, permits) | For construction-to-permanent loans | All |

## 8. AUS-Specific Waivers

The following documents may be waived based on AUS findings. Always verify the specific DU/LP message before omitting:

| Potential Waiver | AUS | Condition |
|-----------------|-----|-----------|
| Tax returns | DU | DU Approve/Eligible with specific message waiving tax returns |
| Tax transcripts | DU | When tax returns are waived |
| Appraisal | DU | DU Property Inspection Waiver (PIW) offered |
| Employment verification | DU | Specific DU message; rare |
| Asset documentation | DU | DU may reduce to 1 month of statements |

**Important:** AUS waivers do not override investor overlays. Always confirm the specific investor accepts the AUS waiver before relying on it.

## 9. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 3.1 | 2025-03-20 | K. Washington | Updated large deposit thresholds; added USDA income eligibility |
| 3.0 | 2024-10-01 | K. Washington | Major revision; reorganized by document category; added AUS waiver section |
| 2.0 | 2024-01-15 | Processing Operations | Added VA and USDA programs |
| 1.0 | 2023-04-01 | Processing Operations | Initial release |
