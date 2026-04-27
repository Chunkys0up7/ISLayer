# Spec-to-JIRA — Technical Design Specification

## Document Control

| Field             | Value                                              |
| ----------------- | -------------------------------------------------- |
| **Spec ID**       | SPEC-TO-JIRA-DESIGN-001                            |
| **Version**       | 1.0                                                |
| **Status**        | Draft                                              |
| **Audience**      | Engineering / Architecture                         |
| **Created**       | 2026-04-27                                         |
| **Related Specs** | EXECUTION-SPEC.md, GROUNDING-AGENT-SPEC.md, TEST-SPEC.md |

---

## 1. Purpose

Extend the MDA Intent Layer from a BPMN-only ingestion pipeline into a **general specification grounding platform** that:

1. Accepts product specifications (PRDs, plans, OKR docs, user-story bundles) as input
2. Decomposes them into structured work units using the existing triple model (capsule, intent, contract)
3. Grounds every unit in source material using the existing zero-hallucination guarantees
4. Synchronises the resulting work units into JIRA as a hierarchy of Epics, Stories, and Sub-tasks
5. Maintains a deterministic, re-runnable pipeline so spec edits cleanly diff into JIRA updates

This document defines the technical architecture. A separate executive overview (`SPEC-TO-JIRA-EXECUTIVE.md`) describes business value and operating model.

---

## 2. Scope

### 2.1 In Scope

- A new **Spec Parser** stage that produces a `ParsedModel` from prose specifications
- A new **Story Parser** stage for pre-existing user-story documents
- Extensions to the enrichment, generation, and verification stages to support spec-derived models
- A new **Stage 7: Issue Tracker Sync** that creates and updates JIRA issues from triples
- Bidirectional ID mapping so the pipeline is idempotent (re-runs update; never duplicate)
- Provenance: every JIRA story traces to specific paragraphs in the source spec
- A tech-corpus pattern for engineering knowledge (architecture decisions, API catalog, runbooks, coding standards)

### 2.2 Out of Scope (V1)

- Two-way sync (JIRA → triples). V1 is one-way: triples are the source of truth
- Real-time updates. V1 runs on demand or on a scheduled cadence
- Auto-merging conflicting edits between JIRA and triples
- Replacing existing JIRA workflows (the system creates and updates issues; status transitions stay manual or follow existing JIRA automations)

---

## 3. Architectural Principles

The extension preserves the architectural principles already embodied in the BPMN pipeline:

| Principle                  | How It Applies to Specs                                                                 |
| -------------------------- | --------------------------------------------------------------------------------------- |
| **Provenance-first**       | Every story carries a citation back to the source paragraph(s) of the spec             |
| **Editor-not-author**      | The LLM organises pre-extracted spec content; it does not invent acceptance criteria   |
| **Gap, not hallucination** | Missing details produce explicit `MISSING_*` gaps, not fabricated requirements         |
| **Schema-enforced output** | All artifacts validate against JSON Schema before being written or synced              |
| **Re-runnability**         | The pipeline is idempotent — same input produces same output; updates diff cleanly     |
| **Anti-UI**                | Stories define WHAT, not HOW (no implementation detail leaks into acceptance criteria) |

---

## 4. Conceptual Model

### 4.1 Mapping Specs to the Existing Triple Model

The triple model (capsule + intent + contract) maps cleanly onto product engineering primitives:

| Existing Concept | Product Engineering Equivalent                              |
| ---------------- | ----------------------------------------------------------- |
| Process          | Epic / Initiative                                           |
| Task (node)      | Story / Task                                                |
| Sequence flow    | Dependency (`blocks` / `is blocked by`)                     |
| Lane             | Owning team or squad                                        |
| Data object      | API contract, schema, or shared data artifact               |
| Boundary event   | Risk, edge case, or rollback path                           |
| Gateway          | Decision gate, conditional acceptance, or feature-flag fork |
| Capsule          | Story description + acceptance criteria + business context  |
| Intent spec      | Definition of Done + outcome contract + invariants          |
| Integration contract | Technical sub-tasks + API contracts + SLAs              |
| Job aid          | Configuration matrix (env-specific values, feature flags)   |
| Corpus document  | Architecture decision, runbook, API spec, coding standard   |

