# Stage 2: Corpus Enricher

**Input:** Parsed BPMN object model from Stage 1
**Output:** Enriched model with gap analysis

---

## Overview

Walk through every node in the parsed model and attempt to resolve its operational context -- procedure documentation, ownership, decision rules, data schemas, regulatory requirements, and integration bindings. Where information is missing, record a structured gap entry. The output is the original parsed model decorated with enrichment annotations and a consolidated gap list.

## Prerequisites

- Parsed BPMN object model (output of Stage 1)
- Access to the knowledge corpus at `corpus/` with its index at `corpus/corpus.config.yaml`
- Access to the enterprise data catalog (schemas, API registry) if available
- The element mapping table at `ontology/bpmn-element-mapping.yaml`

## Instructions

### Step 1: Iterate Over Nodes

For each node in the parsed model's `nodes` array, perform the enrichment checks described in Steps 2 through 7. Attach the results as an `enrichment` object on the node.

### Step 2: Procedure Lookup

Search the knowledge corpus for procedure documents that match this node using the multi-factor scoring algorithm below.

**Procedure:**
1. Load `corpus/corpus.config.yaml` (the corpus index)
2. For each node, filter corpus documents where `doc_type` is `procedure`:
   a. **Exact ID match** (score 1.0): `applies_to.process_ids` contains current `process_id` AND `applies_to.task_name_patterns` regex-matches `bpmn_task_name`
   b. **Name pattern match** (score 0.8): `task_name_patterns` matches `bpmn_task_name` regardless of process_id
   c. **Domain + task type match** (score 0.5): corpus doc's `domain` matches process domain AND `applies_to.task_types` includes the node's task type
   d. **Tag intersection** (score 0.3): corpus doc's `tags` overlap with tokens from `bpmn_task_name`
   e. **Role match** (bonus +0.1): node's `owner_role` appears in `applies_to.roles`
3. Select all matches with score >= 0.3

**Record:**
```yaml
enrichment:
  procedure:
    found: true | false
    corpus_refs:
      - corpus_id: "CRP-PRC-INC-001"
        match_confidence: high | medium | low
        match_score: 0.9
      - corpus_id: "CRP-PRC-INC-004"
        match_confidence: low
        match_score: 0.3
    match_method: "exact_id" | "name_pattern" | "domain_type" | "tag_intersection"
```

If not found, create a gap (see Step 8).

### Step 3: Ownership Resolution

Determine who owns this task.

**Sources** (in priority order):
1. Lane assignment from the parsed model (`node.lane` -> resolve lane name)
2. Participant from the process/collaboration metadata
3. Organizational mapping in the KB (department -> role)

**Record:**
```yaml
enrichment:
  ownership:
    resolved: true | false
    owner_role: "Senior Underwriter"
    owner_team: "Credit Risk"
    source: "lane" | "participant" | "kb_mapping"
```

If the lane is unnamed or no ownership mapping exists, create a gap.

### Step 4: Decision Rule Resolution

For gateway nodes and `businessRuleTask` nodes, check if decision rules are defined.

**Sources:**
1. Condition expressions already on outgoing sequence flows (from Stage 1)
2. DMN references in the BPMN element attributes
3. Business rule documents in the KB

**Record:**
```yaml
enrichment:
  decision_rules:
    defined: true | false
    rule_type: "condition_expression" | "dmn_ref" | "kb_document" | "none"
    rule_ref: "rules/dti-threshold.dmn"
    conditions:
      - flow_id: "flow_123"
        expression: "${dtiRatio < 0.43}"
```

### Step 5: Data Schema Resolution

For each data object or data store referenced by this node (via `data_associations`), check if a schema definition exists.

**Sources:**
1. `itemSubjectRef` from the BPMN data object
2. Enterprise data catalog
3. Schema files in the repository

**Record:**
```yaml
enrichment:
  data_schemas:
    - data_ref: "DataObject_1"
      schema_found: true | false
      schema_ref: "schemas/loan-application.json"
      direction: "input" | "output"
```

### Step 6: Regulatory Context

Check if this task or its domain has regulatory requirements. Filter corpus documents where `doc_type` is `regulation` or `policy` and apply the same multi-factor scoring algorithm described in Step 2.

**Sources:**
1. Corpus documents with `doc_type: regulation` or `doc_type: policy`, matched via the scoring algorithm
2. Compliance mapping documents
3. Lane or participant metadata that implies regulated activity (e.g., "Compliance Officer")

**Record:**
```yaml
enrichment:
  regulatory:
    applicable: true | false
    regulation_refs:
      - "TILA"
      - "ECOA"
    policy_refs:
      - "POL-CR-001"
```

### Step 7: Integration Binding Check

Check if this task has known system integrations.

**Sources:**
1. BPMN element `implementation` attribute (e.g., web service URI)
2. Enterprise API registry
3. Integration documentation in the KB

**Record:**
```yaml
enrichment:
  integration:
    has_binding: true | false
    system_name: "LOS"
    protocol: "rest"
    endpoint_hint: "/api/v2/applications/{id}/income"
```

### Step 8: Gap Recording

For every missing or incomplete enrichment result, create a gap record. Each gap must include:

| Field | Description |
|-------|-------------|
| `gap_id` | Auto-generated: `GAP-{node_id}-{n}` |
| `node_id` | The BPMN node this gap applies to |
| `gap_type` | Category (see table below) |
| `severity` | `critical`, `high`, `medium`, or `low` |
| `description` | Human-readable explanation of what is missing |
| `suggested_resolution` | Recommended action to resolve the gap |

**Gap type categories:**

| gap_type | Severity default | Trigger |
|----------|-----------------|---------|
| `missing_procedure` | high | No procedure found for an executable task |
| `missing_owner` | high | No lane assignment and no ownership mapping |
| `missing_decision_rules` | critical | Gateway has no condition expressions or rule references |
| `missing_data_schema` | medium | Data object referenced but no schema exists |
| `missing_regulatory_context` | low | Domain suggests regulation but no refs found |
| `missing_integration_binding` | medium | Service/send/receive task with no integration info |
| `ambiguous_name` | low | Task name is generic (e.g., "Process", "Handle", "Check") |
| `unnamed_element` | medium | Element has `name: null` |

Severity may be adjusted based on context. For example, `missing_procedure` on a `manualTask` in a non-critical lane may be downgraded to `medium`.

### Step 9: Assemble Enriched Output

Produce the enriched model with this structure:

```yaml
mda_enriched_model:
  source_model: "<reference to Stage 1 output>"
  enrichment_date: "<ISO 8601 timestamp>"
  enriched_by: "<tool or person>"

  # Original parsed model fields (processes, nodes, edges, etc.)
  # are preserved unchanged.

  # Each node in the nodes array now has an enrichment object attached.

  gaps:
    - gap_id: "GAP-Task_1-001"
      node_id: "Task_1"
      gap_type: "missing_procedure"
      severity: "high"
      description: "No procedure document found for 'Verify Borrower Income'"
      suggested_resolution: "Create work instruction WI-INC-001 covering income verification steps"

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
```

## Notes

- Gaps are informational, not blocking. Downstream stages use gaps to populate the `gaps` array in generated triples and to flag areas that need human review.
- If no knowledge base is available (e.g., first-time ingestion of a new process), most tasks will have `missing_procedure` gaps. This is expected.
- Enrichment confidence levels (`high`, `medium`, `low`) help reviewers triage fuzzy matches. A `low` confidence procedure match should be reviewed before being accepted into the capsule.
- The enricher reads the corpus index for candidate filtering, then loads the full `.corpus.md` file only for matched documents to extract content for downstream capsule generation.
