---
# ============================================================================
# INTENT SPECIFICATION TEMPLATE
# ============================================================================
# An Intent Specification defines WHAT an AI agent must achieve for a single
# BPMN task, without dictating HOW (no UI, no implementation).  It is the
# "what the agent must do" half of a triple, paired 1:1 with a Knowledge
# Capsule and bound by an Integration Contract.
# ============================================================================

# --- Identity ---------------------------------------------------------------
# intent_id         Globally unique ID for this intent. Convention: INT-<domain>-<seq>
# bpmn_task_id      The BPMN task element this intent maps to (must match the paired capsule).
# bpmn_task_name    Human-readable BPMN task name (must match the paired capsule).
# process_id        Parent BPMN process or sub-process ID.
# process_name      Human-readable name of the parent process.
intent_id: "INT-{DOMAIN}-{SEQ}"
bpmn_task_id: "{BPMN_TASK_ID}"
bpmn_task_name: "{BPMN Task Name}"
process_id: "{PROCESS_ID}"
process_name: "{Process Name}"

# --- Version & Status -------------------------------------------------------
# version           Semantic version (MAJOR.MINOR.PATCH).
# status            Lifecycle state: draft | in-review | approved | deprecated | retired
version: "1.0.0"
status: "draft"

# --- Provenance --------------------------------------------------------------
# generated_from    Source artifact (e.g. capsule ID, workshop notes, requirements doc).
# generated_date    ISO-8601 date of initial creation.
# generated_by      Person or tool that authored this intent.
# last_modified     ISO-8601 date of last edit.
# last_modified_by  Person or tool that last edited.
generated_from: "{CAP-DOMAIN-SEQ or source-artifact}"
generated_date: "{YYYY-MM-DD}"
generated_by: "{author-name-or-tool}"
last_modified: "{YYYY-MM-DD}"
last_modified_by: "{editor-name-or-tool}"

# --- Ownership ---------------------------------------------------------------
# owner_role        Role accountable for the correctness of this intent (e.g. Product Owner, Solution Architect).
# owner_team        Team or department responsible.
# reviewers         People or roles that must approve changes.
owner_role: "{Solution Architect}"
owner_team: "{Team or Department}"
reviewers:
  - "{Reviewer 1 Name or Role}"
  - "{Reviewer 2 Name or Role}"

# --- Classification ----------------------------------------------------------
# domain            Primary business domain.
# subdomain         Specific area within the domain.
# mda_layer         Model-Driven Architecture layer this intent targets:
#                   CIM (Computation-Independent) | PIM (Platform-Independent) | PSM (Platform-Specific)
domain: "{Domain}"
subdomain: "{Subdomain}"
mda_layer: "{CIM|PIM|PSM}"

# --- Agent Behaviour ---------------------------------------------------------
# agent_type        The kind of agent expected to execute this intent:
#                   llm | rpa | hybrid | human-in-the-loop
# autonomy_level    How much human oversight is required:
#                   full-auto | supervised | human-confirm | human-execute
# confidence_threshold
#                   Minimum confidence score (0.0 - 1.0) the agent must reach
#                   before committing its result.  Below this, escalate.
# timeout_seconds   Maximum wall-clock seconds the agent may spend before the
#                   task is considered timed-out and must be escalated.
# retry_policy      How to handle transient failures: none | fixed-delay | exponential-backoff
# max_retries       Maximum retry attempts before escalation (0 = no retries).
agent_type: "{llm|rpa|hybrid|human-in-the-loop}"
autonomy_level: "{full-auto|supervised|human-confirm|human-execute}"
confidence_threshold: 0.95
timeout_seconds: 300
retry_policy: "{none|fixed-delay|exponential-backoff}"
max_retries: 3

# --- Triple Linkage ----------------------------------------------------------
# capsule_id        ID of the paired Knowledge Capsule (CAP-*).
# contract_id       ID of the paired Integration Contract (ICT-*).
# predecessor_ids   Intent IDs for tasks that must complete before this one.
# successor_ids     Intent IDs for tasks that follow this one.
capsule_id: "CAP-{DOMAIN}-{SEQ}"
contract_id: "ICT-{DOMAIN}-{SEQ}"
predecessor_ids:
  - "{INT-DOMAIN-SEQ}"
successor_ids:
  - "{INT-DOMAIN-SEQ}"