### 4.2 Why the Mapping Holds

The downstream pipeline stages (enrichment, generation, verification) operate on the abstract `ParsedModel`, not on BPMN. They consume **nodes**, **edges**, **lanes**, and **data objects** — primitives that exist in any structured plan. The BPMN parser is one implementation; spec parsers are alternative implementations producing the same abstract model.

---

## 5. Pipeline Architecture

### 5.1 End-to-End Flow

```
                ┌─────────────────────────────────────────────────────┐
                │             INPUT FORMAT ABSTRACTION                │
                ├─────────────┬─────────────┬─────────────────────────┤
                │ BPMN parser │ Spec parser │ Story parser            │
                │ (existing)  │ (new)       │ (new)                   │
                └──────┬──────┴──────┬──────┴────────────┬────────────┘
                       │             │                   │
                       └─────────────┼───────────────────┘
                                     ▼
                              ┌─────────────┐
                              │ ParsedModel │  (unchanged abstraction)
                              └──────┬──────┘
                                     ▼
                       ┌─────────────────────────────┐
                       │ Stage 2: Corpus Enrichment   │
                       │ (multi-signal weighted match)│
                       └──────────┬───────────────────┘
                                  ▼
                       ┌─────────────────────────────┐
                       │ Stage 3-5: Triple Generation │
                       │ (capsule / intent / contract)│
                       └──────────┬───────────────────┘
                                  ▼
                       ┌─────────────────────────────┐
                       │ Stage 6: Validator           │
                       │ (schema + grounding checks)  │
                       └──────────┬───────────────────┘
                                  ▼
                ┌─────────────────────────────────────────────────────┐
                │             OUTPUT TARGET ABSTRACTION               │
                ├──────────────┬──────────────┬───────────────────────┤
                │ Markdown +   │ MkDocs       │ Stage 7:              │
                │ Git/Bitbucket│ docs site    │ JIRA Sync (new)       │
                │ (existing)   │ (existing)   │                       │
                └──────────────┴──────────────┴───────────────────────┘
```

### 5.2 What's New, What's Reused

| Component                         | Status        |
| --------------------------------- | ------------- |
| `cli/parsers/bpmn_parser.py`      | Existing      |
| `cli/parsers/spec_parser.py`      | **New**       |
| `cli/parsers/story_parser.py`     | **New**       |
| `cli/pipeline/stage2_enricher.py` | Reused as-is  |
| `cli/pipeline/stage3_capsule_gen.py` | Reused as-is |
| `cli/pipeline/stage4_intent_gen.py`  | Reused as-is |
| `cli/pipeline/stage5_contract_gen.py`| Reused as-is |
| `cli/pipeline/stage6_validator.py`   | Minor extension for spec-source provenance |
| `cli/pipeline/stage7_jira_sync.py`   | **New**       |
| `cli/jira/client.py`                 | **New**       |
| Tech corpus templates               | **New**       |
| `ontology/spec-element-mapping.yaml`| **New**       |

---

## 6. Stage 1b — Spec Parser

### 6.1 Inputs

The spec parser accepts:

- **Markdown PRDs** — heading-structured documents with sections like Background, Goals, User Stories, Acceptance Criteria
- **YAML/JSON plan documents** — already partially structured
- **Word/Google Doc exports** — converted to markdown via Pandoc or similar
- **Confluence page exports** — converted to markdown

### 6.2 Output

A standard `ParsedModel` with:

- `processes[]` — derived from epic/initiative-level headings
- `nodes[]` — one per story, task, or work unit identified
- `edges[]` — derived from explicit dependencies ("after X", "blocked by Y") or sequencing language
- `lanes[]` — derived from team/owner mentions
- `data_objects[]` — derived from API contracts, schemas, or data references
- `source_file`, `source_paragraphs[]` — paragraph-level provenance

### 6.3 Algorithm

The spec parser is the **only** stage where the LLM acts as a creator, not an editor. Its outputs are constrained by:

