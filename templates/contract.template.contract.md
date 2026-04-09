---
# ============================================================================
# INTEGRATION CONTRACT TEMPLATE
# ============================================================================
# An Integration Contract is the binding agreement between a Knowledge Capsule
# and an Intent Specification.  It defines the exact data schemas, API surface,
# error codes, and change-control rules that keep the triple consistent.
# It is the "how the two halves connect" piece of a triple.
# ============================================================================

# --- Identity ---------------------------------------------------------------
# contract_id       Globally unique ID. Convention: CON-<domain>-<seq>
# contract_name     Human-readable name describing what this contract binds.
# bpmn_task_id      The BPMN task element this contract governs (must match capsule and intent).
# bpmn_task_name    Human-readable BPMN task name.
# process_id        Parent BPMN process or sub-process ID.
# process_name      Human-readable name of the parent process.
contract_id: "CON-{DOMAIN}-{SEQ}"
contract_name: "{Contract Name -- e.g. Invoice Validation Binding}"
bpmn_task_id: "{BPMN_TASK_ID}"
bpmn_task_name: "{BPMN Task Name}"
process_id: "{PROCESS_ID}"
process_name: "{Process Name}"

# --- Version & Status -------------------------------------------------------
# version           Semantic version (MAJOR.MINOR.PATCH).
#                   MAJOR = breaking schema change, MINOR = additive, PATCH = docs/comments.
# status            Lifecycle state: draft | in-review | approved | deprecated | retired
version: "1.0.0"
status: "draft"

# --- Provenance --------------------------------------------------------------
# generated_from    Source artifact (e.g. paired capsule + intent IDs, design doc).
# generated_date    ISO-8601 date of initial creation.
# generated_by      Person or tool that authored this contract.
# last_modified     ISO-8601 date of last edit.
# last_modified_by  Person or tool that last edited.
generated_from: "{CAP-DOMAIN-SEQ + INT-DOMAIN-SEQ}"
generated_date: "{YYYY-MM-DD}"
generated_by: "{author-name-or-tool}"
last_modified: "{YYYY-MM-DD}"
last_modified_by: "{editor-name-or-tool}"

# --- Ownership ---------------------------------------------------------------
# owner_role        Role accountable for this contract (e.g. Integration Architect).
# owner_team        Team or department responsible.
# reviewers         People or roles that must approve changes.
owner_role: "{Integration Architect}"
owner_team: "{Team or Department}"
reviewers:
  - "{Reviewer 1 Name or Role}"
  - "{Reviewer 2 Name or Role}"

# --- Classification ----------------------------------------------------------
# domain            Primary business domain.
# subdomain         Specific area within the domain.
domain: "{Domain}"
subdomain: "{Subdomain}"

# --- Triple Linkage ----------------------------------------------------------
# capsule_id        ID of the paired Knowledge Capsule (CAP-*).
# intent_id         ID of the paired Intent Specification (INT-*).
capsule_id: "CAP-{DOMAIN}-{SEQ}"
intent_id: "INT-{DOMAIN}-{SEQ}"

# --- Input Schema ------------------------------------------------------------
# input_schema      Defines the structure of data the agent receives.
# Each field entry:
#   name            Field name as it appears in the payload.
#   type            Data type: string | integer | float | boolean | date | datetime | object | array
#   required        Whether this field must be present: true | false
#   description     What this field represents.
#   source          Where the value comes from (upstream task, system, user input).
#   constraints     Validation rules: regex, min/max, enum values, etc.
input_schema:
  - name: "{field_name}"
    type: "{string|integer|float|boolean|date|datetime|object|array}"
    required: true
    description: "{What this field represents.}"
    source: "{upstream-task-id or system-name}"
    constraints: "{e.g. maxLength: 255, pattern: '^INV-[0-9]+$'}"
  - name: "{field_name}"
    type: "{type}"
    required: false
    description: "{Description}"
    source: "{Source}"
    constraints: "{Constraints}"

# --- Output Schema -----------------------------------------------------------
# output_schema     Defines the structure of data the agent produces.
#   Same field format as input_schema, but 'destination' replaces 'source'.
output_schema:
  - name: "{field_name}"
    type: "{string|integer|float|boolean|date|datetime|object|array}"
    required: true
    description: "{What this field represents.}"
    destination: "{downstream-task-id or system-name}"
    constraints: "{Validation rules}"
  - name: "{field_name}"
    type: "{type}"
    required: false
    description: "{Description}"
    destination: "{Destination}"
    constraints: "{Constraints}"

