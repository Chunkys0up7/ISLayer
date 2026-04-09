---
corpus_id: "CRP-PRC-MTG-006"
title: "Loan File Packaging Procedure"
slug: "loan-file-packaging"
doc_type: "procedure"
domain: "Mortgage Lending"
subdomain: "Loan Origination"
tags:
  - "file-packaging"
  - "stacking-order"
  - "loan-submission"
  - "quality-check"
  - "document-indexing"
applies_to:
  process_ids:
    - "Process_LoanOrigination"
  task_types:
    - "userTask"
    - "manualTask"
  task_name_patterns:
    - "package.*loan"
    - "assemble.*file"
    - "stack.*order"
    - "submit.*file"
    - "prepare.*submission"
  goal_types:
    - "data_production"
    - "state_transition"
  roles:
    - "loan_processor"
    - "quality_control_analyst"
version: "1.3"
status: "current"
effective_date: "2025-03-01"
review_date: "2026-03-01"
supersedes: null
superseded_by: null
author: "Processing Operations"
last_modified: "2025-02-20"
last_modified_by: "K. Washington"
source: "internal"
source_ref: "SOP-PKG-2025-001"
related_corpus_ids:
  - "CRP-PRC-MTG-005"
  - "CRP-PRC-MTG-007"
  - "CRP-RUL-MTG-002"
policy_refs:
  - "POL-DOC-001"
  - "POL-QC-001"
---

# Loan File Packaging Procedure

## 1. Scope

This procedure governs the assembly, organization, and quality verification of the complete loan file prior to submission to underwriting. Proper file packaging ensures that the underwriter receives a complete, well-organized file that can be decisioned efficiently, reducing turn times and minimizing conditions.

## 2. Prerequisites

| # | Prerequisite | Source |
|---|---|---|
| 1 | All required documents received per completeness checklist (CRP-RUL-MTG-002) | Document tracking |
| 2 | Credit report on file and within 120-day validity | CRP-PRC-MTG-003 |
| 3 | Income verified and documented | Income verification procedures |
| 4 | DTI ratios calculated | CRP-PRC-MTG-004 |
| 5 | Identity verification complete | CRP-PRC-MTG-002 |
| 6 | AUS findings run (DU or LP) | LOS |

## 3. Procedure Steps

### Step 1: Assemble Documents Per Stacking Order

1.1. Organize the loan file documents according to the company standard stacking order. The stacking order ensures underwriters can locate documents quickly and consistently across all files:

**Section 1: Application and Disclosures**
1. Uniform Residential Loan Application (URLA / 1003) - most recent version
2. Loan Estimate (initial and any revised LEs)
3. Intent to Proceed acknowledgment
4. Closing Disclosure (if applicable at this stage)
5. All required disclosures and borrower acknowledgments
6. State-specific disclosures

**Section 2: AUS Findings**
7. DU Findings report or LP Feedback Certificate
8. AUS conditions list

**Section 3: Credit**
9. Tri-merge credit report
10. Credit explanation letters (for derogatory items, if applicable)
11. Rapid rescore documentation (if applicable)

**Section 4: Income and Employment**
12. Pay stubs (most recent 30 days)
13. W-2 forms (most recent 2 years)
14. Federal tax returns with all schedules (most recent 2 years, if required)
15. IRS transcripts (W-2 transcripts, 1040 transcripts)
16. Written VOE (Form 1005) or The Work Number verification
17. Verbal VOE documentation
18. Self-employment documentation (if applicable): business returns, P&L, CPA letter
19. Other income documentation (Social Security award letter, pension, etc.)
20. Income Calculation Worksheet

**Section 5: Assets**
21. Bank statements (most recent 2-3 months, all pages)
22. Retirement account statements
23. Gift letter and donor documentation (if applicable)
24. Earnest money deposit verification
25. Source of funds documentation for large deposits

**Section 6: Property**
26. Purchase contract (fully executed with all addenda)
27. Appraisal report
28. Title commitment or preliminary title report
29. Survey (if required)
30. Flood certification
31. Homeowner's insurance binder or declaration page
32. HOA documentation (budget, questionnaire, dues confirmation)
33. Condo/PUD certification (if applicable)

**Section 7: Identity and Compliance**
34. Government-issued photo ID (copy)
35. SSN verification documentation
36. OFAC screening results
37. HMDA data collection form
38. Anti-steering disclosure
39. Borrower authorization forms

**Section 8: Processor Workup**
40. Processor submission notes / transmittal summary
41. DTI calculation worksheet
42. Compensating factors narrative (if applicable)
43. Conditions tracking sheet
44. Communication log highlights

### Step 2: Verify Document Completeness

2.1. Using the program-specific completeness checklist (CRP-RUL-MTG-002), verify that every required document is present in the file.

2.2. For each document, confirm:
- The correct version is in the file (most recent if multiple versions exist)
- All pages are present (bank statements commonly have missing pages)
- The document is legible (no cut-off text, blurred images, or dark copies)
- Dates are within acceptable ranges (paystubs within 30 days, credit report within 120 days)
- Borrower names are consistent across all documents (or discrepancies are documented)