1. **Structured-output enforcement** — JSON Schema on the LLM response
2. **Paragraph-level provenance** — every node carries `source_paragraphs: [int]` referencing line ranges in the input
3. **Grounding verification** — a verification step (analogous to capsule verification) checks that every node's `name`, `description`, and `acceptance_criteria` field is supported by the cited paragraphs
4. **Round-trip check** — for each node, the system can produce a "source extract" that quotes the supporting paragraphs verbatim

### 6.4 Pseudocode

```python
def parse_spec(spec_path: Path, llm_provider, config) -> ParsedModel:
    raw = read_markdown(spec_path)
    paragraphs = split_into_paragraphs(raw)

    # Step 1: Identify epic/initiative scope
    epic = llm_provider.complete_structured(
        prompt=build_epic_extraction_prompt(paragraphs),
        schema=EPIC_SCHEMA,
    )

    # Step 2: Identify stories with provenance
    stories = llm_provider.complete_structured(
        prompt=build_story_extraction_prompt(paragraphs, epic),
        schema=STORY_LIST_SCHEMA,
    )
    # Each story has: name, description, acceptance_criteria,
    #                 owner_hint, source_paragraphs[], dependencies[]

    # Step 3: Identify dependencies between stories
    edges = llm_provider.complete_structured(
        prompt=build_dependency_prompt(stories),
        schema=DEPENDENCY_LIST_SCHEMA,
    )

    # Step 4: Grounding verification
    for story in stories:
        if not verify_story_grounding(story, paragraphs):
            story.gaps.append(Gap("ungrounded_acceptance_criteria"))

    return ParsedModel(
        processes=[Process(id=epic.id, name=epic.name, ...)],
        nodes=[Node.from_story(s) for s in stories],
        edges=[Edge.from_dep(d) for d in edges],
        ...
    )
```

### 6.5 Schemas

`STORY_SCHEMA`:

```json
{
  "type": "object",
  "properties": {
    "id": {"type": "string"},
    "name": {"type": "string"},
    "description": {"type": "string"},
    "acceptance_criteria": {"type": "array", "items": {"type": "string"}},
    "owner_hint": {"type": "string"},
    "source_paragraphs": {"type": "array", "items": {"type": "integer"}},
    "estimated_complexity": {"type": "string", "enum": ["xs","s","m","l","xl"]},
    "depends_on": {"type": "array", "items": {"type": "string"}}
  },
  "required": ["id","name","description","acceptance_criteria","source_paragraphs"]
}
```

---

## 7. Tech Corpus

### 7.1 Concept

The existing corpus model (procedures, policies, regulations, rules, data dictionaries) maps directly onto an engineering knowledge corpus:

| Original Corpus Type | Tech Corpus Equivalent                                      |
| -------------------- | ----------------------------------------------------------- |
| Procedure            | Runbook, deployment guide, on-call playbook                 |
| Policy               | Coding standard, security policy, naming convention         |
| Regulation           | Compliance requirement, data residency rule, GDPR/SOC mandate |
| Rule                 | Architecture decision record (ADR), design principle        |
| Data dictionary      | API spec, OpenAPI/AsyncAPI definition, schema registry      |
| System               | Service catalog entry, infrastructure component             |
| Training             | Onboarding doc, system tutorial                             |
| Glossary             | Domain term definition, acronym list                        |

### 7.2 Reuse of Matching Algorithm

The 7-factor weighted matching algorithm from `GROUNDING-AGENT-SPEC.md` works unchanged. The factors translate naturally:

- **Subdomain match** → engineering subdomain (auth, payments, frontend, data-platform)
- **Tag overlap ratio** → tech tags (python, postgres, kafka, react)
- **Doc type relevance** → ADR > runbook > tutorial for a new feature story
- **Role match** → owning squad / team
- **Data object match** → API/schema names referenced in the spec
- **Related corpus bonus** → ADRs that build on each other
- **Goal type match** → state_transition (deployments) vs data_production (ETL features)

### 7.3 Outcome

For a story like "Add /v2/refunds endpoint with idempotency support", the enricher matches:

- **Procedure**: deployment runbook for the payments service
- **Policy**: API versioning standard
- **Rule**: ADR-042 "Idempotency keys for state-mutating endpoints"
- **Regulation**: PCI-DSS requirement applicable to payment APIs
- **Data dictionary**: refund object schema in the API catalog

