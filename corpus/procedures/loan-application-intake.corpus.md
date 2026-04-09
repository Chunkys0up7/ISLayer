---
corpus_id: "CRP-PRC-MTG-001"
title: "Loan Application Intake Procedure"
slug: "loan-application-intake"
doc_type: "procedure"
domain: "Mortgage Lending"
subdomain: "Loan Origination"
tags:
  - "loan-application"
  - "intake"
  - "urla"
  - "1003"
  - "loan-estimate"
  - "initial-disclosures"
  - "los-entry"
applies_to:
  process_ids:
    - "Process_LoanOrigination"
  task_types:
    - "userTask"
    - "serviceTask"
  task_name_patterns:
    - "receive.*application"
    - "intake.*loan"
    - "enter.*application"
    - "generate.*disclosure"
    - "assign.*processor"
  goal_types:
    - "data_production"
    - "state_transition"
  roles:
    - "loan_officer"
    - "loan_processor"
    - "intake_specialist"
version: "3.0"
status: "current"
effective_date: "2025-06-01"
review_date: "2026-06-01"
supersedes: null
superseded_by: null
author: "Operations Standards Committee"
last_modified: "2025-05-20"
last_modified_by: "R. Caruso"
source: "internal"
source_ref: "SOP-LO-2025-001"
related_corpus_ids:
  - "CRP-PRC-MTG-002"
  - "CRP-PRC-MTG-005"
  - "CRP-RUL-MTG-002"
  - "CRP-DAT-MTG-001"
regulation_refs:
  - "TILA-RESPA Integrated Disclosure Rule (TRID)"
  - "12 CFR 1026.19(e)"
  - "ECOA Regulation B 12 CFR 1002"
policy_refs:
  - "POL-LO-001"
  - "POL-DISC-001"
---

# Loan Application Intake Procedure

## 1. Scope

This procedure governs the receipt, validation, and initial processing of residential mortgage loan applications. It applies to all application channels (in-branch, online, phone, and third-party originator submissions) and covers purchase, refinance, and cash-out refinance transactions across Conventional, FHA, VA, and USDA loan programs.

The procedure begins when the borrower submits a loan application and ends when the file is assigned to a loan processor with initial disclosures delivered.

## 2. Prerequisites

| # | Prerequisite | Source |
|---|---|---|
| 1 | Completed Uniform Residential Loan Application (URLA / Fannie Mae Form 1003) signed by all borrowers | Borrower |
| 2 | Government-issued photo identification for all borrowers | Borrower |
| 3 | Authorization to pull credit (signed borrower consent) | Borrower |
| 4 | Property address or description (for purchase transactions) | Borrower or Realtor |
| 5 | Purchase contract (if purchase transaction) | Borrower or Realtor |
| 6 | Loan Officer has verified NMLS license is current and active | Compliance |

## 3. Procedure Steps

### Step 1: Receive the Loan Application

1.1. Accept the completed URLA from the borrower through an approved channel. The application may be submitted as a physical form, through the online portal, or via the point-of-sale (POS) system.

1.2. Upon receipt, stamp or electronically tag the application with the received date and time. Under TRID, the date of receipt triggers the three-business-day window for Loan Estimate delivery.

1.3. Confirm the application contains the six pieces of information that constitute an "application" under TRID:
- Borrower's name
- Borrower's income
- Borrower's Social Security Number (for credit report purposes)
- Property address
- Estimated property value
- Mortgage loan amount sought

1.4. If any of the six elements are missing, the submission is considered a pre-application inquiry and does not trigger TRID timelines. Document the status and follow up with the borrower to obtain missing information.

### Step 2: Verify Application Completeness

2.1. Review all sections of the URLA for completeness:
- Section 1: Borrower Information (names, SSN, DOB, citizenship, contact info)
- Section 2: Financial Information (assets, liabilities, other real estate)
- Section 3: Financial Information continued (employment, income)
- Section 4: Loan and Property Information (loan amount, purpose, property details)
- Section 5: Declarations (occupancy, judgments, bankruptcy history)
- Section 6: Acknowledgments and Agreements
- Section 7: Military Service (VA eligibility indicators)
- Section 8: Demographic Information (HMDA data)

2.2. Flag any incomplete fields or inconsistencies. Common issues include:
- Missing co-borrower information when joint application is indicated
- Employment dates that do not cover the most recent two years
- Undisclosed liabilities that may appear on the credit report
- Property address discrepancies between the application and purchase contract

2.3. For items that are incomplete but do not affect the six TRID triggers, generate a document request (see CRP-PRC-MTG-005) and proceed with intake.

### Step 3: Enter Application into Loan Origination System (LOS)

3.1. Log into the Loan Origination System using authorized credentials.

3.2. Create a new loan file and assign a unique loan number. The LOS will auto-generate the loan number in the format: `[Branch Code]-[Year]-[Sequential Number]` (e.g., ATL-2025-004521).

3.3. Enter all borrower and loan information from the URLA into the corresponding LOS fields. Key data entry points include:
- Borrower and co-borrower personal information
- Employment and income details
- Asset accounts and balances
- Liabilities and monthly obligations
- Property information and estimated value
- Loan terms (amount, program, rate if locked, term)
- Transaction details (purchase price, down payment, closing cost estimates)

