---
contract_id: "ICT-PA-VAL-001"
contract_name: "Validate Appraisal Completeness Binding"
bpmn_task_id: "Task_ValidateCompleteness"
bpmn_task_name: "Validate Appraisal Completeness"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"

version: "1.0.0"
status: "draft"

generated_from: "CAP-PA-VAL-001 + INT-PA-VAL-001"
generated_date: "2026-04-09"
generated_by: "mda-pipeline"
last_modified: "2026-04-09"
last_modified_by: "mda-pipeline"

owner_role: "Integration Architect"
owner_team: "Mortgage Technology"
reviewers:
  - "Chief Appraiser"
  - "API Platform Lead"

domain: "Mortgage"
subdomain: "Property Appraisal"

capsule_id: "CAP-PA-VAL-001"
intent_id: "INT-PA-VAL-001"

binding_status: "unbound"

input_schema:
  - name: "loan_number"
    type: "string"
    required: true
    description: "Loan identifier for retrieving the report and program type."
    source: "LOS"
    constraints: "pattern: '^LN-[0-9]{10}$'"
  - name: "document_id"
    type: "string"
    required: true
    description: "Document management ID of the appraisal report to validate."
    source: "Task_ReceiveReport"
    constraints: "pattern: '^DOC-[A-Z0-9]{10}$'"
  - name: "loan_program"
    type: "string"
    required: true
    description: "Loan program type determining checklist variant."
    source: "LOS"
    constraints: "enum: [Conventional, FHA, VA, USDA, Jumbo]"
  - name: "uad_data"
    type: "object"
    required: true
    description: "Parsed UAD fields including appraised value, comparables, GLA."
    source: "Task_ReceiveReport"
    constraints: "Must contain appraised_value, comparable_count, gla_sqft"

output_schema:
  - name: "completeness_status"
    type: "string"
    required: true
    description: "Result of the completeness check."
    destination: "Gateway_Complete"
    constraints: "enum: [Complete, Incomplete]"
  - name: "deficiency_codes"
    type: "array"
    required: false
    description: "List of specific checklist items that failed validation."
    destination: "LOS"
    constraints: "Each code matches pattern: '^[A-Z]{3,4}-[0-9]{3}$'"
  - name: "checklist_version"
    type: "string"
    required: true
    description: "Version of the completeness checklist template used."
    destination: "LOS"
    constraints: "pattern: '^CL-[0-9]+\\.[0-9]+$'"
  - name: "validation_timestamp"
    type: "datetime"
    required: true
    description: "ISO 8601 timestamp of when the validation was performed."
    destination: "LOS"
    constraints: "ISO 8601 format"

error_codes:
  - code: "ERR-PA-VAL-001"
    name: "Checklist Template Missing"
    severity: "error"
    description: "No completeness checklist template exists for the specified loan program."
    resolution: "Escalate to Compliance team to create the checklist template."
  - code: "ERR-PA-VAL-002"
    name: "Report Not Found"
    severity: "critical"
    description: "The document ID does not resolve to a stored report."
    resolution: "Verify document management system connectivity and re-run receipt task."
  - code: "ERR-PA-VAL-003"
    name: "UAD Parse Failure"
    severity: "error"
    description: "Required UAD fields could not be extracted from the XML."
    resolution: "Route to manual data entry and notify the AMC."

max_latency_ms: 45000
throughput: "150 validations/hour"
availability: "99.5%"

min_capsule_version: "1.0.0"
min_intent_version: "1.0.0"
breaking_changes: []

api_endpoints:
  - method: "POST"
    path: "/api/v1/appraisal/validate/completeness"
    description: "Execute the completeness checklist against a received appraisal report."
    request_content_type: "application/json"
    response_content_type: "application/json"

gaps: []
---

# Validate Appraisal Completeness Binding

## Binding Rationale

This contract binds **Validate Appraisal Completeness** (`CAP-PA-VAL-001`) to **Apply Appraisal Completeness Checklist** (`INT-PA-VAL-001`).

The binding ensures that the LLM agent performing the completeness check receives properly structured UAD data and produces a standardized completeness determination. Without this contract, validation results could be inconsistent across loan programs and checklist versions.

**Key guarantees:**

- The agent always receives the loan program type so the correct checklist is applied.
- Deficiency codes use a standardized format for downstream processing.
- The checklist version is recorded for audit traceability.

## Change Protocol

All changes to this contract MUST follow this protocol:

1. **Non-breaking changes** (MINOR/PATCH): Adding optional fields, new deficiency codes, documentation.
2. **Breaking changes** (MAJOR): Removing fields, changing checklist code format. Must trigger coordinated updates.
3. **Review and approval**: All changes require reviewer sign-off.

## Decommissioning

This contract may be decommissioned when the completeness validation is replaced or removed. **Data retention:** 7 years per mortgage regulatory requirements.
