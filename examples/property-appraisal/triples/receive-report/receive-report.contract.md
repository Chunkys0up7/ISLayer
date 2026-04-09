---
contract_id: "ICT-PA-RCV-001"
contract_name: "Receive Appraisal Report Binding"
bpmn_task_id: "Task_ReceiveReport"
bpmn_task_name: "Receive Appraisal Report"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"

version: "1.0.0"
status: "draft"
mda_layer: "PSM"

generated_from: "CAP-PA-RCV-001 + INT-PA-RCV-001"
generated_date: "2026-04-09"
generated_by: "mda-pipeline"
last_modified: "2026-04-09"
last_modified_by: "mda-pipeline"

owner_role: "Integration Architect"
owner_team: "Mortgage Technology"
reviewers:
  - "Appraisal Desk Supervisor"
  - "API Platform Lead"

domain: "Mortgage"
subdomain: "Property Appraisal"

capsule_id: "CAP-PA-RCV-001"
intent_id: "INT-PA-RCV-001"

binding_status: "unbound"

input_schema:
  - name: "order_confirmation_id"
    type: "string"
    required: true
    description: "AMC order confirmation ID linking the report to the original order."
    source: "Appraisal Portal"
    constraints: "pattern: '^ORD-[A-Z0-9]{12}$'"
  - name: "report_pdf"
    type: "string"
    required: true
    description: "Base64-encoded appraisal report PDF or a presigned URL."
    source: "Appraisal Portal"
    constraints: "Non-empty; valid PDF header"
  - name: "uad_xml"
    type: "string"
    required: true
    description: "MISMO UAD XML payload containing structured appraisal data."
    source: "Appraisal Portal"
    constraints: "Valid XML conforming to MISMO 3.4 UAD schema"
  - name: "is_revision"
    type: "boolean"
    required: false
    description: "Indicates whether this report is a revision of a prior submission."
    source: "Appraisal Portal"
    constraints: ""

output_schema:
  - name: "document_id"
    type: "string"
    required: true
    description: "Document management system ID for the stored report."
    destination: "LOS"
    constraints: "pattern: '^DOC-[A-Z0-9]{10}$'"
  - name: "appraised_value"
    type: "float"
    required: true
    description: "Market value opinion from the appraisal report."
    destination: "LOS"
    constraints: "min: 0"
  - name: "effective_date"
    type: "date"
    required: true
    description: "Date of the appraisal inspection or effective valuation date."
    destination: "LOS"
    constraints: "Must be within 120 days of expected closing"
  - name: "appraiser_license_number"
    type: "string"
    required: true
    description: "State license or certification number of the signing appraiser."
    destination: "LOS"
    constraints: "Non-empty"
  - name: "report_status"
    type: "string"
    required: true
    description: "Status assigned upon receipt."
    destination: "LOS"
    constraints: "enum: [Received, Received-Revision]"

error_codes:
  - code: "ERR-PA-RCV-001"
    name: "Corrupt PDF"
    severity: "error"
    description: "The delivered PDF file is corrupt or unreadable."
    resolution: "Reject delivery and request re-submission from the AMC."
  - code: "ERR-PA-RCV-002"
    name: "UAD XML Invalid"
    severity: "error"
    description: "The UAD XML does not conform to the MISMO schema."
    resolution: "Flag for manual data entry and notify AMC of the defect."
  - code: "ERR-PA-RCV-003"
    name: "Orphaned Report"
    severity: "warning"
    description: "The order confirmation ID does not match any active loan."
    resolution: "Quarantine the report and alert the appraisal desk."

max_latency_ms: 15000
throughput: "300 reports/hour"
availability: "99.5%"

min_capsule_version: "1.0.0"
min_intent_version: "1.0.0"
breaking_changes: []

api_endpoints:
  - method: "POST"
    path: "/api/v1/appraisal/reports/ingest"
    description: "Receive and ingest an appraisal report delivery."
    request_content_type: "multipart/form-data"
    response_content_type: "application/json"

gaps: []
---

# Receive Appraisal Report Binding

## Binding Rationale

This contract binds **Receive Appraisal Report** (`CAP-PA-RCV-001`) to **Ingest and Index Appraisal Report** (`INT-PA-RCV-001`).

The binding ensures that inbound appraisal reports from the AMC portal are parsed, stored, and indexed with a consistent schema. Without this contract, reports could be ingested without proper UAD extraction, leading to missing appraised values in the loan file and downstream LTV calculation failures.

**Key guarantees:**

- Every ingested report produces a document management ID traceable to the loan.
- Appraised value and effective date are always extracted and recorded.
- Corrupt or orphaned reports are never silently accepted.

## Change Protocol

All changes to this contract MUST follow this protocol:

1. **Non-breaking changes** (MINOR/PATCH): Adding optional fields, new error codes, documentation updates.
2. **Breaking changes** (MAJOR): Removing fields, changing required status, altering error semantics. Must trigger coordinated updates.
3. **Review and approval**: All changes require reviewer sign-off.

## Decommissioning

This contract may be decommissioned when the report ingestion process is replaced or the parent task is removed. **Data retention:** 7 years per mortgage regulatory requirements.
