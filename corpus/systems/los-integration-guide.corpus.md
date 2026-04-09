---
corpus_id: "CRP-SYS-MTG-001"
title: "LOS (Loan Origination System) Integration Guide"
slug: "los-integration-guide"
doc_type: "system"
domain: "Mortgage Lending"
subdomain: "Core Systems"
tags:
  - system
  - integration
  - LOS
  - API
  - REST
  - loan-origination
applies_to:
  process_ids:
    - "PRC-MTG-ORIG-001"
    - "PRC-MTG-INCV-001"
    - "PRC-MTG-APPR-001"
  task_types:
    - origination
    - verification
    - appraisal
    - underwriting
    - closing
    - system_integration
  task_name_patterns:
    - "*_loan_*"
    - "*_borrower_*"
    - "*_application_*"
  goal_types:
    - integration
    - data_exchange
    - automation
  roles:
    - loan_processor
    - loan_officer
    - underwriter
    - system_administrator
    - developer
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
  - "CRP-SYS-MTG-003"
  - "CRP-GLO-MTG-001"
regulation_refs:
  - "CRP-REG-MTG-002"
policy_refs:
  - "CRP-POL-MTG-010"
---

# LOS (Loan Origination System) Integration Guide

## System Overview

The Loan Origination System (LOS) is the central platform managing the entire mortgage loan lifecycle from initial application intake through closing and post-closing. It serves as the system of record for all loan data, borrower information, property details, and workflow state.

### Core Capabilities

- **Application Management**: Intake, storage, and management of URLA (1003) applications with full MISMO 3.x data model support
- **Workflow Orchestration**: Configurable milestone-based workflows with automated task assignment, SLA tracking, and escalation rules
- **Compliance Engine**: Built-in TRID timing calculations, fee tolerance tracking, disclosure generation, and regulatory audit trail
- **Document Tracking**: Integration with document management systems for tracking required documents, conditions, and stacking order
- **AUS Integration**: Direct submission to Desktop Underwriter (DU) and Loan Product Advisor (LP) with findings parsing
- **Investor Delivery**: Loan packaging, ULDD generation, and submission to GSE and investor delivery systems
- **Reporting**: Real-time pipeline dashboards, pull-through analytics, turn-time reporting, and compliance monitoring

### Base URL

```
Production:  https://los.lendingplatform.internal/api/v2
Staging:     https://los-staging.lendingplatform.internal/api/v2
```

## Endpoints

All endpoints accept and return JSON unless otherwise noted. Dates use ISO 8601 format. Amounts are in USD cents (integer) to avoid floating-point issues.

| Method | Endpoint | Description | Auth Scope |
|--------|----------|-------------|------------|
| `POST` | `/loans` | Create a new loan record from application data | `loans:write` |
| `GET` | `/loans/{loanId}` | Retrieve full loan record including current status | `loans:read` |
| `PATCH` | `/loans/{loanId}` | Update loan fields (partial update) | `loans:write` |
| `GET` | `/loans/{loanId}/status` | Get current loan status and milestone | `loans:read` |
| `POST` | `/loans/{loanId}/status` | Advance or update loan status/milestone | `loans:status` |
| `GET` | `/loans/{loanId}/borrowers` | List all borrowers on the loan | `loans:read` |
| `POST` | `/loans/{loanId}/borrowers` | Add a borrower to the loan | `loans:write` |
| `GET` | `/loans/{loanId}/borrowers/{borrowerId}` | Get borrower details | `loans:read` |
| `PATCH` | `/loans/{loanId}/borrowers/{borrowerId}` | Update borrower information | `loans:write` |
| `GET` | `/loans/{loanId}/property` | Get subject property details | `loans:read` |
| `PATCH` | `/loans/{loanId}/property` | Update property information | `loans:write` |
| `GET` | `/loans/{loanId}/documents` | List tracked documents and conditions | `docs:read` |
| `POST` | `/loans/{loanId}/documents` | Track a new document against the loan | `docs:write` |
| `GET` | `/loans/{loanId}/conditions` | List underwriting conditions | `loans:read` |
| `POST` | `/loans/{loanId}/conditions` | Add an underwriting condition | `loans:write` |
| `PATCH` | `/loans/{loanId}/conditions/{conditionId}` | Update condition status (cleared, waived) | `loans:write` |
| `POST` | `/loans/{loanId}/aus/submit` | Submit to AUS (DU or LP) | `aus:submit` |
| `GET` | `/loans/{loanId}/aus/findings` | Retrieve AUS findings and recommendation | `aus:read` |
| `GET` | `/loans/{loanId}/disclosures` | List generated disclosures and delivery status | `compliance:read` |
| `POST` | `/loans/{loanId}/disclosures/generate` | Generate and send initial disclosures (LE) | `compliance:write` |
| `GET` | `/loans/{loanId}/fees` | Get itemized fee worksheet | `loans:read` |
| `POST` | `/loans/{loanId}/lock` | Lock or re-lock the loan rate | `pricing:write` |
| `GET` | `/loans/{loanId}/timeline` | Get audit timeline of all actions on the loan | `audit:read` |
| `GET` | `/loans` | Search/filter loans (query params: status, loanOfficer, dateRange, borrowerName) | `loans:read` |

