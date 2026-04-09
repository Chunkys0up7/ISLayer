---
corpus_id: "CRP-POL-PA-001"
title: "Appraisal Ordering Policy"
slug: "appraisal-ordering-policy"
doc_type: "policy"
domain: "Mortgage Lending"
subdomain: "Property Appraisal"
tags:
  - "appraisal-ordering"
  - "amc-panel"
  - "rotation-rules"
  - "fee-schedule"
  - "rush-orders"
  - "appraiser-qualifications"
  - "property-type"
applies_to:
  process_ids:
    - "Process_PropertyAppraisal"
    - "Process_AppraisalOrdering"
  task_types:
    - "userTask"
    - "serviceTask"
  task_name_patterns:
    - "order.*appraisal"
    - "select.*amc"
    - "manage.*panel"
  goal_types:
    - "governance"
  roles:
    - "appraisal_coordinator"
    - "loan_processor"
    - "vp_appraisal_operations"
version: "3.0"
status: "current"
effective_date: "2025-06-01"
review_date: "2026-06-01"
supersedes: null
superseded_by: null
author: "Appraisal Operations Committee"
last_modified: "2025-05-22"
last_modified_by: "M. Delgado"
source: "internal"
source_ref: "POL-PA-001"
related_corpus_ids:
  - "CRP-PRC-PA-001"
  - "CRP-POL-PA-002"
  - "CRP-REG-PA-002"
  - "CRP-SYS-PA-001"
regulation_refs:
  - "Dodd-Frank Act Section 1472"
  - "FIRREA Title XI"
  - "Fannie Mae Selling Guide B4-1.1"
policy_refs:
  - "POL-PA-002"
---

# Appraisal Ordering Policy

## 1. Policy Statement

All residential mortgage appraisals shall be ordered through approved Appraisal Management Companies (AMCs) using standardized processes that ensure appraiser independence, fair compensation, appropriate appraiser qualifications, and timely delivery. This policy establishes the governance framework for appraisal ordering, including AMC panel management, rotation rules, fee structures, rush order criteria, and appraiser qualification minimums.

## 2. AMC Panel Management

### 2.1 Panel Composition

The approved AMC panel shall consist of a minimum of 4 and a maximum of 8 active AMCs at any given time. Panel composition must provide:

| Requirement | Minimum |
|---|---|
| National coverage AMCs | 2 |
| Regional/specialty AMCs | 1 |
| Total active AMCs | 4 |
| Geographic coverage | All 50 states and DC (via panel collectively) |

### 2.2 Panel Approval Process

New AMCs are approved through the following process:

1. **Application**: AMC submits application including state registrations, E&O insurance, financial statements, quality control plan, and appraiser panel composition
2. **Due Diligence**: Vendor Management conducts background check, financial review, reference checks, and compliance history review
3. **Pilot Period**: New AMC receives limited orders (maximum 50) over a 90-day pilot with enhanced quality review
4. **Full Approval**: After successful pilot, AMC is added to the active rotation panel
5. **Annual Recertification**: Each AMC undergoes annual recertification including updated state registrations and performance review

### 2.3 Panel Removal Criteria

An AMC may be removed from the panel (temporarily or permanently) for:

| Removal Trigger | Action |
|---|---|
| Performance score below 60 for two consecutive quarters | Suspension pending improvement plan |
| Appraiser independence violation | Immediate suspension; investigation |
| State registration lapse | Suspension for affected states until reinstated |
| Financial instability (e.g., E&O lapse) | Immediate suspension |
| Repeated SLA failures (>20% late deliveries) | Warning, then suspension |
| Compliance finding by regulator | Review; suspension or removal as warranted |

## 3. Rotation Rules

### 3.1 Standard Rotation Algorithm

Orders are distributed among approved AMCs using a weighted rotation algorithm:

```
Assignment Weight = Base Weight x Performance Multiplier x Capacity Factor

Where:
  Base Weight       = Equal share (1/N where N = number of active AMCs)
  Performance Mult. = AMC Performance Score / 80 (normalized to score of 80)
  Capacity Factor   = 1.0 if below max capacity; 0.0 if at max capacity
```

### 3.2 Rotation Exceptions

The rotation may be bypassed in the following situations (requires documentation):

| Exception | Approval Authority |
|---|---|
| Geographic coverage gap (no AMC covers the area) | Appraisal Coordinator |
| Specialty property type requiring specific AMC capability | Appraisal Coordinator |
| AMC at maximum concurrent capacity | Automatic (system-enforced) |
| Prior appraisal transfer (same AMC for continuity) | Underwriter |
| Emergency/disaster area requiring specific AMC coordination | VP Appraisal Operations |

### 3.3 Anti-Cherry-Picking Controls

- No individual may direct orders to a specific AMC to influence value outcomes
- Rotation override reports are generated monthly and reviewed by compliance
- Any pattern of overrides favoring a single AMC triggers an audit

## 4. Fee Schedules

### 4.1 Standard Fee Ranges

Appraisal fees are established based on property type and assignment scope. These ranges represent customary and reasonable fees per Dodd-Frank requirements:

| Property Type | Standard Interior Fee | Exterior-Only Fee | Desktop Fee |
|---|---|---|---|
| SFR (urban/suburban) | $450 - $650 | $250 - $400 | $150 - $275 |
| SFR (rural) | $550 - $850 | $350 - $500 | $200 - $325 |
| Condominium | $450 - $650 | $250 - $400 | $150 - $275 |
| 2-4 Unit | $600 - $900 | $350 - $550 | N/A |
| Manufactured Housing | $500 - $750 | $300 - $500 | N/A |
| Mixed-Use | $700 - $1,100 | N/A | N/A |
| High-Value (>$1M appraised) | $650 - $1,200 | $400 - $700 | $250 - $400 |

### 4.2 Fee Adjustments

| Adjustment Type | Additional Fee | Approval Required |
|---|---|---|
| Rush order (3 business day turnaround) | +$150 - $250 | Appraisal Coordinator |
| Complex property (unique design, large acreage) | +$100 - $300 | Appraisal Coordinator |
| Remote/difficult access | +$75 - $200 | Automatic (AMC-determined) |
| Re-inspection (post-repair) | $125 - $200 | Underwriter |
| Update/recertification of prior appraisal | $200 - $350 | Underwriter |

### 4.3 Fee Collection

Appraisal fees are collected from the borrower prior to order submission. Fee collection methods:
- Credit card at application
- ACH debit authorized at application
- Added to borrower-paid closing costs (with borrower consent)
- Collected by loan officer at application (deposited to trust account)

## 5. Rush Order Criteria

### 5.1 Definition

A rush order is defined as any order requiring completion in fewer than 5 business days from order submission. Standard turnaround is 7-10 business days.

### 5.2 Eligibility for Rush Orders

| Criterion | Requirement |
|---|---|
| Contract closing deadline | Within 15 calendar days |
| Rate lock expiration | Within 10 calendar days |
| Regulatory or court deadline | Documented external deadline |
| Investor commitment expiration | Documented expiration date |
| Construction draw requirement | Time-sensitive disbursement |

### 5.3 Rush Order Restrictions

- Maximum 15% of total monthly orders may be rush orders
- Rush requests exceeding 15% require VP approval
- No rush orders to circumvent the AMC rotation (rush goes to the next AMC in rotation with rush capability)
- Rush fees apply per Section 4.2

## 6. Property Type Requirements

### 6.1 Appraiser Qualification Minimums by Property Type

| Property Type | Minimum Appraiser Credential | Additional Requirements |
|---|---|---|
| SFR (standard) | State Licensed Appraiser | Active license in subject state |
| SFR (>$1M or complex) | State Certified Residential | Active certification in subject state |
| Condominium | State Licensed Appraiser | Condo market experience in subject area |
| 2-4 Unit | State Certified Residential | Multi-family experience |
| Manufactured Housing | State Certified Residential | Manufactured housing endorsement or demonstrated experience |
| Mixed-Use | State Certified General | Commercial and residential competency |
| Rural/Agricultural | State Certified Residential or General | Rural market knowledge; acreage experience |
| FHA Assignment | State Certified (per FHA requirement) | On FHA roster; FHA-specific training |
| VA Assignment | VA Fee Panel Appraiser | VA assignment required; cannot be ordered through AMC |

### 6.2 Geographic Competency

The assigned appraiser must demonstrate competency in the geographic market of the subject property. Competency is evidenced by:
- Primary practice area includes the subject county or MSA
- Minimum of 5 appraisals completed in the subject market area within the prior 12 months
- If these criteria are not met, the appraiser must disclose and address competency per USPAP Competency Rule

## 7. Appraisal Waivers and Alternative Valuations

### 7.1 Appraisal Waiver Eligibility

GSE appraisal waivers (Fannie Mae ACE, Freddie Mac ACE) may be accepted when:
- The DU/LPA system issues a waiver offer
- The loan program and transaction type are eligible
- LTV does not exceed the waiver maximum (generally 80% for purchase, 90% for refinance)
- The property type is eligible (typically SFR and condo only)
- No known property condition issues

### 7.2 Alternative Valuation Products

| Product | When Permitted | Approval Authority |
|---|---|---|
| Desktop appraisal | GSE waiver alternative; investor-approved | Underwriter |
| Hybrid appraisal | GSE-approved with third-party inspection | Underwriter |
| Exterior-only (drive-by) | Refinance with low LTV; investor-approved | Underwriter |
| AVM with property inspection | Non-QM or portfolio products only | Senior Underwriter |

## 8. Monitoring and Reporting

| Metric | Frequency | Target |
|---|---|---|
| AMC rotation compliance | Monthly | >95% orders follow rotation |
| Average turnaround time | Monthly | <8 business days |
| Rush order percentage | Monthly | <15% of total orders |
| Fee variance from schedule | Quarterly | <10% variance from standard ranges |
| Appraiser credential compliance | Monthly | 100% meet minimum qualifications |
| Order rejection / reassignment rate | Monthly | <5% |

## 9. References

- CRP-PRC-PA-001: Appraisal Ordering Procedure
- CRP-POL-PA-002: AMC Selection and Rotation Policy
- CRP-REG-PA-002: Appraiser Independence Requirements
- CRP-SYS-PA-001: Appraisal Portal Integration Guide
- Dodd-Frank Act Section 1472
- Fannie Mae Selling Guide B4-1.1
