---
corpus_id: "CRP-DAT-MTG-001"
title: "Loan Application Data Object"
slug: "loan-application-data"
doc_type: "data-dictionary"
domain: "Mortgage Lending"
subdomain: "Loan Origination"
tags:
  - "data-object"
  - "loan-application"
  - "los"
  - "urla"
  - "schema"
  - "loan-data"
applies_to:
  process_ids:
    - "Process_LoanOrigination"
  task_types:
    - "userTask"
    - "serviceTask"
    - "businessRuleTask"
  task_name_patterns:
    - ".*loan.*"
    - ".*application.*"
  goal_types:
    - "data_production"
    - "decision"
    - "state_transition"
  roles:
    - "loan_officer"
    - "loan_processor"
    - "underwriter"
    - "closer"
version: "3.0"
status: "current"
effective_date: "2025-04-01"
review_date: "2026-04-01"
supersedes: null
superseded_by: null
author: "Data Architecture Team"
last_modified: "2025-03-15"
last_modified_by: "J. Kowalski"
source: "internal"
source_ref: "DICT-LOAN-2025-001"
related_corpus_ids:
  - "CRP-PRC-MTG-001"
  - "CRP-PRC-MTG-004"
  - "CRP-RUL-MTG-001"
  - "CRP-DAT-MTG-002"
regulation_refs:
  - "MISMO v3.6 Data Standards"
  - "HMDA Regulation C"
policy_refs:
  - "POL-DATA-001"
---

# Loan Application Data Object

## 1. Overview

The Loan Application data object represents a residential mortgage loan application throughout its lifecycle in the Loan Origination System (LOS). This data object is created at application intake and persists through closing, post-closing, and servicing transfer. It serves as the master record linking all borrower, property, loan term, and status information.

The data model aligns with MISMO (Mortgage Industry Standards Maintenance Organization) v3.6 data standards where applicable.

## 2. Primary Fields

### 2.1 Loan Identification

| Field Name | Data Type | Format / Constraints | Required | Description |
|-----------|-----------|---------------------|----------|-------------|
| loan_number | String | `[A-Z]{3}-[0-9]{4}-[0-9]{6}` (e.g., ATL-2025-004521) | Yes | Unique loan identifier assigned by the LOS. Auto-generated at file creation. Immutable after assignment. |
| loan_id | UUID | Standard UUID v4 | Yes | System-generated unique identifier for internal use. Primary key in the LOS database. |
| external_loan_id | String | Alphanumeric, max 30 chars | No | Identifier assigned by correspondent lender or broker, if applicable. |
| case_number | String | FHA: `[0-9]{3}-[0-9]{7}`, VA: `[0-9]{2}-[0-9]{2}-[0-9]{1}-[0-9]{6}` | Conditional | FHA case number or VA LIN. Required for government loans. Assigned by agency systems. |

### 2.2 Loan Terms

| Field Name | Data Type | Format / Constraints | Required | Description |
|-----------|-----------|---------------------|----------|-------------|
| loan_amount | Decimal | Positive, max 2 decimal places, max $10,000,000 | Yes | Total loan amount in USD. For purchase: purchase price minus down payment. For refinance: payoff amount plus any cash-out. |
| loan_program | Enum | `CONV_FIXED`, `CONV_ARM`, `FHA_FIXED`, `FHA_ARM`, `VA_FIXED`, `VA_ARM`, `USDA_FIXED`, `JUMBO_FIXED`, `JUMBO_ARM`, `NON_QM` | Yes | Loan program type. Determines eligibility rules, required documentation, and pricing. |
| interest_rate | Decimal | 0.000 - 15.000, 3 decimal places | Conditional | Note rate. Required once rate is locked. Null if rate is floating. |
| rate_lock_status | Enum | `FLOATING`, `LOCKED`, `LOCK_EXPIRED`, `EXTENDED`, `RELOCKED` | Yes | Current status of the rate lock. Default: FLOATING. |
| rate_lock_date | Date | ISO 8601 | Conditional | Date the rate was locked. Required when rate_lock_status is LOCKED. |
| rate_lock_expiration | Date | ISO 8601 | Conditional | Date the rate lock expires. Required when rate_lock_status is LOCKED. |
| loan_term | Integer | 60, 120, 180, 240, 300, 360 (months) | Yes | Loan term in months. Common values: 180 (15-year), 360 (30-year). |
| amortization_type | Enum | `FIXED`, `ARM_5_1`, `ARM_7_1`, `ARM_10_1`, `IO_FIXED`, `IO_ARM` | Yes | Amortization type. Determines payment calculation and qualifying rate. |
| loan_purpose | Enum | `PURCHASE`, `RATE_TERM_REFI`, `CASH_OUT_REFI`, `CONSTRUCTION`, `RENOVATION` | Yes | Purpose of the loan transaction. |
| occupancy_type | Enum | `PRIMARY_RESIDENCE`, `SECOND_HOME`, `INVESTMENT` | Yes | Intended occupancy of the property. Affects eligibility, LTV limits, and pricing. |
| lien_position | Enum | `FIRST`, `SECOND`, `HELOC` | Yes | Lien position. Default: FIRST for purchase and refinance transactions. |

