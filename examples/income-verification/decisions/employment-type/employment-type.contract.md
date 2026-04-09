---
contract_id: "ICT-IV-DEC-001"
intent_id: "INT-IV-DEC-001"
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
    - "evaluatedVariable"
    - "evaluatedValue"
    - "selectedFlow"
    - "evaluatedAt"
  sink: "https://audit.example.com/api/v1/records"
generated_from: "INT-IV-DEC-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PSM"
unbound_sources: []
unbound_sinks:
  - "Audit logging of gateway decisions is recommended for regulatory compliance but the audit endpoint is not yet provisioned"
  - "The process engine must be configured to treat unmatched exclusive gateways as errors, not silent drops"
---

# Integration Contract: Employment Type Decision

## Sources

### Process Engine Variable Evaluation (Internal)
- **Protocol**: Process Engine Native
- **Mechanism**: BPMN expression evaluation on sequence flow conditions
- **Condition Expressions**:
  - Flow_GatewayToW2: `${employmentType == 'W2'}`
  - Flow_GatewayToSelfEmployed: `${employmentType == 'SELF_EMPLOYED'}`

## Sinks

### Gateway Decision Audit Log (Outbound, Optional)
- **Protocol**: REST (HTTPS)
- **Endpoint**: `POST /api/v1/audit/gateway-decisions`
- **Authentication**: Service Account
- **SLA**: 2,000 ms

## Audit

Gateway decisions are logged for regulatory compliance. The audit endpoint is shared with Gateway_Variance.
