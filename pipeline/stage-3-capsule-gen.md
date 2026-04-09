# Stage 3: Capsule Generator

**Input:** Enriched model from Stage 2
**Output:** `.cap.md` files (one per eligible BPMN element)

---

## Overview

Generate a Knowledge Capsule for each BPMN element that warrants one, as defined by `ontology/bpmn-element-mapping.yaml`. Each capsule is a markdown file with YAML frontmatter conforming to `schemas/capsule.schema.json`.

## Prerequisites

- Enriched BPMN model (output of Stage 2)
- `ontology/bpmn-element-mapping.yaml` -- determines which elements produce capsules
- `ontology/id-conventions.yaml` -- ID generation rules
- `schemas/capsule.schema.json` -- frontmatter validation schema

## Instructions

### Step 1: Identify Capsule-Eligible Nodes

Consult `ontology/bpmn-element-mapping.yaml`. For each node in the enriched model, check whether that element type produces a capsule (`generates_capsule: true` or equivalent flag). Typical capsule-eligible elements:

- All task types (userTask, serviceTask, businessRuleTask, scriptTask, manualTask, sendTask, receiveTask)
- callActivity
- subProcess
- Start events and end events
- Boundary events (as exception capsules)
- Gateways (capsule only -- no intent spec for parallel gateways)

Skip elements that serve only as structural connectors (e.g., sequence flows, data associations).

### Step 2: Generate Capsule ID

For each eligible node, generate a `capsule_id` following `ontology/id-conventions.yaml`:

```
CAP-{domain_code}-{subdomain_code}-{sequence_number}
```

- `domain_code`: 2-3 uppercase letters derived from the process domain (e.g., `MO` for Mortgage Origination)
- `subdomain_code`: 3 uppercase letters derived from the task's functional area (e.g., `INC` for Income Verification)
- `sequence_number`: 3-digit zero-padded number, assigned in process flow order

The same ID stem (`{domain_code}-{subdomain_code}-{sequence_number}`) will be reused for the paired intent spec (`INT-...`) and contract (`ICT-...`).

### Step 3: Populate Frontmatter

Build the YAML frontmatter block for each capsule. Map fields from the enriched model:

| Frontmatter field | Source |
|-------------------|--------|
| `capsule_id` | Generated in Step 2 |
| `bpmn_task_id` | `node.id` |
| `bpmn_task_name` | `node.name` |
| `bpmn_task_type` | `node.type` |
| `process_id` | From process metadata |
| `process_name` | From process metadata |
| `version` | `"1.0"` (initial generation) |
| `status` | `"draft"` |
| `generated_from` | Source BPMN filename |
| `generated_date` | Current ISO 8601 timestamp |
| `generated_by` | Tool or agent identifier |
| `last_modified` | Same as `generated_date` |
| `last_modified_by` | Same as `generated_by` |
| `owner_role` | `enrichment.ownership.owner_role` (or null) |
| `owner_team` | `enrichment.ownership.owner_team` (or null) |
| `domain` | Derived from process/lane context |
| `subdomain` | Derived from task functional area |
| `regulation_refs` | `enrichment.regulatory.regulation_refs` (or empty array) |
| `policy_refs` | `enrichment.regulatory.policy_refs` (or empty array) |
| `intent_id` | `INT-{same stem}` |
| `contract_id` | `ICT-{same stem}` |
| `parent_capsule_id` | Set if this node is inside a sub-process (see sub-process rules) |
| `predecessor_ids` | Capsule IDs of nodes connected via incoming sequence flows |
| `successor_ids` | Capsule IDs of nodes connected via outgoing sequence flows |
| `exception_ids` | Capsule IDs of boundary event capsules attached to this node |
| `gaps` | Gap entries from enrichment that apply to this node |

### Step 4: Populate Markdown Body

After the frontmatter `---` delimiter, write the following sections:

#### Purpose

Derive a concise purpose statement from the task name and its position in the process flow.

```markdown
## Purpose

This capsule captures the knowledge required to [action derived from task name]
within the [process name] process. It is owned by [owner_role / owner_team]
and serves as the [Nth] step following [predecessor task names].
```

If the task name is too vague (flagged as `ambiguous_name` gap), note this and provide a best-effort purpose statement.

#### Procedure

If a procedure was found during enrichment (`enrichment.procedure.found == true`):
- Include the procedure content or a reference to it
- Note the match confidence level

If no procedure was found:
- Insert a placeholder:

```markdown
## Procedure

> **GAP: No procedure document found for this task.**
> Suggested resolution: [from gap.suggested_resolution]
>
> This section must be completed before the capsule can advance past `draft` status.
```

