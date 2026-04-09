---
contract_id: "ICT-IV-SEI-001"
intent_id: "INT-IV-SEI-001"
version: "1.0"
status: "draft"
binding_status: "unbound"
sources:
  - name: "DocVault Tax Return Retrieval API"
    protocol: "rest"
    endpoint: "https://docvault.example.com/api/v1/documents/borrower/{borrowerId}/tax-returns"
    auth: "api_key"
    schema_ref: "schemas/tax-return-schedules.json"
    sla_ms: 5000
  - name: "DocVault Corporate Return Retrieval API"
    protocol: "rest"
    endpoint: "https://docvault.example.com/api/v1/documents/business/{entityEin}/corporate-returns"
    auth: "api_key"
    schema_ref: "schemas/corporate-return.json"
    sla_ms: 5000
  - name: "RuleEngine Cash Flow Analysis API"
    protocol: "rest"
    endpoint: "https://rules.example.com/api/v1/rules/cash-flow-analysis/execute"
    auth: "oauth2"
    schema_ref: "schemas/cash-flow-request.json"
    sla_ms: 5000
sinks: []
events: []
rule_engines:
  - name: "Cash Flow Analysis Rules"
    type: "DMN"
    decision_table_id: "DT-IV-CASH-FLOW"
    version: "pending"
audit:
  record_type: "self_employment_income_verification"
  retention_years: 7
  fields_required:
    - "borrowerId"
    - "loanApplicationId"
    - "qualifyingSelfEmploymentAnnual"
    - "businessViabilityStatus"
    - "incomeTrend"
    - "timestamp"
    - "agent_id"
  sink: "https://audit.example.com/api/v1/records"
generated_from: "INT-IV-SEI-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PSM"
unbound_sources:
  - "Cash flow analysis rule set must implement both FHA Form 92900-WS and Fannie Mae Form 1084 variants"
  - "Corporate return retrieval requires entity EIN sourced from K-1 data"
  - "Business viability check integration (Secretary of State API or similar) is not yet designed"
unbound_sinks: []
---

# Integration Contract: Verify Self-Employment Income

## Sources

### DocVault Tax Return Retrieval API (Outbound)
- **Protocol**: REST (HTTPS)
- **Endpoint**: `GET /api/v1/documents/borrower/{borrowerId}/tax-returns?taxYears={year1},{year2}&includeSchedules=C,E,K1`
- **Authentication**: API Key (Header: X-DocVault-Key)
- **SLA**: 5,000 ms

### DocVault Corporate Return Retrieval API (Outbound, Conditional)
- **Protocol**: REST (HTTPS)
- **Endpoint**: `GET /api/v1/documents/business/{entityEin}/corporate-returns?taxYears={year1},{year2}`
- **Authentication**: API Key (Header: X-DocVault-Key)
- **SLA**: 5,000 ms

### RuleEngine Cash Flow Analysis API (Outbound)
- **Protocol**: REST (HTTPS)
- **Endpoint**: `POST /api/v1/rules/cash-flow-analysis/execute`
- **Authentication**: OAuth 2.0 Client Credentials
- **SLA**: 5,000 ms

## Audit

All self-employment income verification actions are logged with 7-year retention per federal lending regulations.
