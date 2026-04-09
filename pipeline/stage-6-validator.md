# Stage 6: Triple Validator

**Input:** Complete set of triples from Stages 3-5
**Output:** Validation report (pass/fail per triple, per process)

---

## Overview

Validate the complete output of the pipeline. Every triple (capsule + intent spec + contract) is checked for internal consistency, cross-reference integrity, and schema conformance. The full process graph is checked for completeness and connectivity. The output is a structured validation report.

## Prerequisites

- All generated `.cap.md`, `.intent.md`, and `.contract.md` files from Stages 3-5
- Parsed BPMN model from Stage 1 (for process graph verification)
- `schemas/capsule.schema.json`
- `schemas/intent.schema.json`
- `schemas/contract.schema.json`
- `ontology/status-lifecycle.yaml`
- `ontology/id-conventions.yaml`

## Validation Checks

### Per-Triple Checks

Run these checks for every triple (each set of capsule + intent + contract sharing the same ID stem).

#### Check 1: Triple Completeness

All three files must exist for each ID stem.

| Condition | Result |
|-----------|--------|
| All three files present | PASS |
| One or two files missing | FAIL -- list which files are missing |

**Exception:** Parallel gateways may have a capsule without an intent spec. This is a PASS if the capsule's `bpmn_task_type` is `parallelGateway`.

#### Check 2: ID Convention Conformance

Each ID must match its expected regex pattern:

| File type | Pattern |
|-----------|---------|
| Capsule | `^CAP-[A-Z]{2,3}-[A-Z]{3}-\d{3}$` |
| Intent | `^INT-[A-Z]{2,3}-[A-Z]{3}-\d{3}$` |
| Contract | `^ICT-[A-Z]{2,3}-[A-Z]{3}-\d{3}$` |

#### Check 3: ID Stem Consistency

The domain code, subdomain code, and sequence number must be identical across the triple:

```
CAP-MO-INC-001
INT-MO-INC-001
ICT-MO-INC-001
    ^^^^^^^^^^
    same stem
```

If any stem segment differs, FAIL.

#### Check 4: Cross-Reference Integrity

Verify that all cross-references are bidirectional and consistent:

| Assertion | Description |
|-----------|-------------|
| `capsule.intent_id == intent.intent_id` | Capsule points to the correct intent |
| `capsule.contract_id == contract.contract_id` | Capsule points to the correct contract |
| `intent.capsule_id == capsule.capsule_id` | Intent points back to the correct capsule |
| `intent.contract_ref == contract.contract_id` | Intent references the correct contract |
| `contract.intent_id == intent.intent_id` | Contract points back to the correct intent |

If any assertion fails, report which reference is wrong and what value was found versus expected.

#### Check 5: Status Consistency

All three files in a triple must have the same `status` value:

```
capsule.status == intent.status == contract.status
```

If they differ, FAIL with the values found.

#### Check 6: Version Consistency

All three files in a triple must have the same `version` value:

```
capsule.version == intent.version == contract.version
```

#### Check 7: Required Fields for Status

Cross-reference the current `status` against `ontology/status-lifecycle.yaml`. Verify that all `required_fields` for that status level are populated.

For example, a triple in `review` status must have:
- All `draft` required fields
- `owner_role` or `owner_team` defined
- All inputs and outputs defined (for intent specs)

#### Check 8: YAML Frontmatter Parsing

Parse the YAML frontmatter of each file. If parsing fails, FAIL with the parser error message. Validate against the corresponding JSON Schema:

| File type | Schema |
|-----------|--------|
| `.cap.md` | `schemas/capsule.schema.json` |
| `.intent.md` | `schemas/intent.schema.json` |
| `.contract.md` | `schemas/contract.schema.json` |

#### Check 9: Invariant Expression Syntax

For each expression in the intent spec's `invariants` array, verify it is syntactically valid. Acceptable forms:

- Comparison: `field_name >= value`
- Membership: `field_name IN ('a', 'b', 'c')`
- Boolean: `field_name == true`
- Length: `field_name.length >= N`
- Date: `field_name <= current_date`

If an expression does not parse, FAIL with the offending expression.

#### Check 10: Gap Entry Completeness

For every entry in the `gaps` array (on any of the three files), verify:

| Required field | Present? |
|----------------|----------|
| `type` | Must be a non-empty string |
| `description` | Must be a non-empty string |
| `severity` | Must be one of: `critical`, `high`, `medium`, `low` |

---

### Per-Process Checks

Run these checks once per BPMN process, using the parsed model from Stage 1 as the reference.

