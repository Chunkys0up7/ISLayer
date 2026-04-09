---
corpus_id: "CRP-DAT-MTG-002"
title: "Credit Report Data Object"
slug: "credit-report-data"
doc_type: "data-dictionary"
domain: "Mortgage Lending"
subdomain: "Credit"
tags:
  - "data-object"
  - "credit-report"
  - "fico-score"
  - "tradeline"
  - "public-records"
  - "fraud-alert"
  - "credit-data"
applies_to:
  process_ids:
    - "Process_LoanOrigination"
  task_types:
    - "userTask"
    - "serviceTask"
    - "businessRuleTask"
  task_name_patterns:
    - ".*credit.*"
    - ".*score.*"
    - ".*tradeline.*"
  goal_types:
    - "data_production"
    - "decision"
  roles:
    - "loan_processor"
    - "underwriter"
    - "loan_officer"
version: "2.0"
status: "current"
effective_date: "2025-04-01"
review_date: "2026-04-01"
supersedes: null
superseded_by: null
author: "Data Architecture Team"
last_modified: "2025-03-15"
last_modified_by: "J. Kowalski"
source: "internal"
source_ref: "DICT-CR-2025-001"
related_corpus_ids:
  - "CRP-PRC-MTG-003"
  - "CRP-POL-MTG-001"
  - "CRP-POL-MTG-002"
  - "CRP-DAT-MTG-001"
regulation_refs:
  - "FCRA 15 U.S.C. 1681"
  - "MISMO v3.6 Credit Data Standards"
policy_refs:
  - "POL-CR-001"
  - "POL-DATA-001"
---

# Credit Report Data Object

## 1. Overview

The Credit Report data object represents a tri-merge residential mortgage credit report (RMCR) as received from the credit report vendor and stored in the Loan Origination System. Each credit report is associated with a single borrower and linked to one or more loan applications. The data model captures bureau scores, tradeline details, public records, inquiries, and fraud indicators.

## 2. Primary Fields

### 2.1 Report Identification

| Field Name | Data Type | Format / Constraints | Required | Description |
|-----------|-----------|---------------------|----------|-------------|
| report_id | UUID | Standard UUID v4 | Yes | System-generated unique identifier for this credit report instance. Primary key. |
| vendor_reference | String | Alphanumeric, max 30 chars | Yes | Reference number assigned by the credit report vendor. Used for vendor communication and reorder requests. |
| borrower_id | UUID | Foreign key to Borrower object | Yes | The borrower to whom this credit report belongs. |
| loan_ids | Array[UUID] | Foreign keys to Loan Application objects | Yes | Loan applications associated with this credit report. A single report may be used across multiple applications for the same borrower. |
| report_type | Enum | `TRI_MERGE`, `SUPPLEMENT`, `SINGLE_BUREAU`, `SOFT_PULL` | Yes | Type of credit report. TRI_MERGE is standard for mortgage underwriting. |
| order_date | DateTime | ISO 8601 | Yes | Date and time the credit report was ordered. |
| received_date | DateTime | ISO 8601 | Yes | Date and time the credit report was received from the vendor. |
| expiration_date | Date | ISO 8601 | Yes | 120 calendar days from order_date. After this date, the report is no longer valid for underwriting without a supplement or reorder. |
| report_status | Enum | `ACTIVE`, `SUPPLEMENTED`, `EXPIRED`, `SUPERSEDED` | Yes | Current status of this report. ACTIVE: within validity period. SUPPLEMENTED: updated by a supplement report. EXPIRED: past 120-day window. SUPERSEDED: replaced by a newer full report. |
| ordering_user | String | Employee ID | Yes | The employee who ordered the credit report. Audit trail field. |
| permissible_purpose_code | Enum | `CREDIT_TRANSACTION`, `CONSUMER_AUTHORIZATION`, `ACCOUNT_REVIEW` | Yes | FCRA permissible purpose under which this report was obtained. |
| cost | Decimal | USD, 2 decimal places | Yes | Actual cost charged by the vendor for this report. |

### 2.2 Bureau Scores

