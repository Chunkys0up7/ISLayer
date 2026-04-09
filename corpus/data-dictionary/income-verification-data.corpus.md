---
corpus_id: "CRP-DAT-IV-001"
title: "Income Verification Data Objects"
slug: "income-verification-data"
doc_type: "data-dictionary"
domain: "Mortgage Lending"
subdomain: "Income Verification"
tags:
  - "data-dictionary"
  - "data-objects"
  - "borrower-income"
  - "income-source"
  - "verification-result"
  - "schema"
  - "field-definitions"
applies_to:
  process_ids:
    - "Process_IncomeVerification"
    - "Process_UnderwritingReview"
    - "Process_DTICalculation"
    - "Process_LoanOrigination"
  task_types:
    - "serviceTask"
    - "businessRuleTask"
    - "userTask"
    - "scriptTask"
  task_name_patterns:
    - ".*income.*"
    - ".*verification.*"
    - ".*qualifying.*"
    - ".*dti.*"
  goal_types:
    - "data_production"
    - "decision"
  roles:
    - "loan_processor"
    - "underwriter"
    - "income_analyst"
    - "system_integrator"
    - "data_analyst"
version: "2.0"
status: "current"
effective_date: "2025-01-01"
review_date: "2026-01-01"
supersedes: null
superseded_by: null
author: "Data Architecture Team"
last_modified: "2024-12-15"
last_modified_by: "S. Nakamura"
source: "internal"
source_ref: "DDM-IV-2024-001"
related_corpus_ids:
  - "CRP-PRC-IV-001"
  - "CRP-PRC-IV-002"
  - "CRP-PRC-IV-003"
  - "CRP-RUL-IV-001"
  - "CRP-RUL-IV-002"
regulation_refs:
  - "MISMO v3.6 Income Schema"
  - "URLA Form 1003"
policy_refs:
  - "POL-DATA-001"
  - "POL-IV-004"
---

# Income Verification Data Objects

## 1. Overview

This document defines the canonical data objects used throughout the Income Verification process. These objects represent the structured data exchanged between tasks in the BPMN process, stored in the Loan Origination System (LOS), and used by business rules and decision logic.

All field names follow camelCase convention. Data types align with JSON Schema primitives. Enumerated values are listed exhaustively -- no other values are valid without a schema update.

## 2. Object: borrower_income

The top-level income record for a single borrower on a loan application. One `borrower_income` object exists per borrower (primary borrower, co-borrower, etc.).

### 2.1. Field Definitions

| Field Name | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| borrowerId | string | Yes | Unique identifier for the borrower within the loan file | UUID format; matches loan application borrower ID |
| loanId | string | Yes | Identifier for the associated loan application | System-generated |
| borrowerRole | enum | Yes | Borrower's role on the application | `primary`, `co_borrower`, `non_occupant_co_borrower`, `co_signer` |
| grossMonthlyIncome | decimal | Yes | Total gross monthly qualifying income (all sources combined) | >= 0.00; precision: 2 decimal places; currency: USD |
| netMonthlyIncome | decimal | No | Total net monthly income (informational; not used for qualification) | >= 0.00; precision: 2 decimal places |
| statedMonthlyIncome | decimal | Yes | Income amount stated on the loan application (URLA) | >= 0.00; precision: 2 decimal places |
| verifiedMonthlyIncome | decimal | No | Calculated qualifying income after verification | >= 0.00; precision: 2 decimal places; null until verification complete |
| variancePercent | decimal | No | Percentage difference between stated and verified income | Calculated: abs(stated - verified) / stated * 100; null until verification complete |
| varianceFlag | enum | No | Result of variance threshold evaluation | `pass`, `exception`, `escalation`; null until evaluation |
| incomeType | enum | Yes | Primary income classification | `w2_employee`, `self_employed`, `commissioned`, `part_time`, `seasonal`, `military`, `retired`, `gig_contract`, `mixed` |
| employmentStatus | enum | Yes | Current employment status | `active`, `on_leave`, `terminated`, `retired`, `unemployed`, `student` |
| employerName | string | Conditional | Name of the primary employer | Required if incomeType is w2_employee, commissioned, part_time, seasonal, or military |
| employerEin | string | Conditional | Employer Identification Number | Required if W-2 or VOE obtained; format: XX-XXXXXXX |
| employmentStartDate | date | Conditional | Date employment with current primary employer began | Required for employment-based income; format: YYYY-MM-DD |
| employmentEndDate | date | No | Date employment ended (if applicable) | Format: YYYY-MM-DD; null if currently employed |
| yearsInPosition | decimal | No | Number of years in current position | Calculated from employmentStartDate; precision: 1 decimal |
| yearsInLineOfWork | decimal | No | Number of years in the same line of work/industry | Per borrower declaration and verification |
| ownershipPercent | decimal | Conditional | Percentage of business ownership | Required if self-employed; 0.00-100.00; triggers SE classification if >= 25.00 |
| verificationStatus | enum | Yes | Overall income verification status | `pending`, `in_progress`, `verified`, `exception`, `failed`, `waived` |
| verificationCompletedDate | date | No | Date income verification was finalized | Format: YYYY-MM-DD; null until verification complete |
| verifiedBy | string | No | User ID of the processor or underwriter who completed verification | System user ID |
| incomeSources | array | Yes | Collection of individual income_source objects | Minimum 1 element; see income_source definition |
| notes | string | No | Free-text processor/underwriter notes about this borrower's income | Max length: 4000 characters |

