---
corpus_id: "CRP-SYS-IV-002"
title: "IVES (IRS Income Verification Express Service) Guide"
slug: "ives-guide"
doc_type: "system"
domain: "Mortgage Lending"
subdomain: "Income Verification"
tags:
  - "ives"
  - "irs"
  - "4506-c"
  - "tax-transcript"
  - "income-verification"
  - "system-integration"
  - "batch-processing"
  - "transcript-retrieval"
applies_to:
  process_ids:
    - "Process_IncomeVerification"
    - "Process_TranscriptRetrieval"
    - "Process_QualityControl"
  task_types:
    - "serviceTask"
    - "sendTask"
    - "receiveTask"
    - "userTask"
  task_name_patterns:
    - "order.*transcript"
    - "retrieve.*transcript"
    - "submit.*4506"
    - "ives.*request"
    - "irs.*transcript"
    - "validate.*tax.*return"
  goal_types:
    - "data_production"
    - "orchestration"
  roles:
    - "loan_processor"
    - "underwriter"
    - "ives_coordinator"
    - "quality_control_analyst"
    - "system_integrator"
version: "2.1"
status: "current"
effective_date: "2025-01-15"
review_date: "2025-07-15"
supersedes: null
superseded_by: null
author: "Technology & Operations Team"
last_modified: "2025-01-10"
last_modified_by: "K. Williams"
source: "internal"
source_ref: "SYS-IV-2025-002"
related_corpus_ids:
  - "CRP-PRC-IV-001"
  - "CRP-PRC-IV-002"
  - "CRP-PRC-IV-003"
  - "CRP-REG-IV-001"
  - "CRP-REG-IV-002"
  - "CRP-POL-IV-001"
  - "CRP-DAT-IV-001"
regulation_refs:
  - "IRS Revenue Procedure 2014-42"
  - "Fannie Mae Selling Guide B3-3.1-07"
  - "FHA 4000.1 II.A.1"
policy_refs:
  - "POL-IV-004"
  - "POL-SYS-001"
  - "POL-DATA-001"
---

# IVES (IRS Income Verification Express Service) Guide

## 1. Overview

### 1.1. What is IVES?

The Income Verification Express Service (IVES) is an IRS program that allows authorized third parties (such as mortgage lenders) to receive tax transcript data for individual and business taxpayers. IVES enables lenders to verify that the tax returns provided by borrowers match what was actually filed with the IRS.

IVES replaces the older process of mailing Form 4506 directly to the IRS and waiting weeks for a response. Through IVES, transcripts are requested electronically via an approved IVES participant (typically a third-party vendor) and returned in a standardized format.

### 1.2. Why IVES Matters

IVES is a critical fraud prevention and quality control tool:

- **Tax return validation:** Confirms that borrower-provided tax returns match IRS records
- **Agency requirement:** Both Fannie Mae and FHA require tax transcript validation for income used in qualification
- **Investor requirement:** Secondary market investors increasingly mandate IVES transcript matching as a condition of purchase
- **Fraud detection:** Fabricated or altered tax returns are identified when they fail to match IRS data

### 1.3. IVES vs. Direct IRS Request

| Feature | IVES (via vendor) | Direct IRS (Form 4506-C mailed) |
|---------|-------------------|--------------------------------|
| Turnaround time | 2-5 business days | 10-20 business days |
| Submission method | Electronic (batch) | Paper mail |
| Cost per request | $2-5 (vendor fee) + IRS fee | IRS fee only |
| Tracking | Real-time status via vendor portal | No tracking; mail-based |
| Format returned | PDF transcript via secure portal | Paper transcript via mail |
| Recommended | **Yes -- primary method** | Backup only |

## 2. Form 4506-C

### 2.1. Purpose

IRS Form 4506-C (IVES Request for Transcript of Tax Return) is the authorization form that the borrower signs to permit the lender (or its authorized agent) to request tax transcripts from the IRS. This replaced the older Form 4506-T for IVES participants.

