---
intent_id: "INT-PA-RCV-001"
intent_name: "Ingest and Index Appraisal Report"
bpmn_task_id: "Task_ReceiveReport"
bpmn_task_name: "Receive Appraisal Report"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"

version: "1.0.0"
status: "draft"

generated_from: "CAP-PA-RCV-001"
generated_date: "2026-04-09"
generated_by: "mda-pipeline"
last_modified: "2026-04-09"
last_modified_by: "mda-pipeline"

owner_role: "Solution Architect"
owner_team: "Mortgage Technology"
reviewers:
  - "Appraisal Desk Supervisor"
  - "Integration Architect"

domain: "Mortgage"
subdomain: "Property Appraisal"
mda_layer: "PIM"

agent_type: "rpa"
autonomy_level: "full-auto"
confidence_threshold: 0.95
timeout_seconds: 60
retry_policy: "fixed-delay"
max_retries: 5

capsule_id: "CAP-PA-RCV-001"
contract_id: "ICT-PA-RCV-001"
predecessor_ids:
  - "INT-PA-ORD-001"
successor_ids:
  - "INT-PA-VAL-001"

preconditions:
  - "An active appraisal order exists in the LOS with status Ordered or Revision Requested."
  - "The inbound report payload contains both a PDF document and a UAD XML file."
postconditions:
  - "The appraisal report PDF is stored in the document management system indexed to the loan number."
  - "Key header fields (appraised value, effective date, appraiser license) have been parsed from the UAD XML."
  - "The LOS appraisal status has been updated to Report Received."
invariants:
  - "The original report PDF is never modified; only metadata and parsed fields are written."
  - "Each report version is stored independently with a link to prior versions if applicable."
success_criteria:
  - "Report ingested and indexed within 30 seconds of receipt."
  - "All UAD XML header fields parsed with zero data loss."

gaps: []
---

# Ingest and Index Appraisal Report

## Outcome Statement

When this intent is fulfilled, the appraisal report has been securely stored in the document management system, key data fields have been extracted from the UAD XML, and the loan file status reflects receipt. The agent achieves this by monitoring the Appraisal Portal for inbound deliveries, validating file integrity, and updating the LOS.

## Outcome Contract

**Preconditions (GIVEN):**

- An open appraisal order exists for the loan.
- The inbound delivery contains a PDF report and UAD XML.

**Postconditions (THEN):**

- Report PDF is indexed in document management under the loan number.
- Appraised value, effective date, and appraiser license are recorded in the LOS.
- Loan appraisal status is updated to Report Received.

**Invariants (ALWAYS):**

- The report PDF is stored as-received without modification.
- Version history is preserved for revised reports.

## Reasoning Guidance

1. **Assess inputs** -- Confirm the inbound delivery contains both PDF and XML files matching an active order.
2. **Validate file integrity** -- Check PDF readability and XML schema conformance.
3. **Parse UAD XML** -- Extract appraised value, effective date, property address, and appraiser credentials.
4. **Store documents** -- Upload the PDF and XML to the document management system with correct loan indexing.
5. **Update LOS** -- Write parsed fields and update the appraisal status.
6. **Validate postconditions** -- Confirm all files are stored and all fields are populated.

## Anti-Patterns

The agent MUST NOT:

- **Generate, suggest, or assume any user-interface element** -- no HTML, CSS, or UI references.
- **Modify the appraisal report content** -- the report must be stored exactly as received.
- **Exceed its autonomy level** -- fully automated for standard receipts but must escalate corrupt files.
- **Ignore confidence thresholds** -- UAD parsing failures must be escalated for manual entry.
- **Accept reports without matching order IDs** -- orphaned reports must be quarantined.
- **Override SLA tracking** -- late reports must trigger notifications regardless of content quality.

## Paired Capsule

| Field | Value |
|-------|-------|
| Capsule ID | `CAP-PA-RCV-001` |
| Capsule Name | Receive Appraisal Report |
| Location | `triples/receive-report/receive-report.cap.md` |

## Paired Integration Contract

| Field | Value |
|-------|-------|
| Contract ID | `ICT-PA-RCV-001` |
| Contract Name | Receive Appraisal Report Binding |
| Location | `triples/receive-report/receive-report.contract.md` |
