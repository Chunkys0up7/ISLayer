# Architecture Specification

## Core Thesis

The MDA Intent Layer is an intent and integration layer. It sits between business process models (owned by analysts) and AI agent runtimes (owned by platform teams). Its sole purpose is to transform BPMN diagrams into structured artifacts that agents can consume without ambiguity.

The intent layer does not execute processes. It does not orchestrate agents. It does not provide a runtime. It produces artifacts --- triples --- that any conforming agent runtime can consume. The architecture enforces this boundary rigorously: the intent layer's output is data, not code.

## Three Artifact Types

Every BPMN task produces exactly one triple. The three artifacts in each triple correspond to the three layers of OMG's Model-Driven Architecture:

| Artifact | MDA Layer | Content | Change Cadence |
|----------|-----------|---------|----------------|
| Knowledge Capsule | CIM companion | Domain knowledge, business rules, edge cases, regulatory constraints, terminology | Quarterly |
| Intent Specification | PIM | Goal definition, preconditions, postconditions, inputs, outputs, outcome verification, forbidden actions | Quarterly |
| Integration Contract | PSM | API endpoints, authentication, event schemas, rate limits, retry policies, error mappings, circuit breaker config | Monthly |

The capsule answers "what does the agent need to know." The intent spec answers "what must the agent achieve." The contract answers "how does the agent connect."

## BPMN Ingestion Pipeline

The pipeline transforms BPMN 2.0 XML into draft triples through six stages:

1. **Parser** --- Reads BPMN XML, extracts elements, builds an in-memory process graph.
2. **Mapper** --- Maps each BPMN element to a triple type using the element mapping ontology (`ontology/bpmn-element-mapping.yaml`). Assigns default goal types. Identifies elements that produce full triples versus metadata-only extraction.
3. **Generator** --- Produces draft artifacts from canonical templates. Populates fields that can be derived deterministically from the BPMN model (IDs, names, predecessor/successor relationships, lane-derived ownership). Leaves all other fields as gaps.
4. **Enricher** --- Applies conservative enrichment. Cross-references data objects, message flows, and boundary events to populate input/output fields and event definitions. Flags anything it cannot determine with certainty.
5. **Linker** --- Builds the cross-reference matrix. Connects each capsule to its intent spec and contract. Resolves call activity references to sub-process repositories. Populates the triple manifest.
6. **Validator** --- Validates all generated artifacts against JSON schemas (`schemas/*.schema.json`). Reports validation errors, gap counts, and cross-reference integrity.

The pipeline is deterministic: the same BPMN input always produces the same draft output. Human enrichment happens after pipeline execution, not during it.

## Knowledge Corpus

The knowledge corpus is the raw material from which capsules are distilled. It contains the procedural knowledge, business rules, regulatory context, and system documentation that an AI agent needs to understand how a business task should be performed.

### What the Corpus Contains

The corpus supports eight document types, each serving a distinct role in the knowledge supply chain:

| doc_type | Purpose |
|----------|---------|
| `procedure` | Step-by-step work instructions for performing a task |
| `policy` | Organizational policies that govern how work is performed |
| `regulation` | External regulatory requirements (statutes, rules, standards) |
| `rule` | Business rules, decision tables, and threshold definitions |
| `data-dictionary` | Field definitions, valid values, data types, and schema documentation |
| `system` | System and integration documentation (API behavior, platform constraints) |
| `training` | Training materials, onboarding guides, and reference examples |
| `glossary` | Domain terminology definitions and abbreviations |

### Where It Lives

The corpus resides in the `corpus/` directory within the engine repository. Each corpus document is a Markdown file with the `.corpus.md` extension. Process-specific repositories may maintain a `corpus-local/` directory for documents scoped to that process; these are merged with the main corpus at enrichment time.

### How It Is Structured

Each corpus document is a Markdown file with YAML frontmatter. The frontmatter contains structured metadata --- document type, domain, applicability rules, tags, and versioning --- while the Markdown body contains the knowledge content itself (procedures, rules, definitions, etc.). The `.corpus.md` extension distinguishes corpus documents from other Markdown files in the repository.

### How It Is Indexed

The file `corpus/corpus.config.yaml` serves as the corpus index. It lists every corpus document with its metadata, enabling the enricher to filter and match candidates without reading every document's full content. The index is the entry point for all corpus lookups during pipeline execution.

### How It Connects to Capsules

During Stage 2 (Enricher), the pipeline matches corpus documents to BPMN tasks using a multi-factor scoring algorithm that considers process IDs, task name patterns, domains, task types, tags, and roles. During Stage 3 (Capsule Generator), the matched corpus content is distilled into capsule sections --- procedures, business rules, regulatory context, inputs/outputs, and exception handling. Each capsule records its source corpus documents in a `corpus_refs` frontmatter field, maintaining full traceability from capsule content back to authoritative source material.

### Single Source of Truth

The corpus is the single source of truth for domain knowledge. Capsules are per-task views distilled from it. When the underlying knowledge changes --- a regulation is updated, a procedure is revised, a business rule threshold is adjusted --- the corpus document is updated and the affected capsules are regenerated. This ensures that capsules always reflect the current state of organizational knowledge without requiring manual synchronization across dozens of individual task artifacts.

## Intent Specification Format Rationale