### 2.2. Completion Requirements

The 4506-C must be completed accurately to avoid IRS rejections:

| Field | Requirement | Common Errors |
|-------|-------------|---------------|
| Line 1a-b: Taxpayer name and SSN | Must match IRS records exactly (name on most recent tax return) | Using a married name when returns were filed under maiden name |
| Line 2a-b: Spouse name and SSN | Required if requesting joint returns | Omitting spouse when returns were filed jointly |
| Line 3: Current address | Must match borrower's current address | Using a prior address |
| Line 4: Previous address | Must be provided if address changed within last 4 years | Leaving blank when address has changed |
| Line 5: Customer file number | Loan number (company-assigned) | Using incorrect or outdated loan number |
| Line 6: Transcript requested | Check "Return Transcript" for IVES | Checking wrong transcript type |
| Line 7: Tax form number | "1040" for personal, "1065" or "1120S" for business | Requesting wrong form type |
| Line 8: Year(s) requested | List each tax year (e.g., 2023, 2024) | Missing a year; requesting too many years |
| Line 9: Signature and date | Borrower must sign and date | Unsigned, undated, or signature doesn't match |

### 2.3. Signature Requirements

- The 4506-C must be signed by the taxpayer (or both taxpayers for joint returns)
- Electronic signatures (e-sign) are acceptable per IRS guidance, provided the e-sign process meets IRS requirements (identity verification, intent to sign, association of signature with the document)
- Signatures must be dated
- The 4506-C is valid for **120 days** from the date of the taxpayer's signature
- If the 4506-C expires before transcripts are received, a new form must be signed

### 2.4. Common Rejection Reasons

| Rejection Code | Meaning | Resolution |
|---------------|---------|------------|
| Name mismatch | Taxpayer name does not match IRS records | Verify correct name per most recent filed return; may need to use SSA-registered name |
| SSN mismatch | SSN does not match the name on IRS records | Verify SSN; check for transposed digits |
| Address mismatch | Address does not match IRS records for the most recent filing year | Use the address from the most recently filed return |
| Form not filed | No tax return on file for the requested year | Confirm return was filed; if filed recently, may need to wait for IRS processing |
| Invalid signature | Signature is missing, illegible, or undated | Obtain a new signed and dated 4506-C |
| Tax year not available | Requested year is too old or not yet processed | Adjust year; returns generally available 6-8 weeks after filing |

## 3. Transcript Types

### 3.1. Available Transcript Types

| Type | Content | Use in Mortgage Lending |
|------|---------|------------------------|
| **Tax Return Transcript** | Line-by-line data from the tax return as originally filed | Primary transcript for income verification |
| **Tax Account Transcript** | Filing status, taxable income, payments made, refund or balance due | Supplementary; useful for confirming filing and payment history |
| **Record of Account** | Combines Return Transcript and Account Transcript | Comprehensive; used when both data sets are needed |
| **Wage and Income Transcript** | W-2, 1099, and other information returns filed by third parties | Useful for verifying employment and income sources independently of the borrower's return |

### 3.2. Recommended Transcript Requests

| Scenario | Transcript Types to Request |
|----------|----------------------------|
| W-2 employee, standard verification | Tax Return Transcript (1040) for 2 years |
| Self-employed, Schedule C | Tax Return Transcript (1040) for 2 years |
| Self-employed, partnership | Tax Return Transcript (1040) for 2 years + Tax Return Transcript (1065) for 2 years |
| Self-employed, S-Corp | Tax Return Transcript (1040) for 2 years + Tax Return Transcript (1120S) for 2 years |
| W-2 income with discrepancies | Tax Return Transcript (1040) + Wage and Income Transcript for 2 years |
| Fraud investigation | Record of Account for all applicable years |

## 4. IVES Workflow

### 4.1. Process Flow

