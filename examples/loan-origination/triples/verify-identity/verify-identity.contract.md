---
contract_id: "ICT-LO-IDV-001"
intent_id: "INT-LO-IDV-001"
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
    endpoint: "https://docvault.example.com/api/v1/documents/{document_id}/binary"
    auth: "oauth2"
    schema_ref: "schemas/id-document.json"
    sla_ms: 3000
  - name: "Identity Verification Service"
    protocol: "rest"
    endpoint: "https://idv.example.com/api/v1/verify"
    auth: "api_key"
    schema_ref: "schemas/idv-request.json"
    sla_ms: 15000
  - name: "OFAC Screening Service"
    protocol: "rest"
    endpoint: "https://compliance.example.com/api/v1/ofac/screen"
    auth: "mtls"
    schema_ref: "schemas/ofac-request.json"
    sla_ms: 5000
sinks:
  - name: "LOS Database"
    protocol: "rest"
    endpoint: "https://los.example.com/api/v2/applications/{loan_number}/identity"
    auth: "oauth2"
    schema_ref: "schemas/identity-result.json"
    sla_ms: 2000
    idempotency_key: "loan_number"
  - name: "Compliance Database"
    protocol: "rest"
    endpoint: "https://compliance.example.com/api/v1/cip/records"
    auth: "mtls"
    schema_ref: "schemas/cip-record.json"
    sla_ms: 3000
events:
  - topic: "loan.identity.verified"
    schema_ref: "schemas/events/identity-verified.json"
    delivery: "at_least_once"
    key_field: "loan_number"
  - topic: "loan.identity.flagged"
    schema_ref: "schemas/events/identity-flagged.json"
    delivery: "at_least_once"
    key_field: "loan_number"
audit:
  record_type: "identity_verification"
  retention_years: 7
  fields_required:
    - "loan_number"
    - "borrower_ssn_masked"
    - "verification_score"
    - "ofac_result"
    - "data_sources_used"
    - "timestamp"
  sink: "https://audit.example.com/api/v1/records"
generated_from: "INT-LO-IDV-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PSM"
---

# Integration Contract: Verify Borrower Identity

## Sources

### LOS Database
- **Protocol**: REST
- **Endpoint**: `GET /api/v2/borrowers/{borrower_id}/profile`
- **Purpose**: Retrieve borrower profile for verification

### DocVault
- **Protocol**: REST
- **Endpoint**: `GET /api/v1/documents/{document_id}/binary`
- **Purpose**: Retrieve government ID image for document authentication

### Identity Verification Service
- **Protocol**: REST
- **Endpoint**: `POST /api/v1/verify`
- **Purpose**: Cross-reference borrower identity against public records

### OFAC Screening Service
- **Protocol**: REST (mTLS)
- **Endpoint**: `POST /api/v1/ofac/screen`
- **Purpose**: Screen against sanctions lists

## Sinks

### LOS Database
- **Endpoint**: `PUT /api/v2/applications/{loan_number}/identity`
- **Idempotency**: Keyed on `loan_number`

### Compliance Database
- **Endpoint**: `POST /api/v1/cip/records`
- **Purpose**: CIP compliance audit trail

## Audit

Identity verification records retained for 7 years per BSA/AML regulations.
