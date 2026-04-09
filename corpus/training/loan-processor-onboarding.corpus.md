---
corpus_id: "CRP-TRN-MTG-001"
title: "Loan Processor Onboarding Guide"
slug: "loan-processor-onboarding"
doc_type: "training"
domain: "Mortgage Lending"
subdomain: "Operations"
tags:
  - training
  - onboarding
  - loan-processor
  - mortgage-process
  - roles
  - systems
applies_to:
  process_ids:
    - "PRC-MTG-ORIG-001"
    - "PRC-MTG-INCV-001"
    - "PRC-MTG-APPR-001"
  task_types:
    - origination
    - verification
    - appraisal
    - processing
    - training
  task_name_patterns:
    - "*"
  goal_types:
    - training
    - onboarding
    - reference
  roles:
    - loan_processor
    - loan_officer
    - underwriter
    - trainee
version: "1.0"
status: "current"
effective_date: "2026-01-01"
review_date: "2026-07-01"
supersedes: null
superseded_by: null
author: "MDA Demo"
last_modified: "2026-04-09"
last_modified_by: "MDA Demo"
source: "internal"
source_ref: null
related_corpus_ids:
  - "CRP-GLO-MTG-001"
  - "CRP-SYS-MTG-001"
  - "CRP-SYS-MTG-002"
  - "CRP-SYS-MTG-003"
  - "CRP-POL-MTG-010"
regulation_refs:
  - "CRP-REG-MTG-001"
  - "CRP-REG-MTG-002"
  - "CRP-REG-MTG-003"
policy_refs:
  - "CRP-POL-MTG-010"
---

# Loan Processor Onboarding Guide

## Welcome

This guide provides new loan processors with a comprehensive overview of the mortgage lending process, the roles involved, the systems you will use daily, and the compliance fundamentals that govern every transaction. As a loan processor, you are the operational backbone of the lending team -- responsible for assembling complete, accurate loan files, coordinating with borrowers and third parties, and ensuring every loan progresses smoothly through the pipeline.

## The Mortgage Lending Lifecycle

### Phase 1: Application and Origination

The mortgage process begins when a borrower submits a loan application (URLA/1003). The loan officer (LO) takes the application, advises the borrower on available products, and collects initial documentation. Key activities include:

- **Application Intake**: The LO enters the application into the LOS (Loan Origination System). The system creates a loan record and assigns it a unique loan number. The six pieces of information that trigger TRID obligations are: borrower name, income, SSN, property address, estimated property value, and loan amount.
- **Initial Disclosures**: Within 3 business days of application, the Loan Estimate (LE) and other initial disclosures must be delivered to the borrower. The compliance engine in the LOS tracks this deadline. Missing it is a TRID violation.
- **Intent to Proceed**: The borrower must indicate intent to proceed within 10 business days. Until intent is received, the lender cannot charge fees other than a reasonable credit report fee.
- **Rate Lock**: The LO may lock the borrower's interest rate at application or later. The lock period (typically 30-60 days) defines the window for closing at the locked rate.

### Phase 2: Processing

This is where you spend most of your time. Processing involves gathering, organizing, and verifying all documentation needed for underwriting. Your responsibilities include:

**Document Collection**
- Request and track all required documents from the borrower: pay stubs (most recent 30 days), W-2s (2 years), tax returns (2 years), bank statements (2 months), asset statements, photo ID
- Upload all documents to DocVault with correct classification and tagging
- Track document status in the LOS using the conditions and documents screens
- Follow up with the borrower on outstanding items within 48 hours of the initial request

**Income Verification**
- Review pay stubs for consistency with application data: employer name, pay frequency, YTD earnings, deductions
- Calculate qualifying income based on loan program guidelines (base salary is straightforward; bonus, overtime, and commission income typically require a 2-year history and trending analysis)
- For self-employed borrowers, analyze business tax returns (1120-S, 1065, Schedule C) in addition to personal returns. Self-employment income requires averaging the most recent 2 years and identifying non-recurring items.
- Order Verification of Employment (VOE) or use automated employment verification services
- Perform verbal VOE within 10 business days of closing to confirm current employment

