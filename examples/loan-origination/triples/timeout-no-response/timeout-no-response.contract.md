---
contract_id: "ICT-LO-TMO-001"
intent_id: "INT-LO-TMO-001"
version: "1.0"
status: "draft"
binding_status: "unbound"
sources:
  - name: "LOS Database"
    protocol: "rest"
    endpoint: "https://los.example.com/api/v2/applications/{loan_number}"
    auth: "oauth2"
    schema_ref: "schemas/loan-application.json"
    sla_ms: 1000
  - name: "DocVault"
    protocol: "rest"
    endpoint: "https://docvault.example.com/api/v1/checklists/{loan_number}/status"
    auth: "oauth2"
    schema_ref: "schemas/doc-submission-status.json"
    sla_ms: 2000
sinks:
  - name: "LOS Database"
    protocol: "rest"
    endpoint: "https://los.example.com/api/v2/applications/{loan_number}/withdraw"
    auth: "oauth2"
    schema_ref: "schemas/withdrawal-record.json"
    sla_ms: 3000
    idempotency_key: "loan_number"
  - name: "Email Service"
    protocol: "rest"
    endpoint: "https://notifications.example.com/api/v1/send"
    auth: "api_key"
    schema_ref: "schemas/email-payload.json"
    sla_ms: 10000
  - name: "Compliance Notice Service"
    protocol: "rest"
    endpoint: "https://compliance.example.com/api/v1/notices/adverse-action"
    auth: "mtls"
    schema_ref: "schemas/adverse-action-notice.json"
    sla_ms: 5000
events:
  - topic: "loan.application.withdrawn"
    schema_ref: "schemas/events/application-withdrawn.json"
    delivery: "at_least_once"
    key_field: "loan_number"
audit:
  record_type: "application_withdrawal"
  retention_years: 7
  fields_required:
    - "loan_number"
    - "withdrawal_reason"
    - "adverse_action_notice_required"
    - "adverse_action_notice_sent"
    - "timestamp"
  sink: "https://audit.example.com/api/v1/records"
generated_from: "INT-LO-TMO-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PSM"
---

# Integration Contract: Timeout - No Response

## Sources

### LOS Database
- **Endpoint**: `GET /api/v2/applications/{loan_number}`
- **Purpose**: Retrieve application details for withdrawal processing

### DocVault
- **Endpoint**: `GET /api/v1/checklists/{loan_number}/status`
- **Purpose**: Final check for last-minute document uploads (race condition handling)

## Sinks

### LOS Database
- **Endpoint**: `POST /api/v2/applications/{loan_number}/withdraw`
- **Purpose**: Record application withdrawal

### Compliance Notice Service
- **Protocol**: REST (mTLS)
- **Endpoint**: `POST /api/v1/notices/adverse-action`
- **Purpose**: Generate and deliver adverse action notice if required

## Audit

Withdrawal records retained for 7 years. Must track whether adverse action notice was required and sent.
