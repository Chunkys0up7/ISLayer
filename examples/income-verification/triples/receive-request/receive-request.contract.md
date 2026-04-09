---
contract_id: "ICT-IV-REQ-001"
intent_id: "INT-IV-REQ-001"
version: "1.0"
status: "draft"
binding_status: "unbound"
sources:
  - name: "Income Verification Request Queue"
    protocol: "amqp"
    endpoint: "income.verification.requests"
    auth: "service_account"
    schema_ref: "schemas/verification-request.json"
    sla_ms: 1000
  - name: "LOS Borrower Profile API"
    protocol: "rest"
    endpoint: "https://los.example.com/api/v2/borrowers/{borrowerId}/profile"
    auth: "oauth2"
    schema_ref: "schemas/borrower-profile.json"
    sla_ms: 5000
  - name: "DocVault Document Status API"
    protocol: "rest"
    endpoint: "https://docvault.example.com/api/v1/documents/{docId}/status"
    auth: "api_key"
    schema_ref: "schemas/document-status.json"
    sla_ms: 3000
sinks:
  - name: "Verification Acknowledgement Channel"
    protocol: "amqp"
    endpoint: "income.verification.acknowledgements"
    auth: "service_account"
    schema_ref: "schemas/verification-ack.json"
    sla_ms: 1000
events:
  - topic: "income.verification.acknowledged"
    schema_ref: "schemas/events/verification-acknowledged.json"
    delivery: "at_least_once"
    key_field: "loanApplicationId"
audit:
  record_type: "verification_request_intake"
  retention_years: 7
  fields_required:
    - "loanApplicationId"
    - "borrowerId"
    - "requestedBy"
    - "timestamp"
    - "agent_id"
  sink: "https://audit.example.com/api/v1/records"
generated_from: "INT-IV-REQ-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PSM"
unbound_sources:
  - "Message broker implementation (AMQP vs Kafka) is not yet determined"
  - "OAuth2 token endpoint for LOS API is environment-specific and not yet configured"
unbound_sinks:
  - "Acknowledgement channel broker implementation not yet determined"
---

# Integration Contract: Receive Verification Request

## Sources

### Income Verification Request Queue (Inbound)
- **Protocol**: Message Broker (AMQP / Kafka)
- **Channel**: `income.verification.requests`
- **Direction**: Consume
- **SLA**: 1,000 ms

### LOS Borrower Profile API (Outbound)
- **Protocol**: REST (HTTPS)
- **Endpoint**: `GET /api/v2/borrowers/{borrowerId}/profile`
- **Authentication**: OAuth 2.0 Client Credentials
- **SLA**: 5,000 ms

### DocVault Document Status API (Outbound)
- **Protocol**: REST (HTTPS)
- **Endpoint**: `GET /api/v1/documents/{docId}/status`
- **Authentication**: API Key (Header: X-DocVault-Key)
- **SLA**: 3,000 ms

## Sinks

### Verification Acknowledgement Channel (Outbound)
- **Protocol**: Message Broker (AMQP / Kafka)
- **Channel**: `income.verification.acknowledgements`
- **Direction**: Produce

## Events

- **Topic**: `income.verification.acknowledged`
- **Delivery**: At-least-once
- **Key**: `loanApplicationId`

## Audit

All verification request intake actions are logged with 7-year retention per federal lending regulations.