Intent specs are deliberately platform-independent. They define outcomes, not procedures. An intent spec says "the agent must produce a verified income figure" --- it never says "call the Payroll API" or "query the income_records table." This separation ensures that intent specs survive platform migrations, vendor changes, and API version upgrades without modification.

Key structural decisions:

- **Goal type** is drawn from a controlled vocabulary (`ontology/goal-types.yaml`): data_production, decision, notification, state_transition, orchestration. This enables agent runtimes to select appropriate execution strategies.
- **Preconditions** are observable states, not implementation checks. "Borrower has submitted tax returns" rather than "tax_return_document_id is not null."
- **Outcome verification** is a set of conditions that confirm success. These are the agent's acceptance criteria.
- **Forbidden actions** are explicit prohibitions. They constrain the solution space, preventing agents from taking shortcuts that violate business rules or compliance requirements.

## Integration Contract Format Rationale

Integration contracts are the only artifacts that contain technology-specific detail. This isolation means that when an API changes, only the contract changes --- the intent spec and capsule remain stable.

Key structural decisions:

- **Endpoint definitions** include the full connection specification: URL pattern, HTTP method, authentication scheme, required headers, request/response schemas.
- **Event schemas** define the structure of messages consumed or produced by the task.
- **Error mappings** translate platform-specific error codes into business-meaningful outcomes. An HTTP 429 becomes "rate limit exceeded --- retry with backoff." An HTTP 404 becomes "borrower record not found --- escalate to manual review."
- **Circuit breaker configuration** defines failure thresholds, timeout durations, and fallback behavior. This is operational detail that belongs in the contract, not the intent spec.

## Anti-UI Principle

Intent specifications must never be satisfied through browser automation, screen scraping, UI clicks, or any form of graphical interface interaction. This is a hard architectural constraint, not a preference.

Rationale:

- UI-based execution is fragile. A CSS class change breaks the agent.
- UI-based execution is unauditable. There is no structured request/response to log.
- UI-based execution violates the PSM boundary. The UI is a presentation layer, not an integration layer.

If a task can only be fulfilled through a UI, the integration contract must be flagged with a gap status. The gap indicates that an API or event-based integration path must be established before the triple can reach `current` status.

## Triple-File Structure

Within a process repository, each task's artifacts follow a consistent naming and directory convention:

```
process-repo/
├── triple-manifest.json          # Index of all triples in this process
├── tasks/
│   ├── {task-id}/
│   │   ├── {task-id}.cap.md      # Knowledge Capsule
│   │   ├── {task-id}.intent.md   # Intent Specification
│   │   └── {task-id}.contract.md # Integration Contract
│   ├── {task-id}/
│   │   ├── ...
```

The triple manifest (`triple-manifest.json`) is a machine-readable index validated against `schemas/triple-manifest.schema.json`. It lists every triple in the process, its current lifecycle status, gap counts, and cross-references.

## Cross-Reference Matrix

Every artifact cross-references the other two artifacts in its triple:

- The capsule references `intent_id` and `contract_id`.
- The intent spec references `capsule_id` and `contract_id`.
- The contract references `capsule_id` and `intent_id`.

Cross-process references (call activities, sub-processes) include the target repository and the target triple ID. The linker stage validates that all cross-references resolve to existing artifacts.

The triple manifest aggregates these references into a single index, enabling tools and agents to navigate the entire process graph without parsing individual artifacts.

## Intent-Driven Agentic Execution Pattern

When an agent receives a triple, it follows this consumption pattern:

1. **Read the capsule** to acquire domain knowledge. The capsule provides business rules, terminology, edge cases, and regulatory constraints. The agent internalizes this context before attempting execution.
2. **Read the intent spec** to understand the goal. The agent identifies the goal type, checks preconditions against current state, and plans an execution strategy that satisfies the outcome verification criteria while avoiding forbidden actions.
3. **Read the contract** to determine how to connect. The agent uses endpoint definitions, authentication schemes, and event schemas to make concrete API calls or publish/subscribe to events.
4. **Execute and verify.** The agent performs the task, then checks the outcome verification criteria. If all criteria are met, the task is complete. If any criteria fail, the agent can retry, escalate, or report failure --- depending on the contract's error mapping and circuit breaker configuration.

This pattern is deliberately generic. Any agent runtime that can read structured markdown and JSON can consume triples. The architecture does not prescribe a specific agent framework, LLM provider, or orchestration platform.

## Why This Architecture Wins

**Separation of concerns.** Business knowledge, intent definition, and platform integration are isolated in separate artifacts with separate change cadences. A change to an API endpoint does not require re-reviewing business rules.

**Agent replaceability.** Because triples are data, not code, any conforming agent can consume them. Swapping agent runtimes, LLM providers, or orchestration platforms requires zero changes to the triples themselves.

**BPMN becomes executable.** Organizations with existing BPMN investments --- and most large enterprises have substantial BPMN libraries --- can transform those models into agent-executable specifications without discarding their process modeling investment.

**Knowledge and execution unified.** The capsule ensures that domain knowledge travels with the task. Agents do not need to search documentation, ask humans, or guess at business rules. The knowledge is co-located with the intent and the integration path, forming a complete work package.

**Auditable by construction.** Every triple traces back to a BPMN task. Every lifecycle transition is recorded in Git history. Every gap is explicitly flagged. The architecture produces an audit trail as a natural byproduct of normal operation.