3.4. Attach the original application document (scanned or electronic) to the loan file in the document management module.

3.5. Verify data entry accuracy by running the LOS data validation check. Correct any flagged errors before proceeding.

### Step 4: Generate Initial Disclosures (Loan Estimate)

4.1. Within the LOS, initiate the disclosure generation workflow. The system will produce the following documents:
- **Loan Estimate (LE):** Itemized estimate of loan terms, projected payments, and closing costs per TRID requirements
- **TILA Disclosure:** Truth-in-Lending statement with APR calculation
- **Intent to Proceed form:** Borrower acknowledgment to continue with the application
- **Affiliated Business Arrangement (AfBA) disclosure** (if applicable)
- **Servicing Disclosure:** Statement regarding the potential transfer of servicing
- **ECOA Notice / Appraisal Disclosure**
- **State-specific disclosures** as required by the property state

4.2. Review the generated Loan Estimate for accuracy:
- Confirm the loan amount, interest rate, and estimated monthly payment are correct
- Verify closing cost estimates align with the applicable fee schedule
- Ensure all tolerance categories (zero, 10%, unlimited) are properly classified
- Check that the estimated cash-to-close figure is reasonable

4.3. Deliver the Loan Estimate to the borrower within **three business days** of the application date. Delivery methods:
- Electronic delivery (e-consent must be on file per E-SIGN Act)
- First-class mail (add three calendar days for mailbox rule)
- In-person delivery with signed acknowledgment

4.4. Record the disclosure delivery date and method in the LOS compliance tracking module. This date is critical for TRID tolerance monitoring.

### Step 5: Assign to Loan Processor

5.1. Based on workload balancing and loan complexity, assign the file to an available loan processor. Assignment criteria include:
- Processor capacity (target: 25-35 active files per processor)
- Loan program expertise (FHA, VA, and USDA loans may require specialized processors)
- Branch or region alignment
- Priority flags (rate-lock expiration, contract deadlines)

5.2. Generate the processor assignment notification in the LOS, which will:
- Send an email notification to the assigned processor
- Add the file to the processor's active pipeline queue
- Create an initial task checklist based on the loan program
- Set milestone due dates based on the target closing date

5.3. Transfer any borrower communications or notes from the origination phase to the processor's notes section.

5.4. Update the loan status in the LOS from "Application Received" to "In Processing."

## 4. Quality Checks

| Check | Criteria | Action if Failed |
|-------|----------|-----------------|
| TRID trigger validation | All six application elements present | Mark as pre-application; do not start TRID clock |
| Data entry accuracy | LOS validation check passes with zero errors | Correct all flagged items before generating disclosures |
| LE delivery timing | Delivered within 3 business days of application | Escalate immediately to compliance; document reason for delay |
| LE accuracy | Loan terms and closing costs match current pricing | Regenerate LE with corrected figures; restart tolerance clock if needed |
| Duplicate check | No existing loan file for same borrower/property combination | Merge or close duplicate; investigate potential fraud |
| NMLS verification | Originating LO has active NMLS license in the property state | Stop processing; reassign to licensed LO |

## 5. Timing Requirements

| Milestone | Deadline | Regulatory Basis |
|-----------|----------|-----------------|
| Loan Estimate delivery | 3 business days from application | 12 CFR 1026.19(e)(1)(iii) |
| Borrower Intent to Proceed | 10 business days from LE delivery (or application expires) | Company policy; TRID best practice |
| Processor assignment | 1 business day from application | Company SLA |
| Initial document request | 1 business day from processor assignment | Company SLA |

## 6. Common Pitfalls

1. **Starting the TRID clock prematurely.** If the borrower has not provided all six trigger elements, the Loan Estimate clock should not start. However, once all six are received, the clock starts immediately even if other information is missing.

2. **Incorrect tolerance classification on the Loan Estimate.** Third-party fees where the lender selects the provider are in the zero-tolerance bucket. Misclassifying these as 10% tolerance fees can result in TRID tolerance violations at closing.

3. **Failing to obtain e-consent before electronic delivery.** The borrower must affirmatively consent to electronic delivery under the E-SIGN Act before the Loan Estimate can be delivered electronically. Without e-consent, use mail delivery and add three calendar days.

4. **Overlooking state-specific disclosure requirements.** Many states require additional disclosures at application (e.g., California MLDS, Texas Section 50(a)(6) notices). Failure to deliver state disclosures can delay closing or create compliance risk.

5. **Not verifying the purchase contract matches the application.** Property address, purchase price, seller concessions, and closing date must be consistent between the application and the purchase contract. Discrepancies must be resolved before generating the LE.

## 7. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 3.0 | 2025-05-20 | R. Caruso | Updated for 2025 URLA form changes; added e-consent verification |
| 2.2 | 2024-09-01 | R. Caruso | Revised processor assignment criteria; added workload targets |
| 2.0 | 2024-01-15 | Operations Standards Committee | Major revision for TRID 2.0 alignment |
| 1.0 | 2022-03-01 | Operations Standards Committee | Initial release |
