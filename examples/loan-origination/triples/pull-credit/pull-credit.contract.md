---
contract_id: "ICT-LO-CRC-001"
intent_id: "INT-LO-CRC-001"
version: "1.0"
status: "draft"
binding_status: "unbound"
sources:
  - name: "LOS Database"
    protocol: "rest"
    endpoint: "https://los.example.com/api/v2/borrowers/{borrower_id}/profile"
    auth: "oauth2"
    schema_ref: "schemas/borrower-profile.json"
    sla_ms: 1000
  - name: "DocVault"
    protocol: "rest"
    endpoint: "https://docvault.example.com/api/v1/documents?type=credit_auth&loan={loan_number}"
    auth: "oauth2"
    schema_ref: "schemas/credit-auth.json"
    sla_ms: 2000
  - name: "CreditBureau Tri-Merge Service"
    protocol: "rest"
    endpoint: "https://cra-gateway.example.com/api/v1/trimerge"
    auth: "mtls"
    schema_ref: "schemas/trimerge-request.json"
    sla_ms: 60000
sinks:
  - name: "DocVault"
    protocol: "rest"
    endpoint: "https://docvault.example.com/api/v1/documents"
    auth: "oauth2"
    schema_ref: "schemas/credit-report-upload.json"
    sla_ms: 5000
    idempotency_key: "loan_number+pull_date"
  - name: "LOS Database"
    protocol: "rest"
    endpoint: "https://los.example.com/api/v2/applications/{loan_number}/credit"
    auth: "oauth2"
    schema_ref: "schemas/credit-summary.json"
    sla_ms: 2000
events:
  - topic: "loan.credit.report.received"
    schema_ref: "schemas/events/credit-report-received.json"
    delivery: "at_least_once"
    key_field: "loan_number"
audit:
  record_type: "credit_pull"
  retention_years: 7
  fields_required:
    - "loan_number"
    - "borrower_ssn_masked"
    - "bureaus_queried"
    - "representative_score"
    - "pull_timestamp"
    - "permissible_purpose"
  sink: "https://audit.example.com/api/v1/records"
generated_from: "INT-LO-CRC-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PSM"
---

# Integration Contract: Pull Credit Report

## Sources

### CreditBureau Tri-Merge Service
- **Protocol**: REST (mTLS)
- **Endpoint**: `POST /api/v1/trimerge`
- **SLA**: 60,000 ms (credit bureau responses can be slow)
- **Format**: MISMO XML response

## Sinks

### DocVault
- **Endpoint**: `POST /api/v1/documents`
- **Purpose**: Store full credit report

### LOS Database
- **Endpoint**: `PUT /api/v2/applications/{loan_number}/credit`
- **Purpose**: Persist credit scores and tradeline summary

## Audit

Credit pull records retained for 7 years. Must log permissible purpose and all bureaus queried per FCRA.
