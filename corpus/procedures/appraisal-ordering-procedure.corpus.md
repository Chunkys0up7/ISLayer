---
corpus_id: "CRP-PRC-PA-001"
title: "Appraisal Ordering Procedure"
slug: "appraisal-ordering-procedure"
doc_type: "procedure"
domain: "Mortgage Lending"
subdomain: "Property Appraisal"
tags:
  - "appraisal-ordering"
  - "amc-selection"
  - "mismo-xml"
  - "appraiser-independence"
  - "dodd-frank"
  - "property-valuation"
applies_to:
  process_ids:
    - "Process_PropertyAppraisal"
    - "Process_AppraisalOrdering"
  task_types:
    - "userTask"
    - "serviceTask"
  task_name_patterns:
    - "order.*appraisal"
    - "submit.*appraisal.*order"
    - "select.*amc"
    - "assign.*appraiser"
  goal_types:
    - "initiation"
  roles:
    - "loan_processor"
    - "appraisal_coordinator"
    - "underwriter"
version: "1.2"
status: "current"
effective_date: "2025-06-01"
review_date: "2026-06-01"
supersedes: null
superseded_by: null
author: "Appraisal Operations Committee"
last_modified: "2025-05-15"
last_modified_by: "M. Delgado"
source: "internal"
source_ref: "SOP-PA-2025-001"
related_corpus_ids:
  - "CRP-POL-PA-001"
  - "CRP-POL-PA-002"
  - "CRP-REG-PA-002"
  - "CRP-SYS-PA-001"
regulation_refs:
  - "Dodd-Frank Act Section 1472"
  - "FIRREA Title XI"
  - "Fannie Mae Selling Guide B4-1.1-01"
policy_refs:
  - "POL-PA-001"
  - "POL-PA-002"
---

# Appraisal Ordering Procedure

## 1. Scope

This procedure governs the end-to-end process of ordering a property appraisal through an approved Appraisal Management Company (AMC). It covers AMC selection, order submission, independence verification, and assignment tracking. All appraisal orders must comply with Dodd-Frank Section 1472 appraiser independence requirements and internal AMC rotation policies.

## 2. Prerequisites

| # | Prerequisite | Source |
|---|---|---|
| 1 | Loan application registered in LOS with valid property address | Loan Origination System |
| 2 | Borrower has paid or authorized the appraisal fee | Fee collection system |
| 3 | Property type and loan program determined | Loan processor / underwriter |
| 4 | AMC panel current and approved (see CRP-POL-PA-002) | Vendor management |
| 5 | No existing valid appraisal on file for the subject property (or transfer eligibility confirmed) | Appraisal archive |

## 3. Procedure Steps

### Step 1: Select AMC from Approved Panel

1.1. Access the AMC rotation queue in the appraisal ordering portal. The system enforces the rotation algorithm defined in CRP-POL-PA-002.

1.2. Verify the selected AMC has geographic coverage for the subject property's county and state. If the primary AMC lacks coverage, the system advances to the next AMC in the rotation.

1.3. Confirm the AMC's current performance score meets the minimum threshold (score >= 70 out of 100). AMCs below threshold are automatically bypassed.

1.4. For specialty property types (manufactured housing, mixed-use, agricultural), verify the AMC maintains a certified panel of appraisers with the required competency endorsement for that property type.

1.5. Document the AMC selection in the order log. If the rotation was overridden for any reason, record the justification. Valid override reasons include:
- Geographic coverage gap
- Performance score below threshold
- Specialty property type requiring specific appraiser competency
- AMC at maximum concurrent order capacity

### Step 2: Prepare and Submit Order via Portal

2.1. Compile the order package with the following required data elements:

| Data Element | Source | Required |
|---|---|---|
| Property address (standardized USPS format) | Loan application | Yes |
| Property type (SFR, condo, 2-4 unit, manufactured) | Loan application | Yes |
| Loan purpose (purchase, refinance, cash-out) | Loan application | Yes |
| Loan program (conventional, FHA, VA, USDA, jumbo) | Loan application | Yes |
| Estimated value (if refinance) | Borrower estimate | Conditional |
| Purchase price and contract date (if purchase) | Purchase agreement | Conditional |
| Borrower contact information | Loan application | Yes |
| Property access instructions | Borrower / listing agent | Yes |
| Applicable form type (1004, 1073, 2055) | Program requirements | Yes |
| Rush indicator and justification | Processor | Optional |
| Special instructions or known property issues | Processor notes | Optional |

2.2. Format the order as MISMO XML per the current MISMO Reference Model (v3.4 or later). The appraisal portal generates the XML payload automatically from the order form fields.

2.3. Include any available comparable sales data from the MLS or internal comparable database. Providing comparable data assists the appraiser but must not be presented as a value directive.

2.4. Attach the following supporting documents to the order:
- Property listing sheet (if purchase transaction)
- Prior appraisal (if available and relevant, e.g., for reconsideration of value)
- HOA documents (for condo or PUD properties)
- Legal description or survey (if available)

2.5. Submit the order through the AMC portal API endpoint. Record the order confirmation number and estimated completion date returned by the system.

### Step 3: Confirm Appraiser Independence (Dodd-Frank Section 1472)

3.1. Prior to order finalization, the system generates an Appraiser Independence Certification (AIC) record. Verify the following conditions are met:

| Independence Requirement | Verification Method |
|---|---|
| No loan production staff selected the appraiser | System audit: order initiated by approved role only |
| No value target communicated to appraiser | Order review: no value language in instructions field |
| Appraiser fee is customary and reasonable for the market | Fee schedule comparison against county benchmarks |
| No prior relationship between appraiser and interested parties | Conflict-of-interest check against borrower/seller/agent names |
| AMC is registered in the subject property state | AMC registration database lookup |

3.2. If any independence check fails, halt the order and escalate to the Appraisal Compliance Officer. Do not resubmit until the independence concern is resolved and documented.

3.3. The AIC record is stored in the compliance archive and linked to the loan file.

### Step 4: Track Assignment Acceptance

4.1. Monitor the order status via the AMC portal. Expected status progression:

| Status | Expected Timeline |
|---|---|
| Order Received | Immediate (upon submission) |
| Appraiser Assigned | Within 24 hours |
| Inspection Scheduled | Within 48 hours of assignment |
| Inspection Completed | Per agreed schedule |
| Report Submitted | Within 5-7 business days of inspection |

4.2. If the order is not accepted within 24 hours, the portal triggers an automatic follow-up notification to the AMC.

4.3. If the order is declined or unassigned after 48 hours, escalate to the appraisal coordinator for reassignment to the next AMC in the rotation queue.

4.4. Upon appraiser assignment, verify the assigned appraiser holds:
- Active state license or certification for the subject property state
- Appropriate credential level for the property type and transaction value
- No active disciplinary actions on the state appraiser regulatory board

4.5. Record all status changes and timestamps in the appraisal tracking log.

## 4. Exception Handling

| Exception | Action |
|---|---|
| No AMC available in rotation with geographic coverage | Escalate to VP of Appraisal Operations for manual AMC sourcing |
| Borrower requests specific appraiser | Decline per independence requirements; document the request |
| Loan officer provides value information in order | Reject order, remove value language, re-submit, log compliance event |
| Property in remote or underserved area | Allow extended timeline (up to 15 business days); consider desktop or hybrid appraisal if investor guidelines permit |

## 5. Quality Controls

- All orders are logged with timestamps, AMC selection rationale, and independence certification status
- Monthly audit of 10% of orders for independence compliance
- AMC performance reviews conducted quarterly per CRP-POL-PA-002
- Order rejection and reassignment rates tracked as KPIs

## 6. References

- CRP-POL-PA-001: Appraisal Ordering Policy
- CRP-POL-PA-002: AMC Selection and Rotation Policy
- CRP-REG-PA-002: Appraiser Independence Requirements
- CRP-SYS-PA-001: Appraisal Portal Integration Guide
- Dodd-Frank Act Section 1472 (15 USC 1639e)
- Fannie Mae Selling Guide B4-1.1-01
