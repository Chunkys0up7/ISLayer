---
corpus_id: "CRP-SYS-MTG-002"
title: "DocVault Integration Guide"
slug: "docvault-integration-guide"
doc_type: "system"
domain: "Mortgage Lending"
subdomain: "Document Management"
tags:
  - system
  - integration
  - document-management
  - OCR
  - API
  - REST
applies_to:
  process_ids:
    - "PRC-MTG-INCV-001"
    - "PRC-MTG-APPR-001"
  task_types:
    - verification
    - appraisal
    - document_management
    - processing
  task_name_patterns:
    - "*_document_*"
    - "*_upload_*"
    - "*_retrieve_*"
    - "*_verify_*"
  goal_types:
    - integration
    - document_storage
    - data_extraction
  roles:
    - loan_processor
    - underwriter
    - appraiser
    - compliance_officer
    - system_administrator
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
  - "CRP-SYS-MTG-001"
  - "CRP-SYS-MTG-003"
  - "CRP-POL-MTG-010"
regulation_refs: []
policy_refs:
  - "CRP-POL-MTG-010"
---

# DocVault Integration Guide

## System Overview

DocVault is the enterprise document management system (DMS) used to store, organize, retrieve, and process all documents associated with mortgage loan files. It provides secure cloud-based storage with integrated OCR/data extraction, full-text search, version control, and retention policy enforcement.

### Core Capabilities

- **Document Storage**: Encrypted at-rest storage (AES-256) with automatic replication across availability zones. Supports PDF, TIFF, JPEG, PNG, and structured data formats (XML, JSON).
- **OCR and Data Extraction**: Automated text extraction from scanned documents with field-level data recognition for common mortgage forms (W-2, pay stubs, bank statements, tax returns, appraisal reports).
- **Document Classification**: ML-based automatic classification of uploaded documents into standardized document types (over 120 mortgage document categories).
- **Search**: Full-text search across all document content with metadata filtering by loan, borrower, document type, date range, and status.
- **Version Control**: Immutable document versions with full audit trail. Documents cannot be deleted, only superseded. Supports redaction with original preserved in compliance vault.
- **Retention Management**: Automated retention policy enforcement with configurable rules by document type and regulatory requirement.
- **Stacking Order**: Virtual loan file organization following investor stacking order requirements.

### Base URL

```
Production:  https://docvault.lendingplatform.internal/api/v1
Staging:     https://docvault-staging.lendingplatform.internal/api/v1
```

## Endpoints

| Method | Endpoint | Description | Auth Scope |
|--------|----------|-------------|------------|
| `POST` | `/documents` | Upload a new document (multipart/form-data) | `documents:write` |
| `GET` | `/documents/{documentId}` | Retrieve document metadata | `documents:read` |
| `GET` | `/documents/{documentId}/content` | Download document content (binary) | `documents:read` |
| `GET` | `/documents/{documentId}/thumbnail` | Get document thumbnail preview | `documents:read` |
| `GET` | `/documents/{documentId}/versions` | List all versions of a document | `documents:read` |
| `POST` | `/documents/{documentId}/versions` | Upload a new version of an existing document | `documents:write` |
| `PATCH` | `/documents/{documentId}/metadata` | Update document metadata (type, tags, status) | `documents:write` |
| `GET` | `/documents/{documentId}/extraction` | Get OCR/extraction results | `extraction:read` |
| `POST` | `/documents/{documentId}/extraction/reprocess` | Re-run OCR/extraction with updated config | `extraction:write` |
| `GET` | `/loans/{loanId}/documents` | List all documents for a loan | `documents:read` |
| `GET` | `/loans/{loanId}/stacking-order` | Get documents in investor stacking order | `documents:read` |
| `POST` | `/search` | Full-text search across documents | `documents:read` |
| `GET` | `/document-types` | List available document type classifications | `documents:read` |
| `POST` | `/batches` | Upload multiple documents in a batch | `documents:write` |
| `GET` | `/batches/{batchId}` | Check batch upload status | `documents:read` |

## Authentication

DocVault uses the same OAuth 2.0 infrastructure as the LOS. Service accounts authenticate via client credentials grant.

### Scopes

| Scope | Description |
|-------|-------------|
| `documents:read` | Read document metadata and content |
| `documents:write` | Upload documents and update metadata |
| `extraction:read` | Read OCR/extraction results |
| `extraction:write` | Trigger re-extraction |

## Data Formats

### Document Upload Request

```
POST /documents
Content-Type: multipart/form-data

Fields:
  file: (binary file content)
  loanId: "LN-2026-00145892"
  borrowerId: "BRW-78923" (optional)
  documentType: "W2"
  documentYear: "2025"
  description: "2025 W-2 from Acme Corporation"
  sourceSystem: "borrower_portal"
  tags: ["income", "verification", "2025"]
```

