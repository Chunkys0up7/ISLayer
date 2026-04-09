---
contract_id: "ICT-LO-APP-001"
intent_id: "INT-LO-APP-001"
version: "1.0"
status: "draft"
binding_status: "unbound"
sources:
  - name: "LOS Intake API"
    protocol: "rest"
    endpoint: "https://los.example.com/api/v2/applications/intake"
    auth: "oauth2"
    schema_ref: "schemas/urla-1003.json"
    sla_ms: 2000
  - name: "DocVault"
    protocol: "rest"
    endpoint: "https://docvault.example.com/api/v1/documents"
    auth: "oauth2"
    schema_ref: "schemas/id-document.json"
    sla_ms: 3000
sinks:
  - name: "LOS Database"
    protocol: "rest"
    endpoint: "https://los.example.com/api/v2/applications"
    auth: "oauth2"
    schema_ref: "schemas/loan-application.json"
    sla_ms: 5000
    idempotency_key: "loan_number"
  - name: "Email Service"
    protocol: "rest"
    endpoint: "https://notifications.example.com/api/v1/send"
    auth: "api_key"
    schema_ref: "schemas/email-payload.json"
    sla_ms: 10000
events:
  - topic: "loan.application.received"
    schema_ref: "schemas/events/application-received.json"
    delivery: "at_least_once"
    key_field: "loan_number"
audit:
  record_type: "application_intake"
  retention_years: 7
  fields_required:
    - "loan_number"
    - "borrower_ssn_masked"
    - "intake_channel"
    - "timestamp"
    - "agent_id"
  sink: "https://audit.example.com/api/v1/records"
generated_from: "INT-LO-APP-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PSM"
---

# Integration Contract: Receive Loan Application

## Sources

### LOS Intake API
- **Protocol**: REST (HTTPS)
- **Endpoint**: `POST /api/v2/applications/intake`
- **Authentication**: OAuth 2.0 (client credentials)
- **Payload**: URLA 1003 form data in JSON format
- **SLA**: 2,000 ms response time

### DocVault
- **Protocol**: REST (HTTPS)
- **Endpoint**: `GET /api/v1/documents/{document_id}`
- **Authentication**: OAuth 2.0
- **Payload**: Borrower identity document metadata and binary
- **SLA**: 3,000 ms response time

## Sinks

### LOS Database
- **Protocol**: REST (HTTPS)
- **Endpoint**: `POST /api/v2/applications`
- **Idempotency**: Keyed on `loan_number`

### Email Service
- **Protocol**: REST (HTTPS)
- **Endpoint**: `POST /api/v1/send`
- **Purpose**: Borrower acknowledgment letter

## Events

- **Topic**: `loan.application.received`
- **Delivery**: At-least-once
- **Key**: `loan_number`

## Audit

All application intake actions are logged with 7-year retention per federal lending regulations.
