---
contract_id: "ICT-LO-PKG-001"
intent_id: "INT-LO-PKG-001"
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
  - name: "DocVault"
    protocol: "rest"
    endpoint: "https://docvault.example.com/api/v1/documents?loan={loan_number}"
    auth: "oauth2"
    schema_ref: "schemas/document-list.json"
    sla_ms: 5000
sinks:
  - name: "LOS Database"
    protocol: "rest"
    endpoint: "https://los.example.com/api/v2/applications/{loan_number}/package"
    auth: "oauth2"
    schema_ref: "schemas/loan-package.json"
    sla_ms: 5000
    idempotency_key: "loan_number+package_version"
events:
  - topic: "loan.file.packaged"
    schema_ref: "schemas/events/file-packaged.json"
    delivery: "at_least_once"
    key_field: "loan_number"
audit:
  record_type: "loan_packaging"
  retention_years: 7
  fields_required:
    - "loan_number"
    - "document_count"
    - "qc_result"
    - "processor_id"
    - "timestamp"
  sink: "https://audit.example.com/api/v1/records"
generated_from: "INT-LO-PKG-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PSM"
---

# Integration Contract: Package Loan File

## Sources

### LOS Database
- **Endpoint**: `GET /api/v2/applications/{loan_number}`
- **Purpose**: Retrieve full loan application data and assessment results

### DocVault
- **Endpoint**: `GET /api/v1/documents?loan={loan_number}`
- **Purpose**: Retrieve all supporting documents for the loan

## Sinks

### LOS Database
- **Endpoint**: `PUT /api/v2/applications/{loan_number}/package`
- **Purpose**: Persist the assembled loan file package with QC results

## Audit

Loan packaging records retained for 7 years. Must log document count, QC result, and processor identity.
