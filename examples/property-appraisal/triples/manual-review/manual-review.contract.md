---
contract_id: "ICT-PA-MRV-001"
contract_name: "Manual Appraisal Review Binding"
bpmn_task_id: "Task_ManualReview"
bpmn_task_name: "Flag for Manual Review"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"

version: "1.0.0"
status: "draft"
mda_layer: "PSM"

generated_from: "CAP-PA-MRV-001 + INT-PA-MRV-001"
generated_date: "2026-04-09"
generated_by: "mda-pipeline"
last_modified: "2026-04-09"
last_modified_by: "mda-pipeline"

owner_role: "Integration Architect"
owner_team: "Mortgage Technology"
reviewers:
  - "Underwriting Manager"
  - "Risk Officer"

domain: "Mortgage"
subdomain: "Property Appraisal"

capsule_id: "CAP-PA-MRV-001"
intent_id: "INT-PA-MRV-001"

binding_status: "unbound"

input_schema:
  - name: "loan_number"
    type: "string"
    required: true
    description: "Loan identifier."
    source: "LOS"
    constraints: "pattern: '^LN-[0-9]{10}$'"
  - name: "ltv_ratio"
    type: "float"
    required: true
    description: "Calculated LTV ratio."
    source: "Task_AssessValue"
    constraints: "min: 0"
  - name: "ltv_determination"
    type: "string"
    required: true
    description: "LTV routing decision."
    source: "Task_AssessValue"
    constraints: "enum: [Exceeds_LTV]"
  - name: "adjustment_flags"
    type: "array"
    required: false
    description: "Comparable adjustment flags from the value assessment."
    source: "Task_AssessValue"
    constraints: ""
  - name: "value_assessment_summary"
    type: "string"
    required: true
    description: "Summary of value assessment findings."
    source: "Task_AssessValue"
    constraints: "maxLength: 5000"
  - name: "document_id"
    type: "string"
    required: true
    description: "Document management ID of the appraisal report."
    source: "LOS"
    constraints: "pattern: '^DOC-[A-Z0-9]{10}$'"

output_schema:
  - name: "review_decision"
    type: "string"
    required: true
    description: "Underwriter's decision on the appraisal."
    destination: "LOS"
    constraints: "enum: [Accept, Conditional_Accept, Request_Additional_Work, Deny]"
  - name: "decision_rationale"
    type: "string"
    required: true
    description: "Written explanation supporting the decision."
    destination: "LOS"
    constraints: "minLength: 50, maxLength: 10000"
  - name: "conditions"
    type: "array"
    required: false
    description: "List of conditions imposed with the decision."
    destination: "LOS"
    constraints: ""
  - name: "reviewer_id"
    type: "string"
    required: true
    description: "Identifier of the underwriter who performed the review."
    destination: "Audit Trail"
    constraints: "pattern: '^UW-[0-9]{6}$'"

error_codes:
  - code: "ERR-PA-MRV-001"
    name: "No Qualified Reviewer"
    severity: "error"
    description: "No underwriter with required qualifications is available."
    resolution: "Escalate to Underwriting Manager for manual assignment."
  - code: "ERR-PA-MRV-002"
    name: "SLA Breach"
    severity: "warning"
    description: "The review was not completed within the 2 business day SLA."
    resolution: "Auto-escalate to Underwriting Manager."

max_latency_ms: 172800000
throughput: "50 reviews/day"
availability: "99.0%"

min_capsule_version: "1.0.0"
min_intent_version: "1.0.0"
breaking_changes: []

api_endpoints:
  - method: "POST"
    path: "/api/v1/underwriting/review/appraisal"
    description: "Create a manual appraisal review task in the underwriting queue."
    request_content_type: "application/json"
    response_content_type: "application/json"
  - method: "PUT"
    path: "/api/v1/underwriting/review/{review_id}/decision"
    description: "Record the underwriter's review decision."
    request_content_type: "application/json"
    response_content_type: "application/json"

gaps: []
---

# Manual Appraisal Review Binding

## Binding Rationale

This contract binds **Flag for Manual Review** (`CAP-PA-MRV-001`) to **Prepare and Route Manual Appraisal Review** (`INT-PA-MRV-001`).

The binding ensures the review package sent to the underwriter contains all necessary context for an informed decision. Without this contract, review packages could be incomplete, causing the underwriter to request additional information and extending the review timeline.

**Key guarantees:**

- The review package always includes the LTV calculation, risk flags, and the full appraisal report.
- The underwriter's decision must include a rationale of at least 50 characters.
- Reviewer qualifications are verified before assignment.

## Change Protocol

1. **Non-breaking changes** (MINOR/PATCH): Adding optional fields, new error codes, documentation.
2. **Breaking changes** (MAJOR): Changing decision enum values, modifying rationale requirements. Must trigger coordinated updates.
3. **Review and approval**: All changes require reviewer sign-off.

## Decommissioning

This contract may be decommissioned when the manual review process is replaced. **Data retention:** 7 years per mortgage regulatory requirements.
