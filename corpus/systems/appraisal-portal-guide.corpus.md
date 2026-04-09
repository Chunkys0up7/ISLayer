---
corpus_id: "CRP-SYS-PA-001"
title: "Appraisal Portal Integration Guide"
slug: "appraisal-portal-guide"
doc_type: "system"
domain: "Mortgage Lending"
subdomain: "Property Appraisal"
tags:
  - "appraisal-portal"
  - "amc-api"
  - "mismo-xml"
  - "uad-xml"
  - "webhooks"
  - "order-management"
  - "report-retrieval"
  - "error-codes"
applies_to:
  process_ids:
    - "Process_PropertyAppraisal"
    - "Process_AppraisalOrdering"
    - "Process_SystemIntegration"
  task_types:
    - "serviceTask"
  task_name_patterns:
    - "order.*appraisal"
    - "submit.*order"
    - "receive.*report"
    - "poll.*status"
    - "retrieve.*appraisal"
  goal_types:
    - "system_integration"
  roles:
    - "appraisal_coordinator"
    - "system_administrator"
    - "integration_engineer"
    - "loan_processor"
version: "3.1"
status: "current"
effective_date: "2025-06-01"
review_date: "2026-06-01"
supersedes: null
superseded_by: null
author: "Integration Engineering Team"
last_modified: "2025-05-28"
last_modified_by: "J. Chen"
source: "internal"
source_ref: "SYS-PA-2025-001"
related_corpus_ids:
  - "CRP-PRC-PA-001"
  - "CRP-PRC-PA-002"
  - "CRP-DAT-PA-001"
  - "CRP-POL-PA-001"
regulation_refs:
  - "MISMO Reference Model v3.4"
policy_refs:
  - "POL-IT-003"
  - "POL-PA-001"
---

# Appraisal Portal Integration Guide

## 1. Overview

The Appraisal Portal is the system interface between the lender's Loan Origination System (LOS) and approved AMC platforms. It handles appraisal order submission, status tracking, report retrieval, and revision request management. The portal supports both interactive (browser-based) and automated (API-based) workflows. This guide covers the API integration layer, which is the primary interface for automated order processing.

## 2. System Architecture

### 2.1 Integration Components

| Component | Description | Protocol |
|---|---|---|
| Order Submission API | Sends appraisal orders to AMC platforms | REST API (HTTPS) with MISMO XML payload |
| Status Polling API | Queries current status of submitted orders | REST API (HTTPS), JSON response |
| Report Retrieval API | Downloads completed appraisal reports | REST API (HTTPS), multipart response (PDF + XML) |
| Webhook Receiver | Receives real-time status notifications from AMCs | HTTPS POST (inbound) |
| Revision Request API | Submits revision requests to AMCs | REST API (HTTPS) with structured payload |
| Portal UI | Browser-based interface for manual operations | HTTPS (web application) |

### 2.2 Authentication

| Method | Usage | Token Lifetime |
|---|---|---|
| OAuth 2.0 (Client Credentials) | API-to-API authentication | 1 hour |
| API Key + HMAC Signature | Legacy AMC integrations | N/A (key-based) |
| SAML 2.0 SSO | Portal UI user authentication | 8-hour session |

### 2.3 Environment Endpoints

| Environment | Base URL | Purpose |
|---|---|---|
| Production | https://appraisal-api.internal.example.com/v3 | Live operations |
| Staging | https://appraisal-api-staging.internal.example.com/v3 | Pre-production testing |
| Sandbox | https://appraisal-api-sandbox.internal.example.com/v3 | AMC onboarding and integration testing |

## 3. AMC Ordering Portal API

### 3.1 Submit Order

**Endpoint:** `POST /orders`

**Request Headers:**
| Header | Value |
|---|---|
| Content-Type | application/xml |
| Authorization | Bearer {oauth_token} |
| X-AMC-Target | {amc_identifier} |
| X-Request-Id | {uuid} |
| X-Loan-Number | {loan_number} |

**Request Body:** MISMO XML v3.4 Appraisal Order Message

Key MISMO XML elements in the order payload:

| XML Element Path | Description | Required |
|---|---|---|
| /MESSAGE/DEAL_SETS/DEAL_SET/DEALS/DEAL/COLLATERALS/COLLATERAL/SUBJECT_PROPERTY/ADDRESS | Property address | Yes |
| /MESSAGE/DEAL_SETS/DEAL_SET/DEALS/DEAL/COLLATERALS/COLLATERAL/SUBJECT_PROPERTY/PROPERTY_DETAIL | Property type, legal description | Yes |
| /MESSAGE/DEAL_SETS/DEAL_SET/DEALS/DEAL/LOANS/LOAN/LOAN_DETAIL | Loan purpose, program type | Yes |
| /MESSAGE/DEAL_SETS/DEAL_SET/DEALS/DEAL/SERVICES/SERVICE/VALUATION/VALUATION_REQUEST | Form type, inspection type, rush indicator | Yes |
| /MESSAGE/DEAL_SETS/DEAL_SET/DEALS/DEAL/PARTIES/PARTY[@PartyRoleType='Borrower'] | Borrower contact info | Yes |
| /MESSAGE/DEAL_SETS/DEAL_SET/DEALS/DEAL/SERVICES/SERVICE/VALUATION/VALUATION_REQUEST/PROPERTY_ACCESS | Access instructions, contact info | Yes |

**Response (Success - 201 Created):**

```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "amc_reference": "AMC-2025-123456",
  "status": "RECEIVED",
  "estimated_completion_date": "2025-06-15",
  "assigned_fee": 550.00,
  "created_at": "2025-06-01T14:30:00Z"
}
```

### 3.2 Get Order Status

**Endpoint:** `GET /orders/{order_id}/status`

**Response:**

```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "APPRAISER_ASSIGNED",
  "appraiser_name": "Jane Smith",
  "appraiser_license": "CR-12345",
  "appraiser_license_state": "CA",
  "inspection_scheduled_date": "2025-06-05",
  "estimated_completion_date": "2025-06-12",
  "last_updated": "2025-06-02T09:15:00Z",
  "status_history": [
    {"status": "RECEIVED", "timestamp": "2025-06-01T14:30:00Z"},
    {"status": "APPRAISER_ASSIGNED", "timestamp": "2025-06-02T09:15:00Z"}
  ]
}
```

**Status Enum Values:**

| Status | Description |
|---|---|
| RECEIVED | Order received by AMC |
| APPRAISER_ASSIGNED | Appraiser has been assigned to the order |
| INSPECTION_SCHEDULED | Property inspection date scheduled |
| INSPECTION_COMPLETED | Property inspection completed |
| REPORT_IN_PROGRESS | Appraiser is preparing the report |
| REPORT_SUBMITTED | Report submitted by appraiser to AMC QC |
| QC_REVIEW | AMC quality control review in progress |
| REPORT_DELIVERED | Report delivered to lender |
| REVISION_REQUESTED | Lender has requested a revision |
| REVISION_IN_PROGRESS | Appraiser is working on the revision |
| REVISION_DELIVERED | Revised report delivered |
| CANCELLED | Order cancelled |
| ON_HOLD | Order placed on hold |
| DECLINED | Order declined by AMC (no appraiser available) |

### 3.3 Batch Status Polling

**Endpoint:** `GET /orders/status?since={iso_datetime}&limit={int}`

Returns status updates for all orders modified since the specified timestamp. Used for periodic batch synchronization.

**Response:**

```json
{
  "orders": [
    {
      "order_id": "...",
      "status": "REPORT_DELIVERED",
      "last_updated": "2025-06-10T16:00:00Z"
    }
  ],
  "total_count": 15,
  "next_cursor": "eyJvcmRlcl9pZCI6..."
}
```

**Polling Frequency:** Every 15 minutes during business hours (6 AM - 9 PM local); every 60 minutes outside business hours.

## 4. MISMO XML Format for Orders

### 4.1 Schema Version

All orders use MISMO Reference Model v3.4 or later. The schema XSD files are maintained at:
- Production: `/schemas/mismo/v3.4/ValuationMessage.xsd`
- The portal validates all outbound XML against the schema before transmission

### 4.2 Required Namespace

