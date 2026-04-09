---
intent_id: "INT-PA-MRV-001"
intent_name: "Prepare and Route Manual Appraisal Review"
bpmn_task_id: "Task_ManualReview"
bpmn_task_name: "Flag for Manual Review"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"
goal: "Perform senior underwriter review of appraisal when LTV exceeds program thresholds"
goal_type: "decision"

version: "1.0.0"
status: "draft"

generated_from: "CAP-PA-MRV-001"
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

agent_type: "human-in-the-loop"
autonomy_level: "human-execute"
confidence_threshold: 0.0
timeout_seconds: 172800
retry_policy: "none"
max_retries: 0

capsule_id: "CAP-PA-MRV-001"
contract_id: "ICT-PA-MRV-001"
contract_ref: "ICT-PA-MRV-001"
predecessor_ids:
  - "INT-PA-ASV-001"
successor_ids: []

preconditions:
  - "The LTV ratio has been calculated and exceeds the program maximum or risk flags are present."
  - "The appraisal report and value assessment summary are available."
postconditions:
  - "A review package has been assembled and assigned to a qualified underwriter."
  - "The underwriter has recorded a decision with rationale."
invariants:
  - "The review package contains all necessary documents for an informed decision."
  - "Only qualified underwriters (USPAP SR3 competent) can be assigned."
success_criteria:
  - "Review package assembled within 15 minutes of routing."
  - "Underwriter decision recorded within 2 business days."

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

# Prepare and Route Manual Appraisal Review

## Outcome Statement

When this intent is fulfilled, a complete review package has been assembled and assigned to a qualified senior underwriter, who has rendered a decision on the appraisal's acceptability. The agent prepares the package and routes it, but the decision itself is made entirely by the human underwriter.

## Outcome Contract

**Preconditions (GIVEN):**

- The value assessment has identified an LTV exception or risk flag.
- All appraisal documents and assessment results are available.

**Postconditions (THEN):**

- A review package has been created and assigned to a qualified underwriter.
- The underwriter's decision and rationale have been recorded.

**Invariants (ALWAYS):**

- The review package is complete and contains all relevant documents.
- The assigned reviewer has appropriate qualifications.

## Reasoning Guidance

1. **Assess inputs** -- Gather the value assessment summary, appraisal report, and loan file details.
2. **Assemble review package** -- Compile all relevant documents into a structured review packet.
3. **Select reviewer** -- Query the underwriting team for the next available qualified reviewer.
4. **Create work queue item** -- Add the review task with appropriate priority.
5. **Monitor for completion** -- Track SLA compliance and escalate if breached.
6. **Record outcome** -- Capture the underwriter's decision and rationale.

## Anti-Patterns

The agent MUST NOT:

- **Generate, suggest, or assume any user-interface element** -- no HTML, CSS, or UI references.
- **Make the underwriting decision** -- the agent facilitates the review; the human decides.
- **Override the underwriter's decision** -- the recorded decision is final within this task.
- **Assign unqualified reviewers** -- credentials must be verified before assignment.
- **Skip SLA monitoring** -- late reviews must trigger escalation.

## Paired Capsule

| Field | Value |
|-------|-------|
| Capsule ID | `CAP-PA-MRV-001` |
| Capsule Name | Flag for Manual Review |
| Location | `triples/manual-review/manual-review.cap.md` |

## Paired Integration Contract

| Field | Value |
|-------|-------|
| Contract ID | `ICT-PA-MRV-001` |
| Contract Name | Manual Appraisal Review Binding |
| Location | `triples/manual-review/manual-review.contract.md` |
