---
contract_id: "ICT-IV-DEC-002"
intent_id: "INT-IV-DEC-002"
version: "1.0"
status: "draft"
binding_status: "unbound"
sources:
  - name: "Process Engine Variable Evaluation"
    protocol: "process_engine_native"
    endpoint: "internal"
    auth: "none"
    schema_ref: null
    sla_ms: 100
sinks:
  - name: "Variance Exception Notification"
    protocol: "rest"
    endpoint: "https://underwriting.example.com/api/v1/underwriting/exceptions"
    auth: "oauth2"
    schema_ref: "schemas/variance-exception.json"
    sla_ms: 3000
  - name: "Gateway Decision Audit Log"
    protocol: "rest"
    endpoint: "https://audit.example.com/api/v1/audit/gateway-decisions"
    auth: "service_account"
    schema_ref: "schemas/gateway-decision-audit.json"
    sla_ms: 2000
events: []
audit:
  record_type: "gateway_decision"
  retention_years: 7
  fields_required:
    - "gatewayId"
    - "processInstanceId"
    - "loanApplicationId"
    - "variancePercent"
    - "varianceThreshold"
    - "selectedFlow"
    - "evaluatedAt"
  sink: "https://audit.example.com/api/v1/records"
generated_from: "INT-IV-DEC-002"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PSM"
unbound_sources: []
unbound_sinks:
  - "The exception notification endpoint is required for the underwriter queue but is not yet provisioned"
  - "Audit logging endpoint is shared with Gateway_EmploymentType"
  - "The BPMN error event (End_VarianceException) throws error code ERR_VARIANCE_001 which can be caught by a parent process"
---

# Integration Contract: Variance Threshold Decision

## Sources

### Process Engine Variable Evaluation (Internal)
- **Protocol**: Process Engine Native
- **Mechanism**: BPMN expression evaluation on sequence flow conditions
- **Condition Expressions**:
  - Flow_VarianceToEmit: `${variancePercent <= varianceThreshold}`
  - Flow_VarianceToException: `${variancePercent > varianceThreshold}`

## Sinks

### Variance Exception Notification (Outbound, Triggered on Exception Path)
- **Protocol**: REST (HTTPS)
- **Endpoint**: `POST /api/v1/underwriting/exceptions`
- **Authentication**: OAuth 2.0 Client Credentials
- **SLA**: 3,000 ms

### Gateway Decision Audit Log (Outbound, Optional)
- **Protocol**: REST (HTTPS)
- **Endpoint**: `POST /api/v1/audit/gateway-decisions`
- **Authentication**: Service Account
- **SLA**: 2,000 ms

## Audit

Gateway decisions are logged for regulatory compliance. The audit endpoint is shared with Gateway_EmploymentType.
