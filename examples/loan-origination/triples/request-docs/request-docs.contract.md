---
contract_id: "ICT-LO-DOC-001"
intent_id: "INT-LO-DOC-001"
version: "1.0"
status: "draft"
binding_status: "unbound"
sources:
  - name: "LOS Database"
    protocol: "rest"
    endpoint: "https://los.example.com/api/v2/applications/{loan_number}/dti"
    auth: "oauth2"
    schema_ref: "schemas/dti-result.json"
    sla_ms: 1000
  - name: "Template Library"
    protocol: "rest"
    endpoint: "https://templates.example.com/api/v1/templates/doc-request"
    auth: "api_key"
    schema_ref: "schemas/doc-request-template.json"
    sla_ms: 2000
sinks:
  - name: "LOS Database"
    protocol: "rest"
    endpoint: "https://los.example.com/api/v2/applications/{loan_number}/doc-requests"
    auth: "oauth2"
    schema_ref: "schemas/doc-request-record.json"
    sla_ms: 2000
    idempotency_key: "loan_number+request_sequence"
  - name: "Email Service"
    protocol: "rest"
    endpoint: "https://notifications.example.com/api/v1/send"
    auth: "api_key"
    schema_ref: "schemas/email-payload.json"
    sla_ms: 10000
  - name: "Borrower Portal"
    protocol: "rest"
    endpoint: "https://portal.example.com/api/v1/upload-links"
    auth: "oauth2"
    schema_ref: "schemas/upload-link-request.json"
    sla_ms: 3000
events:
  - topic: "loan.docs.requested"
    schema_ref: "schemas/events/docs-requested.json"
    delivery: "at_least_once"
    key_field: "loan_number"
audit:
  record_type: "document_request"
  retention_years: 7
  fields_required:
    - "loan_number"
    - "items_requested"
    - "delivery_channel"
    - "deadline"
    - "request_count"
    - "timestamp"
  sink: "https://audit.example.com/api/v1/records"
generated_from: "INT-LO-DOC-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PSM"
---

# Integration Contract: Request Additional Documentation

## Sources

### LOS Database
- **Endpoint**: `GET /api/v2/applications/{loan_number}/dti`
- **Purpose**: Retrieve DTI result with missing documents list

### Template Library
- **Endpoint**: `GET /api/v1/templates/doc-request`
- **Purpose**: Retrieve document request letter template

## Sinks

### Email Service
- **Endpoint**: `POST /api/v1/send`
- **Purpose**: Deliver document request to borrower

### Borrower Portal
- **Endpoint**: `POST /api/v1/upload-links`
- **Purpose**: Generate secure upload link for document submission

## Audit

Document request records retained for 7 years. Logs all items requested and delivery channels used.
