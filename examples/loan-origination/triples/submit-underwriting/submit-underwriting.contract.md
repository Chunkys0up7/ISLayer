---
contract_id: "ICT-LO-SUB-001"
intent_id: "INT-LO-SUB-001"
version: "1.0"
status: "draft"
binding_status: "unbound"
sources:
  - name: "LOS Database"
    protocol: "rest"
    endpoint: "https://los.example.com/api/v2/applications/{loan_number}/package"
    auth: "oauth2"
    schema_ref: "schemas/loan-package.json"
    sla_ms: 2000
sinks:
  - name: "Underwriting Queue"
    protocol: "message_queue"
    endpoint: "amqps://mq.example.com/uw-submissions"
    auth: "mtls"
    schema_ref: "schemas/uw-submission.json"
    sla_ms: 5000
    idempotency_key: "loan_number"
  - name: "LOS Database"
    protocol: "rest"
    endpoint: "https://los.example.com/api/v2/applications/{loan_number}/status"
    auth: "oauth2"
    schema_ref: "schemas/status-update.json"
    sla_ms: 2000
  - name: "Email Service"
    protocol: "rest"
    endpoint: "https://notifications.example.com/api/v1/send"
    auth: "api_key"
    schema_ref: "schemas/email-payload.json"
    sla_ms: 10000
events:
  - topic: "loan.submitted.underwriting"
    schema_ref: "schemas/events/submitted-underwriting.json"
    delivery: "exactly_once"
    key_field: "loan_number"
audit:
  record_type: "underwriting_submission"
  retention_years: 7
  fields_required:
    - "loan_number"
    - "assigned_queue"
    - "priority"
    - "processor_id"
    - "submission_timestamp"
  sink: "https://audit.example.com/api/v1/records"
generated_from: "INT-LO-SUB-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PSM"
---

# Integration Contract: Submit to Underwriting

## Sources

### LOS Database
- **Endpoint**: `GET /api/v2/applications/{loan_number}/package`
- **Purpose**: Retrieve the packaged loan file for submission

## Sinks

### Underwriting Queue
- **Protocol**: AMQP (mTLS)
- **Endpoint**: `amqps://mq.example.com/uw-submissions`
- **Purpose**: Place loan file in the underwriting processing queue
- **Delivery**: Exactly-once semantics

### Email Service
- **Purpose**: Notify loan officer and borrower of submission

## Audit

Underwriting submission records retained for 7 years. Must log queue assignment, priority, and processor identity.
