---
intent_id: "INT-PA-DEC-002"
intent_name: "Route Based on LTV Threshold"
bpmn_task_id: "Gateway_LTV"
bpmn_task_name: "Value Within LTV?"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"

version: "1.0.0"
status: "draft"

generated_from: "CAP-PA-DEC-002"
generated_date: "2026-04-09"
generated_by: "mda-pipeline"
last_modified: "2026-04-09"
last_modified_by: "mda-pipeline"

owner_role: "Solution Architect"
owner_team: "Mortgage Technology"
reviewers:
  - "Underwriting Manager"
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

capsule_id: "CAP-PA-DEC-002"
contract_id: "ICT-PA-DEC-002"
predecessor_ids:
  - "INT-PA-ASV-001"
successor_ids:
  - "INT-PA-NTF-001"
  - "INT-PA-MRV-001"

preconditions:
  - "The value assessment task has produced an ltv_determination value."
postconditions:
  - "The process flow has been routed to exactly one downstream path."
invariants:
  - "No data transformation occurs; this is pure routing logic."
success_criteria:
  - "Routing decision made within 1 second."
  - "100% accuracy in mapping LTV determination to the correct path."

gaps: []
---

# Route Based on LTV Threshold

## Outcome Statement

When this intent is fulfilled, the process flow has been directed to either completion notification (for loans within LTV) or manual review (for loans exceeding LTV) based on the upstream value assessment. This is a deterministic routing decision.

## Outcome Contract

**Preconditions (GIVEN):**

- An ltv_determination of "Within_LTV" or "Exceeds_LTV" is available.

**Postconditions (THEN):**

- Exactly one downstream path has been activated.

**Invariants (ALWAYS):**

- No data is modified; this is pure routing logic.

## Reasoning Guidance

1. **Read ltv_determination** -- Retrieve the value from the assessment task output.
2. **Apply routing rule** -- If "Within_LTV," route to Task_EmitComplete. If "Exceeds_LTV," route to Task_ManualReview.
3. **Validate postconditions** -- Confirm exactly one path was activated.

## Anti-Patterns

The agent MUST NOT:

- **Generate, suggest, or assume any user-interface element** -- no HTML, CSS, or UI references.
- **Override the LTV determination** -- the gateway routes; it does not re-evaluate.
- **Grant LTV exceptions** -- exceptions must flow through manual review.
- **Route to both paths simultaneously** -- exactly one path must be selected.

## Paired Capsule

| Field | Value |
|-------|-------|
| Capsule ID | `CAP-PA-DEC-002` |
| Capsule Name | LTV Decision Gateway |
| Location | `decisions/ltv-check/ltv-check.cap.md` |

## Paired Integration Contract

| Field | Value |
|-------|-------|
| Contract ID | `ICT-PA-DEC-002` |
| Contract Name | LTV Decision Binding |
| Location | `decisions/ltv-check/ltv-check.contract.md` |
