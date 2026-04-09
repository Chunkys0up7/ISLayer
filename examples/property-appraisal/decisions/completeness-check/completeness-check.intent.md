---
intent_id: "INT-PA-DEC-001"
intent_name: "Route Based on Appraisal Completeness"
bpmn_task_id: "Gateway_Complete"
bpmn_task_name: "Complete?"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"
goal: "Determine whether appraisal report passes completeness validation"
goal_type: "decision"

version: "1.0.0"
status: "draft"

generated_from: "CAP-PA-DEC-001"
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

agent_type: "rpa"
autonomy_level: "full-auto"
confidence_threshold: 1.0
timeout_seconds: 5
retry_policy: "none"
max_retries: 0

capsule_id: "CAP-PA-DEC-001"
contract_id: "ICT-PA-DEC-001"
contract_ref: "ICT-PA-DEC-001"
predecessor_ids:
  - "INT-PA-VAL-001"
successor_ids:
  - "INT-PA-ASV-001"
  - "INT-PA-REV-001"

preconditions:
  - "The completeness validation task has produced a completeness_status value."
postconditions:
  - "The process flow has been routed to exactly one downstream path."
invariants:
  - "No data transformation occurs at this gateway; it is a pure routing decision."
success_criteria:
  - "Routing decision made within 1 second."
  - "100% accuracy in mapping completeness status to the correct path."

execution_hints:
  preferred_agent: "property-appraisal-agent"
  tool_access: []
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"

gaps: []
---

# Route Based on Appraisal Completeness

## Outcome Statement

When this intent is fulfilled, the process flow has been directed to either value assessment (for complete reports) or revision request (for incomplete reports) based on the upstream validation result. This is a deterministic routing decision with no ambiguity.

## Outcome Contract

**Preconditions (GIVEN):**

- A completeness_status of "Complete" or "Incomplete" is available.

**Postconditions (THEN):**

- Exactly one downstream path has been activated.

**Invariants (ALWAYS):**

- No data is modified; this is pure routing logic.

## Reasoning Guidance

1. **Read completeness_status** -- Retrieve the value from the validation task output.
2. **Apply routing rule** -- If "Complete," route to Task_AssessValue. If "Incomplete," route to Task_RequestRevision.
3. **Validate postconditions** -- Confirm exactly one path was activated.

## Anti-Patterns

The agent MUST NOT:

- **Generate, suggest, or assume any user-interface element** -- no HTML, CSS, or UI references.
- **Override the completeness determination** -- the gateway routes; it does not re-evaluate.
- **Route to both paths simultaneously** -- exactly one path must be selected.
- **Introduce delays** -- routing must be immediate.

## Paired Capsule

| Field | Value |
|-------|-------|
| Capsule ID | `CAP-PA-DEC-001` |
| Capsule Name | Completeness Decision Gateway |
| Location | `decisions/completeness-check/completeness-check.cap.md` |

## Paired Integration Contract

| Field | Value |
|-------|-------|
| Contract ID | `ICT-PA-DEC-001` |
| Contract Name | Completeness Decision Binding |
| Location | `decisions/completeness-check/completeness-check.contract.md` |