### 2.2. Business Rules

- `grossMonthlyIncome` must equal the sum of all `income_source.verifiedMonthlyAmount` values where `verificationStatus` = `verified`
- `variancePercent` is calculated only when both `statedMonthlyIncome` and `verifiedMonthlyIncome` are populated
- `varianceFlag` is set by applying CRP-RUL-IV-002 rules based on the loan program
- If `ownershipPercent` >= 25.00, the `incomeType` must be `self_employed` or `mixed`
- `verificationStatus` cannot be `verified` until all required `income_source` items have `verificationStatus` = `verified`

## 3. Object: income_source

Represents a single stream of income. A borrower may have multiple income sources (e.g., base salary from primary job, overtime from primary job, rental income from an investment property).

### 3.1. Field Definitions

| Field Name | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| sourceId | string | Yes | Unique identifier for this income source | UUID format |
| borrowerId | string | Yes | Reference to the parent borrower_income record | Must match a valid borrower_income.borrowerId |
| sourceType | enum | Yes | Classification of the income source | See enumerated values below |
| sourceSubType | enum | No | Further classification within the source type | See enumerated values below |
| employerName | string | Conditional | Employer or payer name for this income source | Required for employment-derived income |
| description | string | No | Free-text description of the income source | Max length: 500 characters |
| statedAmount | decimal | Yes | Amount declared on the loan application for this source | >= 0.00; precision: 2 decimal places |
| statedFrequency | enum | Yes | Pay frequency as declared | `weekly`, `bi_weekly`, `semi_monthly`, `monthly`, `quarterly`, `annual`, `irregular` |
| rawAmount | decimal | No | Amount per pay period from source documentation (paystub, etc.) | >= 0.00; precision: 2 decimal places |
| rawFrequency | enum | No | Pay frequency from source documentation | Same enum as statedFrequency |
| calculatedMonthlyAmount | decimal | No | Monthly amount after frequency conversion | Calculated: rawAmount * frequencyMultiplier |
| averagedMonthlyAmount | decimal | No | Monthly amount after 12-month or 24-month averaging | For variable income types |
| verifiedMonthlyAmount | decimal | No | Final verified monthly amount used for qualifying | After all adjustments (trending, averaging, gross-up) |
| grossUpApplied | boolean | No | Whether non-taxable gross-up was applied | Default: false |
| grossUpFactor | decimal | No | Gross-up multiplier applied | 1.00-1.25; null if grossUpApplied = false |
| year1Amount | decimal | No | Total income for this source in the earlier of the 2 verification years | From W-2, Schedule C, or K-1 |
| year2Amount | decimal | No | Total income for this source in the more recent verification year | From W-2, Schedule C, or K-1 |
| ytdAmount | decimal | No | Year-to-date income for the current year | From paystub or P&L |
| ytdMonthsElapsed | decimal | No | Number of months elapsed in the current year for annualization | Precision: 1 decimal |
| ytdAnnualized | decimal | No | Annualized YTD figure | Calculated: ytdAmount / ytdMonthsElapsed * 12 |
| trendDirection | enum | No | Year-over-year trend | `increasing`, `stable`, `declining_minor`, `declining_moderate`, `declining_significant`, `loss` |
| trendVariancePercent | decimal | No | Year-over-year change percentage | Calculated: (year2Amount - year1Amount) / year1Amount * 100 |
| varianceFromStated | decimal | No | Variance between stated and verified for this source | Calculated: abs(statedAmount_monthly - verifiedMonthlyAmount) / statedAmount_monthly * 100 |
| verificationStatus | enum | Yes | Verification status for this specific source | `pending`, `in_progress`, `verified`, `excluded`, `failed`, `waived` |
| verificationMethod | enum | No | Method used to verify this income source | `twn`, `written_voe`, `payroll_provider`, `cpa_letter`, `tax_return`, `irs_transcript`, `bank_statement`, `lease_agreement`, `benefit_letter`, `court_order` |
| evidenceRefs | array | No | References to supporting documents in the DMS | Array of document reference IDs (strings) |
| exclusionReason | string | No | Reason if this income source was excluded from qualifying | Required if verificationStatus = `excluded`; max 500 characters |
| startDate | date | No | When the borrower began receiving this income | Format: YYYY-MM-DD |
| endDate | date | No | When this income is expected to end (if known) | Format: YYYY-MM-DD; null if ongoing |
| continuanceYears | decimal | No | Expected years of continuance from closing date | Must be >= 3.0 for qualifying income |