### Document Metadata Response

```json
{
  "documentId": "DOC-2026-A7B3C9D1",
  "loanId": "LN-2026-00145892",
  "borrowerId": "BRW-78923",
  "documentType": "W2",
  "documentTypeLabel": "W-2 Wage and Tax Statement",
  "documentYear": "2025",
  "description": "2025 W-2 from Acme Corporation",
  "fileName": "w2_2025_acme.pdf",
  "fileSize": 245760,
  "mimeType": "application/pdf",
  "pageCount": 2,
  "uploadedAt": "2026-03-20T09:15:00Z",
  "uploadedBy": "SVC-borrower-portal",
  "status": "CLASSIFIED",
  "classificationConfidence": 0.97,
  "extractionStatus": "COMPLETED",
  "retentionPolicy": "7_YEAR_LENDING",
  "retentionExpiry": "2033-03-20",
  "version": 1,
  "tags": ["income", "verification", "2025"],
  "checksum": "sha256:a1b2c3d4e5f6..."
}
```

### OCR Extraction Result (W-2 Example)

```json
{
  "documentId": "DOC-2026-A7B3C9D1",
  "extractionId": "EXT-9F8E7D6C",
  "documentType": "W2",
  "extractionStatus": "COMPLETED",
  "confidence": 0.94,
  "processedAt": "2026-03-20T09:15:45Z",
  "fields": {
    "employerName": { "value": "Acme Corporation", "confidence": 0.99 },
    "employerEIN": { "value": "36-1234567", "confidence": 0.97 },
    "employeeName": { "value": "Jane Smith", "confidence": 0.98 },
    "employeeSSN": { "value": "***-**-6789", "confidence": 0.96 },
    "wagesTipsComp": { "value": 130000.00, "confidence": 0.95, "box": "1" },
    "federalTaxWithheld": { "value": 26000.00, "confidence": 0.94, "box": "2" },
    "socialSecurityWages": { "value": 130000.00, "confidence": 0.93, "box": "3" },
    "socialSecurityTax": { "value": 8060.00, "confidence": 0.95, "box": "4" },
    "medicareWages": { "value": 130000.00, "confidence": 0.94, "box": "5" },
    "medicareTax": { "value": 1885.00, "confidence": 0.96, "box": "6" },
    "taxYear": { "value": "2025", "confidence": 0.99 }
  },
  "rawText": "...",
  "boundingBoxes": { ... }
}
```

### Supported Document Types (Common Mortgage Types)

| Code | Label | Category | OCR Supported |
|------|-------|----------|--------------|
| `W2` | W-2 Wage and Tax Statement | Income | Yes |
| `PAYSTUB` | Pay Stub | Income | Yes |
| `TAX_RETURN_1040` | IRS Form 1040 | Income | Yes |
| `TAX_RETURN_1120S` | IRS Form 1120-S (S-Corp) | Income | Yes |
| `BANK_STATEMENT` | Bank Statement | Assets | Yes |
| `INVESTMENT_STATEMENT` | Investment/Brokerage Statement | Assets | Yes |
| `VOE` | Verification of Employment | Income | Yes |
| `VOD` | Verification of Deposit | Assets | Yes |
| `APPRAISAL_REPORT` | Appraisal Report (1004/1073) | Property | Yes |
| `TITLE_COMMITMENT` | Title Commitment | Closing | Partial |
| `HAZARD_INSURANCE` | Homeowner's Insurance Policy | Closing | Partial |
| `PURCHASE_CONTRACT` | Purchase Agreement/Contract | Closing | Partial |
| `DRIVERS_LICENSE` | Driver's License / Photo ID | Identity | Yes |
| `CREDIT_REPORT` | Tri-Merge Credit Report | Credit | Yes |
| `CLOSING_DISCLOSURE` | Closing Disclosure (CD) | Compliance | Yes |
| `LOAN_ESTIMATE` | Loan Estimate (LE) | Compliance | Yes |

## Event Topics

DocVault publishes events to the event bus when documents are processed.

| Event Topic | Trigger | Key Payload Fields |
|------------|---------|-------------------|
| `docvault.document.uploaded` | New document uploaded | documentId, loanId, documentType |
| `docvault.document.classified` | ML classification completed | documentId, documentType, confidence |
| `docvault.extraction.completed` | OCR/extraction finished | documentId, extractionId, fields |
| `docvault.extraction.failed` | Extraction error | documentId, errorCode, errorMessage |
| `docvault.document.version.created` | New version uploaded | documentId, version, previousVersion |
| `docvault.batch.completed` | Batch upload finished | batchId, documentCount, successCount |
