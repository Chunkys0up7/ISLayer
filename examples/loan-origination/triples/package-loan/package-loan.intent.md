---
intent_id: "INT-LO-PKG-001"
capsule_id: "CAP-LO-PKG-001"
bpmn_task_id: "Task_PackageLoan"
version: "1.0"
status: "draft"
goal: "Assemble a complete, quality-checked loan file package from all application materials, verifications, and assessments, ready for underwriting submission."
goal_type: "data_production"
preconditions:
  - "DTI assessment has passed (dti_result.eligible == true and dti_result.docs_complete == true)."
  - "All required documents are on file in DocVault."
  - "Identity verification and credit report are current and valid."
inputs:
  - name: "loan_application"
    source: "LOS Database"
    schema_ref: "schemas/loan-application.json"
    required: true
  - name: "credit_report"
    source: "DocVault"
    schema_ref: "schemas/credit-report.json"
    required: true
  - name: "dti_result"
    source: "LOS Database"
    schema_ref: "schemas/dti-result.json"
    required: true
  - name: "supporting_documents"
    source: "DocVault"
    schema_ref: "schemas/document-list.json"
    required: true
outputs:
  - name: "packaged_loan_file"
    type: "object"
    sink: "LOS Database"
    invariants:
      - "packaged_loan_file.qc_status == 'pass'"
      - "packaged_loan_file.document_count matches checklist requirements"
      - "packaged_loan_file.data_reconciliation_status == 'consistent'"
  - name: "qc_checklist_result"
    type: "object"
    sink: "LOS Database"
  - name: "processor_cover_memo"
    type: "string"
    sink: "LOS Database"
invariants:
  - "Processor does not make eligibility or credit decisions."
  - "No expired documents are included in the package."
success_criteria:
  - "All required documents are present and current."
  - "Data reconciliation passes with no unresolved discrepancies."
  - "Automated QC checklist returns a pass result."
  - "Cover memo is attached summarizing the loan file."
failure_modes:
  - mode: "Missing required documents after eligible determination"
    detection: "Document checklist audit shows gaps"
    action: "Return to loan officer for resolution, do not submit to underwriting"
  - mode: "Data reconciliation failure"
    detection: "Cross-check reveals conflicting data between documents"
    action: "Flag discrepancies, route to loan officer for clarification"
  - mode: "QC checklist failure"
    detection: "Automated QC returns fail result"
    action: "Review failed items, resolve if possible, or escalate to processor supervisor"
contract_ref: "ICT-LO-PKG-001"
idempotency: "safe"
timeout_seconds: 300
side_effects:
  - "Creates packaged loan file record in LOS"
  - "Publishes loan.file.packaged event"
execution_hints:
  preferred_agent: "loan-processing-service"
  tool_access:
    - "los_api"
    - "docvault_api"
    - "qc_engine"
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"
generated_from: "CAP-LO-PKG-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PIM"
---

# Intent: Package Loan File

## Goal

Assemble a complete, quality-checked loan file package from all application materials, verifications, and assessments, ready for underwriting submission.

## Execution Notes

This is a generic task performed by the Processing Team. It involves document assembly, data reconciliation, and QC validation. The processor should not make any credit or eligibility decisions.