## Authentication

The LOS API uses OAuth 2.0 with client credentials grant for service-to-service communication and authorization code grant for user-context operations.

### Client Credentials Flow (Service-to-Service)

```
POST /auth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id={service_client_id}
&client_secret={service_client_secret}
&scope=loans:read loans:write docs:read
```

### Token Response

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "loans:read loans:write docs:read"
}
```

### Scopes

| Scope | Description |
|-------|-------------|
| `loans:read` | Read loan, borrower, and property data |
| `loans:write` | Create and update loan records |
| `loans:status` | Advance loan milestone/status |
| `docs:read` | Read document tracking records |
| `docs:write` | Create and update document tracking |
| `aus:submit` | Submit loans to automated underwriting |
| `aus:read` | Read AUS findings |
| `compliance:read` | Read disclosure and compliance data |
| `compliance:write` | Generate and send disclosures |
| `pricing:write` | Lock and re-lock loan rates |
| `audit:read` | Read audit trail and timeline |

### Rate Limits

- Standard API calls: 1,000 requests per minute per client
- AUS submissions: 100 per hour per client
- Disclosure generation: 200 per hour per client
- Bulk operations: 50 per minute per client

## Data Formats

### Loan Object (Core Fields)

```json
{
  "loanId": "LN-2026-00145892",
  "loanNumber": "2026001458",
  "loanType": "Conventional",
  "loanPurpose": "Purchase",
  "loanProgram": "30YR_FIXED",
  "loanAmountCents": 35000000,
  "interestRate": 6.375,
  "propertyType": "SingleFamily",
  "occupancyType": "PrimaryResidence",
  "status": "Processing",
  "milestone": "SUBMITTED_TO_UW",
  "applicationDate": "2026-03-15T14:30:00Z",
  "estimatedClosingDate": "2026-04-30",
  "loanOfficerId": "LO-4521",
  "processorId": "LP-1187",
  "underwriterId": null,
  "branchId": "BR-045",
  "channelType": "Retail",
  "ausType": "DU",
  "ausRecommendation": "Approve/Eligible",
  "tridLeIssueDate": "2026-03-16",
  "tridCdIssueDate": null,
  "rateLock": {
    "locked": true,
    "lockDate": "2026-03-20",
    "lockExpirationDate": "2026-04-20",
    "lockedRate": 6.375,
    "lockedPoints": 0.5
  }
}
```

### Borrower Object

```json
{
  "borrowerId": "BRW-78923",
  "loanId": "LN-2026-00145892",
  "borrowerType": "Primary",
  "firstName": "Jane",
  "lastName": "Smith",
  "ssn": "***-**-6789",
  "dateOfBirth": "1985-07-22",
  "email": "jane.smith@email.com",
  "phone": "+15551234567",
  "currentAddress": {
    "street": "456 Oak Avenue",
    "city": "Springfield",
    "state": "IL",
    "zip": "62704"
  },
  "employment": {
    "employerName": "Acme Corporation",
    "position": "Senior Engineer",
    "startDate": "2019-03-01",
    "monthlyIncomeCents": 1083333,
    "employmentType": "W2_SALARIED"
  },
  "creditScore": {
    "equifax": 742,
    "experian": 738,
    "transunion": 745,
    "representativeScore": 742
  },
  "dtiRatio": {
    "frontEnd": 28.5,
    "backEnd": 38.2
  }
}
```

### Property Object

```json
{
  "propertyId": "PROP-55612",
  "loanId": "LN-2026-00145892",
  "address": {
    "street": "123 Main Street",
    "city": "Springfield",
    "state": "IL",
    "zip": "62701",
    "county": "Sangamon"
  },
  "propertyType": "SingleFamily",
  "yearBuilt": 2005,
  "squareFeet": 2200,
  "bedrooms": 4,
  "bathrooms": 2.5,
  "purchasePriceCents": 42500000,
  "appraisedValueCents": 43000000,
  "ltvPercent": 82.35,
  "cltvPercent": 82.35,
  "floodZone": "X",
  "appraisalStatus": "COMPLETED",
  "appraisalOrderId": "APR-2026-88743"
}
```

### Loan Statuses (Milestones)

| Status Code | Display Name | Description |
|-------------|-------------|-------------|
| `APPLICATION_RECEIVED` | Application Received | Initial application submitted |
| `DISCLOSURES_SENT` | Disclosures Sent | LE and initial disclosures delivered |
| `DISCLOSURES_SIGNED` | Disclosures Signed | Borrower signed intent to proceed |
| `PROCESSING` | In Processing | Processor gathering documents and data |
| `SUBMITTED_TO_UW` | Submitted to UW | Loan file submitted for underwriting review |
| `UW_REVIEW` | In Underwriting | Underwriter actively reviewing the file |
| `UW_SUSPENDED` | UW Suspended | Additional information needed from borrower |
| `UW_APPROVED_CONDITIONS` | Approved with Conditions | Conditionally approved, conditions outstanding |
| `CONDITIONS_SUBMITTED` | Conditions Submitted | Conditions documents submitted for review |
| `CLEAR_TO_CLOSE` | Clear to Close | All conditions satisfied, ready for closing |
| `CD_SENT` | Closing Disclosure Sent | CD delivered, waiting period started |
| `CLOSING_SCHEDULED` | Closing Scheduled | Settlement date confirmed |
| `CLOSED_FUNDED` | Closed/Funded | Loan closed and funds disbursed |
| `POST_CLOSING` | Post-Closing | Post-closing QC and investor delivery |
| `DENIED` | Denied | Application denied |
| `WITHDRAWN` | Withdrawn | Application withdrawn by borrower |

## Event Topics

The LOS publishes domain events to the event bus for consumption by downstream systems. All events include a standard envelope with metadata.

| Event Topic | Event Type | Payload Summary | Consumers |
|------------|-----------|----------------|-----------|
| `los.loan.created` | Loan Created | loanId, loanType, applicationDate | DocVault, Compliance, CRM |
| `los.loan.status.changed` | Status Changed | loanId, previousStatus, newStatus, timestamp | All systems |
| `los.borrower.added` | Borrower Added | loanId, borrowerId, borrowerType | Income Verification, Credit |
| `los.borrower.updated` | Borrower Updated | loanId, borrowerId, changedFields | Income Verification |
| `los.property.updated` | Property Updated | loanId, propertyId, changedFields | Appraisal, Flood, Title |
| `los.document.received` | Document Received | loanId, documentType, docVaultId | Processing, Underwriting |
| `los.condition.added` | Condition Added | loanId, conditionId, conditionType | Processing, Borrower Portal |
| `los.condition.cleared` | Condition Cleared | loanId, conditionId | Underwriting |
| `los.aus.completed` | AUS Completed | loanId, ausType, recommendation, findingsCount | Underwriting, Compliance |
| `los.disclosure.sent` | Disclosure Sent | loanId, disclosureType, deliveryMethod | Compliance, Timeline |
| `los.rate.locked` | Rate Locked | loanId, rate, points, lockExpiration | Pricing, Secondary |
| `los.appraisal.ordered` | Appraisal Ordered | loanId, appraisalOrderId, propertyId | Appraisal Management |
| `los.appraisal.completed` | Appraisal Completed | loanId, appraisedValue, appraisalOrderId | Underwriting, Processing |
| `los.clear.to.close` | Clear to Close | loanId, closingDate | Closing, Title, Escrow |
| `los.loan.funded` | Loan Funded | loanId, fundingDate, fundingAmount | Post-Closing, Investor |
