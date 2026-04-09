---
contract_id: "ICT-IV-CLS-001"
intent_id: "INT-IV-CLS-001"
version: "1.0"
status: "draft"
binding_status: "unbound"
sources:
  - name: "RuleEngine Classification API"
    protocol: "rest"
    endpoint: "https://rules.example.com/api/v1/rules/employment-classification/execute"
    auth: "oauth2"
    schema_ref: "schemas/employment-classification-request.json"
    sla_ms: 3000
sinks: []
events: []
rule_engines:
  - name: "Employment Classification Rules"
    type: "DMN"
    decision_table_id: "DT-IV-EMPLOYMENT-CLASS"
    version: "pending"
audit:
  record_type: "employment_classification"
  retention_years: 7
  fields_required:
    - "borrowerId"
    - "loanApplicationId"
    - "employmentType"
    - "employmentClassification"
    - "timestamp"
    - "agent_id"
  sink: "https://audit.example.com/api/v1/records"
generated_from: "INT-IV-CLS-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PSM"
unbound_sources:
  - "RuleEngine decision table ID for employment classification is not yet assigned"
  - "Classification rules may vary by loanProgram; rule table must support program-specific branches"
unbound_sinks: []
---

# Integration Contract: Classify Employment Type

## Sources

### RuleEngine Classification API (Outbound)
- **Protocol**: REST (HTTPS)
- **Endpoint**: `POST /api/v1/rules/employment-classification/execute`
- **Authentication**: OAuth 2.0 Client Credentials
- **SLA**: 3,000 ms

## Events

No outbound events. Classification result is stored in process context.

## Audit

All employment classification decisions are logged with 7-year retention per federal lending regulations. The RuleEngine is expected to support DMN (Decision Model and Notation) execution.