# --- Outcome Contract (summary) ---------------------------------------------
# preconditions     Conditions that MUST be true before the agent begins.
# postconditions    Conditions that MUST be true when the agent finishes successfully.
# invariants        Conditions that must remain true throughout execution.
# success_criteria  Measurable criteria that define a successful outcome.
preconditions:
  - "{Precondition 1 -- e.g. All invoice line items are present in the input payload.}"
  - "{Precondition 2}"
postconditions:
  - "{Postcondition 1 -- e.g. Every line item has a validation status of PASS or FAIL.}"
  - "{Postcondition 2}"
invariants:
  - "{Invariant 1 -- e.g. No line item is deleted or added during validation.}"
success_criteria:
  - "{Criterion 1 -- e.g. 100% of line items processed with zero data loss.}"

# --- Gaps --------------------------------------------------------------------
# gaps   Known ambiguities, open design questions, or missing information.
gaps:
  - "{Description of gap or open question -- who can resolve}"
---

# {Intent Name}

## Outcome Statement

<!-- One to three sentences describing the desired end-state AFTER the agent
     has completed this task.  Write in terms of business outcomes, not
     technical steps. -->

{When this intent is fulfilled, [describe the measurable business outcome].
The agent achieves this by [high-level approach] while respecting
[key constraints or regulations].}

## Outcome Contract

<!-- Formal pre/post conditions restated in prose for clarity.  This section
     is the authoritative definition of "done". -->

**Preconditions (GIVEN):**

- {Restate each precondition in plain language.}

**Postconditions (THEN):**

- {Restate each postcondition in plain language.}

**Invariants (ALWAYS):**

- {Restate each invariant in plain language.}

## Reasoning Guidance

<!-- Numbered steps providing the agent with a recommended chain-of-thought.
     These are GUIDANCE, not rigid instructions -- the agent may adapt its
     approach as long as postconditions are met. -->

1. **Assess inputs** -- {Verify that all preconditions are satisfied and inputs conform to the contract schema.}
2. **Extract relevant context** -- {Identify the key data elements from the paired capsule's business rules and procedure.}
3. **Apply business rules** -- {Evaluate each rule from the capsule against the input data, recording pass/fail per item.}
4. **Determine confidence** -- {Calculate an overall confidence score; if below the threshold, flag for human review.}
5. **Compose output** -- {Build the output payload conforming to the integration contract schema.}
6. **Validate postconditions** -- {Confirm all postconditions and invariants hold before committing the result.}

## Anti-Patterns

<!-- Things the agent must NEVER do.  These are hard constraints, not
     suggestions.  Always include the anti-UI items below plus any
     task-specific prohibitions. -->

The agent MUST NOT:

- **Generate, suggest, or assume any user-interface element** -- no HTML, no CSS, no screen layouts, no form designs, no UI framework references.  The intent layer is UI-agnostic.
- **Produce wireframes, mockups, or visual design artifacts** -- presentation is a downstream concern outside the triple.
- **Reference specific frontend technologies** (React, Angular, SwiftUI, etc.) in its reasoning or output.
- **Modify, delete, or fabricate input data** -- the agent operates on data as-received; any corrections must be flagged, not silently applied.
- **Exceed its autonomy level** -- if `autonomy_level` requires human confirmation, the agent must pause and request it.
- **Ignore confidence thresholds** -- results below `confidence_threshold` must be escalated, never silently committed.
- {Task-specific anti-pattern 1 -- e.g. "Approve an invoice that fails any business rule without human override."}
- {Task-specific anti-pattern 2}

## Paired Capsule

<!-- Reference to the Knowledge Capsule that provides the business context
     for this intent.  The capsule contains the procedure, rules, and
     domain knowledge the agent draws upon. -->

| Field | Value |
|-------|-------|
| Capsule ID | `CAP-{DOMAIN}-{SEQ}` |
| Capsule Name | {BPMN Task Name} |
| Location | `capsules/{capsule-filename}.cap.md` |

## Paired Integration Contract

<!-- Reference to the Integration Contract that defines the data schemas,
     APIs, and technical bindings for this intent. -->

| Field | Value |
|-------|-------|
| Contract ID | `ICT-{DOMAIN}-{SEQ}` |
| Contract Name | {Contract Name} |
| Location | `contracts/{contract-filename}.contract.md` |
