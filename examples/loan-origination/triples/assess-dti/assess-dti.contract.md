---
contract_id: "ICT-LO-DTI-001"
intent_id: "INT-LO-DTI-001"
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
  - name: "DocVault Checklist"
    protocol: "rest"
    endpoint: "https://docvault.example.com/api/v1/checklists/{loan_number}/status"
    auth: "oauth2"
    schema_ref: "schemas/doc-checklist-status.json"
    sla_ms: 2000
sinks:
  - name: "LOS Database"
    protocol: "rest"
    endpoint: "https://los.example.com/api/v2/applications/{loan_number}/dti"
    auth: "oauth2"
    schema_ref: "schemas/dti-result.json"
    sla_ms: 2000
    idempotency_key: "loan_number+assessment_timestamp"
rule_engines:
  - name: "DTI Calculation Engine"
    version: "3.2"
    endpoint: "https://rules.example.com/api/v1/dti/evaluate"
events:
  - topic: "loan.dti.assessed"
    schema_ref: "schemas/events/dti-assessed.json"
    delivery: "at_least_once"
    key_field: "loan_number"
audit:
  record_type: "dti_assessment"
  retention_years: 7
  fields_required:
    - "loan_number"
    - "front_end_ratio"
    - "back_end_ratio"
    - "eligible"
    - "qm_compliant"
    - "product_type"
    - "timestamp"
  sink: "https://audit.example.com/api/v1/records"
generated_from: "INT-LO-DTI-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PSM"
---

# Integration Contract: Assess Debt-to-Income Ratio

## Sources

### LOS Database
- **Endpoint**: `GET /api/v2/applications/{loan_number}`
- **Purpose**: Retrieve loan application with income data and credit summary

### DocVault Checklist
- **Endpoint**: `GET /api/v1/checklists/{loan_number}/status`
- **Purpose**: Check income documentation completeness

## Rule Engine

### DTI Calculation Engine
- **Version**: 3.2
- **Endpoint**: `POST /api/v1/dti/evaluate`
- **Purpose**: Apply product-specific DTI thresholds and QM rules

## Sinks

### LOS Database
- **Endpoint**: `PUT /api/v2/applications/{loan_number}/dti`
- **Purpose**: Persist DTI results

## Audit

DTI assessment records retained for 7 years per QM/ATR regulatory requirements.