**Property and Collateral**
- Order the appraisal through the appraisal management company (AMC). The appraiser must be independent and randomly assigned (per Dodd-Frank appraisal independence requirements).
- Review the appraisal report when received: check for property condition issues, comparable sales adequacy, and ensure the appraised value supports the LTV
- Order title search and review the preliminary title commitment for liens, encumbrances, and exceptions
- Verify flood zone determination and order flood insurance if required
- Verify homeowner's insurance is in place with adequate coverage

**Credit Review**
- Pull tri-merge credit report at application (or verify the LO has pulled it)
- Review for derogatory items, open collections, judgments, and recent inquiries
- Calculate total monthly debt obligations for DTI computation
- If credit disputes exist, work with the borrower to document and resolve them
- A credit refresh may be needed if the report ages beyond 120 days before closing

### Phase 3: Underwriting

Once you have assembled the complete loan file, submit it to the underwriter. The underwriting process includes:

- **AUS Submission**: Submit the loan through Desktop Underwriter (DU) or Loan Product Advisor (LP). The AUS evaluates the borrower's credit, capacity, capital, and collateral and produces a recommendation (Approve/Eligible, Refer, etc.)
- **Manual Review**: The underwriter reviews the entire file against agency guidelines and the AUS findings. They may add conditions (items that must be satisfied before closing).
- **Conditions**: Conditions are categorized as Prior-to-Doc (PTD), Prior-to-Close (PTC), or Prior-to-Fund (PTF). As a processor, you are responsible for collecting condition documents from the borrower and clearing them with the underwriter.
- **Suspended Files**: If the underwriter suspends the file (additional information needed), treat this as urgent. Borrower communication and document collection must happen within 24 hours.

### Phase 4: Clear to Close (CTC)

When all underwriting conditions are satisfied, the underwriter issues a Clear to Close. This triggers:

- **Closing Disclosure (CD)**: Must be prepared and delivered to the borrower at least 3 business days before the scheduled closing date. Review the CD carefully against the LE for fee tolerance compliance.
- **Closing Coordination**: Work with the title company/settlement agent, borrower, and real estate agents to schedule the closing. Prepare the closing package with all required documents.
- **Final Verifications**: Complete verbal VOE (within 10 business days of closing), verify no changes to borrower's financial condition, refresh credit if needed.

### Phase 5: Closing and Post-Closing

- **Closing**: The borrower signs all loan documents at the closing table. Funds are disbursed, and the deed is recorded.
- **Post-Closing QC**: A quality control review is performed on a sample of closed loans to verify data integrity, compliance, and documentation completeness.
- **Investor Delivery**: The loan is packaged and delivered to the investor or GSE for purchase. ULDD (Uniform Loan Delivery Dataset) data is submitted electronically.

## Key Roles

| Role | Primary Responsibilities |
|------|------------------------|
| **Loan Officer (LO)** | Originate applications, advise borrowers on products, price and lock loans, maintain borrower relationship |
| **Loan Processor** | Assemble loan file, collect and verify documents, coordinate third-party services, manage pipeline, clear conditions |
| **Underwriter** | Evaluate loan risk, review documentation against guidelines, issue conditions, make credit decisions |
| **Closer** | Prepare closing documents, coordinate settlement, ensure funds disbursement, verify TRID compliance |
| **Compliance Officer** | Monitor regulatory adherence, conduct audits, update policies, manage examination responses |
| **Appraiser** | Independently determine property market value following USPAP standards |
| **Title Officer** | Search public records for title defects, issue title commitment and policy |

## Core Systems

### Loan Origination System (LOS)

The LOS is your primary work platform. Reference the LOS Integration Guide (CRP-SYS-MTG-001) for technical details. Day-to-day usage includes:

- **Loan Dashboard**: View your pipeline, sorted by milestone and age. Prioritize loans approaching SLA deadlines (color-coded yellow at 75% of SLA, red at 90%).
- **Document Checklist**: The LOS maintains a checklist of required documents by loan type. Check off items as they are received and uploaded to DocVault. Missing items appear highlighted.
- **Condition Screen**: View underwriting conditions, upload clearing documents, and request underwriter review. Conditions have three statuses: Open, Submitted, Cleared.
- **Timeline/Audit Trail**: Every action on a loan is logged. Use the timeline to track what has happened and when. This is essential for TRID timing compliance.
- **Alerts and Tasks**: The system generates automated tasks for time-sensitive items (LE delivery deadline, CD waiting period, rate lock expiration). Never ignore a system alert.

