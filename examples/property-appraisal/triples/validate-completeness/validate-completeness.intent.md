---
intent_id: "INT-PA-VAL-001"
intent_name: "Apply Appraisal Completeness Checklist"
bpmn_task_id: "Task_ValidateCompleteness"
bpmn_task_name: "Validate Appraisal Completeness"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"
goal: "Validate appraisal report against completeness checklist per USPAP and agency requirements"
goal_type: "decision"

version: "1.0.0"
status: "draft"

generated_from: "CAP-PA-VAL-001"
generated_date: "2026-04-09"
generated_by: "mda-pipeline"
last_modified: "2026-04-09"
last_modified_by: "mda-pipeline"

owner_role: "Solution Architect"
owner_team: "Mortgage Technology"
reviewers:
  - "Chief Appraiser"
  - "Integration Architect"

domain: "Mortgage"
subdomain: "Property Appraisal"
mda_layer: "PIM"

agent_type: "llm"
autonomy_level: "supervised"
confidence_threshold: 0.92
timeout_seconds: 180
retry_policy: "none"
max_retries: 0

capsule_id: "CAP-PA-VAL-001"
contract_id: "ICT-PA-VAL-001"
contract_ref: "ICT-PA-VAL-001"
predecessor_ids:
  - "INT-PA-RCV-001"
successor_ids:
  - "INT-PA-ASV-001"
  - "INT-PA-REV-001"

preconditions:
  - "An appraisal report PDF and UAD XML exist in the document management system for the loan."
  - "The applicable completeness checklist template is available for the loan program type."
postconditions:
  - "The report has a completeness status of either Complete or Incomplete."
  - "If Incomplete, all deficiency codes are recorded in the LOS."
  - "A routing decision has been emitted for the downstream gateway."
invariants:
  - "The appraisal report content is not modified during validation."
  - "Every checklist item is evaluated; no items are skipped."
success_criteria:
  - "Completeness determination matches the manual review result in 95% of cases."
  - "All deficiency codes accurately reflect the actual missing content."

execution_hints:
  preferred_agent: "property-appraisal-agent"
  tool_access: []
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"

gaps:
  - "ML-based photograph quality detection not yet scoped -- Data Science team to evaluate"
---

# Apply Appraisal Completeness Checklist

## Outcome Statement

When this intent is fulfilled, the appraisal report has been systematically evaluated against the applicable completeness checklist, and a definitive completeness status with any deficiency codes has been recorded. The agent achieves this by analyzing both the structured UAD data and the unstructured PDF content while respecting the specific checklist variant for the loan program.

## Outcome Contract

**Preconditions (GIVEN):**

- The appraisal report PDF and UAD XML are available in document management.
- The correct checklist template is loaded for the loan program (Conventional, FHA, VA).

**Postconditions (THEN):**

- A completeness status (Complete/Incomplete) is recorded.
- Any deficiency codes are enumerated and stored.
- The routing decision is emitted for the process gateway.

**Invariants (ALWAYS):**

- Report content is read-only during validation.
- Every checklist item receives a pass/fail evaluation.

## Reasoning Guidance

1. **Assess inputs** -- Load the report PDF, UAD XML, and the applicable checklist template.
2. **Evaluate structured fields** -- Check UAD XML for required fields: appraised value, comparable sales count, GLA, site area, and appraiser certification.
3. **Evaluate unstructured content** -- Analyze the PDF for signature presence, photograph count and quality, sketch/floor plan, and narrative sections.
4. **Apply program-specific rules** -- For FHA loans, verify additional requirements (deficiency photos, case number, well/septic docs).
5. **Determine confidence** -- If any checklist item cannot be definitively evaluated, flag for human review.
6. **Compose output** -- Produce the completeness status and any deficiency codes.
7. **Validate postconditions** -- Confirm all checklist items were evaluated and the routing decision is set.

## Anti-Patterns

The agent MUST NOT:

- **Generate, suggest, or assume any user-interface element** -- no HTML, CSS, or UI references.
- **Modify the appraisal report** -- the agent evaluates but never alters report content.
- **Skip checklist items** -- every item must be evaluated even if earlier items fail.
- **Override the completeness determination** -- if any required item fails, the report is Incomplete.
- **Ignore confidence thresholds** -- uncertain evaluations must be escalated to the appraisal desk.
- **Accept photographs without verification** -- missing or unreadable photos must be flagged.

## Paired Capsule

| Field | Value |
|-------|-------|
| Capsule ID | `CAP-PA-VAL-001` |
| Capsule Name | Validate Appraisal Completeness |
| Location | `triples/validate-completeness/validate-completeness.cap.md` |

## Paired Integration Contract

| Field | Value |
|-------|-------|
| Contract ID | `ICT-PA-VAL-001` |
| Contract Name | Validate Appraisal Completeness Binding |
| Location | `triples/validate-completeness/validate-completeness.contract.md` |