The capsule generated for the story cites all five — exactly the same grounding pattern as the BPMN pipeline.

---

## 8. Triple Generation Adaptations

### 8.1 Capsule

Capsule sections map naturally to JIRA story fields:

| Capsule Section       | JIRA Story Field                              |
| --------------------- | --------------------------------------------- |
| Purpose               | Description (top paragraph)                   |
| Procedure             | Description (implementation guidance)         |
| Business Rules        | Description (constraints)                     |
| Inputs Required       | Description (table) + linked API specs        |
| Outputs Produced      | Description (table) + linked API specs        |
| Decision Parameters (job aid) | Description (decision table) + custom field |
| Exception Handling    | Description (edge cases) + risk register link |
| Regulatory Context    | Compliance custom field + linked policy ADR   |
| Notes                 | Comments thread starter                       |

### 8.2 Intent

Intent fields map to **acceptance criteria and Definition of Done**:

| Intent Field      | JIRA Equivalent                                       |
| ----------------- | ----------------------------------------------------- |
| `goal`            | Story summary line                                    |
| `preconditions`   | "Given..." in Gherkin acceptance criteria             |
| `outputs`         | "Then..." in Gherkin acceptance criteria              |
| `invariants`      | Definition of Done items                              |
| `success_criteria`| Acceptance criteria checklist                         |
| `failure_modes`   | Risk register entries / rollback criteria             |
| `forbidden_actions` | Architectural guardrails (no UI scraping, no PII in logs) |

### 8.3 Contract

The integration contract becomes the **technical breakdown**:

- Each `source` in the contract → Sub-task: "Integrate with {source.name}"
- Each `sink` → Sub-task: "Publish to {sink.name}"
- Each `event` → Sub-task: "Emit {event.topic}"
- `audit` requirements → Sub-task: "Add audit logging"
- `sla_ms` and `retry_policy` → Custom fields

This gives Engineering a JIRA breakdown that is automatically aligned with the API catalog and architecture standards.

---

## 9. Stage 7 — JIRA Synchronisation

### 9.1 Sync Strategy

**Idempotent, one-way (triples → JIRA)**, keyed by stable IDs.

Each triple has a stable `capsule_id` (e.g., `CAP-PAY-RFD-001`). The first sync creates a JIRA issue and stores the JIRA key (e.g., `PAY-1234`) in a local map file (`jira-sync.map.yaml`). Subsequent syncs:

1. Look up the JIRA key in the map
2. If found → update the existing issue (description, acceptance criteria, sub-tasks)
3. If not found → create a new issue and append to the map
4. Compute a hash of the triple content; skip update if unchanged

### 9.2 Hierarchy

```
Epic (one per process / initiative)
  ├── Story  (one per "task" triple)
  │     ├── Sub-task: source binding (one per contract.source)
  │     ├── Sub-task: sink binding   (one per contract.sink)
  │     ├── Sub-task: event emission (one per contract.event)
  │     └── Sub-task: audit logging  (one if contract.audit defined)
  ├── Story  (decision triples become spike/decision stories)
  │     └── ...
  └── ...
```

### 9.3 Field Mapping

| Triple Source                              | JIRA Field                         |
| ------------------------------------------ | ---------------------------------- |
| Process / epic name                        | Epic name                          |
| `capsule_id`                               | Custom field: "Triple ID"          |
| Capsule body (Purpose section)             | Description (top section)          |
| Capsule body (full)                        | Description (full markdown)        |
| Intent `goal`                              | Summary                            |
| Intent `success_criteria`                  | Acceptance Criteria custom field   |
| Intent `failure_modes`                     | Risk register linked items         |
| Capsule `owner_role`                       | Component / Team field             |
| Capsule `predecessor_ids`                  | "is blocked by" link               |
| Capsule `successor_ids`                    | "blocks" link                      |
| Capsule `regulation_refs`                  | Compliance custom field            |
| Capsule `corpus_refs`                      | Custom field: "Evidence Links" (markdown list with links to corpus docs) |
| Capsule `gaps`                             | Custom field: "Open Questions"     |
| Capsule `grounding_verification.valid`     | Custom field: "Spec Grounded?"     |
| Contract `sources` / `sinks` / `events`    | Sub-tasks (see 9.2)                |
| Contract `binding_status`                  | Custom field: "Integration Readiness" |
| Job aid `dimensions` and `rules`           | Custom field: "Decision Matrix" + linked attachment |
| Triple `version`                           | Custom field: "Triple Version"     |