| Field Name | Data Type | Format / Constraints | Required | Description |
|-----------|-----------|---------------------|----------|-------------|
| bureau_scores | Object | Contains three bureau sub-objects | Yes | Credit scores from each bureau. |
| bureau_scores.experian | Object | See Bureau Score sub-object | Conditional | Experian score data. Required if Experian reported. |
| bureau_scores.experian.score | Integer | 300-850, or null | Conditional | FICO Score 2 (Experian/Fair Isaac Risk Model v2). Null if bureau did not return a score. |
| bureau_scores.experian.score_model | String | Fixed: "FICO_2" | Yes | Score model identifier. |
| bureau_scores.experian.factors | Array[String] | Up to 4 reason codes | No | Score factor codes explaining the primary reasons for the score (e.g., "Amount owed on accounts is too high"). |
| bureau_scores.equifax | Object | See Bureau Score sub-object | Conditional | Equifax score data. |
| bureau_scores.equifax.score | Integer | 300-850, or null | Conditional | FICO Score 5 (Equifax Beacon 5.0). |
| bureau_scores.equifax.score_model | String | Fixed: "FICO_5" | Yes | Score model identifier. |
| bureau_scores.equifax.factors | Array[String] | Up to 4 reason codes | No | Score factor codes. |
| bureau_scores.transunion | Object | See Bureau Score sub-object | Conditional | TransUnion score data. |
| bureau_scores.transunion.score | Integer | 300-850, or null | Conditional | FICO Score 4 (TransUnion FICO Risk Score 04). |
| bureau_scores.transunion.score_model | String | Fixed: "FICO_4" | Yes | Score model identifier. |
| bureau_scores.transunion.factors | Array[String] | Up to 4 reason codes | No | Score factor codes. |
| representative_score | Integer | 300-850 | Yes | The representative score for this borrower, calculated per score selection rules: middle of three scores, lower of two scores, or the single available score. |
| scores_available_count | Integer | 0-3 | Yes | Number of bureaus that returned a valid score. Used for score selection logic and thin-file identification. |

### 2.3 Tradelines

| Field Name | Data Type | Format / Constraints | Required | Description |
|-----------|-----------|---------------------|----------|-------------|
| tradelines | Array[Object] | 0-N tradeline objects | Yes | Array of all credit tradelines (accounts) reported across all three bureaus. Deduplicated by account identifier. |
| tradelines[].tradeline_id | UUID | Auto-generated | Yes | Unique identifier for this tradeline within the report. |
| tradelines[].creditor_name | String | Max 100 chars | Yes | Name of the creditor or lender. |
| tradelines[].account_number | String | Last 4 digits only (masked) | Yes | Masked account number for identification. Full number not stored per data security policy. |
| tradelines[].account_type | Enum | `REVOLVING`, `INSTALLMENT`, `MORTGAGE`, `OPEN`, `COLLECTION`, `CHARGE_OFF`, `OTHER` | Yes | Type of credit account. |
| tradelines[].ownership | Enum | `INDIVIDUAL`, `JOINT`, `AUTHORIZED_USER`, `CO_SIGNER`, `TERMINATED` | Yes | Borrower's responsibility on the account. |
| tradelines[].current_balance | Decimal | USD, 2 decimal places | Yes | Current outstanding balance. |
| tradelines[].credit_limit | Decimal | USD, 2 decimal places | Conditional | Credit limit or original loan amount. Required for REVOLVING and INSTALLMENT accounts. |
| tradelines[].monthly_payment | Decimal | USD, 2 decimal places | Yes | Minimum required monthly payment. If not reported, calculated per program rules (e.g., 5% of balance for unreported revolving). |
| tradelines[].payment_reported | Boolean | true/false | Yes | Whether the bureau reported a specific monthly payment amount. If false, monthly_payment is a calculated value. |
| tradelines[].account_status | Enum | `OPEN`, `CLOSED`, `PAID`, `CHARGED_OFF`, `COLLECTION`, `FORECLOSURE`, `INCLUDED_IN_BANKRUPTCY` | Yes | Current status of the account. |
| tradelines[].date_opened | Date | ISO 8601 | Yes | Date the account was opened. |
| tradelines[].date_last_activity | Date | ISO 8601 | No | Date of the most recent account activity. |
| tradelines[].date_closed | Date | ISO 8601 | Conditional | Date the account was closed, if applicable. |
| tradelines[].payment_history | Object | See Payment History sub-object | Yes | Rolling 24-month payment history showing on-time and late payment indicators. |
| tradelines[].payment_history.late_30 | Integer | 0-24 | Yes | Count of 30-day late payments in the past 24 months. |
| tradelines[].payment_history.late_60 | Integer | 0-24 | Yes | Count of 60-day late payments in the past 24 months. |
| tradelines[].payment_history.late_90 | Integer | 0-24 | Yes | Count of 90-day late payments in the past 24 months. |
| tradelines[].payment_history.late_120_plus | Integer | 0-24 | Yes | Count of 120+ day late payments in the past 24 months. |
| tradelines[].remaining_payments | Integer | 0-999 | No | Estimated remaining number of payments on installment accounts. Used for the 10-payment exclusion rule (Conventional). |
| tradelines[].is_medical | Boolean | true/false | Yes | Whether the tradeline is identified as a medical account. Affects DTI treatment per program rules. |
| tradelines[].dispute_status | Enum | `NONE`, `CONSUMER_DISPUTE`, `RESOLVED`, `REINVESTIGATION` | Yes | Whether the consumer has an active dispute on this tradeline. Active disputes may affect AUS findings. |
| tradelines[].reporting_bureaus | Array[Enum] | `EXPERIAN`, `EQUIFAX`, `TRANSUNION` | Yes | Which bureaus report this tradeline. |

