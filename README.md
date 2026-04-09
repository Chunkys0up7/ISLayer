# MDA Intent Layer

An MDA-aligned transformation pipeline that converts BPMN process models into agent-executable intent specifications. The intent layer bridges the gap between business process modeling and AI agentic execution by producing structured artifacts that give an agent everything it needs to perform a business task without human intervention.

## What This Is

The MDA Intent Layer takes BPMN 2.0 process diagrams --- the standard for documenting business processes --- and transforms them into a set of machine-readable artifacts that AI agents can consume directly. The transformation follows the OMG Model-Driven Architecture (MDA) framework, providing formal traceability from business process to executable specification.

See [METHODOLOGY.md](METHODOLOGY.md) for the full theoretical foundation.

## The Three Artifacts

Every BPMN task produces exactly one **triple** --- three artifacts that together form a self-contained work package for an agent:

| Artifact | MDA Layer | Purpose |
|----------|-----------|---------|
| **Knowledge Capsule** | CIM companion | Domain knowledge, business rules, edge cases, regulatory constraints |
| **Intent Specification** | PIM | What outcome must be achieved, preconditions, postconditions, verification criteria |
| **Integration Contract** | PSM | API endpoints, event schemas, authentication, error handling, retry policies |

### Core Principle: One BPMN Task = One Triple

The mapping between BPMN tasks and triples is strict and 1:1. No merging of tasks into a single spec. No splitting of a task across multiple specs. This constraint ensures full traceability from process model to executable specification.

## Anti-UI Principle

Intent specifications must never be satisfied through browser automation, screen scraping, UI clicks, or any form of graphical interface interaction. If the only path to fulfillment is through a UI, the integration contract is incomplete and must be flagged for remediation. Agents execute through APIs and events, not through simulated human interaction.

## Directory Structure

```
mda-intent-engine/
├── METHODOLOGY.md          # MDA alignment rationale and theoretical foundation
├── CHANGELOG.md            # Project changelog
├── schemas/                # JSON Schemas for artifact validation
│   ├── capsule.schema.json
│   ├── intent.schema.json
│   ├── contract.schema.json
│   └── triple-manifest.schema.json
├── templates/              # Canonical templates for each artifact type
│   ├── capsule.template.cap.md
│   ├── intent.template.intent.md
│   ├── contract.template.contract.md
│   └── process-repo-scaffold/
├── ontology/               # Controlled vocabularies and element mappings
│   ├── goal-types.yaml
│   ├── status-lifecycle.yaml
│   └── bpmn-element-mapping.yaml
├── pipeline/               # Pipeline stage definitions
├── validation/             # Validation tooling
├── examples/               # Demo BPMN processes
│   ├── loan-origination/
│   ├── income-verification/
│   └── property-appraisal/
└── docs/                   # Detailed guides
    ├── architecture.md
    ├── governance-model.md
    └── lifecycle-management.md
```

## How to Use

1. **Create a process repository** using the scaffold in `templates/process-repo-scaffold/`. Each repository corresponds to one bounded context (one business process).

2. **Ingest a BPMN diagram** by running it through the transformation pipeline. The pipeline parses the BPMN XML, maps elements to triples, generates draft artifacts using the canonical templates, and validates them against the JSON schemas.

3. **Review the generated triples.** Draft triples will have gaps --- places where the pipeline could not determine business rules, API endpoints, or edge cases. Gaps are flagged honestly rather than filled with fabricated content. Human reviewers fill gaps and promote triples through the lifecycle (draft, review, approved, current).

4. **Agents consume current triples.** Once a triple reaches `current` status, it is a complete, validated work package. An agent receives the capsule (domain knowledge), the intent spec (what to achieve), and the contract (how to connect), and executes the task.

## Documentation

### User Guides

- [docs/getting-started.md](docs/getting-started.md) --- Quick start: install, explore demos, create your first process
- [docs/cli-reference.md](docs/cli-reference.md) --- Complete CLI command reference (all 17 commands)
- [docs/process-owner-guide.md](docs/process-owner-guide.md) --- Day-to-day guide for process owners
- [docs/corpus-authoring.md](docs/corpus-authoring.md) --- How to write and maintain corpus documents
- [docs/triple-review.md](docs/triple-review.md) --- Review checklist for triple PRs

### Architecture and Governance

- [METHODOLOGY.md](METHODOLOGY.md) --- Theoretical foundation, MDA alignment, core principles
- [docs/architecture.md](docs/architecture.md) --- System architecture and design decisions
- [docs/governance-model.md](docs/governance-model.md) --- Roles, PR workflows, CI/CD requirements
- [docs/lifecycle-management.md](docs/lifecycle-management.md) --- Status lifecycle, versioning, change management

## License

License terms to be determined.
