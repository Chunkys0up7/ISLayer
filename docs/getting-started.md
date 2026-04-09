# Getting Started

This guide walks you through setting up the MDA Intent Layer and running your first BPMN ingestion. You will parse a real BPMN process, explore the generated triples, and scaffold your own process repository -- all in about 15 minutes.

## Prerequisites

- **Python 3.10+** -- check with `python --version`
- **Git**
- **A BPMN 2.0 XML file** -- or use one of the three included demos
- **(Optional) An LLM API key** -- Anthropic (`ANTHROPIC_API_KEY`), OpenAI (`OPENAI_API_KEY`), or a local [Ollama](https://ollama.ai) instance. Without one the CLI still works in `--skip-llm` mode.

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/Chunkys0up7/ISLayer.git
cd ISLayer
pip install -r cli/requirements.txt
```

This installs the core dependencies: PyYAML, jsonschema, Rich, Jinja2, and the optional LLM SDKs (anthropic, openai). MkDocs and mkdocs-material are included for documentation serving.

### 2. Explore the Demo Data

The repo ships with three fully worked examples under `examples/`. Start with `income-verification` -- a mortgage-underwriting process that verifies applicant income through W-2s, self-employment docs, and IRS transcripts.

```bash
cd examples/income-verification
```

**See what triples already exist:**

```bash
python ../../cli/mda.py status
```

This shows every BPMN task and whether its capsule, intent, and contract files are present. You should see five tasks: `receive-request`, `classify-employment`, `verify-w2`, `verify-self-employment`, `calc-qualifying`, and `emit-verified`.

**Parse the BPMN file into a typed object model:**

```bash
python ../../cli/mda.py parse bpmn/income-verification.bpmn
```

This reads the BPMN 2.0 XML and outputs a structured YAML representation of all tasks, gateways, sequence flows, and data objects.

**Search the knowledge corpus:**

```bash
python ../../cli/mda.py corpus search "income"
```

The corpus contains procedure docs, policies, regulations, rules, data dictionaries, system descriptions, training materials, and glossary entries that feed into capsule generation.

**Validate all triples against their schemas:**

```bash
python ../../cli/mda.py validate
```

This checks every `.cap.md`, `.intent.md`, and `.contract.md` file against the JSON schemas in `schemas/` and reports any structural or cross-reference issues.

**View open gaps:**

```bash
python ../../cli/mda.py gaps
```

Gaps flag missing content, unbound integrations, or incomplete decision logic that need human attention before the triples are production-ready.

**Generate a process graph:**

```bash
python ../../cli/mda.py graph --format mermaid
```

Outputs a Mermaid diagram showing how triples connect through predecessors, successors, and data flows. Paste the output into any Mermaid renderer to visualize.

**Launch the documentation site:**

```bash
python ../../cli/mda.py docs serve
```

Opens a local MkDocs site on port 8000 with rendered capsules, intents, contracts, and the process graph. Use `--port 9000` to change the port.

### 3. Create Your First Process

From the repo root, scaffold a new process repository:

```bash
cd ../..
python cli/mda.py init my-process --domain "My Domain" --prefix MP
```

This creates a ready-to-use directory structure:

```
my-process/
  mda.config.yaml       # Process configuration (domain, naming, integrations)
  bpmn/                  # Place your BPMN 2.0 XML files here
  triples/               # Generated capsule/intent/contract files
  decisions/             # DMN decision tables
  graph/                 # Process graph outputs
  gaps/                  # Gap analysis reports
  audit/                 # Audit trail records
  README.md
```

### 4. Ingest a BPMN File

Copy your BPMN file into the scaffolded directory and run the ingestion pipeline:

```bash
cd my-process

# Place your BPMN file
cp /path/to/my-process.bpmn bpmn/
```

**Without an LLM (template stubs with gaps):**

```bash
python ../cli/mda.py ingest bpmn/my-process.bpmn --skip-llm
```

This runs the full pipeline -- parse, map, generate -- but produces template stubs instead of LLM-generated content. Each stub contains the correct structure with `TODO` markers where human or LLM input is needed. This is the fastest way to get started and see the output shape.

**With an LLM (full content generation from corpus):**

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python ../cli/mda.py ingest bpmn/my-process.bpmn
```

The LLM reads your corpus documents and generates complete capsule procedures, intent specifications, and contract bindings. You can also use `--stages 1,2,3` to run specific pipeline stages individually.

### 5. Review and Edit Triples

After ingestion, each BPMN task gets a folder under `triples/` with three files:

```
triples/
  receive-request/
    receive-request.cap.md        # Knowledge Capsule (HOW)
    receive-request.intent.md     # Intent Specification (WHAT)
    receive-request.contract.md   # Integration Contract (WHERE)
    triple.manifest.json          # Links the three files together
```

**The review workflow:**

1. Open the generated `.cap.md` files and review the step-by-step procedures. These describe *how* a human would perform the task.
2. Check the `.intent.md` files for correct goal definitions, preconditions, and postconditions. These describe *what* outcome an agent must achieve.
3. Verify the `.contract.md` files map to the right systems and APIs. These describe *where* the agent connects.
4. Fill in any gaps flagged by `mda gaps` -- missing decision logic, unbound integrations, or incomplete data definitions.
5. Run `mda validate` to confirm everything passes schema validation.
6. Submit a pull request for team review.

### 6. Build the Knowledge Corpus

The corpus is the source-of-truth that feeds capsule generation. Add documents to give the LLM better context:

```bash
# Scaffold a new procedure document
python ../cli/mda.py corpus add procedure --domain "My Domain" --title "My Procedure"
```

This creates a Markdown file in the corpus with the correct frontmatter schema. Edit the file to add your procedure content, then rebuild the index:

```bash
python ../cli/mda.py corpus index
```

Supported corpus document types: `procedure`, `policy`, `regulation`, `rule`, `data-dictionary`, `system`, `training`, `glossary`.

## Project Structure

The MDA Intent Layer has two kinds of repositories:

**Engine repo** (this repository) -- contains the shared infrastructure:

| Directory     | Purpose                                          |
|---------------|--------------------------------------------------|
| `cli/`        | The `mda` CLI tool and all pipeline logic        |
| `schemas/`    | JSON schemas for capsules, intents, and contracts |
| `templates/`  | Jinja2 templates for triple generation           |
| `ontology/`   | ID conventions, status lifecycles, taxonomies    |
| `pipeline/`   | Pipeline stage definitions                       |
| `corpus/`     | Shared knowledge corpus                          |
| `validation/` | Validation rules and checks                      |

**Process repos** (one per BPMN process) -- contain process-specific artifacts:

| Directory    | Purpose                                      |
|--------------|----------------------------------------------|
| `bpmn/`      | Source BPMN 2.0 XML and metadata             |
| `triples/`   | Generated capsule + intent + contract files  |
| `decisions/` | DMN decision tables                          |
| `graph/`     | Process flow graphs (YAML, Mermaid, DOT)     |
| `gaps/`      | Gap analysis reports                         |
| `audit/`     | Audit trail of ingestion and review actions  |

## Core Concepts

**One BPMN Task = One Triple.** Every user task in a BPMN process maps to exactly three artifacts:

- **Knowledge Capsule** (`.cap.md`) -- The human-readable procedure. Describes *how* to perform the task step by step, including decision criteria, edge cases, and references to source regulations or policies.

- **Intent Specification** (`.intent.md`) -- The agent-executable outcome contract. Describes *what* the agent must achieve: the goal type, preconditions, postconditions, and success criteria. An agent reads this to know the desired outcome without being told the exact steps.

- **Integration Contract** (`.contract.md`) -- The API and system bindings. Describes *where* the agent connects: REST endpoints, event buses, data stores, and their schemas. Maps each system interaction to a concrete integration point.

**Knowledge Corpus** -- The collection of source documents (procedures, policies, regulations, data dictionaries) that provide the raw material for capsule generation. The LLM reads the corpus to produce accurate, grounded capsule content.

**Anti-UI Principle** -- Intent specifications never reference browser automation, UI clicks, or screen coordinates. Intents describe business outcomes and system interactions, not GUI workflows.

## Next Steps

- [CLI Reference](cli-reference.md) -- Full command reference for every `mda` subcommand
- [Architecture](architecture.md) -- System design and pipeline internals
- [Governance Model](governance-model.md) -- Review, approval, and versioning workflows
- [Lifecycle Management](lifecycle-management.md) -- How triples move from draft to production
- [Corpus Authoring Guide](corpus-authoring.md) -- Writing effective corpus documents
- [Triple Review Guide](triple-review.md) -- Reviewing generated triples for quality
