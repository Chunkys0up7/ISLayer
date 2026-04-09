# Stage 4: Intent Generator

**Input:** Enriched model from Stage 2 + Capsules from Stage 3
**Output:** `.intent.md` files (one per eligible BPMN element)

---

## Overview

Generate an Intent Specification for each BPMN element that warrants one, as defined by `ontology/bpmn-element-mapping.yaml`. Each intent spec is a markdown file with YAML frontmatter conforming to `schemas/intent.schema.json`. Intent specs define **what** an agent must achieve (the goal) without prescribing **how** (the implementation).

## Prerequisites

- Enriched BPMN model (output of Stage 2)
- Generated capsules (output of Stage 3)
- `ontology/bpmn-element-mapping.yaml` -- determines which elements produce intent specs and their default `goal_type`
- `ontology/goal-types.yaml` -- the five goal type definitions
- `ontology/id-conventions.yaml` -- ID generation rules
- `schemas/intent.schema.json` -- frontmatter validation schema

## Core Principle: Anti-UI

Intent specs describe outcomes achievable through APIs, data operations, and system integrations. They never describe UI interactions.

> **If the only way to achieve an outcome is through a UI, the intent spec stays in `status: blocked` with a gap noted.**

This means: no browser automation, no screen scraping, no UI clicking, no RPA-style macros. If a task currently requires manual UI interaction and no API exists, the intent spec documents the desired outcome and records a `missing_integration_binding` gap.

## Instructions

### Step 1: Identify Intent-Eligible Nodes

Consult `ontology/bpmn-element-mapping.yaml`. Each element type has a flag indicating whether it produces an intent spec. Generally:

- **Produces intent spec:** userTask, serviceTask, businessRuleTask, scriptTask, manualTask, sendTask, receiveTask, callActivity, subProcess, start events, end events, exclusive/inclusive/event-based gateways
- **Does not produce intent spec:** parallelGateway (capsule only), intermediate throw events (notification only, handled by contract), structural elements

### Step 2: Generate Intent ID

Use the same ID stem as the paired capsule:

```
INT-{domain_code}-{subdomain_code}-{sequence_number}
```

The stem must match the capsule: if the capsule is `CAP-MO-INC-001`, the intent is `INT-MO-INC-001`.

### Step 3: Derive Goal Statement

The `goal` field is a single sentence describing the outcome this task achieves. Derive it from:

1. The task name (primary source)
2. The process context (what comes before and after)
3. The capsule's Purpose section

**Good goal statements:**
- "Produce a verified income record by cross-referencing tax returns against employer-reported wages"
- "Determine whether the applicant's debt-to-income ratio meets the threshold for the selected loan program"

**Bad goal statements (too vague):**
- "Process the application"
- "Handle the request"

If the task name is too vague to derive a meaningful goal, use the best available context and record an `ambiguous_name` gap.

### Step 4: Set Goal Type

Look up the `default_goal_type` for this element type in `ontology/bpmn-element-mapping.yaml`. Cross-reference with `ontology/goal-types.yaml`:

| goal_type | Typical elements |
|-----------|-----------------|
| `data_production` | serviceTask, scriptTask, userTask, manualTask |
| `decision` | businessRuleTask, exclusiveGateway, inclusiveGateway, eventBasedGateway |
| `notification` | sendTask, intermediateThrowEvent |
| `state_transition` | receiveTask, startEvent, endEvent, intermediateCatchEvent |
| `orchestration` | callActivity, subProcess |

Override the default if the enrichment data or task context clearly indicates a different goal type.

### Step 5: Extract Preconditions

Preconditions are statements that must be true before execution begins. Sources:

1. **Incoming sequence flow conditions.** If the sequence flow into this task has a `condition_expression`, convert it to a precondition statement.
2. **Gateway conditions on paths leading here.** Walk backward through the graph to the nearest gateway. The condition that routes to this task's path is a precondition.
3. **Data availability.** If the task requires specific inputs, their availability is a precondition (e.g., "Credit report must be available in the data store").
4. **Process state.** Predecessor tasks must have completed (implied by the sequence flow but make explicit for clarity).

```yaml
preconditions:
  - "Loan application has been submitted and assigned an application ID"
  - "Borrower has provided at least two years of tax returns"
  - "DTI ratio check has not already been completed for this application"
```

### Step 6: Extract Inputs

For each data input needed by this task:

| Field | Source |
|-------|--------|
| `name` | Data object name or derived from context |
| `source` | Data object ID, predecessor capsule ID, or system name |
| `schema_ref` | From enrichment data schema resolution |
| `required` | `true` unless the input is optional per the process logic |

Sources of input data:
- `data_associations` with `direction: input` in the parsed model
- Outputs of predecessor tasks (follow incoming sequence flows, look at predecessor capsule outputs)
- Enrichment integration bindings

### Step 7: Extract Outputs

For each data output produced by this task:

| Field | Source |
|-------|--------|
| `name` | Data object name or derived from context |
| `type` | Data type (string, object, boolean, etc.) |
| `sink` | Data object ID, successor capsule ID, or system name |
| `invariants` | Constraints on the output value |

Sources of output data:
- `data_associations` with `direction: output` in the parsed model
- Inputs required by successor tasks
- Enrichment integration bindings

### Step 8: Define Invariants

Invariants are conditions that must hold true throughout execution. Sources:

