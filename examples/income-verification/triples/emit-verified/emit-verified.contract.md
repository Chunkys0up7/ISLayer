---
contract_id: "ICT-IV-NTF-001"
intent_id: "INT-IV-NTF-001"
version: "1.0"
status: "draft"
binding_status: "unbound"
sources: []
sinks:
  - name: "Underwriting Event Bus"
    protocol: "kafka"
    endpoint: "underwriting.events"
    auth: "service_account"
    schema_ref: "schemas/events/income-verified.json"
    sla_ms: 5000
    idempotency_key: "loanApplicationId"
  - name: "LOS Application Status Update API"
    protocol: "rest"
    endpoint: "https://los.example.com/api/v2/applications/{loanApplicationId}/status"
    auth: "oauth2"
    schema_ref: "schemas/los-status-update.json"
    sla_ms: 5000
events:
  - topic: "underwriting.events"
    schema_ref: "schemas/events/income-verified.json"
    delivery: "at_least_once"
    key_field: "loanApplicationId"
audit:
  record_type: "income_verified_event"
  retention_years: 5
  fields_required:
    - "loanApplicationId"
    - "borrowerId"
    - "totalQualifyingMonthlyIncome"
    - "varianceStatus"
    - "verifiedAt"
    - "agent_id"
  sink: "https://audit.example.com/api/v1/records"
generated_from: "INT-IV-NTF-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PSM"
unbound_sources: []
unbound_sinks:
  - "Kafka topic configuration (partitions, replication factor, retention) is managed by platform team"
  - "Dead-letter queue topic underwriting.events.dlq not yet provisioned"
  - "Event schema registry integration for schema evolution is planned but not yet implemented"
  - "LOS OAuth2 token endpoint is environment-specific"
---

# Integration Contract: Emit Income Verified Event

## Sinks

### Underwriting Event Bus (Outbound)
- **Protocol**: Kafka
- **Topic**: `underwriting.events`
- **Partition Key**: `loanApplicationId`
- **Delivery**: At-least-once
- **SLA**: 5,000 ms

### LOS Application Status Update API (Outbound)
- **Protocol**: REST (HTTPS)
- **Endpoint**: `PATCH /api/v2/applications/{loanApplicationId}/status`
- **Authentication**: OAuth 2.0 Client Credentials
- **SLA**: 5,000 ms

## Events

- **Topic**: `underwriting.events`
- **Event Type**: `IncomeVerified`
- **Delivery**: At-least-once
- **Key**: `loanApplicationId`

## Audit

All income verification event publications are logged with 5-year retention per Fannie Mae record retention requirements.