### 2.3 Property Information

| Field Name | Data Type | Format / Constraints | Required | Description |
|-----------|-----------|---------------------|----------|-------------|
| property_address | Object | See Address sub-object | Yes | Full address of the subject property. |
| property_address.street | String | Max 100 chars | Yes | Street address including unit number. |
| property_address.city | String | Max 50 chars | Yes | City name. |
| property_address.state | String | 2-character state code | Yes | US state abbreviation. |
| property_address.zip_code | String | `[0-9]{5}` or `[0-9]{5}-[0-9]{4}` | Yes | ZIP code (5 or 9 digit). |
| property_address.county | String | Max 50 chars | Yes | County name. Used for conforming loan limit determination and USDA eligibility. |
| property_type | Enum | `SFR`, `CONDO`, `PUD`, `MULTI_2`, `MULTI_3`, `MULTI_4`, `MANUFACTURED`, `COOP`, `TOWNHOUSE` | Yes | Property type classification. Affects program eligibility and LTV limits. |
| number_of_units | Integer | 1-4 | Yes | Number of dwelling units. Derived from property_type for multi-unit properties. |
| estimated_value | Decimal | Positive, 2 decimal places | Yes | Estimated property value at application. Updated with appraised value when available. |
| appraised_value | Decimal | Positive, 2 decimal places | Conditional | Appraised value from the appraisal report. Required before closing (unless appraisal waiver). |
| purchase_price | Decimal | Positive, 2 decimal places | Conditional | Contract purchase price. Required for purchase transactions. |
| year_built | Integer | 1800-current year | No | Year the property was constructed. |
| legal_description | String | Max 500 chars | No | Legal description from title commitment. |

### 2.4 Borrower References

| Field Name | Data Type | Format / Constraints | Required | Description |
|-----------|-----------|---------------------|----------|-------------|
| borrower_ids | Array[UUID] | 1-4 UUIDs | Yes | References to Borrower data objects associated with this loan. Minimum one borrower. |
| primary_borrower_id | UUID | Must be in borrower_ids array | Yes | Reference to the primary borrower. |
| co_borrower_ids | Array[UUID] | 0-3 UUIDs | No | References to co-borrowers, if any. |

### 2.5 Financial Calculations

| Field Name | Data Type | Format / Constraints | Required | Description |
|-----------|-----------|---------------------|----------|-------------|
| ltv_ratio | Decimal | 0.00 - 105.00, 2 decimal places | Yes | Loan-to-Value ratio. Calculated: loan_amount / lesser of (appraised_value, purchase_price) * 100. |
| cltv_ratio | Decimal | 0.00 - 105.00, 2 decimal places | No | Combined Loan-to-Value ratio. Includes subordinate financing. |
| front_end_dti | Decimal | 0.00 - 99.99, 2 decimal places | Yes | Front-end (housing) debt-to-income ratio. |
| back_end_dti | Decimal | 0.00 - 99.99, 2 decimal places | Yes | Back-end (total) debt-to-income ratio. |
| qualifying_income | Decimal | Monthly, 2 decimal places | Yes | Total verified qualifying monthly income for all borrowers. |
| total_housing_expense | Decimal | Monthly, 2 decimal places | Yes | Total proposed monthly housing expense (PITIA + MI). |
| total_monthly_liabilities | Decimal | Monthly, 2 decimal places | Yes | Total recurring monthly liabilities from credit report and other obligations. |
| qualifying_credit_score | Integer | 300-850 | Yes | Lowest representative score among qualifying borrowers. |
| cash_to_close | Decimal | 2 decimal places | Yes | Estimated or final cash required from borrower at closing. |
| reserves_months | Decimal | 0.0 - 99.0, 1 decimal place | No | Verified reserves expressed as months of PITIA. |