#### Business Rules

Populate from `enrichment.decision_rules` if applicable:
- Condition expressions from gateway paths
- DMN references
- Business rule document references

If this is not a decision-bearing node, write: "No business rules apply to this task."

#### Inputs

List each data input from:
- Data input associations in the BPMN model
- Predecessor task outputs (inferred from sequence flows)

Format as a table:

```markdown
## Inputs

| Name | Source | Schema | Required |
|------|--------|--------|----------|
| Loan Application | DataObject_1 | schemas/loan-application.json | Yes |
| Credit Report | Predecessor: CAP-MO-CRD-002 | - | Yes |
```

#### Outputs

List each data output, following the same pattern:

```markdown
## Outputs

| Name | Sink | Schema |
|------|------|--------|
| Verified Income Record | DataObject_5 | schemas/income-record.json |
```

#### Exception Handling

For each boundary event attached to this task:
- Describe the exception type (timer, error, message, etc.)
- Reference the exception capsule ID
- Describe the expected handling behavior

If no boundary events exist: "No boundary events are attached to this task."

## Special Cases

### Sub-Process Handling

When a node is a `subProcess` or `callActivity`:

1. Create a **parent capsule** for the sub-process itself with `bpmn_task_type: subProcess`
2. Create **child capsules** for each task inside the sub-process
3. Set `parent_capsule_id` on each child capsule to the parent's `capsule_id`
4. The parent capsule's procedure section should describe the overall sub-process flow
5. `predecessor_ids` and `successor_ids` on child capsules reference other child capsules within the same sub-process (internal flow)

### Parallel Gateway Handling

Parallel gateways (`parallelGateway`) receive a capsule but typically do **not** receive an intent spec, because they represent structural flow control rather than a goal-oriented action.

- Set `intent_id` to the generated ID (it will exist but contain only orchestration metadata)
- The capsule's purpose should describe the fork/join semantics
- `successor_ids` should list all parallel branches

### Boundary Event Handling

Boundary events produce **exception capsules**:

- The exception capsule's `parent_capsule_id` is the task the event is attached to
- The parent capsule's `exception_ids` array includes the exception capsule's ID
- Exception capsule names follow the pattern: "Exception: {event_type} on {parent_task_name}"
- The procedure section describes what happens when the boundary event fires

### Gateway-Only Capsules

Exclusive and inclusive gateways produce capsules with:
- `bpmn_task_type` set to the gateway type
- Business Rules section populated with the condition expressions from outgoing flows
- No procedure section (replaced with "Decision logic is defined in Business Rules below")

## Output File Naming

Each capsule is written to:

```
triples/{process_id}/{capsule_id}.cap.md
```

## Validation Before Output

Before writing each capsule file, verify:

1. `capsule_id` matches the pattern `^CAP-[A-Z]{2,3}-[A-Z]{3}-\d{3}$`
2. All required frontmatter fields are present per `schemas/capsule.schema.json`
3. `intent_id` and `contract_id` use the same ID stem
4. `predecessor_ids` and `successor_ids` reference valid capsule IDs (within this generation batch)
5. YAML frontmatter parses without error

## Corpus-to-Capsule Content Flow

For each capsule being generated, the generator reads the matched corpus documents from the enricher output and populates body sections:

1. **Procedure section**: Read the highest-confidence `doc_type: procedure` match. Extract numbered steps from its markdown body. If multiple procedure docs matched, use the highest-confidence match; list lower-confidence matches in Notes as "See also: CRP-PRC-XXX-NNN".

2. **Business Rules section**: Read matched `doc_type: rule` corpus documents. Extract decision tables and rule statements.

3. **Regulatory Context section**: Read matched `doc_type: regulation` corpus documents. Extract key requirements. Cite the corpus_id.

4. **Inputs/Outputs tables**: Read matched `doc_type: data-dictionary` corpus documents. Resolve field names, types, and valid values.

5. **Exception Handling**: Combine boundary event information from BPMN with procedural exception handling from corpus procedures.

### Corpus References in Frontmatter

Each generated capsule must include a `corpus_refs` field in its YAML frontmatter that traces the capsule content back to its source corpus documents:

```yaml
corpus_refs:
  - corpus_id: "CRP-PRC-XXX-NNN"
    section: "Procedure"
    match_confidence: "high"
  - corpus_id: "CRP-REG-XXX-NNN"
    section: "Regulatory Context"
    match_confidence: "medium"
```

This field is populated from the enricher's `corpus_refs` output for the corresponding node. Each entry records which corpus document contributed to which capsule section and at what confidence level.
