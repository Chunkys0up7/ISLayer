---
corpus_id: "CRP-PRC-MTG-005"
title: "Document Request and Follow-Up Procedure"
slug: "document-request-procedure"
doc_type: "procedure"
domain: "Mortgage Lending"
subdomain: "Loan Origination"
tags:
  - "document-request"
  - "follow-up"
  - "missing-documents"
  - "borrower-communication"
  - "escalation"
  - "document-collection"
applies_to:
  process_ids:
    - "Process_LoanOrigination"
  task_types:
    - "userTask"
    - "sendTask"
  task_name_patterns:
    - "request.*doc"
    - "follow.*up.*doc"
    - "missing.*doc"
    - "send.*request"
  goal_types:
    - "notification"
    - "data_production"
  roles:
    - "loan_processor"
    - "loan_officer"
    - "document_specialist"
version: "1.5"
status: "current"
effective_date: "2025-02-01"
review_date: "2026-02-01"
supersedes: null
superseded_by: null
author: "Processing Operations"
last_modified: "2025-01-15"
last_modified_by: "K. Washington"
source: "internal"
source_ref: "SOP-DOC-2025-001"
related_corpus_ids:
  - "CRP-PRC-MTG-001"
  - "CRP-PRC-MTG-006"
  - "CRP-RUL-MTG-002"
regulation_refs:
  - "TRID 12 CFR 1026.19"
  - "ECOA Regulation B Adverse Action Timing"
policy_refs:
  - "POL-DOC-001"
  - "POL-COMM-001"
---

# Document Request and Follow-Up Procedure

## 1. Scope

This procedure governs the identification, request, tracking, and escalation of documents needed from borrowers during the mortgage loan origination process. It ensures timely collection of required documentation while maintaining a professional borrower experience and adhering to regulatory timelines.

The procedure applies from initial document request through file completion or application expiration.

## 2. Prerequisites

| # | Prerequisite | Source |
|---|---|---|
| 1 | Loan application entered in LOS with loan number assigned | CRP-PRC-MTG-001 |
| 2 | Document completeness checklist generated for the loan program | CRP-RUL-MTG-002 |
| 3 | Borrower preferred communication channel documented | Application |
| 4 | Borrower contact information verified | Application |

## 3. Procedure Steps

### Step 1: Identify Missing Documents

1.1. Generate the program-specific document completeness checklist from the LOS (see CRP-RUL-MTG-002). The checklist is auto-populated based on:
- Loan program (Conventional, FHA, VA, USDA)
- Loan purpose (purchase, rate-term refinance, cash-out refinance)
- Employment type (W-2, self-employed, retired)
- Property type (single-family, condo, multi-unit, manufactured)
- Transaction specifics (gift funds, co-signer, trust ownership)

1.2. Compare documents currently in the loan file against the checklist. Mark each item as:
- **Received:** Document on file and verified acceptable
- **Received - Needs Update:** Document on file but outdated, illegible, or incomplete
- **Missing:** Not yet received from borrower
- **Not Applicable:** Not required for this transaction (document reason)
- **Waived:** Waived by AUS findings (document DU/LP message ID)

1.3. Compile the list of missing and needs-update items for the document request.

### Step 2: Generate the Document Request Letter

2.1. Create the document request using the LOS document request template. The request must include:
- Loan number and borrower name(s)
- Date of request
- Itemized list of required documents with clear descriptions of what is needed
- Specific formatting requirements (e.g., "all pages of bank statement including blank pages")
- Acceptable submission methods (secure upload portal, email, fax, in-person)
- Due date (initial request: 7 calendar days from request date)
- Processor name and direct contact information

2.2. For each requested document, provide sufficient detail so the borrower understands exactly what is needed. Examples of clear vs. unclear requests:

| Unclear Request | Clear Request |
|----------------|---------------|
| "Bank statements" | "Most recent two consecutive monthly statements for your Chase savings account ending in 4521, including all pages" |
| "Tax returns" | "2023 and 2024 federal tax returns (IRS Form 1040) with all schedules, W-2s, and 1099s" |
| "Pay stubs" | "Most recent 30 days of consecutive pay stubs from ABC Corporation, showing year-to-date earnings" |
| "Insurance" | "Homeowner's insurance quote or binder for 123 Main St showing coverage of at least $350,000" |

2.3. Include a brief explanation of why each document is needed (e.g., "required to verify employment income" or "needed to confirm source of down payment funds").

### Step 3: Send the Document Request

3.1. Deliver the document request through the borrower's preferred communication channel:

| Channel | Method | Documentation |
|---------|--------|---------------|
| Secure Portal | Upload request to borrower portal with notification email | System-logged; preferred method |
| Email | Send via company email with encrypted attachment or secure link | Save sent email to loan file |
| Phone | Call borrower to discuss needed items; follow up with written request | Document call in notes; send written confirmation |
| Mail | Send first-class mail (add 3 days to due date for delivery) | Keep copy in file |

