---
contract_id: "ICT-LO-DEC-001"
intent_id: "INT-LO-DEC-001"
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
sinks:
  - name: "Process Engine"
    protocol: "rest"
    endpoint: "https://bpm.example.com/api/v1/process/{instance_id}/signal"
    auth: "oauth2"
    schema_ref: "schemas/routing-signal.json"
    sla_ms: 1000
events:
  - topic: "loan.eligibility.decided"
    schema_ref: "schemas/events/eligibility-decided.json"
    delivery: "at_least_once"
    key_field: "loan_number"
audit:
  record_type: "eligibility_decision"
  retention_years: 7
  fields_required:
    - "loan_number"
    - "dti_eligible"
    - "docs_complete"
    - "routing_decision"
    - "timestamp"
  sink: "https://audit.example.com/api/v1/records"
generated_from: "INT-LO-DEC-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PSM"
---

# Integration Contract: Loan Eligibility Decision

## Sources

### LOS Database
- **Endpoint**: `GET /api/v2/applications/{loan_number}/dti`
- **Purpose**: Retrieve DTI result for decision evaluation

## Sinks

### Process Engine
- **Endpoint**: `POST /api/v1/process/{instance_id}/signal`
- **Purpose**: Signal the process engine with the routing decision

## Audit

Eligibility decisions retained for 7 years per fair lending requirements.