# --- Error Codes -------------------------------------------------------------
# error_codes       Enumerated error conditions the agent may raise.
#   code            Machine-readable error code (e.g. ERR-VAL-001).
#   name            Short human-readable name.
#   severity        critical | error | warning | info
#   description     What this error means and when it occurs.
#   resolution      Recommended remediation or escalation path.
error_codes:
  - code: "ERR-{DOMAIN}-{SEQ}-001"
    name: "{Error Name}"
    severity: "{critical|error|warning|info}"
    description: "{When and why this error occurs.}"
    resolution: "{How to fix or escalate.}"
  - code: "ERR-{DOMAIN}-{SEQ}-002"
    name: "{Error Name}"
    severity: "{severity}"
    description: "{Description}"
    resolution: "{Resolution}"

# --- SLA & Performance -------------------------------------------------------
# max_latency_ms    Maximum acceptable response time in milliseconds.
# throughput        Expected volume (e.g. "500 invoices/hour").
# availability      Uptime target (e.g. "99.9%").
max_latency_ms: 5000
throughput: "{expected-volume-per-unit-time}"
availability: "{target-uptime-percentage}"

# --- Compatibility -----------------------------------------------------------
# min_capsule_version   Minimum capsule version this contract is compatible with.
# min_intent_version    Minimum intent version this contract is compatible with.
# breaking_changes      List of versions where breaking changes were introduced.
min_capsule_version: "1.0.0"
min_intent_version: "1.0.0"
breaking_changes: []

# --- Gaps --------------------------------------------------------------------
# gaps   Known gaps, open design questions, or unresolved schema issues.
gaps:
  - "{Description of gap or open question -- who can resolve}"
---

# {Contract Name}

## Binding Rationale

<!-- Explain WHY this contract exists and what it guarantees.  Describe
     the relationship between the capsule (business knowledge) and the
     intent (agent behaviour) that this contract mediates. -->

This contract binds **{Capsule Name}** (`{CAP-DOMAIN-SEQ}`) to
**{Intent Name}** (`{INT-DOMAIN-SEQ}`).

{Explain the purpose of the binding.  Why do these two artifacts need a
formal contract?  What consistency guarantees does it provide?  What would
break if the contract were absent or violated?}

**Key guarantees:**

- {Guarantee 1 -- e.g. "The agent will always receive a complete invoice header before processing line items."}
- {Guarantee 2 -- e.g. "Every output field maps to a documented destination with a defined consumer."}
- {Guarantee 3 -- e.g. "Error codes are exhaustive; the agent will never produce an undocumented error."}

## Change Protocol

<!-- Define the rules for evolving this contract.  This section is critical
     for maintaining triple consistency over time. -->

All changes to this contract MUST follow this protocol:

1. **Non-breaking changes** (MINOR/PATCH version bump):
   - Adding optional fields to input or output schemas.
   - Adding new error codes.
   - Updating descriptions, constraints, or documentation.
   - These require review by `reviewers` but do not force updates to the
     paired capsule or intent.

2. **Breaking changes** (MAJOR version bump):
   - Removing or renaming fields in input or output schemas.
   - Changing a field from optional to required.
   - Altering the semantics of an existing error code.
   - Changing data types or tightening constraints on existing fields.
   - These MUST trigger a coordinated update to the paired capsule and intent.
   - Add the old version to `breaking_changes` for traceability.

3. **Review and approval**:
   - All changes require at least one reviewer from `reviewers`.
   - Breaking changes require approval from `owner_role` of all three
     triple members (capsule, intent, contract).

4. **Version alignment**:
   - After a breaking change, update `min_capsule_version` and
     `min_intent_version` to reflect the minimum compatible versions.
   - Validation tooling should reject triples where version constraints
     are not satisfied.

## Decommissioning

<!-- Define the conditions and process for retiring this contract. -->

This contract may be decommissioned when:

- {Condition 1 -- e.g. "The parent BPMN task is removed from the process model."}
- {Condition 2 -- e.g. "The task is replaced by a new task with a new triple."}
- {Condition 3 -- e.g. "The business process is retired entirely."}

**Decommissioning steps:**

1. Set `status` to `deprecated` and notify all `reviewers`.
2. Ensure no active agent or system references this contract's schemas.
3. Update the paired capsule and intent to `deprecated` status.
4. After a grace period of {N days/sprints}, set `status` to `retired`.
5. Archive the triple (capsule + intent + contract) for audit trail retention.

**Data retention:** {State any regulatory or policy requirements for how
long the retired contract and its associated triple must be preserved.}