### 9.4 Conflict Handling

Out of scope for V1 — the triple is the source of truth. If a developer edits a JIRA story directly, the next pipeline run will overwrite the description. A configurable `protected_fields` list in `mda.config.yaml` can specify JIRA fields the sync will never overwrite (e.g., `Sprint`, `Story Points` if estimated by the team, `Status`).

### 9.5 API Client

`cli/jira/client.py` wraps the JIRA REST API:

- Uses Personal Access Tokens (PATs) from environment variables
- Implements rate limiting, retry with exponential backoff, and idempotent create
- Supports JIRA Cloud, JIRA Server, and JIRA Data Center
- All field mappings configurable via `mda.config.yaml > jira > field_mapping`
- Offers a `--dry-run` mode that prints planned changes without calling the API

### 9.6 Configuration

```yaml
jira:
  enabled: true
  base_url: "https://example.atlassian.net"
  api_token_env: "JIRA_API_TOKEN"
  user_email_env: "JIRA_USER_EMAIL"
  project_key: "PAY"
  epic_issue_type: "Epic"
  story_issue_type: "Story"
  subtask_issue_type: "Sub-task"
  protected_fields: ["Sprint", "Story Points", "Status"]
  custom_field_mapping:
    triple_id: "customfield_10100"
    evidence_links: "customfield_10101"
    open_questions: "customfield_10102"
    grounded: "customfield_10103"
  sync_map_path: "jira-sync.map.yaml"
  dry_run: false
```

---

## 10. New CLI Commands

| Command                           | Purpose                                                              |
| --------------------------------- | -------------------------------------------------------------------- |
| `mda parse-spec <path>`           | Parse a PRD / spec markdown file into a `ParsedModel`                |
| `mda parse-stories <path>`        | Parse a user-story bundle into a `ParsedModel`                       |
| `mda jira sync`                   | Push triples to JIRA (creates / updates with idempotent map)         |
| `mda jira diff`                   | Show what would change if `mda jira sync` were run now               |
| `mda jira pull-status`            | Read-only: pull JIRA statuses back into a status report (no writes)  |
| `mda corpus add --tech <type>`    | Add a tech corpus document (ADR, runbook, API spec, etc.)            |

The existing commands (`mda enrich`, `mda generate`, `mda validate`, `mda gaps`, `mda graph`, `mda docs`) work unchanged with spec-derived models.

---

## 11. Verification Checks

Adds new check categories to `TEST-SPEC.md`:

| Check ID | Name                                | Severity | Description                                                           |
| -------- | ----------------------------------- | -------- | --------------------------------------------------------------------- |
| S01      | Spec parser provenance              | CRITICAL | Every parsed node has `source_paragraphs[]` populated                 |
| S02      | Spec grounding round-trip           | HIGH     | Each node's claims are present in the cited source paragraphs         |
| S03      | Story has acceptance criteria       | HIGH     | Every story-derived node has at least one acceptance criterion        |
| S04      | Tech corpus matched                 | MEDIUM   | Every story has at least one tech-corpus match (ADR, runbook, etc.)   |
| J01      | JIRA sync idempotency               | CRITICAL | Re-running `mda jira sync` on unchanged triples produces zero updates |
| J02      | JIRA hierarchy consistency          | HIGH     | Every Story has a parent Epic; every Sub-task has a parent Story      |
| J03      | JIRA dependency integrity           | HIGH     | All `predecessor_ids` resolve to existing JIRA links                  |
| J04      | Protected fields untouched          | HIGH     | Sync never modifies fields listed in `jira.protected_fields`          |
| J05      | Sync map integrity                  | MEDIUM   | `jira-sync.map.yaml` references no orphaned triples                   |

The existing G01–G07 grounding checks apply to spec-parsed inputs as well as BPMN-parsed inputs.

---

## 12. Implementation Plan

### 12.1 Milestones

