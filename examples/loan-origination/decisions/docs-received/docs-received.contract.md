---
contract_id: "ICT-LO-DEC-002"
intent_id: "INT-LO-DEC-002"
version: "1.0"
status: "draft"
binding_status: "unbound"
sources:
  - name: "DocVault"
    protocol: "rest"
    endpoint: "https://docvault.example.com/api/v1/checklists/{loan_number}/status"
    auth: "oauth2"
    schema_ref: "schemas/doc-submission-status.json"
    sla_ms: 2000
  - name: "LOS Database"
    protocol: "rest"
    endpoint: "https://los.example.com/api/v2/applications/{loan_number}/doc-requests"
    auth: "oauth2"
    schema_ref: "schemas/doc-request-record.json"
    sla_ms: 1000
sinks:
  - name: "Process Engine"
    protocol: "rest"
    endpoint: "https://bpm.example.com/api/v1/process/{instance_id}/signal"
    auth: "oauth2"
    schema_ref: "schemas/routing-signal.json"
    sla_ms: 1000
events:
  - topic: "loan.docs.decision"
    schema_ref: "schemas/events/docs-decision.json"
    delivery: "at_least_once"
    key_field: "loan_number"
audit:
  record_type: "docs_received_decision"
  retention_years: 7
  fields_required:
    - "loan_number"
    - "docs_received"
    - "items_submitted"
    - "items_outstanding"
    - "routing_decision"
    - "timestamp"
  sink: "https://audit.example.com/api/v1/records"
generated_from: "INT-LO-DEC-002"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PSM"
---

# Integration Contract: Docs Received Decision

## Sources

### DocVault
- **Endpoint**: `GET /api/v1/checklists/{loan_number}/status`
- **Purpose**: Check document submission completeness

### LOS Database
- **Endpoint**: `GET /api/v2/applications/{loan_number}/doc-requests`
- **Purpose**: Retrieve the original request to compare against submissions

## Sinks

### Process Engine
- **Endpoint**: `POST /api/v1/process/{instance_id}/signal`
- **Purpose**: Signal routing decision to process engine

## Audit

Document receipt decisions retained for 7 years.