```
1. Borrower signs Form 4506-C
   │
2. Processor uploads 4506-C to IVES vendor portal
   │ (or submits via LOS integration)
   │
3. IVES vendor validates the form and submits to IRS
   │ (electronic batch submission)
   │
4. IRS processes the request
   │ (2-5 business days typical)
   │
5. IRS returns transcript data to IVES vendor
   │
6. IVES vendor delivers transcripts via secure portal / API
   │
7. Processor retrieves transcripts
   │
8. Processor/underwriter compares transcripts to borrower-provided returns
   │
9. Results documented in income verification file
```

### 4.2. Submission Process

**Manual Submission (Vendor Portal):**
1. Log into the IVES vendor portal (credentials managed per POL-SYS-001)
2. Create a new transcript request
3. Enter borrower information (name, SSN, address) exactly as it appears on the 4506-C
4. Upload the signed 4506-C (PDF format, minimum 200 DPI resolution)
5. Select transcript type(s) and tax year(s)
6. Submit the request
7. Record the request confirmation number in the LOS

**Automated Submission (LOS Integration):**
1. When the 4506-C is signed and stored in the DMS, the LOS can trigger an automated IVES request through the vendor API
2. The integration maps borrower data from the LOS to the vendor's request format
3. Confirmation is returned to the LOS and logged automatically
4. This method is preferred for efficiency and accuracy

### 4.3. Retrieval and Matching

**Retrieval:**
- Transcripts are delivered to the vendor portal as PDF documents
- Automated integrations may deliver transcript data as structured XML or JSON
- The processor is notified via email or LOS task when transcripts are available
- Transcripts must be downloaded and stored in the DMS within 5 business days of availability

**Matching Process:**
The processor or underwriter must compare key fields between the borrower-provided tax return and the IRS transcript:

| Field to Compare | Source: Tax Return | Source: Transcript | Tolerance |
|-----------------|-------------------|-------------------|-----------|
| Filing status | 1040 header | Transcript header | Must match exactly |
| Adjusted Gross Income (AGI) | 1040 Line 11 | Transcript AGI line | Within $500 (FHA) or $200 (internal policy) |
| Total income | 1040 Line 9 | Transcript total income | Within $500 |
| Wages, salaries | 1040 Line 1a | Transcript wages line | Within $200 |
| Business income/loss | Schedule C Line 31 | Transcript business income | Within $500 |
| Taxable income | 1040 Line 15 | Transcript taxable income | Within $200 |
| Tax liability | 1040 Line 24 | Transcript total tax | Within $200 |

**Match Results:**

| Result | Criteria | Action |
|--------|----------|--------|
| **Full Match** | All compared fields within tolerance | Document match; proceed with verification |
| **Minor Discrepancy** | 1-2 fields slightly outside tolerance | Document discrepancy; likely due to rounding or IRS adjustment; proceed with explanation |
| **Material Discrepancy** | Key fields (AGI, income) significantly outside tolerance | Investigate; request explanation from borrower; check for amended returns |
| **No Return Found** | IRS has no record for the requested year | Confirm return was filed; check filing status; may need to wait if recently filed |
| **Amended Return** | Transcript shows amended return indicators | Obtain the amended return (Form 1040-X); use amended figures for income calculation |

## 5. Turnaround Times and SLAs

### 5.1. Expected Turnaround

| Phase | Duration | Notes |
|-------|----------|-------|
| Form validation by vendor | Same day | Rejects returned within hours |
| IRS processing (standard) | 2-5 business days | During non-peak season |
| IRS processing (peak: Feb-May) | 5-10 business days | Tax filing season volume |
| IRS processing (new filings) | 6-8 weeks after filing | Returns filed within the current season |
| Vendor delivery after IRS return | Same day | Automated delivery |
| Total (standard) | **3-6 business days** | Typical end-to-end |
| Total (peak season) | **6-12 business days** | Plan accordingly |

