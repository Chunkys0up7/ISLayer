# MDA Intent Layer

An MDA-aligned transformation pipeline that converts BPMN process models into agent-executable intent specifications. It bridges business process modeling and AI agentic execution by producing structured artifacts that give an agent everything it needs to perform a business task.

## Quick Start

```bash
# Clone
git clone https://github.com/Chunkys0up7/ISLayer.git
cd ISLayer

# Install dependencies
pip install -r requirements.txt

# Explore the demo data
cd examples/income-verification
python ../../cli/mda.py status          # See triple status
python ../../cli/mda.py parse bpmn/income-verification.bpmn   # Parse BPMN
python ../../cli/mda.py corpus search "income"                 # Search corpus
python ../../cli/mda.py validate        # Validate triples
python ../../cli/mda.py docs serve      # Browse as a website
```

See [docs/getting-started.md](docs/getting-started.md) for a full walkthrough.

## What This Is

The MDA Intent Layer takes BPMN 2.0 process diagrams and transforms them into machine-readable artifacts that AI agents consume directly. The transformation follows the OMG Model-Driven Architecture (MDA) framework, providing formal traceability from business process to executable specification.

Every BPMN task produces exactly one **triple** --- three artifacts that together form a complete work package:

| Artifact | MDA Layer | Purpose |
|----------|-----------|---------|
| **Knowledge Capsule** (`.cap.md`) | CIM companion | Domain knowledge, business rules, regulatory constraints --- the HOW |
| **Intent Specification** (`.intent.md`) | PIM | Required outcome, preconditions, invariants, failure modes --- the WHAT |
| **Integration Contract** (`.contract.md`) | PSM | API endpoints, event schemas, authentication, SLAs --- the WHERE |

These triples are fed by a **Knowledge Corpus** --- 46 source documents (procedures, policies, regulations, rules, data dictionaries, system guides) that the pipeline draws from when generating capsules.

See [METHODOLOGY.md](METHODOLOGY.md) for the full theoretical foundation.

## CLI

The `mda` CLI provides 17 commands across 5 categories:

| Category | Commands |
|----------|----------|
| **Project** | `init`, `config` |
| **BPMN Ingestion** | `parse`, `ingest`, `reingest` |
| **Corpus** | `corpus index`, `corpus add`, `corpus search`, `corpus validate` |
| **Triples** | `validate`, `status`, `gaps`, `graph` |
| **LLM-Powered** | `enrich`, `generate`, `review` |
| **Docs** | `docs generate`, `docs build`, `docs serve` |

```bash
python cli/mda.py <command> [options]
```

LLM integration is provider-agnostic (Anthropic Claude, OpenAI, or local Ollama). All LLM commands have a `--skip-llm` fallback that produces template stubs.

See [docs/cli-reference.md](docs/cli-reference.md) for the complete reference.

## Project Structure

```
ISLayer/
├── README.md
├── METHODOLOGY.md              # MDA alignment rationale
├── CHANGELOG.md
├── requirements.txt            # Python dependencies
│
├── cli/                        # Python CLI (the mda command)
│   ├── mda.py                  # Entry point
│   ├── commands/               # Command handlers (14 commands)
│   ├── pipeline/               # 6-stage transformation pipeline
│   ├── models/                 # Data models (BPMN, enriched, triple, corpus)
│   ├── mda_io/                 # File I/O (frontmatter, BPMN XML, schema validation)
│   ├── llm/                    # LLM providers (Anthropic, OpenAI, Ollama) + prompts
│   └── output/                 # Console + JSON output formatting
│
├── schemas/                    # JSON Schema validation (5 schemas)
│   ├── capsule.schema.json
│   ├── intent.schema.json
│   ├── contract.schema.json
│   ├── corpus-document.schema.json
│   └── triple-manifest.schema.json
│
├── ontology/                   # Controlled vocabularies (5 files)
│   ├── goal-types.yaml         # data_production, decision, notification, state_transition, orchestration
│   ├── status-lifecycle.yaml   # draft, review, approved, current, deprecated, archived
│   ├── bpmn-element-mapping.yaml
│   ├── id-conventions.yaml
│   └── corpus-taxonomy.yaml    # 8 corpus document types
│
├── corpus/                     # Knowledge corpus (46 source documents)
│   ├── corpus.config.yaml      # Searchable index
│   ├── procedures/             # Step-by-step work instructions
│   ├── policies/               # Organizational policies
│   ├── regulations/            # Regulatory reference summaries
│   ├── rules/                  # Decision tables and business rules
│   ├── data-dictionary/        # Data object definitions
│   ├── systems/                # System/API documentation
│   ├── training/               # Onboarding guides
│   └── glossary/               # Domain terminology
│
├── templates/                  # Canonical file templates
│   ├── capsule.template.cap.md
│   ├── intent.template.intent.md
│   ├── contract.template.contract.md
│   └── mkdocs/                 # MkDocs site generation templates
│
├── pipeline/                   # Pipeline stage documentation (6 stages)
│
├── examples/                   # 3 demo processes with full triples
│   ├── loan-origination/       # 10 triples, BPMN, graph, gaps
│   ├── income-verification/    # 8 triples, BPMN, graph, gaps
│   └── property-appraisal/     # 9 triples, BPMN, graph, gaps
│
└── docs/                       # User guides and architecture docs
```

## Core Principles

- **One BPMN Task = One Triple** --- strict 1:1 mapping for full traceability
- **Anti-UI Principle** --- intents never use browser automation, screen scraping, or UI clicks
- **Conservative Enrichment** --- flag gaps rather than hallucinate content
- **Separation of Change Rates** --- capsules change quarterly, contracts change monthly, runtime changes weekly
- **Artifacts for Agents** --- every triple is designed to be consumed by an AI agent

## Documentation

### User Guides

- [Getting Started](docs/getting-started.md) --- Install, explore demos, create your first process (15 min)
- [CLI Reference](docs/cli-reference.md) --- All 17 commands with arguments, options, and examples
- [Process Owner Guide](docs/process-owner-guide.md) --- Day-to-day workflows for managing a process
- [Corpus Authoring Guide](docs/corpus-authoring.md) --- How to write and maintain corpus documents
- [Triple Review Guide](docs/triple-review.md) --- Review checklists by role

### Specifications

- [EXECUTION-SPEC.md](EXECUTION-SPEC.md) --- Complete build-from-scratch specification (5,342 lines)
- [TEST-SPEC.md](TEST-SPEC.md) --- Test suite recreation specification (1,251 lines)

### Architecture and Governance

- [Methodology](METHODOLOGY.md) --- MDA alignment, core principles, glossary
- [Architecture](docs/architecture.md) --- System design, pipeline stages, knowledge corpus
- [Governance Model](docs/governance-model.md) --- Roles, PR workflows, CI/CD
- [Lifecycle Management](docs/lifecycle-management.md) --- Status lifecycle, versioning, re-ingestion

## License

This project is licensed under the MIT License --- see [LICENSE](LICENSE) for details.