### 2.4 Public Records

| Field Name | Data Type | Format / Constraints | Required | Description |
|-----------|-----------|---------------------|----------|-------------|
| public_records | Array[Object] | 0-N public record objects | Yes | Array of public records (bankruptcies, judgments, tax liens) reported on the credit report. |
| public_records[].record_id | UUID | Auto-generated | Yes | Unique identifier for this public record. |
| public_records[].record_type | Enum | `BANKRUPTCY_CH7`, `BANKRUPTCY_CH13`, `TAX_LIEN_FEDERAL`, `TAX_LIEN_STATE`, `JUDGMENT`, `FORECLOSURE`, `CIVIL_CLAIM` | Yes | Type of public record. |
| public_records[].filed_date | Date | ISO 8601 | Yes | Date the public record was filed. |
| public_records[].resolved_date | Date | ISO 8601 | Conditional | Date the record was discharged, satisfied, or released. Null if still active. |
| public_records[].status | Enum | `FILED`, `DISCHARGED`, `DISMISSED`, `SATISFIED`, `RELEASED`, `ACTIVE` | Yes | Current status of the public record. |
| public_records[].amount | Decimal | USD, 2 decimal places | Conditional | Dollar amount associated with the record (e.g., judgment amount, lien amount). |
| public_records[].court_name | String | Max 100 chars | No | Name of the court or filing jurisdiction. |
| public_records[].reporting_bureaus | Array[Enum] | `EXPERIAN`, `EQUIFAX`, `TRANSUNION` | Yes | Which bureaus report this record. |

### 2.5 Inquiries

| Field Name | Data Type | Format / Constraints | Required | Description |
|-----------|-----------|---------------------|----------|-------------|
| inquiries | Array[Object] | 0-N inquiry objects | Yes | Array of credit inquiries (hard pulls) in the past 24 months. |
| inquiries[].inquiry_id | UUID | Auto-generated | Yes | Unique identifier for this inquiry. |
| inquiries[].creditor_name | String | Max 100 chars | Yes | Name of the entity that pulled the credit report. |
| inquiries[].inquiry_date | Date | ISO 8601 | Yes | Date of the inquiry. |
| inquiries[].inquiry_type | Enum | `MORTGAGE`, `AUTO`, `CREDIT_CARD`, `STUDENT_LOAN`, `PERSONAL_LOAN`, `OTHER` | Yes | Category of the inquiry based on industry code. |
| inquiries[].is_promotional | Boolean | true/false | Yes | Whether this is a promotional (soft) inquiry vs. a hard inquiry. Only hard inquiries affect the score. |

