---
contract_id: "ICT-PA-ASV-001"
contract_name: "Assess Property Value Binding"
bpmn_task_id: "Task_AssessValue"
bpmn_task_name: "Assess Property Value"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"

version: "1.0.0"
status: "draft"

generated_from: "CAP-PA-ASV-001 + INT-PA-ASV-001"
generated_date: "2026-04-09"
generated_by: "mda-pipeline"
last_modified: "2026-04-09"
last_modified_by: "mda-pipeline"

owner_role: "Integration Architect"
owner_team: "Mortgage Technology"
reviewers:
  - "Chief Appraiser"
  - "Risk Officer"

domain: "Mortgage"
subdomain: "Property Appraisal"

capsule_id: "CAP-PA-ASV-001"
intent_id: "INT-PA-ASV-001"

binding_status: "unbound"

input_schema:
  - name: "loan_number"
    type: "string"
    required: true
    description: "Loan identifier."
    source: "LOS"
    constraints: "pattern: '^LN-[0-9]{10}$'"
  - name: "appraised_value"
    type: "float"
    required: true
    description: "Market value opinion from the appraisal report."
    source: "Task_ReceiveReport"
    constraints: "min: 1000"
  - name: "loan_amount"
    type: "float"
    required: true
    description: "Requested loan amount."
    source: "LOS"
    constraints: "min: 1000"
  - name: "purchase_price"
    type: "float"
    required: false
    description: "Contract purchase price. Required for purchase transactions."
    source: "LOS"
    constraints: "min: 1000 (when present)"
  - name: "transaction_type"
    type: "string"
    required: true
    description: "Purchase or refinance."
    source: "LOS"
    constraints: "enum: [Purchase, Refinance, Cash-Out-Refinance]"
  - name: "loan_program"
    type: "string"
    required: true
    description: "Loan program determining LTV limits."
    source: "LOS"
    constraints: "enum: [Conventional, FHA, VA, USDA, Jumbo, Non-QM]"
  - name: "comparable_sales"
    type: "array"
    required: true
    description: "Array of comparable sale records with prices, dates, and adjustments."
    source: "UAD XML"
    constraints: "minItems: 3"
  - name: "market_conditions"
    type: "string"
    required: false
    description: "Market condition indicator from the appraisal."
    source: "UAD XML"
    constraints: "enum: [Stable, Increasing, Declining]"

output_schema:
  - name: "ltv_ratio"
    type: "float"
    required: true
    description: "Calculated loan-to-value ratio as a percentage."
    destination: "LOS"
    constraints: "min: 0, max: 200"
  - name: "ltv_determination"
    type: "string"
    required: true
    description: "Whether the LTV is within or exceeds program limits."
    destination: "Gateway_LTV"
    constraints: "enum: [Within_LTV, Exceeds_LTV]"
  - name: "max_ltv_threshold"
    type: "float"
    required: true
    description: "Maximum LTV allowed by the loan program."
    destination: "LOS"
    constraints: "min: 0, max: 100"
  - name: "adjustment_flags"
    type: "array"
    required: false
    description: "Flags for comparable adjustments exceeding thresholds."
    destination: "LOS"
    constraints: "Each flag includes comparable_id, flag_type, and value"
  - name: "market_condition_flags"
    type: "array"
    required: false
    description: "Risk flags related to market conditions."
    destination: "LOS"
    constraints: ""
  - name: "value_assessment_summary"
    type: "string"
    required: true
    description: "Narrative summary of the value assessment findings."
    destination: "LOS"
    constraints: "maxLength: 5000"

error_codes:
  - code: "ERR-PA-ASV-001"
    name: "Missing Purchase Price"
    severity: "error"
    description: "Purchase transaction is missing the contract price."
    resolution: "Request the loan officer to update the LOS with the purchase price."
  - code: "ERR-PA-ASV-002"
    name: "LTV Calculation Error"
    severity: "critical"
    description: "The LTV calculation produced a zero, negative, or impossible result."
    resolution: "Log data integrity error and halt processing for manual review."
  - code: "ERR-PA-ASV-003"
    name: "Insufficient Comparables"
    severity: "error"
    description: "Fewer than three comparable sales available for analysis."
    resolution: "This should have been caught in completeness validation; re-route to validation."
  - code: "ERR-PA-ASV-004"
    name: "MLS Data Unavailable"
    severity: "warning"
    description: "Comparable sales could not be cross-referenced against MLS data."
    resolution: "Proceed with appraiser-reported data and flag as Unverified Comparables."

max_latency_ms: 60000
throughput: "100 assessments/hour"
availability: "99.5%"

min_capsule_version: "1.0.0"
min_intent_version: "1.0.0"
breaking_changes: []

api_endpoints:
  - method: "POST"
    path: "/api/v1/appraisal/assess/value"
    description: "Calculate LTV and assess property value adequacy."
    request_content_type: "application/json"
    response_content_type: "application/json"
  - method: "GET"
    path: "/api/v1/market-data/comparables"
    description: "Retrieve MLS comparable sales data for cross-validation."
    response_content_type: "application/json"

gaps:
  - "MLS API integration pending vendor contract -- Integration Architect tracking"
---

# Assess Property Value Binding

## Binding Rationale

This contract binds **Assess Property Value** (`CAP-PA-ASV-001`) to **Calculate LTV and Assess Collateral Adequacy** (`INT-PA-ASV-001`).

The binding ensures the hybrid agent receives all necessary inputs for LTV calculation and comparable analysis, and produces a standardized output that drives the downstream LTV gateway. Without this contract, LTV calculations could use inconsistent denominators (appraised value vs. purchase price) or miss adjustment threshold violations.

**Key guarantees:**

- LTV calculation always uses the correct denominator based on transaction type.
- Comparable adjustment thresholds (15% net / 25% gross) are enforced.
- The routing decision is based on the calculated LTV vs. program-specific maximum.

## Change Protocol

1. **Non-breaking changes** (MINOR/PATCH): Adding optional fields, new error codes, documentation.
2. **Breaking changes** (MAJOR): Changing LTV calculation logic, modifying threshold values. Must trigger coordinated updates.
3. **Review and approval**: All changes require reviewer sign-off.

## Decommissioning

This contract may be decommissioned when the value assessment is replaced. **Data retention:** 7 years per mortgage regulatory requirements.