3.2. For the initial request, a phone call in addition to the written request is recommended to ensure the borrower understands the requirements and to answer questions.

3.3. Log the request in the LOS document tracking module with:
- Date and time sent
- Channel used
- Items requested
- Due date
- Status: "Requested"

### Step 4: Follow-Up Schedule

4.1. If documents are not received by the due date, initiate the following follow-up sequence:

| Day | Action | Channel | Escalation Level |
|-----|--------|---------|-----------------|
| Day 3 | Courtesy reminder | Email or text (if consent given) | None |
| Day 7 (initial due date) | First follow-up | Phone call + email | Notify loan officer |
| Day 10 | Second follow-up | Phone call + email | Loan officer contacts borrower directly |
| Day 14 | Urgency notice | Phone + certified letter or portal notification | Processing manager notified |
| Day 21 | Escalation warning | Phone + formal notice | File flagged for potential expiration |
| Day 30 | Final notice / expiration | Formal letter | Application expiration initiated |

4.2. Document each follow-up attempt in the LOS communication log with:
- Date and time
- Method of contact (call, email, text, letter)
- Person contacted (borrower, co-borrower, loan officer)
- Outcome (left message, spoke with borrower, document received, etc.)
- Next follow-up date

4.3. If the borrower is partially responsive (some documents received, others outstanding), update the checklist and send a revised request listing only the remaining items.

### Step 5: Handle Escalation

5.1. **Day 14 Escalation:** At the 14-day mark, the processing manager reviews the file to determine:
- Whether the outstanding documents are critical to proceeding (if not, processing may continue on other aspects)
- Whether the borrower has communicated a valid reason for the delay (medical issue, travel, employer delay)
- Whether an extension is warranted (up to 15 additional days maximum)

5.2. **Day 21 Escalation:** If documents are still outstanding at day 21:
- Send a formal notice advising the borrower that the application will expire if documents are not received within 9 calendar days
- The loan officer must make a personal contact attempt
- Document the escalation in the LOS with the processing manager's notes

5.3. **Day 30 Application Expiration:** If critical documents are not received within 30 calendar days of the initial request:
- The application is considered abandoned
- Generate an application withdrawal letter or adverse action notice as appropriate
- Update the loan status to "Withdrawn - Incomplete Documentation"
- Close the file per document retention policies
- If the borrower contacts after expiration, a new application may be required

### Step 6: Receive and Process Documents

6.1. When documents are received, immediately:
- Log receipt in the LOS with the date, source, and items received
- Update the document checklist status from "Missing" to "Received"
- Review each document for completeness and acceptability
- If a document is incomplete or illegible, contact the borrower the same day and request a replacement

6.2. Upload all received documents to the document management system with proper indexing:
- Document category (Income, Asset, Property, Identity, etc.)
- Document type (W-2, Bank Statement, Appraisal, etc.)
- Borrower association (Primary Borrower, Co-Borrower)
- Date received

6.3. If all required documents are now received, update the loan status and notify the processor that the file is ready for packaging (CRP-PRC-MTG-006).

## 4. Quality Checks

| Check | Criteria | Action if Failed |
|-------|----------|-----------------|
| Request clarity | Each item has specific description per Step 2.2 | Revise request with clearer descriptions |
| Follow-up adherence | Follow-up schedule maintained per timeline | Log missed follow-ups; escalate as needed |
| Communication log | All contacts documented in LOS | Complete missing log entries |
| Document review | Received documents reviewed within 1 business day | Prioritize review to avoid further delays |
| Expiration compliance | 30-day expiration enforced or extension documented | Process expiration or document extension rationale |

## 5. Common Pitfalls

1. **Vague document requests.** Borrowers often provide the wrong documents when requests are not specific. Always include account numbers (last 4 digits), date ranges, and page requirements.

2. **Not following up consistently.** Missing follow-up touchpoints leads to files stalling in the pipeline. Use the LOS task manager to set automatic follow-up reminders.

3. **Accepting partial documents without notifying the borrower.** When a borrower sends only page 1 of a 3-page bank statement, acknowledge receipt of what was received and immediately request the remaining pages.

4. **Not coordinating with the loan officer.** The loan officer often has the best relationship with the borrower. Involving the LO at the 7-day mark (not waiting until day 21) improves response rates.

5. **Allowing files to age beyond 30 days without action.** Aged files with incomplete documentation consume processing capacity. Enforce the 30-day expiration policy unless a documented extension is granted.

## 6. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.5 | 2025-01-15 | K. Washington | Updated follow-up timeline; added text message option with consent |
| 1.0 | 2023-06-01 | Processing Operations | Initial release |
