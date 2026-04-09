---
contract_id: "ICT-PA-NTF-001"
contract_name: "Emit Appraisal Complete Binding"
bpmn_task_id: "Task_EmitComplete"
bpmn_task_name: "Emit Appraisal Complete Event"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"

version: "1.0.0"
status: "draft"

generated_from: "CAP-PA-NTF-001 + INT-PA-NTF-001"
generated_date: "2026-04-09"
generated_by: "mda-pipeline"
last_modified: "2026-04-09"
last_modified_by: "mda-pipeline"

owner_role: "Integration Architect"
owner_team: "Mortgage Technology"
reviewers:
  - "Loan Processing Manager"
  - "API Platform Lead"

domain: "Mortgage"
subdomain: "Property Appraisal"

capsule_id: "CAP-PA-NTF-001"
intent_id: "INT-PA-NTF-001"

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
    description: "Final appraised value."
    source: "LOS"
    constraints: "min: 1000"
  - name: "ltv_ratio"
    type: "float"
    required: true
    description: "Calculated LTV ratio."
    source: "Task_AssessValue"
    constraints: "min: 0, max: 100"
  - name: "effective_date"
    type: "date"
    required: true
    description: "Appraisal effective date."
    source: "LOS"
    constraints: ""
  - name: "rate_lock_expiration"
    type: "date"
    required: false
    description: "Rate lock expiration date for alert checking."
    source: "LOS"
    constraints: ""

output_schema:
  - name: "event_id"
    type: "string"
    required: true
    description: "Unique identifier for the published completion event."
    destination: "Event Bus"
    constraints: "pattern: '^EVT-[A-Z0-9]{12}$'"
  - name: "event_timestamp"
    type: "datetime"
    required: true
    description: "Timestamp when the event was published."
    destination: "Audit Trail"
    constraints: "ISO 8601 format"
  - name: "delivery_trigger_id"
    type: "string"
    required: true
    description: "Reference ID for the borrower appraisal delivery workflow."
    destination: "Disclosure System"
    constraints: "pattern: '^DLV-[A-Z0-9]{10}$'"
  - name: "lock_alert_required"
    type: "boolean"
    required: true
    description: "Whether a rate lock expiration alert was generated."
    destination: "LOS"
    constraints: ""

error_codes:
  - code: "ERR-PA-NTF-001"
    name: "Event Bus Unavailable"
    severity: "error"
    description: "The enterprise event bus is not accepting messages."
    resolution: "Queue the event for retry with exponential backoff. Proceed with LOS update."
  - code: "ERR-PA-NTF-002"
    name: "Borrower Delivery Failure"
    severity: "error"
    description: "The disclosure system could not accept the delivery trigger."
    resolution: "Flag for manual delivery and alert the loan officer."

max_latency_ms: 10000
throughput: "500 events/hour"
availability: "99.9%"

min_capsule_version: "1.0.0"
min_intent_version: "1.0.0"
breaking_changes: []

api_endpoints:
  - method: "POST"
    path: "/api/v1/events/appraisal-complete"
    description: "Publish an appraisal completion domain event."
    request_content_type: "application/json"
    response_content_type: "application/json"
  - method: "POST"
    path: "/api/v1/disclosures/appraisal-delivery"
    description: "Trigger borrower appraisal report delivery."
    request_content_type: "application/json"
    response_content_type: "application/json"

gaps: []
---

# Emit Appraisal Complete Binding

## Binding Rationale

This contract binds **Emit Appraisal Complete Event** (`CAP-PA-NTF-001`) to **Publish Appraisal Completion Event** (`INT-PA-NTF-001`).

The binding ensures that the completion event payload is structured consistently for all downstream consumers (underwriting, closing, investor commitment) and that the borrower delivery is always triggered alongside the event. Without this contract, event schema drift could cause downstream processing failures.

**Key guarantees:**

- The event payload always includes the appraised value, LTV ratio, and effective date.
- The borrower delivery trigger is coupled with the completion event.
- Rate lock expiration alerts are checked automatically.

## Change Protocol

1. **Non-breaking changes** (MINOR/PATCH): Adding optional fields, new error codes, documentation.
2. **Breaking changes** (MAJOR): Changing event schema, removing required fields. Must trigger coordinated updates with all event consumers.
3. **Review and approval**: All changes require reviewer sign-off.

## Decommissioning

This contract may be decommissioned when the notification process is replaced. **Data retention:** 7 years per mortgage regulatory requirements.