### 3.2. Enumerated Values for sourceType

| Value | Description |
|-------|-------------|
| `base_salary` | Fixed salary or hourly base pay |
| `overtime` | Overtime earnings |
| `bonus` | Bonus compensation |
| `commission` | Commission earnings |
| `tips` | Tip income |
| `self_employment` | Self-employment / business income |
| `rental` | Rental income from investment property |
| `social_security` | Social Security retirement or disability |
| `pension` | Employer pension or annuity |
| `va_benefits` | VA disability or pension benefits |
| `disability` | Non-VA disability income |
| `alimony` | Court-ordered alimony/spousal support |
| `child_support` | Court-ordered child support |
| `interest_dividend` | Investment interest and dividends |
| `trust` | Trust income |
| `notes_receivable` | Income from notes receivable |
| `housing_allowance` | Employer-provided housing allowance |
| `military_entitlement` | BAH, BAS, or other military entitlements |
| `foster_care` | Foster care income |
| `boarder` | Boarder/rental room income |
| `other` | Other qualifying income |

### 3.3. Enumerated Values for sourceSubType

| Value | Applies To | Description |
|-------|-----------|-------------|
| `schedule_c` | self_employment | Sole proprietorship |
| `k1_partnership` | self_employment | Partnership (Form 1065 K-1) |
| `k1_s_corp` | self_employment | S-Corporation (Form 1120S K-1) |
| `c_corp` | self_employment | C-Corporation (Form 1120) |
| `full_time` | base_salary | Full-time (30+ hours/week) |
| `part_time` | base_salary | Part-time (< 30 hours/week) |
| `seasonal` | base_salary | Seasonal employment |
| `contract` | base_salary | Contract/temporary |

## 4. Object: verification_result

The output object produced at the conclusion of the income verification process. This is the authoritative record of the income verification determination.

### 4.1. Field Definitions