| Milestone | Deliverable | Effort |
| --- | --- | --- |
| **M1** — Spec parser MVP | `cli/parsers/spec_parser.py` + provenance tracking + S01/S02 checks | 3-4 weeks |
| **M2** — Tech corpus | Templates for ADR/runbook/API-spec, sample tech corpus, doc updates | 2 weeks |
| **M3** — Story parser | `cli/parsers/story_parser.py` for pre-existing user-story bundles | 1-2 weeks |
| **M4** — JIRA client | `cli/jira/client.py` with idempotent create/update, dry-run, retries | 3 weeks |
| **M5** — Stage 7 sync | `cli/pipeline/stage7_jira_sync.py`, sync map, hierarchy, field mapping | 3 weeks |
| **M6** — End-to-end | Integration tests, sample end-to-end PRD-to-JIRA run, docs site update | 2 weeks |

Total: ~14-16 weeks for a single engineer; less in parallel.

### 12.2 Sequencing Notes

- M1 must precede M3 (story parser is a constrained variant of spec parser)
- M2 can run in parallel with M1
- M4 and M5 are sequential
- M6 integrates everything; needs M1+M5 complete

### 12.3 Risk Register

| Risk | Likelihood | Mitigation |
| --- | --- | --- |
| LLM spec parsing produces drift between runs | High | Temperature 0.0-0.1, structured output, deterministic seed where supported, hash-based idempotency |
| JIRA custom-field IDs vary per instance | High | All field mappings in config, no hard-coded IDs |
| Large specs exceed LLM context | Medium | Chunked extraction with cross-chunk dependency resolution pass |
| Conflicting JIRA edits (manual vs sync) | Medium | `protected_fields` config + clear documentation of one-way model |
| Tech corpus quality lags spec quality | Medium | Same gap-flagging mechanism; gaps drive corpus authoring backlog |
| Compliance / audit concerns over generated stories | Low | Provenance chain provides auditable trail; grounding verification logs retained |

---

## 13. Architectural Invariants Preserved

The extension does not alter:

- Triple schemas (`schemas/capsule.schema.json`, `intent.schema.json`, `contract.schema.json`)
- Ontology files (`goal-types.yaml`, `status-lifecycle.yaml`, etc.)
- The grounding verification algorithm (`GROUNDING-AGENT-SPEC.md`)
- The job aid model
- The lifecycle states (draft / review / approved / current / deprecated / archived)

Anything that consumes triples today (the docs site, the validator, the gap reporter) continues to work with spec-derived triples without change.

---

## 14. Open Questions

1. **Story-point estimation** — Should the LLM produce estimates? If so, with what calibration data? Recommendation: V1 outputs a `complexity` enum (xs/s/m/l/xl); estimates are added by the team manually
2. **Bidirectional sync** — When (if ever) should JIRA edits flow back to triples? Recommendation: defer to V2; collect feedback from V1 usage first
3. **Multi-instance JIRA** — How to handle organisations with multiple JIRA instances (Cloud + Data Center)? Recommendation: per-process configuration; one instance per `mda.config.yaml`
4. **Status pull-back** — Should JIRA status be visible in `mda status`? Recommendation: yes, via `mda jira pull-status`, but read-only — does not influence triple state
5. **PII in specs** — How to handle sensitive content in source PRDs that should not appear in JIRA? Recommendation: a `redact` config block listing patterns to scrub before sync

---

## 15. Glossary

| Term | Definition |
| --- | --- |
| **Spec parser** | A new pipeline stage that converts prose specifications into a `ParsedModel` |
| **Story parser** | A specialisation of spec parser for pre-existing user-story documents |
| **Tech corpus** | An engineering knowledge corpus (ADRs, runbooks, API specs, coding standards) |
| **Sync map** | A YAML file mapping `capsule_id` to JIRA issue key, enabling idempotent updates |
| **Protected fields** | JIRA fields the sync will never overwrite (e.g., Sprint, Story Points) |
| **Round-trip check** | A verification that a parsed node's claims can be quoted verbatim from its source paragraphs |
| **Triple** | The capsule + intent + contract artifact set produced for each work unit |
| **Provenance chain** | The recorded path from a generated artifact back to its source material |