```xml
<MESSAGE xmlns="http://www.mismo.org/residential/2009/schemas"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         MISMOVersionID="3.4.0">
```

### 4.3 Validation Rules

| Rule | Description | Error Code |
|---|---|---|
| Schema validation | XML must conform to MISMO v3.4 XSD | XML-001 |
| Required elements | All required elements must be present and non-empty | XML-002 |
| Address standardization | Property address must be USPS-standardized | XML-003 |
| Party validation | Borrower party must include phone or email | XML-004 |
| Form type validation | Requested form type must be valid for property type | XML-005 |
| State code validation | State codes must be valid 2-letter abbreviations | XML-006 |

## 5. Report Retrieval

### 5.1 Download Report

**Endpoint:** `GET /orders/{order_id}/report`

**Response:** Multipart response containing:

| Part | Content-Type | Description |
|---|---|---|
| Part 1 | application/pdf | Appraisal report PDF (human-readable) |
| Part 2 | application/xml | UAD XML data file (machine-readable) |
| Part 3 | application/json | Report metadata (appraiser info, dates, status) |

### 5.2 UAD XML Report Format

The UAD XML file follows the Fannie Mae / Freddie Mac Uniform Appraisal Dataset specification. Key data elements extracted by the system:

| Data Element | XML Path | Maps To |
|---|---|---|
| Appraised value | /VALUATION_RESPONSE/PROPERTY_VALUATION/VALUE | AppraisalReport.appraised_value |
| Condition rating | /PROPERTY/IMPROVEMENT/CONDITION_RATING | AppraisalReport.condition_rating |
| Quality rating | /PROPERTY/IMPROVEMENT/QUALITY_RATING | AppraisalReport.quality_rating |
| GLA | /PROPERTY/IMPROVEMENT/GROSS_LIVING_AREA | AppraisalReport.gla_sqft |
| Form type | /VALUATION_RESPONSE/REPORT_FORM_TYPE | AppraisalReport.form_type |
| Effective date | /VALUATION_RESPONSE/EFFECTIVE_DATE | AppraisalReport.effective_date |
| Comparable sales | /VALUATION_RESPONSE/COMPARABLE_SALES/COMPARABLE[] | AppraisalReport.comparable_sales[] |

### 5.3 Report Storage

Retrieved reports are stored in the document management system:
- PDF: Stored as loan document with document type "APPRAISAL_REPORT"
- UAD XML: Parsed and loaded into the AppraisalReport data object (CRP-DAT-PA-001)
- Both files are immutable after storage (no modification permitted)
- Retention period: Life of loan + 7 years (per regulatory requirements)

## 6. Webhook Notifications

### 6.1 Configuration

AMCs are configured to send webhook notifications to the portal's inbound endpoint for real-time status updates.

**Webhook Endpoint:** `POST /webhooks/amc-notifications`

**Authentication:** Each AMC is assigned a webhook secret key. Notifications include an HMAC-SHA256 signature in the `X-Webhook-Signature` header for verification.

### 6.2 Webhook Payload

```json
{
  "event_type": "ORDER_STATUS_CHANGED",
  "amc_identifier": "AMC-APEX",
  "order_reference": "AMC-2025-123456",
  "lender_order_id": "550e8400-e29b-41d4-a716-446655440000",
  "new_status": "REPORT_DELIVERED",
  "previous_status": "QC_REVIEW",
  "timestamp": "2025-06-10T16:00:00Z",
  "details": {
    "appraiser_name": "Jane Smith",
    "appraised_value": 425000,
    "report_available": true
  }
}
```

### 6.3 Webhook Event Types

| Event Type | Trigger | Action |
|---|---|---|
| ORDER_STATUS_CHANGED | Any status transition | Update order status in tracking system |
| REPORT_DELIVERED | Report available for download | Trigger automated report retrieval |
| APPRAISER_ASSIGNED | Appraiser assigned to order | Record appraiser info; initiate credential verification |
| INSPECTION_SCHEDULED | Inspection date set | Update estimated completion date |
| ORDER_DECLINED | AMC declined the order | Alert appraisal coordinator for reassignment |
| REVISION_DELIVERED | Revised report available | Trigger revised report retrieval |
| FEE_CHANGE | Fee adjusted (complexity, rush) | Update fee record; notify if above threshold |