1. **Business rules** from the capsule (convert to formal invariant expressions where possible)
2. **Data type constraints** (e.g., "income_amount >= 0", "application_status IN ('processing', 'pending_review')")
3. **Regulatory constraints** from enrichment (e.g., "All PII must be encrypted at rest")

Express invariants as evaluable expressions when possible:

```yaml
invariants:
  - "income_amount >= 0"
  - "tax_years.length >= 2"
  - "verification_date <= current_date"
```

### Step 9: Define Success Criteria

Success criteria define how to determine the task completed correctly:

```yaml
success_criteria:
  - "Verified income record is persisted to the data store"
  - "Income record contains amounts for all provided tax years"
  - "Verification status is set to 'verified' or 'discrepancy_found'"
```

### Step 10: Define Failure Modes

For each known way this task can fail:

| Field | Source |
|-------|--------|
| `mode` | Description of the failure |
| `detection` | How to detect it occurred |
| `action` | What to do (retry, escalate, compensate, abort) |

Sources:
- Boundary events attached to the task (error events, timer events)
- Error paths from downstream gateways
- Known system failure modes from enrichment

```yaml
failure_modes:
  - mode: "Tax return data is unreadable or corrupt"
    detection: "Parser throws FormatException on document"
    action: "Route to manual review queue via error boundary event"
  - mode: "External income verification service is unavailable"
    detection: "HTTP 503 or timeout after 30 seconds"
    action: "Retry with exponential backoff (max 3 attempts), then escalate"
```

### Step 11: Set Execution Boundaries

| Field | Value |
|-------|-------|
| `contract_ref` | `ICT-{same stem}` |
| `idempotency` | `"safe"` if re-execution produces the same result; `"unsafe"` otherwise |
| `retry_policy` | Default: `"exponential_backoff_3x"` (adjust per task type) |
| `timeout_seconds` | Default: `300` for service tasks, `86400` for user tasks (adjust per context) |
| `mda_layer` | Always `"PIM"` |

### Step 12: Set Forbidden Actions

Every intent spec must include `forbidden_actions` in the `execution_hints`:

```yaml
execution_hints:
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"
```

Add additional forbidden actions based on context (e.g., `"direct_database_write"` if writes must go through an API).

### Step 13: Write the Markdown Body

After the frontmatter `---` delimiter, write these sections:

#### Outcome Statement

A paragraph-length description of what successful execution looks like. This is the expanded version of the `goal` field.

```markdown
## Outcome Statement

When this intent is fulfilled, [describe the end state]. The executing agent will have
[specific achievements] and the following data will be available: [list key outputs].
This outcome advances the process toward [next major milestone].
```

#### Outcome Contract

Summarize the inputs, outputs, and invariants in a human-readable format. This mirrors the frontmatter but in prose form for reviewers.

```markdown
## Outcome Contract

**Requires:** [list inputs with sources]

**Produces:** [list outputs with destinations]

**Guarantees:** [list invariants in plain language]
```

#### Reasoning Guidance

Step-by-step guidance for the executing agent. This is not a rigid procedure -- it describes the logical steps the agent should consider. Each step should reference the relevant inputs/outputs and invariants.

```markdown
## Reasoning Guidance

1. Retrieve [input] from [source]
2. Validate that [precondition] holds
3. Perform [core operation] ensuring [invariant]
4. Persist [output] to [sink]
5. Verify [success criteria]
```

#### Anti-Patterns

Explicitly list what the agent must NOT do:

```markdown
## Anti-Patterns

- **Do not** interact with any user interface to accomplish this task
- **Do not** scrape web pages or automate browser interactions
- **Do not** bypass API authentication or authorization checks
- **Do not** [additional context-specific anti-patterns]
```

## Special Cases

### Blocked Intent Specs

If a task requires UI interaction and no API alternative exists:

1. Set `status: "blocked"` (this is an extension -- use `"draft"` with a critical gap if `blocked` is not a valid status in the lifecycle)
2. Add a gap:
   ```yaml
   gaps:
     - type: "missing_integration_binding"
       description: "This task currently requires UI interaction. No API endpoint exists."
       severity: "critical"
   ```
3. In the Outcome Statement, describe the desired outcome (not the UI steps)
4. In the Reasoning Guidance, write: "This intent is blocked pending API availability. See gaps."

### Gateway Intent Specs

For exclusive/inclusive gateways:
- `goal_type`: `decision`
- The goal is the decision itself (e.g., "Determine the approval path based on DTI ratio")
- Inputs are the data points the decision evaluates
- Outputs are the decision result and the selected path
- Business rules from the capsule become invariants

### Sub-Process Intent Specs

For sub-processes and call activities:
- `goal_type`: `orchestration`
- The goal describes the overall outcome of the sub-process
- Inputs/outputs are the sub-process boundary data (what goes in and comes out)
- The Reasoning Guidance describes the coordination of child tasks, not the child task details

## Output File Naming

Each intent spec is written to:

```
triples/{process_id}/{intent_id}.intent.md
```

## Validation Before Output

Before writing each intent spec file, verify:

1. `intent_id` matches the pattern `^INT-[A-Z]{2,3}-[A-Z]{3}-\d{3}$`
2. All required frontmatter fields are present per `schemas/intent.schema.json`
3. `capsule_id` references an existing capsule from Stage 3
4. `contract_ref` uses the same ID stem
5. `goal_type` is one of the five allowed values in `ontology/goal-types.yaml`
6. At least one input and one output are defined (or gaps are recorded)
7. `forbidden_actions` includes the four mandatory anti-UI entries
8. YAML frontmatter parses without error