| Field Name | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| resultId | string | Yes | Unique identifier for this verification result | UUID format |
| loanId | string | Yes | Associated loan application | Must match a valid loan |
| borrowerId | string | Yes | Associated borrower | Must match a valid borrower_income.borrowerId |
| qualifiedMonthlyIncome | decimal | Yes | Final total qualifying monthly income | >= 0.00; sum of all verified income sources |
| statedMonthlyIncome | decimal | Yes | Originally stated monthly income | From loan application |
| variancePercent | decimal | Yes | Overall variance between stated and qualified | Calculated per CRP-RUL-IV-002 |
| varianceFlag | enum | Yes | Variance evaluation result | `pass`, `exception`, `escalation` |
| loanProgram | enum | Yes | Loan program for threshold application | `conventional`, `fha`, `va`, `usda` |
| confidenceScore | decimal | No | System-generated confidence in the income determination | 0.00-100.00; based on documentation completeness and consistency |
| incomeSourceCount | integer | Yes | Number of verified income sources | Count of income_source objects with verificationStatus = `verified` |
| excludedSourceCount | integer | No | Number of excluded income sources | Count of income_source objects with verificationStatus = `excluded` |
| hasDeclineFlag | boolean | Yes | Whether any income source shows declining trend | True if any income_source.trendDirection starts with `declining` |
| hasBusinessLoss | boolean | Yes | Whether any self-employment source shows a net loss | True if any SE income_source has negative verifiedMonthlyAmount |
| totalBusinessLoss | decimal | No | Sum of all SE business losses (negative value) | <= 0.00; only populated if hasBusinessLoss = true |
| grossUpApplied | boolean | Yes | Whether any income source has gross-up | True if any income_source.grossUpApplied = true |
| exceptionNarrative | string | No | Explanation for any exceptions or unusual determinations | Required if varianceFlag != `pass` or hasDeclineFlag = true; max 4000 characters |
| compensatingFactors | array | No | List of compensating factors cited | Array of strings; e.g., ["strong_reserves", "low_ltv", "excellent_credit"] |
| evidenceTrail | array | Yes | Ordered list of all document references supporting this determination | Array of document reference IDs |
| processorId | string | Yes | User ID of the processor who completed the verification | System user ID |
| underwriterId | string | No | User ID of the underwriter who reviewed (if applicable) | System user ID; required if varianceFlag = `exception` or `escalation` |
| completedDate | datetime | Yes | Timestamp when the verification result was finalized | ISO 8601 format |
| status | enum | Yes | Status of the verification result | `draft`, `submitted`, `approved`, `returned`, `superseded` |

### 4.2. Business Rules

- `qualifiedMonthlyIncome` must equal the parent `borrower_income.grossMonthlyIncome` when status = `approved`
- `varianceFlag` must be derived from CRP-RUL-IV-002 using the `loanProgram` and `variancePercent`
- `evidenceTrail` must contain at minimum one reference per verified income source
- `confidenceScore` calculation factors:
  - +20 points: All income sources have IRS transcript match
  - +20 points: VOE or TWN obtained for all employment sources
  - +15 points: No declining income trends
  - +15 points: Variance <= 5%
  - +10 points: Two full years of documentation for all sources
  - +10 points: All paystubs within 30 days
  - +10 points: No exceptions or escalations
  - Score capped at 100.00

### 4.3. Compensating Factor Valid Values

| Value | Description |
|-------|-------------|
| `strong_reserves` | Borrower has 6+ months of reserves |
| `low_ltv` | Loan-to-value ratio <= 75% |
| `excellent_credit` | Credit score >= 740 |
| `low_dti` | DTI ratio <= 36% even with reduced income |
| `long_employment` | 5+ years with current employer |
| `residual_income` | VA residual income exceeds requirements by 20%+ |
| `housing_history` | 12+ months of on-time housing payments |
| `documented_explanation` | Reasonable written explanation for anomaly |
| `temporary_event` | Income decline attributable to documented one-time event |

## 5. Object Relationships

```
loan_application (1)
  └── borrower_income (1..n, one per borrower)
        ├── income_source (1..n, one per income stream)
        │     └── evidenceRefs → Document Management System
        └── verification_result (1, final determination)
              └── evidenceTrail → Document Management System
```

## 6. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.0 | 2024-12-15 | S. Nakamura | Added confidenceScore, compensating factors, expanded enumerations |
| 1.5 | 2024-05-01 | S. Nakamura | Added grossUp fields, trendDirection enum, sourceSubType |
| 1.0 | 2022-01-10 | Data Architecture Team | Initial release |
