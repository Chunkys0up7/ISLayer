---
contract_id: "ICT-IV-W2V-001"
intent_id: "INT-IV-W2V-001"
version: "1.0"
status: "draft"
binding_status: "unbound"
sources:
  - name: "DocVault W-2 Retrieval API"
    protocol: "rest"
    endpoint: "https://docvault.example.com/api/v1/documents/borrower/{borrowerId}/w2"
    auth: "api_key"
    schema_ref: "schemas/w2-document.json"
    sla_ms: 5000
  - name: "DocVault Tax Return Retrieval API"
    protocol: "rest"
    endpoint: "https://docvault.example.com/api/v1/documents/borrower/{borrowerId}/1040"
    auth: "api_key"
    schema_ref: "schemas/tax-return-1040.json"
    sla_ms: 5000
  - name: "IRS IVES Transcript Service"
    protocol: "rest"
    endpoint: "https://ives.example.com/api/v1/irs/ives/request-transcript"
    auth: "mtls_oauth2"
    schema_ref: "schemas/ives-request.json"
    sla_ms: 30000
sinks: []
events: []
audit:
  record_type: "w2_income_verification"
  retention_years: 7
  fields_required:
    - "borrowerId"
    - "loanApplicationId"
    - "verifiedAnnualIncome"
    - "incomeTrend"
    - "timestamp"
    - "agent_id"
  sink: "https://audit.example.com/api/v1/records"
generated_from: "INT-IV-W2V-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PSM"
unbound_sources:
  - "IVES integration is optional; many lenders rely on borrower-provided transcripts uploaded to DocVault"
  - "OCR extraction confidence threshold for auto-acceptance is not yet defined (suggested: 0.95)"
  - "Tax year calculation logic must account for filing deadlines"
unbound_sinks: []
---

# Integration Contract: Verify W-2 Income

## Sources

### DocVault W-2 Retrieval API (Outbound)
- **Protocol**: REST (HTTPS)
- **Endpoint**: `GET /api/v1/documents/borrower/{borrowerId}/w2?taxYears={year1},{year2}`
- **Authentication**: API Key (Header: X-DocVault-Key)
- **SLA**: 5,000 ms

### DocVault Tax Return Retrieval API (Outbound)
- **Protocol**: REST (HTTPS)
- **Endpoint**: `GET /api/v1/documents/borrower/{borrowerId}/1040?taxYears={year1},{year2}`
- **Authentication**: API Key (Header: X-DocVault-Key)
- **SLA**: 5,000 ms

### IRS IVES Transcript Service (Outbound, Optional)
- **Protocol**: REST (HTTPS) with mTLS
- **Endpoint**: `POST /api/v1/irs/ives/request-transcript`
- **Authentication**: mTLS + OAuth 2.0
- **SLA**: 30,000 ms (asynchronous -- returns request ID)

## Audit

All W-2 income verification actions are logged with 7-year retention per federal lending regulations.
