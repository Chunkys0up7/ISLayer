---
contract_id: "ICT-PA-REV-001"
contract_name: "Request Appraisal Revision Binding"
bpmn_task_id: "Task_RequestRevision"
bpmn_task_name: "Request Appraisal Revision"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"

version: "1.0.0"
status: "draft"

generated_from: "CAP-PA-REV-001 + INT-PA-REV-001"
generated_date: "2026-04-09"
generated_by: "mda-pipeline"
last_modified: "2026-04-09"
last_modified_by: "mda-pipeline"

owner_role: "Integration Architect"
owner_team: "Mortgage Technology"
reviewers:
  - "Chief Appraiser"
  - "Compliance Officer"

domain: "Mortgage"
subdomain: "Property Appraisal"

capsule_id: "CAP-PA-REV-001"
intent_id: "INT-PA-REV-001"

binding_status: "unbound"

input_schema:
  - name: "order_confirmation_id"
    type: "string"
    required: true
    description: "AMC order reference for the appraisal engagement."
    source: "LOS"
    constraints: "pattern: '^ORD-[A-Z0-9]{12}$'"
  - name: "deficiency_codes"
    type: "array"
    required: true
    description: "List of deficiency codes from the completeness check."
    source: "Task_ValidateCompleteness"
    constraints: "minItems: 1; each code matches pattern: '^[A-Z]{3,4}-[0-9]{3}$'"
  - name: "revision_count"
    type: "integer"
    required: true
    description: "Number of prior revision requests for this engagement."
    source: "LOS"
    constraints: "min: 0, max: 2"

output_schema:
  - name: "revision_request_id"
    type: "string"
    required: true
    description: "Unique ID assigned to this revision request."
    destination: "LOS"
    constraints: "pattern: '^REV-[A-Z0-9]{10}$'"
  - name: "revision_status"
    type: "string"
    required: true
    description: "Status of the revision request."
    destination: "LOS"
    constraints: "enum: [Submitted, Acknowledged]"
  - name: "expected_revision_date"
    type: "date"
    required: true
    description: "Date by which the revised report is expected."
    destination: "LOS"
    constraints: "Must be within 10 business days of request date"

error_codes:
  - code: "ERR-PA-REV-001"
    name: "Max Revisions Exceeded"
    severity: "error"
    description: "The engagement has reached the maximum number of revision requests."
    resolution: "Escalate to Chief Appraiser for a new appraisal order."
  - code: "ERR-PA-REV-002"
    name: "Value Influence Detected"
    severity: "critical"
    description: "The revision request contains language that could influence the appraised value."
    resolution: "Block transmission and route to appraisal desk for manual review."

max_latency_ms: 20000
throughput: "100 requests/hour"
availability: "99.5%"

min_capsule_version: "1.0.0"
min_intent_version: "1.0.0"
breaking_changes: []

api_endpoints:
  - method: "POST"
    path: "/api/v1/appraisal/orders/{order_id}/revision"
    description: "Submit a revision request for a received appraisal report."
    request_content_type: "application/json"
    response_content_type: "application/json"

gaps: []
---

# Request Appraisal Revision Binding

## Binding Rationale

This contract binds **Request Appraisal Revision** (`CAP-PA-REV-001`) to **Compose and Transmit Appraisal Revision Request** (`INT-PA-REV-001`).

The binding ensures that revision requests are structured consistently, reference valid deficiency codes, and pass through compliance filtering before reaching the AMC. Without this contract, revision requests could contain unstructured or value-influencing language, creating regulatory risk.

**Key guarantees:**

- Deficiency codes from the validation step map directly to the revision request payload.
- The revision count is enforced at the contract level.
- Value-influencing language is detected and blocked before transmission.

## Change Protocol

1. **Non-breaking changes** (MINOR/PATCH): Adding optional fields, new error codes, documentation.
2. **Breaking changes** (MAJOR): Changing deficiency code format, removing fields. Must trigger coordinated updates.
3. **Review and approval**: All changes require reviewer sign-off.

## Decommissioning

This contract may be decommissioned when the revision process is replaced. **Data retention:** 7 years per mortgage regulatory requirements.