### 5.2. Escalation for Delays

If transcripts have not been received within 10 business days:

1. Check the vendor portal for status updates or IRS rejection notices
2. If the request is pending with no status update, contact the vendor support line
3. If the IRS has not responded, the vendor may resubmit the request
4. Document all follow-up attempts in the LOS
5. If transcripts remain unavailable and closing is imminent, escalate to underwriting for alternative documentation acceptance (per POL-IV-004)

## 6. Integration Architecture

### 6.1. System Integration Pattern

The IVES workflow follows an **asynchronous request-response** pattern:

```
LOS ──(1) Submit Request──> IVES Vendor API
                               │
                          (2) Validate & Batch
                               │
                          (3) Submit to IRS
                               │
                        [Async Processing]
                               │
                          (4) IRS Response
                               │
IVES Vendor ──(5) Webhook/Poll──> LOS
                               │
LOS ──(6) Download Transcript──> DMS
```

### 6.2. API Integration Details

**Outbound Request (LOS to Vendor):**
- Protocol: HTTPS (TLS 1.2 minimum)
- Authentication: API key + OAuth 2.0 client credentials
- Format: JSON (request body) + PDF (4506-C attachment as base64)
- Timeout: 30 seconds for submission acknowledgment
- Retry: 3 retries with exponential backoff (5s, 15s, 45s)

**Inbound Response (Vendor to LOS):**
- Delivery: Webhook callback to registered endpoint, or polling at 15-minute intervals
- Format: JSON (status and metadata) + PDF (transcript document)
- Security: Webhook payload signed with HMAC-SHA256; verified by LOS

### 6.3. Data Security

- All data transmission is encrypted in transit (TLS 1.2+)
- Transcripts are encrypted at rest in the DMS (AES-256)
- Access to transcript data is restricted to authorized roles (processor, underwriter, QC)
- SSN data is masked in all logs and audit trails (last 4 digits only)
- 4506-C forms are classified as PII-Sensitive and follow data retention policies per POL-DATA-001
- Vendor access to borrower data is governed by a signed Business Associate Agreement

## 7. Troubleshooting

### 7.1. Common Issues and Resolutions

| Issue | Likely Cause | Resolution |
|-------|-------------|------------|
| Transcript shows $0 income | Return not yet processed by IRS | Wait 6-8 weeks after filing date; resubmit |
| Transcript shows different filing status | Amended return filed; spouse filed separately | Obtain both versions; use most recent |
| Multiple transcripts returned for same year | Amended return exists | Review both original and amended; use amended figures |
| Request rejected: "No record" | Return not filed, or wrong SSN/name | Verify with borrower; may need to file return |
| Vendor portal shows "Pending" for > 10 days | IRS backlog or system issue | Contact vendor support; consider resubmission |
| Transcript data truncated | IRS system limitation for complex returns | Request Record of Account for complete data |
| Business transcript not available | Business return processed separately | Submit separate request with business EIN |

### 7.2. When Transcripts Cannot Be Obtained

In rare cases where transcripts remain unavailable after exhausting all options:

1. Document all attempts and IRS responses in the file
2. Underwriter must determine if the loan can proceed without transcripts
3. For Fannie Mae: transcripts are required; if unavailable, alternative evidence per Selling Guide B3-3.1-07 may be accepted with documented justification
4. For FHA: transcripts are required per 4000.1; unavailability may delay closing
5. Post-closing transcript retrieval must be attempted within 120 days per company policy
6. If post-closing transcripts reveal material discrepancies, initiate a quality review per POL-QC-001

## 8. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.1 | 2025-01-10 | K. Williams | Updated turnaround times, added API integration details, expanded troubleshooting |
| 2.0 | 2024-05-01 | K. Williams | Major revision for Form 4506-C (replaced 4506-T references), updated vendor integration |
| 1.0 | 2022-01-10 | Technology & Operations Team | Initial release |
