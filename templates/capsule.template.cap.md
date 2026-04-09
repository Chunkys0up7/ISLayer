---
# ============================================================================
# KNOWLEDGE CAPSULE TEMPLATE
# ============================================================================
# A Knowledge Capsule captures the full business-knowledge context of a single
# BPMN task: what it does, why, how, under what rules, and with which inputs
# and outputs.  It is the "what the business knows" half of a triple.
# ============================================================================

# --- Identity ---------------------------------------------------------------
# capsule_id        Globally unique ID for this capsule. Convention: CAP-<domain>-<seq>
# bpmn_task_id      The ID of the BPMN task element this capsule describes.
# bpmn_task_name    Human-readable name of the BPMN task.
# bpmn_task_type    BPMN task type: userTask | serviceTask | scriptTask | manualTask | sendTask | receiveTask | businessRuleTask | subProcess
# process_id        ID of the parent BPMN process or sub-process.
# process_name      Human-readable name of the parent process.
capsule_id: "CAP-{DOMAIN}-{SEQ}"
bpmn_task_id: "{BPMN_TASK_ID}"
bpmn_task_name: "{BPMN Task Name}"
bpmn_task_type: "{userTask|serviceTask|scriptTask|manualTask|sendTask|receiveTask|businessRuleTask|subProcess}"
process_id: "{PROCESS_ID}"
process_name: "{Process Name}"

# --- Version & Status -------------------------------------------------------
# version           Semantic version of this capsule (MAJOR.MINOR.PATCH).
# status            Lifecycle state: draft | in-review | approved | deprecated | retired
version: "1.0.0"
status: "draft"

# --- Provenance --------------------------------------------------------------
# generated_from    Source artifact this capsule was derived from (e.g. BPMN file path, Confluence page URL).
# generated_date    ISO-8601 date when this capsule was first generated.
# generated_by      Person or tool that created the initial version.
# last_modified     ISO-8601 date of the most recent edit.
# last_modified_by  Person or tool that made the most recent edit.
generated_from: "{source-artifact-path-or-url}"
generated_date: "{YYYY-MM-DD}"
generated_by: "{author-name-or-tool}"
last_modified: "{YYYY-MM-DD}"
last_modified_by: "{editor-name-or-tool}"

# --- Ownership ---------------------------------------------------------------
# owner_role        The role accountable for this capsule's accuracy (e.g. Process Owner, SME).
# owner_team        The team or department that owns the business process.
# reviewers         List of people or roles that must review changes to this capsule.
owner_role: "{Process Owner}"
owner_team: "{Team or Department}"
reviewers:
  - "{Reviewer 1 Name or Role}"
  - "{Reviewer 2 Name or Role}"

# --- Classification ----------------------------------------------------------
# domain            Primary business domain (e.g. Finance, HR, Supply-Chain).
# subdomain         More specific area within the domain (e.g. Accounts-Payable).
# regulation_refs   External regulations that govern this task (e.g. SOX Section 404, GDPR Art. 17).
# policy_refs       Internal policy documents that govern this task.
domain: "{Domain}"
subdomain: "{Subdomain}"
regulation_refs:
  - "{REG-ID: Regulation Title}"
policy_refs:
  - "{POL-ID: Policy Title}"

# --- Triple Linkage ----------------------------------------------------------
# intent_id            ID of the paired Intent Specification (INT-*).
# contract_id          ID of the paired Integration Contract (CON-*).
# parent_capsule_id    If this capsule is a decomposition of a higher-level capsule, reference it here.
# predecessor_ids      Capsule IDs for tasks that must complete before this one (sequence flow).
# successor_ids        Capsule IDs for tasks that follow this one.
# exception_ids        Capsule IDs for exception-handling or compensation tasks linked to this one.
intent_id: "INT-{DOMAIN}-{SEQ}"
contract_id: "CON-{DOMAIN}-{SEQ}"
parent_capsule_id: ""
predecessor_ids:
  - "{CAP-DOMAIN-SEQ}"
successor_ids:
  - "{CAP-DOMAIN-SEQ}"
exception_ids: []

# --- Gaps --------------------------------------------------------------------
# gaps   Known gaps, ambiguities, or open questions about this capsule's content.
#        Each entry should note what is missing and, if possible, who can resolve it.
gaps:
  - "{Description of gap or open question -- who can resolve}"
---

# {BPMN Task Name}

## Purpose

<!-- One paragraph explaining WHY this task exists in the process and WHAT
     business outcome it produces.  Focus on the "so that..." value. -->

{Describe the business purpose of this task -- why it exists, what value it
delivers, and what would go wrong if it were skipped.}

## Procedure

<!-- Numbered steps describing HOW a human (or system acting on behalf of a
     human) performs this task.  Keep steps atomic and verifiable. -->

1. {First step of the procedure.}
2. {Second step of the procedure.}
3. {Third step of the procedure.}

## Business Rules

<!-- Bullet list of rules, constraints, thresholds, or conditions that govern
     how this task must be performed.  Reference regulation or policy IDs
     where applicable. -->

- {Rule 1 -- e.g. "Approval is required for amounts exceeding $10,000 (POL-FIN-003)."}
- {Rule 2 -- e.g. "Customer must be notified within 24 hours of status change."}
- {Rule 3}

## Inputs Required

<!-- Table of all data or artifacts consumed by this task. -->

| Input | Source | Description |
|-------|--------|-------------|
| {Input Name} | {Source system, upstream task, or external party} | {Brief description of the input and its expected format.} |
| {Input Name} | {Source} | {Description} |

## Outputs Produced

<!-- Table of all data or artifacts produced by this task. -->

| Output | Destination | Description |
|--------|-------------|-------------|
| {Output Name} | {Downstream task, system, or external party} | {Brief description of the output and its format.} |
| {Output Name} | {Destination} | {Description} |

## Exception Handling

<!-- Bullet list of known exception scenarios.  Bold the exception name and
     describe the expected response or escalation path. -->

- **{Exception Name}** -- {What triggers this exception and how it should be handled or escalated.}
- **{Exception Name}** -- {Handling instructions.}

## Regulatory Context

<!-- Describe any regulatory or compliance considerations specific to this task.
     Reference regulation_refs from the frontmatter and explain how they apply. -->

{Explain which regulations apply, what controls are in place, and any audit
or evidence-retention requirements.}

## Notes

<!-- Any additional context, historical decisions, caveats, or links to
     supporting material that reviewers or future editors should know about. -->

- {Note or caveat.}