### 6.4 Webhook Reliability

| Feature | Implementation |
|---|---|
| Retry policy | AMC retries failed deliveries 3 times with exponential backoff |
| Idempotency | Portal deduplicates by event_type + order_reference + timestamp |
| Ordering | Events are processed in timestamp order; out-of-order events are queued |
| Monitoring | Webhook receipt rate monitored; alert if no webhooks received from AMC for 4+ hours |

## 7. Error Codes

### 7.1 API Error Response Format

```json
{
  "error_code": "ORD-003",
  "error_message": "Property address failed USPS standardization",
  "details": "Street address '123 Main' could not be standardized. Please provide full street suffix.",
  "timestamp": "2025-06-01T14:30:00Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 7.2 Error Code Reference

| Code | Category | Description | Resolution |
|---|---|---|---|
| ORD-001 | Order | AMC not found or not in approved panel | Verify AMC identifier; check panel status |
| ORD-002 | Order | AMC not registered in subject property state | Select different AMC with state coverage |
| ORD-003 | Order | Property address failed standardization | Correct address and resubmit |
| ORD-004 | Order | Invalid form type for property type | Correct form type per property type matrix |
| ORD-005 | Order | Duplicate order detected (same property + loan within 30 days) | Confirm intentional re-order; use override flag |
| ORD-006 | Order | AMC at maximum concurrent capacity | System auto-routes to next AMC in rotation |
| ORD-007 | Order | Appraisal fee exceeds maximum threshold | Review fee; escalate to coordinator if valid |
| XML-001 | Validation | MISMO XML schema validation failed | Review XML against XSD; correct structure |
| XML-002 | Validation | Required XML element missing or empty | Populate all required fields |
| XML-003 | Validation | Address element format invalid | Use USPS-standardized address format |
| XML-004 | Validation | Borrower contact information missing | Include phone or email for borrower |
| XML-005 | Validation | Invalid form type code | Use valid form type enum value |
| XML-006 | Validation | Invalid state code | Use 2-letter state abbreviation |
| RPT-001 | Report | Report not yet available for download | Check order status; report not yet delivered |
| RPT-002 | Report | UAD XML parsing failed | Notify AMC; request corrected XML |
| RPT-003 | Report | PDF corrupt or unreadable | Notify AMC; request re-delivery |
| RPT-004 | Report | PDF and XML data mismatch | Notify AMC; request reconciled report |
| REV-001 | Revision | Revision request exceeds maximum (2 per order) | Escalate to manual review or new appraisal |
| REV-002 | Revision | Original appraiser unavailable for revision | AMC assigns replacement appraiser |
| REV-003 | Revision | Revision request content flagged for independence concern | Review request language; resubmit after compliance review |
| WHK-001 | Webhook | Invalid webhook signature | Verify AMC webhook secret configuration |
| WHK-002 | Webhook | Unknown order reference in webhook | Log for investigation; may indicate AMC data error |
| WHK-003 | Webhook | Webhook payload validation failed | Log details; notify AMC of payload format issue |
| AUTH-001 | Authentication | OAuth token expired or invalid | Refresh token; re-authenticate |
| AUTH-002 | Authentication | API key not recognized | Verify API key configuration |
| AUTH-003 | Authentication | Insufficient permissions for requested operation | Check role-based access configuration |

## 8. Rate Limits and Performance

| Metric | Limit |
|---|---|
| API requests per minute (per AMC) | 60 |
| Concurrent report downloads | 10 |
| Maximum XML payload size | 5 MB |
| Maximum PDF report size | 50 MB |
| Status polling frequency (minimum interval) | 5 minutes |
| Webhook processing timeout | 30 seconds |
| API response time SLA | 95th percentile < 2 seconds |

## 9. References

- CRP-PRC-PA-001: Appraisal Ordering Procedure
- CRP-PRC-PA-002: Appraisal Report Review Procedure
- CRP-DAT-PA-001: Appraisal Report Data Object
- CRP-POL-PA-001: Appraisal Ordering Policy
- MISMO Reference Model v3.4