### 2.6 Fraud Indicators

| Field Name | Data Type | Format / Constraints | Required | Description |
|-----------|-----------|---------------------|----------|-------------|
| fraud_alerts | Array[Object] | 0-N fraud alert objects | Yes | Array of fraud alerts, security freezes, or consumer statements on the credit file. |
| fraud_alerts[].alert_type | Enum | `INITIAL_FRAUD_ALERT`, `EXTENDED_FRAUD_ALERT`, `ACTIVE_DUTY_ALERT`, `SECURITY_FREEZE`, `CONSUMER_STATEMENT` | Yes | Type of fraud indicator. |
| fraud_alerts[].alert_date | Date | ISO 8601 | Yes | Date the alert was placed. |
| fraud_alerts[].expiration_date | Date | ISO 8601 | Conditional | Date the alert expires (initial alerts: 1 year; extended: 7 years). |
| fraud_alerts[].contact_phone | String | 10-digit US phone | Conditional | Phone number specified in the fraud alert. Required for INITIAL_FRAUD_ALERT and EXTENDED_FRAUD_ALERT. The processor must contact the borrower at this number per FCRA. |
| fraud_alerts[].message | String | Max 500 chars | No | Consumer statement or alert message text. |
| fraud_alerts[].bureaus | Array[Enum] | `EXPERIAN`, `EQUIFAX`, `TRANSUNION` | Yes | Which bureaus report this alert. |

## 3. Computed Fields

| Field Name | Computation | Description |
|-----------|-------------|-------------|
| total_revolving_balance | Sum of current_balance where account_type = REVOLVING and account_status = OPEN | Total outstanding revolving credit balance. |
| total_revolving_limit | Sum of credit_limit where account_type = REVOLVING and account_status = OPEN | Total available revolving credit limit. |
| revolving_utilization | total_revolving_balance / total_revolving_limit * 100 | Aggregate revolving credit utilization percentage. Key credit health indicator. |
| total_monthly_obligations | Sum of monthly_payment for all open tradelines (excluding authorized user unless qualifying) | Total minimum monthly credit obligations from the credit report. |
| open_tradeline_count | Count of tradelines where account_status = OPEN | Number of currently open credit accounts. |
| derogatory_count | Count of tradelines with late_30 > 0 or late_60 > 0 or late_90 > 0 or late_120_plus > 0 in past 24 months | Number of accounts with derogatory payment history in the evaluation period. |
| credit_age_months | Months between the earliest tradeline date_opened and report order_date | Age of the oldest tradeline. Indicator of credit history depth. |

## 4. Relationships

| Related Object | Relationship | Description |
|---------------|-------------|-------------|
| Borrower | N:1 | Many credit reports can exist for one borrower (reissues, supplements) |
| Loan Application (CRP-DAT-MTG-001) | N:N | A credit report may apply to multiple loan applications; a loan may reference multiple credit reports |
| OFAC Screening | 1:1 | Each credit report pull is paired with an OFAC screening |

## 5. Data Quality Rules

| Rule | Validation | Error Level |
|------|-----------|-------------|
| Score range | All scores must be 300-850 or null | Error |
| Representative score logic | representative_score must equal middle of 3, lower of 2, or single score | Error |
| Expiration calculation | expiration_date must equal order_date + 120 days | Warning |
| Tradeline balance non-negative | current_balance >= 0 for all tradelines | Error |
| Fraud alert phone required | If alert_type is INITIAL or EXTENDED, contact_phone must be populated | Error |
| Report completeness | At least one bureau must report data | Error |

## 6. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.0 | 2025-03-15 | J. Kowalski | Added fraud indicators section; expanded tradeline fields; added computed fields |
| 1.0 | 2023-05-01 | Data Architecture Team | Initial release |