### DocVault (Document Management)

Reference the DocVault Integration Guide (CRP-SYS-MTG-002). Key processor activities:

- **Upload**: Drag and drop documents or use bulk upload. Always select the correct document type and associate with the correct borrower.
- **OCR Extraction**: DocVault automatically extracts data from common forms (W-2, pay stubs, bank statements). Review extracted data for accuracy before relying on it.
- **Search**: Use full-text search to find specific documents across the loan file. Filter by document type, borrower, or date.

### Event Bus

Reference the Event Bus Integration Guide (CRP-SYS-MTG-003). As a processor, you do not interact with the event bus directly, but understanding it helps:

- When you update a loan status in the LOS, events are published automatically that trigger downstream systems (notifications to the borrower portal, compliance tracking, analytics).
- When documents are uploaded to DocVault, extraction events trigger automated data verification workflows.

## Compliance Essentials

### TRID Timing Cheat Sheet

| Deadline | Rule | Consequence of Missing |
|----------|------|----------------------|
| LE within 3 business days of application | TILA/Reg Z | Regulatory violation, potential enforcement action |
| Borrower intent to proceed within 10 business days | TRID | Cannot charge fees beyond credit report fee |
| CD at least 3 business days before closing | TILA/Reg Z | Must delay closing |
| Fee tolerance at closing (LE vs CD) | TRID | Must refund excess within 60 days |
| Verbal VOE within 10 business days of closing | Agency guideline | Loan may not be eligible for delivery |

### Fair Lending Reminders

- Treat all borrowers equally regardless of race, color, religion, national origin, sex, marital status, or age
- Apply the same documentation requirements consistently. Do not request additional documents from certain borrowers that are not requested from others in similar situations
- If a borrower discloses public assistance income, evaluate it the same way you evaluate employment income
- Never discourage an applicant from applying based on any prohibited factor

### Document Retention

All documents must be retained per the Document Retention Policy (CRP-POL-MTG-010). In practice:
- Never delete documents from DocVault
- If a corrected version is received, upload it as a new version (DocVault preserves all versions automatically)
- Closed and denied loan files are retained for a minimum of 7 years

## Common Processor Mistakes to Avoid

1. **Missing TRID Deadlines**: Always check the LE delivery date immediately upon receiving a new file. This is the most common compliance violation.
2. **Incorrect Income Calculation**: Averaging variable income (overtime, bonus, commission) requires exactly 2 years of history. Do not use 1 year. If the income is declining year-over-year, use the most recent year only.
3. **Stale Credit Reports**: Credit reports expire after 120 days. Track expiration dates and order refreshes proactively.
4. **Incomplete Condition Documentation**: When submitting condition documents to the underwriter, include a cover memo explaining what is being submitted and which conditions it satisfies.
5. **Forgetting Verbal VOE**: This must be completed within 10 business days of closing. Set a reminder in the LOS when the closing date is scheduled.
6. **Fee Tolerance Errors**: When preparing the CD, compare every fee to the original LE. If any zero-tolerance fee has increased, you need a valid changed circumstance documented.
7. **Missing Signatures**: Verify all application pages are signed and dated. The redesigned URLA has multiple signature lines; each must be completed.
8. **Document Misclassification**: When uploading to DocVault, use the correct document type. Misclassified documents create confusion during underwriting and post-closing QC.

## Your First Week Checklist

- [ ] Complete LOS system training (online module, approximately 4 hours)
- [ ] Complete DocVault system training (online module, approximately 2 hours)
- [ ] Review the Mortgage Lending Glossary (CRP-GLO-MTG-001)
- [ ] Read TILA/Regulation Z Summary (CRP-REG-MTG-002) -- focus on TRID timing
- [ ] Read ECOA/Regulation B Summary (CRP-REG-MTG-003) -- focus on fair lending basics
- [ ] Read FCRA Summary (CRP-REG-MTG-001) -- focus on permissible purpose and adverse action
- [ ] Review Document Retention Policy (CRP-POL-MTG-010)
- [ ] Shadow an experienced processor for a minimum of 3 loan files
- [ ] Process your first loan file under supervision (assigned by your manager)
- [ ] Complete compliance awareness training and attestation
