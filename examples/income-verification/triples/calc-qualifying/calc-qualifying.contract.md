---
contract_id: "ICT-IV-QAL-001"
intent_id: "INT-IV-QAL-001"
version: "1.0"
status: "draft"
binding_status: "unbound"
sources:
  - name: "RuleEngine Income Aggregation API"
    protocol: "rest"
    endpoint: "https://rules.example.com/api/v1/rules/income-aggregation/execute"
    auth: "oauth2"
    schema_ref: "schemas/income-aggregation-request.json"
    sla_ms: 3000
sinks: []
events: []
rule_engines:
  - name: "Income Aggregation Rules"
    type: "DMN"
    decision_table_id: "DT-IV-INCOME-AGG"
    version: "pending"
audit:
  record_type: "qualifying_income_calculation"
  retention_years: 7
  fields_required:
    - "borrowerId"
    - "loanApplicationId"
    - "totalQualifyingMonthlyIncome"
    - "variancePercent"
    - "varianceStatus"
    - "timestamp"
    - "agent_id"
  sink: "https://audit.example.com/api/v1/records"
generated_from: "INT-IV-QAL-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PSM"
unbound_sources:
  - "RuleEngine must support program-specific variance thresholds configurable per loan program"
  - "Income aggregation rules should be versioned and auditable for regulatory examination"
  - "USDA program requires additional household income check against area median income limits (integration not yet designed)"
unbound_sinks: []
---

# Integration Contract: Calculate Qualifying Income

## Sources

### RuleEngine Income Aggregation API (Outbound)
- **Protocol**: REST (HTTPS)
- **Endpoint**: `POST /api/v1/rules/income-aggregation/execute`
- **Authentication**: OAuth 2.0 Client Credentials
- **SLA**: 3,000 ms

## Events

No outbound events. Income result is stored in process context for downstream consumption.

## Audit

All qualifying income calculations are logged with 7-year retention per federal lending regulations.