2.3. If any documents are missing or deficient, return to CRP-PRC-MTG-005 (Document Request) to obtain the items before proceeding. Do not submit an incomplete file to underwriting.

### Step 3: Index Documents in the LOS

3.1. Ensure all documents are properly indexed in the LOS document management module. Each document must be tagged with:
- Document type (from the LOS document type library)
- Document category (Application, Income, Asset, Property, Compliance)
- Borrower association (Primary, Co-Borrower, Joint)
- Effective date
- Number of pages

3.2. Verify that no documents are misfiled under incorrect categories. Common misfiling errors:
- W-2 forms filed under "Tax Returns" instead of "W-2"
- Gift letters filed under "Assets" without the corresponding donor bank statements
- Amended applications filed in the wrong version order

3.3. Remove any duplicate documents from the file. If multiple versions of the same document exist (e.g., updated pay stubs), keep only the most recent version in the active file and archive prior versions.

### Step 4: Add Processor Notes and Transmittal Summary

4.1. Prepare the processor transmittal summary, which serves as the underwriter's roadmap to the file. The summary must include:

**Loan Summary:**
- Loan number, borrower name(s), and property address
- Loan program, amount, rate (if locked), and term
- Loan purpose and occupancy type
- LTV, CLTV, and DTI ratios

**Income Summary:**
- Each income source with the verified monthly amount
- Any income calculation notes or trending observations
- VOE status (written and verbal)

**Asset Summary:**
- Source of down payment and closing costs
- Verified liquid reserves after closing (in months of PITIA)
- Any large deposits explained

**Credit Summary:**
- Representative credit score and qualifying score
- Significant derogatory items and seasoning
- Credit depth assessment

**Property Summary:**
- Property type and occupancy
- Appraised value (if available at this stage)
- Title issues or property concerns

**Conditions and Notes:**
- AUS conditions from DU/LP findings
- Items that may require underwriter attention
- Compensating factors narrative (if DTI exceeds standard limits)
- Any exceptions or unusual circumstances

4.2. The transmittal summary should be thorough but concise. Target length is 1-2 pages. Avoid restating information that is obvious from the documents themselves.

### Step 5: Perform Pre-Submission Quality Check

5.1. Before submitting to underwriting, the processor (or a designated QC reviewer) must perform the following checks:

| QC Check | Description | Pass Criteria |
|----------|-------------|---------------|
| Application accuracy | LOS data matches source documents | All fields reconcile |
| Income calculation | DTI worksheet math verified | Calculations are correct |
| Credit score selection | Representative score correctly determined | Matches middle/lower score rule |
| Program eligibility | Credit score, DTI, LTV meet program minimums | Meets CRP-RUL-MTG-001 criteria |
| Document dates | All documents within validity windows | Paystubs < 30 days, credit < 120 days |
| Disclosure compliance | LE delivered within TRID timeline | Delivery date documented |
| OFAC screening | Screening current and clear | Screening on file |
| Stacking order | File organized per company standard | Matches Section 1 stacking order |
| Name consistency | Borrower name consistent or variations documented | No unexplained name discrepancies |
| Fraud indicators | No unresolved red flags | Red flag checklist completed |

5.2. Document the QC review results on the pre-submission QC checklist form. If any items fail, correct them before proceeding.

### Step 6: Submit the Loan Package

6.1. Once the file passes QC review, submit the completed package to underwriting through the LOS submission workflow.

6.2. The submission will:
- Route the file to the underwriting queue based on loan program and complexity
- Generate an underwriting submission timestamp
- Notify the assigned underwriter (or the queue manager) of the new submission
- Update the loan status from "Processing" to "Submitted to Underwriting"

6.3. Record the submission date and time in the loan file. This date is used for underwriting SLA tracking.

## 4. Quality Checks

| Check | Criteria | Action if Failed |
|-------|----------|-----------------|
| Stacking order compliance | File follows standard stacking order | Reorganize before submission |
| Completeness | All checklist items present | Obtain missing documents |
| Legibility | All documents readable | Request new copies |
| Indexing accuracy | LOS indexing matches actual documents | Correct indexing |
| Transmittal quality | Summary is complete and accurate | Revise transmittal |
| QC checklist | All pre-submission checks passed | Resolve failures |

## 5. Common Pitfalls

1. **Submitting files with missing pages.** Bank statements and tax returns are notorious for missing pages. Always verify page counts and ensure "Page X of Y" sequences are complete.

2. **Not updating the AUS findings after file changes.** If income, assets, or liabilities changed after the initial DU/LP run, re-run the AUS before submission to ensure findings are current.

3. **Illegible document copies.** Dark scans, rotated pages, and partially cut-off text create underwriting conditions and delays. Preview all documents for readability before submission.

4. **Weak transmittal summaries.** A transmittal that simply lists "see documents" provides no value. Underwriters rely on the transmittal to understand the story of the file. Include relevant context and flag items proactively.

5. **Not removing superseded documents.** Multiple versions of the same document (e.g., three different paystubs when only the most recent is needed) confuse the underwriter and waste review time.

## 6. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.3 | 2025-02-20 | K. Washington | Updated stacking order for 2025 URLA changes; added QC checklist detail |
| 1.0 | 2023-08-01 | Processing Operations | Initial release |