#### Check 11: BPMN Coverage

Every BPMN task in the Stage 1 parsed model that is capsule-eligible (per `ontology/bpmn-element-mapping.yaml`) must have exactly one triple.

| Condition | Result |
|-----------|--------|
| Every eligible task has one triple | PASS |
| A task has no triple | FAIL -- `MISSING_TRIPLE: {bpmn_task_id}` |
| A task has more than one triple | FAIL -- `DUPLICATE_TRIPLE: {bpmn_task_id}` |

#### Check 12: Process Graph Connectivity

The set of capsules should form a connected graph (when traversed via `predecessor_ids` and `successor_ids`). No capsule should be unreachable from the start event capsule.

| Condition | Result |
|-----------|--------|
| All capsules reachable from start | PASS |
| Orphan capsule(s) found | FAIL -- list orphan capsule IDs |

#### Check 13: Predecessor/Successor Reference Validity

Every ID in every capsule's `predecessor_ids` and `successor_ids` must reference an existing capsule ID in the current set.

| Condition | Result |
|-----------|--------|
| All references resolve | PASS |
| Dangling reference found | FAIL -- `DANGLING_REF: {capsule_id} references {missing_id}` |

#### Check 14: Exception Reference Validity

Every ID in every capsule's `exception_ids` must reference an existing capsule ID.

#### Check 15: Start and End Event Triples

At least one triple must correspond to a start event and at least one to an end event for each process.

| Condition | Result |
|-----------|--------|
| Start event triple exists | PASS |
| End event triple exists | PASS |
| Missing start or end event triple | FAIL -- specify which is missing |

#### Check 16: No Circular Dependencies

Walk the `predecessor_ids` / `successor_ids` graph and detect cycles. The process flow should be a directed acyclic graph (DAG).

| Condition | Result |
|-----------|--------|
| No cycles detected | PASS |
| Cycle detected | FAIL -- list the cycle path (e.g., `CAP-MO-INC-001 -> CAP-MO-INC-003 -> CAP-MO-INC-001`) |

**Note:** This check is about the capsule dependency graph, not the BPMN graph. Loops in BPMN (e.g., rework loops) should be modeled with distinct capsules for each iteration entry, not as circular predecessor/successor references.

#### Check 17: Gap Tracking Completeness

Every gap from the Stage 2 enriched model should appear in at least one triple's `gaps` array. No gap should be silently dropped.

---

## Output Format

The validation report must follow this structure:

```yaml
mda_validation_report:
  report_date: "<ISO 8601 timestamp>"
  validated_by: "<tool or person>"
  source_bpmn: "<filename>"
  overall_result: PASS | FAIL

  per_triple_results:
    - triple_stem: "MO-INC-001"
      capsule_id: "CAP-MO-INC-001"
      intent_id: "INT-MO-INC-001"
      contract_id: "ICT-MO-INC-001"
      result: PASS | FAIL
      checks:
        - check: "triple_completeness"
          result: PASS
        - check: "id_convention"
          result: PASS
        - check: "id_stem_consistency"
          result: PASS
        - check: "cross_reference_integrity"
          result: FAIL
          details: "capsule.intent_id is 'INT-MO-INC-002' but expected 'INT-MO-INC-001'"
        # ... all 10 per-triple checks

  per_process_results:
    - process_id: "Process_1"
      process_name: "Mortgage Origination"
      result: PASS | FAIL
      checks:
        - check: "bpmn_coverage"
          result: PASS
        - check: "graph_connectivity"
          result: PASS
        # ... all 7 per-process checks

  gap_summary:
    total: 12
    by_severity:
      critical: 1
      high: 4
      medium: 5
      low: 2
    by_type:
      missing_procedure: 3
      missing_owner: 2
      missing_decision_rules: 1
      missing_data_schema: 4
      missing_integration_binding: 2

  recommendations:
    - severity: critical
      description: "Resolve GAP-Task_5-001 (missing_decision_rules on exclusive gateway) before advancing any triples past draft status"
    - severity: high
      description: "4 tasks lack ownership assignment. Review lane mappings in the BPMN model or update the organizational knowledge base"
```

## Result Determination

- **Overall PASS:** All per-triple checks pass AND all per-process checks pass
- **Overall FAIL:** Any check fails

A pipeline run that produces FAIL is not necessarily broken -- gaps and draft status are expected on initial ingestion. The report helps prioritize what needs human attention before triples can advance through the status lifecycle.

## Re-Validation

After addressing failures, re-run Stage 6 on the updated triples. The validator is idempotent and can be run as many times as needed.