### 2.6 Loan Status and Workflow

| Field Name | Data Type | Format / Constraints | Required | Description |
|-----------|-----------|---------------------|----------|-------------|
| status | Enum | See status values below | Yes | Current loan pipeline status. |
| status_date | DateTime | ISO 8601 | Yes | Date and time of the most recent status change. |
| status_history | Array[Object] | status, date, changed_by, notes | Yes | Audit trail of all status changes. Immutable append-only. |
| assigned_lo | String | Employee ID | Yes | Loan officer assigned to this loan. |
| assigned_processor | String | Employee ID | Conditional | Processor assigned to this loan. Required once status moves to IN_PROCESSING. |
| assigned_underwriter | String | Employee ID | Conditional | Underwriter assigned. Required once status moves to IN_UNDERWRITING. |
| target_closing_date | Date | ISO 8601 | Conditional | Target closing date. Required for purchase transactions. |
| actual_closing_date | Date | ISO 8601 | Conditional | Actual closing date. Set when loan closes. |

**Loan Status Values:**

| Status Code | Display Name | Description |
|-------------|-------------|-------------|
| APP_RECEIVED | Application Received | Application has been received; initial disclosures pending |
| DISCLOSED | Disclosed | Loan Estimate delivered; awaiting Intent to Proceed |
| IN_PROCESSING | In Processing | Assigned to processor; documents being collected |
| SUBMITTED_UW | Submitted to Underwriting | Complete file submitted to underwriting queue |
| IN_UNDERWRITING | In Underwriting | Underwriter actively reviewing the file |
| APPROVED | Approved | Underwriter has approved; conditions may exist |
| COND_APPROVAL | Conditional Approval | Approved with outstanding prior-to-closing conditions |
| CLEAR_TO_CLOSE | Clear to Close | All conditions cleared; Closing Disclosure sent |
| CLOSING_SCHEDULED | Closing Scheduled | Settlement date confirmed |
| CLOSED_FUNDED | Closed / Funded | Loan has closed and funded |
| SUSPENDED | Suspended | Underwriting has suspended; additional info needed |
| DENIED | Denied | Loan denied; adverse action notice issued |
| WITHDRAWN | Withdrawn | Borrower withdrew application |
| CANCELLED | Cancelled | Application cancelled by lender (e.g., fraud, incomplete) |

## 3. Relationships

| Related Object | Relationship | Description |
|---------------|-------------|-------------|
| Borrower | 1:N | One loan has one or more borrowers |
| Credit Report (CRP-DAT-MTG-002) | 1:N | One loan may have multiple credit reports (reissues) |
| Appraisal | 1:1 | One loan typically has one appraisal |
| Disclosure | 1:N | One loan may have multiple disclosure packages (initial + revised) |
| Condition | 1:N | One loan may have multiple underwriting conditions |
| Document | 1:N | One loan has many associated documents |
| Note / Comment | 1:N | One loan has many processor/underwriter notes |

## 4. Data Quality Rules

| Rule | Validation | Error Level |
|------|-----------|-------------|
| Loan amount > 0 | loan_amount must be positive | Error (blocks save) |
| LTV calculation | ltv_ratio must equal loan_amount / value * 100 within 0.01 tolerance | Warning (requires review) |
| DTI calculation | back_end_dti must equal (housing + liabilities) / income * 100 within 0.01 | Warning |
| Borrower required | borrower_ids must contain at least one entry | Error |
| Rate lock consistency | If rate_lock_status = LOCKED, interest_rate and rate_lock_date must be populated | Error |
| Status transition | Status changes must follow valid state machine transitions | Error |
| Occupancy consistency | If occupancy_type = INVESTMENT, loan_program cannot be FHA, VA, or USDA | Error |

## 5. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 3.0 | 2025-03-15 | J. Kowalski | Added rate lock fields; expanded status values; aligned with MISMO v3.6 |
| 2.0 | 2024-06-01 | J. Kowalski | Added financial calculation fields; expanded property fields |
| 1.0 | 2023-01-01 | Data Architecture Team | Initial release |
