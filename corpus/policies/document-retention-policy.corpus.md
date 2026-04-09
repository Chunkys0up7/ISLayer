---
corpus_id: "CRP-POL-MTG-010"
title: "General Document Retention Policy"
slug: "document-retention-policy"
doc_type: "policy"
domain: "Mortgage Lending"
subdomain: "Compliance"
tags:
  - policy
  - retention
  - compliance
  - document-management
  - records
applies_to:
  process_ids:
    - "PRC-MTG-ORIG-001"
    - "PRC-MTG-INCV-001"
    - "PRC-MTG-APPR-001"
  task_types:
    - origination
    - verification
    - appraisal
    - closing
    - post_closing
    - document_management
  task_name_patterns:
    - "*_document_*"
    - "*_record_*"
    - "*_retention_*"
  goal_types:
    - compliance
    - risk_management
    - audit
  roles:
    - loan_processor
    - underwriter
    - closer
    - compliance_officer
    - records_manager
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
  - "CRP-SYS-MTG-002"
  - "CRP-GLO-MTG-001"
regulation_refs:
  - "CRP-REG-MTG-001"
  - "CRP-REG-MTG-002"
  - "CRP-REG-MTG-003"
policy_refs: []
---

# General Document Retention Policy

## Purpose

This policy establishes the minimum retention requirements for all documents, records, and data associated with mortgage lending operations. It ensures compliance with federal and state regulatory requirements, supports audit and examination readiness, and provides clear guidance for document lifecycle management.

## Scope

This policy applies to all mortgage lending documents regardless of format (paper, electronic, imaged) across the full loan lifecycle: application, processing, underwriting, closing, post-closing, and servicing. It covers all loan types originated or acquired by the organization, including conventional, FHA, VA, and USDA loans.

## Regulatory Basis

Retention periods are driven by the most restrictive applicable requirement among the following:

- **TILA / Regulation Z (12 CFR 1026)**: Requires retention of evidence of compliance with disclosure requirements for 2 years after the date disclosures are required to be made or action is required to be taken.
- **ECOA / Regulation B (12 CFR 1002)**: Requires retention of applications and related records for 25 months (original creditor) after notification of action taken. For HMDA reporters, retention is extended to 36 months.
- **FCRA / Regulation V**: Requires records supporting permissible purpose and adverse action notices.
- **RESPA / Regulation X (12 CFR 1024)**: Requires retention of servicing records for the life of the loan plus a reasonable period.
- **BSA/AML**: Requires retention of CTRs and SARs for 5 years from the date of filing.
- **IRS Requirements**: W-9, 1099, and related tax documents must be retained for at least 4 years.
- **State Requirements**: Various state laws may impose longer retention periods. The most restrictive requirement applies.

## Retention Schedule

### Minimum Retention Periods by Document Category

| Category | Document Types | Minimum Retention | Trigger Event | Regulatory Driver |
|----------|---------------|-------------------|---------------|-------------------|
| **Loan Application** | URLA (1003), supplement forms, initial disclosures | 7 years | Loan closing or denial date | ECOA, Company Policy |
| **Credit Documents** | Credit reports, credit supplements, credit explanations | 7 years | Loan closing or denial date | FCRA, ECOA |
| **Income Documents** | W-2s, pay stubs, tax returns, VOE, bank statements | 7 years | Loan closing date | Company Policy |
| **Property Documents** | Appraisal reports, title documents, survey, insurance | 7 years | Loan closing date | USPAP, Company Policy |
| **Disclosures** | Loan Estimate, Closing Disclosure, TILA disclosures | 7 years | Date of disclosure | TILA, TRID |
| **Underwriting** | AUS findings, underwriting decision, conditions | 7 years | Loan closing or denial date | Company Policy |
| **Closing Documents** | Note, deed of trust, HUD-1/CD, closing instructions | Life of loan + 7 years | Loan payoff or charge-off | RESPA, State Law |
| **Adverse Action** | Denial notices, counter-offer notices, withdrawal docs | 7 years | Date of notice | ECOA, FCRA |
| **Compliance** | HMDA LAR data, CRA records, fair lending analysis | 7 years | Calendar year of origination | HMDA, CRA |
| **BSA/AML** | CTRs, SARs, CIP records, OFAC screening results | 5 years minimum | Date of filing or record | BSA |
| **Correspondence** | Borrower communications, internal memos, emails | 7 years | Date of communication | Company Policy |
| **Quality Control** | QC review reports, findings, remediation records | 7 years | Date of QC review | GSE Requirements |

### Format and Storage Requirements

| Requirement | Standard |
|-------------|----------|
| **Electronic Storage** | All documents must be stored in DocVault (CRP-SYS-MTG-002) with full audit trail |
| **Image Quality** | Minimum 200 DPI for scanned documents; 300 DPI preferred for documents requiring OCR |
| **File Formats** | PDF/A for long-term archival; original format preserved alongside archived copy |
| **Encryption** | AES-256 encryption at rest; TLS 1.2+ in transit |
| **Access Controls** | Role-based access; minimum two authorized personnel for destruction approval |
| **Backup** | Daily incremental, weekly full backup; geographically separated disaster recovery |
| **Integrity** | SHA-256 checksums verified at storage and retrieval; tamper-evident logging |

## Document Destruction

### Destruction Rules

1. **No Early Destruction**: Documents must not be destroyed before the applicable retention period expires, regardless of the format or storage cost.
2. **Litigation Hold Override**: Any document subject to a litigation hold, regulatory examination, or government investigation must be retained indefinitely until the hold is released by Legal, regardless of the standard retention period.
3. **Destruction Authorization**: Document destruction requires written authorization from both the Records Manager and the Compliance Officer. Batch destruction requests must be reviewed for litigation holds before approval.
4. **Destruction Method**: Paper documents must be cross-cut shredded. Electronic records must be permanently deleted using NIST 800-88 compliant methods. Deletion must be verified and logged.
5. **Destruction Log**: A destruction log must be maintained recording the document identifier, type, loan number, retention period, destruction date, destruction method, and authorizing personnel. The destruction log itself must be retained for 10 years.
6. **Exceptions**: Documents involved in active disputes, complaints, or regulatory matters must not be destroyed until the matter is fully resolved and any applicable appeal period has expired.

### Automated Retention in DocVault

DocVault enforces retention policies automatically:
- Documents are tagged with a retention policy code at upload time based on document type
- The system prevents deletion of documents within their retention period
- Automated alerts are generated 90 days before retention expiry for review
- Expired documents are flagged for destruction review, not automatically deleted
- Destruction requires manual approval workflow completion before documents are purged

## Roles and Responsibilities

| Role | Responsibility |
|------|---------------|
| **Records Manager** | Oversees retention policy implementation, conducts annual reviews, authorizes destruction |
| **Compliance Officer** | Reviews regulatory changes, approves retention schedule updates, authorizes destruction |
| **Loan Processors** | Ensure all required documents are captured in DocVault during processing |
| **IT/Systems** | Maintain DocVault infrastructure, backup integrity, and disaster recovery readiness |
| **All Staff** | Follow retention procedures, report potential retention issues, comply with litigation holds |

## Audit and Monitoring

- Quarterly audits of a random sample of closed and denied loan files to verify retention compliance
- Annual review of the retention schedule against current regulatory requirements
- Monthly monitoring reports on DocVault storage, expiring documents, and destruction queue
- Immediate reporting of any inadvertent document destruction to Compliance and Legal
