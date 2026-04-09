# CLI Reference

Complete reference for the `mda` command-line interface. The MDA Intent Layer CLI transforms BPMN process models into agent-executable intent specifications through a multi-stage pipeline.

## Installation

```bash
# Clone the repo
git clone https://github.com/Chunkys0up7/ISLayer.git
cd ISLayer

# Install dependencies
pip install -r cli/requirements.txt
```

## Usage

```
python cli/mda.py <command> [options]
```

### Global Options

These flags can be used with any command.

| Flag | Description |
|------|-------------|
| `--json` | Output in JSON format (for piping to other tools) |
| `-v, --verbose` | Verbose output with stack traces on errors |
| `--dry-run` | Show what would be done without making changes |
| `--config <path>` | Path to mda.config.yaml (auto-detected by default) |

---

## Commands

### Project Management

#### `mda init`

Scaffold a new process repository with the standard directory structure and a starter `mda.config.yaml`.

```
mda init <name> [options]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `name` | string | *(required)* | Process name (kebab-case recommended, e.g. `income-verification`) |
| `--domain` | string | none | Process domain (e.g. `Mortgage Lending`) |
| `--prefix` | string | none | 2-3 letter ID prefix used in artifact naming (e.g. `IV`) |
| `--output-dir` | path | current directory | Directory where the project folder will be created |

**Examples**

```bash
# Scaffold a basic project
mda init loan-origination

# Scaffold with domain and prefix
mda init income-verification --domain "Mortgage Lending" --prefix IV

# Create project in a specific directory
mda init property-appraisal --domain "Mortgage Lending" --prefix PA --output-dir ./projects
```

**Example Output**

```
Created project: income-verification
  income-verification/
    mda.config.yaml
    bpmn/
    triples/
    decisions/
    corpus/
    graph/
    gaps/
    audit/
```

**Notes**
- The `--prefix` value is used in generated artifact IDs (e.g. `CAP-IV-001`). Pick a short, unique prefix per process.
- If `--output-dir` is omitted, the project is created in the current working directory.

---

#### `mda config`

Show, get, set, or validate configuration values in `mda.config.yaml`.

```
mda config [options]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--show` | flag | `true` | Show the full current configuration |
| `--set <KEY> <VALUE>` | string pair | none | Set a config value by dotted key path |
| `--get <KEY>` | string | none | Get a single config value by dotted key path |
| `--validate` | flag | `false` | Validate the config file against the expected schema |

**Examples**

```bash
# Show the full config
mda config

# Get a specific value
mda config --get process.domain

# Set a value
mda config --set naming.id_prefix LO

# Validate the config file
mda config --validate
```

**Example Output**

```
# mda config --get process.domain
Mortgage Lending

# mda config --validate
Config valid: mda.config.yaml
  process.id: Process_LoanOrigination
  process.name: Loan Origination
  pipeline.version: 0.1.0-demo
```

**Notes**
- Key paths use dot notation: `process.name`, `naming.id_prefix`, `defaults.status`.
- `--show` is the default action when no other flag is provided.

---

### BPMN Ingestion

#### `mda parse`

Parse a BPMN 2.0 XML file into a typed object model (activities, gateways, events, sequence flows).

```
mda parse <bpmn_file> [options]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `bpmn_file` | path | *(required)* | Path to a BPMN 2.0 XML file |
| `--output` | path | stdout | Output file path for the parsed model |
| `--format` | `yaml` or `json` | `yaml` | Output format |

**Examples**

```bash
# Parse to stdout as YAML
mda parse bpmn/loan-origination.bpmn

# Parse to a file in JSON format
mda parse bpmn/loan-origination.bpmn --output parsed-model.json --format json

# Parse with verbose output
mda parse bpmn/income-verification.bpmn -v --output models/iv-parsed.yaml
```

**Example Output**

```yaml
process:
  id: Process_LoanOrigination
  name: Loan Origination
  elements:
    - id: Task_VerifyIncome
      type: serviceTask
      name: Verify Applicant Income
    - id: Gateway_CreditCheck
      type: exclusiveGateway
      name: Credit Score Decision
    ...
```

**Notes**
- This is Stage 1 of the pipeline. The parsed model feeds into `mda enrich` and `mda ingest`.
- Only BPMN 2.0 XML is supported. Visio or other proprietary formats must be exported to BPMN first.

---

#### `mda ingest`

Run the full pipeline: parse BPMN, enrich with corpus knowledge, generate triples (capsule, intent, contract), and validate.

```
mda ingest <bpmn_file> [options]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `bpmn_file` | path | *(required)* | Path to a BPMN 2.0 XML file |
| `--skip-llm` | flag | `false` | Skip LLM enrichment and generation; produce template stubs instead |
| `--stages` | string | all stages | Comma-separated stage numbers to run (e.g. `1,2,3`) |
| `--no-validate` | flag | `false` | Skip the validation stage at the end of the pipeline |

**Examples**

```bash
# Full ingestion pipeline
mda ingest bpmn/loan-origination.bpmn

# Ingest without calling the LLM (useful for testing or offline work)
mda ingest bpmn/income-verification.bpmn --skip-llm

# Run only stages 1 and 2 (parse + enrich)
mda ingest bpmn/property-appraisal.bpmn --stages 1,2

# Ingest with JSON output and skip validation
mda ingest bpmn/loan-origination.bpmn --json --no-validate
```

**Example Output**

```
Ingesting: bpmn/loan-origination.bpmn
  Stage 1: Parsing BPMN ............. OK (12 elements)
  Stage 2: Enriching with corpus .... OK (8 corpus matches)
  Stage 3: Generating triples ....... OK (12 capsules, 12 intents, 12 contracts)
  Stage 4: Validating ............... OK (0 errors, 2 warnings)

Output written to: triples/
```

**Notes**
- Use `--skip-llm` for offline work or CI environments where no API key is available. The generated stubs will have placeholder fields marked for manual review.
- `--stages` accepts a comma-separated list of integers. The stages are: 1 (parse), 2 (enrich), 3 (generate), 4 (validate).
- Combine `--dry-run` with `mda ingest` to preview the pipeline plan without writing any files.

---

#### `mda reingest`

Re-ingest an updated BPMN file, computing a diff against the previously ingested version and updating only changed triples.

```
mda reingest <bpmn_file> [options]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `bpmn_file` | path | *(required)* | Path to the updated BPMN 2.0 XML file |
| `--force` | flag | `false` | Force full regeneration without computing a diff |

**Examples**

```bash
# Re-ingest after BPMN edits (only changed elements are updated)
mda reingest bpmn/loan-origination.bpmn

# Force full regeneration
mda reingest bpmn/loan-origination.bpmn --force

# Preview what would change
mda reingest bpmn/income-verification.bpmn --dry-run
```

**Example Output**

```
Comparing against previous ingestion...
  Added:   Task_EscrowSetup
  Changed: Task_VerifyIncome (name updated)
  Removed: Task_ManualReview

Re-ingesting 2 elements (1 added, 1 changed)...
  Generating triples for Task_EscrowSetup .... OK
  Updating triples for Task_VerifyIncome ..... OK
  Archiving triples for Task_ManualReview .... OK
```

**Notes**
- The diff is computed against the previously parsed model stored during the last `mda ingest` or `mda reingest`.
- Removed elements have their triples archived, not deleted, preserving audit history.
- Use `--force` after schema or ontology changes to regenerate everything from scratch.

---

### Corpus Management

#### `mda corpus index`

Regenerate the `corpus.config.yaml` index by scanning all documents in the corpus directory.

```
mda corpus index
```

**Examples**

```bash
# Rebuild the corpus index
mda corpus index

# Rebuild with verbose output
mda corpus index -v
```

**Example Output**

```
Scanning corpus/...
  Found 14 documents across 5 types
  Updated corpus.config.yaml

Summary:
  procedure:        4
  policy:           3
  regulation:       2
  data-dictionary:  3
  glossary:         2
```

**Notes**
- Run this after manually adding or removing files from the `corpus/` directory.
- The generated index is used by `mda enrich` and `mda corpus search`.

---

#### `mda corpus add`

Scaffold a new corpus document with the correct frontmatter and directory structure.

```
mda corpus add <type> [options]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `type` | choice | *(required)* | Document type. One of: `procedure`, `policy`, `regulation`, `rule`, `data-dictionary`, `system`, `training`, `glossary` |
| `--domain` | string | none | Document domain (e.g. `Underwriting`) |
| `--title` | string | none | Document title |

**Examples**

```bash
# Add a new policy document
mda corpus add policy --domain "Underwriting" --title "Credit Score Thresholds"

# Add a regulation reference
mda corpus add regulation --title "TRID Disclosure Requirements"

# Add a data dictionary
mda corpus add data-dictionary --domain "Loan Origination"
```

**Example Output**

```
Created: corpus/policy/credit-score-thresholds.md
  type: policy
  domain: Underwriting
  title: Credit Score Thresholds

Edit the file to add content, then run: mda corpus index
```

**Notes**
- After adding a document, populate its content and run `mda corpus index` to update the index.
- Supported types: `procedure`, `policy`, `regulation`, `rule`, `data-dictionary`, `system`, `training`, `glossary`.

---

#### `mda corpus search`

Search corpus documents by full-text query with optional filters.

```
mda corpus search <query> [options]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `query` | string | *(required)* | Search query text |
| `--type` | string | none | Filter by document type (e.g. `policy`) |
| `--domain` | string | none | Filter by domain (e.g. `Underwriting`) |
| `--tags` | string | none | Filter by tags (comma-separated) |
| `--limit` | int | `10` | Maximum number of results to return |

**Examples**

```bash
# Search for anything mentioning credit scores
mda corpus search "credit score"

# Search only policy documents
mda corpus search "income verification" --type policy

# Search with domain filter and limit
mda corpus search "appraisal" --domain "Mortgage Lending" --limit 5

# Search with tags
mda corpus search "disclosure" --tags "compliance,trid"
```

**Example Output**

```
Found 3 results for "credit score":

  1. corpus/policy/credit-score-thresholds.md  (policy, Underwriting)
     ...minimum credit score of 620 for conventional loans...

  2. corpus/rule/credit-decision-matrix.md  (rule, Underwriting)
     ...credit score bands: 620-679 (fair), 680-739 (good)...

  3. corpus/data-dictionary/applicant-fields.md  (data-dictionary, Loan Origination)
     ...credit_score: integer, FICO score range 300-850...
```

---

#### `mda corpus validate`

Validate all corpus documents against the expected frontmatter schema and structure.

```
mda corpus validate
```

**Examples**

```bash
# Validate all corpus documents
mda corpus validate

# Validate with JSON output for CI
mda corpus validate --json
```

**Example Output**

```
Validating corpus documents...
  corpus/policy/credit-score-thresholds.md ......... OK
  corpus/rule/credit-decision-matrix.md ............ OK
  corpus/procedure/income-verification-steps.md .... WARN: missing 'domain' field
  corpus/glossary/lending-terms.md ................. OK

Result: 4 documents, 0 errors, 1 warning
```

---

### Triple Management

#### `mda validate`

Validate generated triples against their JSON schemas and cross-reference integrity rules.

```
mda validate [path] [options]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `path` | path | all triples | Path to a specific triple file or directory to validate |
| `--fail-on` | choice | none | Exit with non-zero code on this severity or higher. One of: `critical`, `high`, `medium`, `low` |

**Examples**

```bash
# Validate all triples in the project
mda validate

# Validate a specific triple directory
mda validate triples/Task_VerifyIncome/

# Validate and fail on high-severity issues (useful in CI)
mda validate --fail-on high

# Validate a single file
mda validate triples/Task_VerifyIncome/capsule.yaml
```

**Example Output**

```
Validating triples...
  triples/Task_VerifyIncome/
    capsule.yaml ......... OK
    intent.yaml .......... OK
    contract.yaml ........ WARN: missing sla.response_time_ms
  triples/Gateway_CreditCheck/
    capsule.yaml ......... OK
    intent.yaml .......... ERROR: invalid schema - missing 'preconditions'
    contract.yaml ........ OK

Result: 6 files, 1 error, 1 warning
```

**Notes**
- Schemas are resolved from the paths in `mda.config.yaml` under `pipeline.schemas`.
- Use `--fail-on critical` in CI pipelines to block merges on critical validation errors.

---

#### `mda status`

Show a summary of triple completion status across all process elements.

```
mda status
```

**Examples**

```bash
# Show status overview
mda status

# Show status in JSON format
mda status --json
```

**Example Output**

```
Triple Status: Loan Origination
  Total elements: 12

  Status breakdown:
    complete:    7  (58%)
    draft:       3  (25%)
    stub:        2  (17%)

  By type:
    capsules:    12/12
    intents:     10/12
    contracts:    9/12

  Binding status:
    bound:       5
    unbound:     7
```

---

#### `mda gaps`

List gaps and missing information across all triples.

```
mda gaps [options]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--severity` | choice | all | Filter by severity: `critical`, `high`, `medium`, `low` |
| `--type` | string | none | Filter by gap type (e.g. `missing-field`, `unresolved-reference`) |
| `--process` | string | none | Filter by process ID |

**Examples**

```bash
# Show all gaps
mda gaps

# Show only critical gaps
mda gaps --severity critical

# Filter by gap type
mda gaps --type missing-field

# Filter by process
mda gaps --process Process_LoanOrigination
```

**Example Output**

```
Gaps Report: Loan Origination
  Total gaps: 8

  CRITICAL (2):
    Task_VerifyIncome/intent.yaml
      - Missing required field: preconditions
    Gateway_CreditCheck/contract.yaml
      - Missing required field: error_handling

  HIGH (3):
    Task_VerifyIncome/contract.yaml
      - Missing SLA definition: response_time_ms
    Task_DocumentCollection/intent.yaml
      - Unresolved corpus reference: DOC-REF-042
    Task_AppraisalOrder/capsule.yaml
      - Missing domain_context annotations

  MEDIUM (3):
    ...
```

---

#### `mda graph`

Generate a process graph showing element relationships, sequence flows, and triple linkages.

```
mda graph [options]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--format` | choice | `yaml` | Output format: `yaml`, `mermaid`, or `dot` |
| `--output` | path | stdout | Output file path |

**Examples**

```bash
# Generate graph as YAML
mda graph

# Generate a Mermaid diagram
mda graph --format mermaid --output graph/process-flow.md

# Generate Graphviz DOT for visualization
mda graph --format dot --output graph/process-flow.dot
```

**Example Output (Mermaid)**

```
graph TD
  Start_LoanApp[Start: Loan Application Received]
  Task_VerifyIncome[Verify Applicant Income]
  Gateway_CreditCheck{Credit Score Decision}
  Task_Approve[Approve Loan]
  Task_Decline[Decline Loan]
  End_Complete[End: Process Complete]

  Start_LoanApp --> Task_VerifyIncome
  Task_VerifyIncome --> Gateway_CreditCheck
  Gateway_CreditCheck -->|Score >= 680| Task_Approve
  Gateway_CreditCheck -->|Score < 680| Task_Decline
  Task_Approve --> End_Complete
  Task_Decline --> End_Complete
```

**Notes**
- The `mermaid` format produces a diagram that renders natively in GitHub and MkDocs.
- The `dot` format can be rendered with Graphviz: `dot -Tpng process-flow.dot -o process-flow.png`.

---

### LLM-Powered

#### `mda enrich`

Enrich a parsed BPMN model with knowledge from the corpus. This is Stage 2 of the pipeline: the enriched model maps each process element to relevant policies, procedures, and rules.

```
mda enrich <model> [options]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `model` | path | *(required)* | Path to a parsed model YAML or JSON file (output of `mda parse`) |
| `--corpus-path` | path | config default | Path to the corpus directory |
| `--output` | path | stdout | Output file path for the enriched model |

**Examples**

```bash
# Enrich a parsed model
mda enrich models/loan-origination-parsed.yaml

# Enrich with a specific corpus and save output
mda enrich models/iv-parsed.yaml --corpus-path ./corpus --output models/iv-enriched.yaml

# Enrich in dry-run mode (shows corpus matches without writing)
mda enrich models/property-appraisal-parsed.yaml --dry-run
```

**Example Output**

```
Enriching model: models/loan-origination-parsed.yaml
  Corpus: corpus/ (14 documents)

  Task_VerifyIncome:
    Matched: corpus/procedure/income-verification-steps.md (0.92)
    Matched: corpus/policy/income-documentation-requirements.md (0.87)
  Gateway_CreditCheck:
    Matched: corpus/rule/credit-decision-matrix.md (0.95)
    Matched: corpus/policy/credit-score-thresholds.md (0.89)
  ...

Enriched model written to: models/loan-origination-enriched.yaml
  12 elements enriched, 23 corpus matches
```

**Notes**
- Requires an LLM API key unless the corpus matching uses a local embedding model.
- The match score (0.0-1.0) indicates relevance. Matches below 0.5 are excluded by default.

---

#### `mda generate`

Generate triple artifacts (capsule, intent, and/or contract YAML files) from an enriched model using the LLM.

```
mda generate <type> [options]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `type` | choice | *(required)* | Artifact type to generate: `capsule`, `intent`, `contract`, or `all` |
| `--enriched-model` | path | none | Path to the enriched model file |
| `--nodes` | string | all nodes | Comma-separated node IDs to generate for |
| `--force` | flag | `false` | Overwrite existing triple files |

**Examples**

```bash
# Generate all triple types for all elements
mda generate all --enriched-model models/loan-origination-enriched.yaml

# Generate only capsules
mda generate capsule --enriched-model models/iv-enriched.yaml

# Generate contracts for specific nodes
mda generate contract --enriched-model models/lo-enriched.yaml --nodes Task_VerifyIncome,Task_DocumentCollection

# Force overwrite existing files
mda generate all --enriched-model models/pa-enriched.yaml --force
```

**Example Output**

```
Generating triples from: models/loan-origination-enriched.yaml
  Type: all

  Task_VerifyIncome:
    capsule.yaml .... generated
    intent.yaml ..... generated
    contract.yaml ... generated
  Gateway_CreditCheck:
    capsule.yaml .... generated
    intent.yaml ..... generated
    contract.yaml ... generated
  ...

Generated: 36 files (12 capsules, 12 intents, 12 contracts)
Output directory: triples/
```

**Notes**
- Requires an LLM API key. Use `mda ingest --skip-llm` for offline stub generation.
- Use `--nodes` to regenerate triples for specific elements after targeted corpus updates.
- Existing files are skipped unless `--force` is provided.

---

#### `mda review`

Run an LLM-assisted quality review on a triple directory, checking for completeness, accuracy, and consistency.

```
mda review <triple_path> [options]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `triple_path` | path | *(required)* | Path to a triple directory (e.g. `triples/Task_VerifyIncome/`) |
| `--aspect` | choice | `all` | Review aspect: `completeness`, `accuracy`, `consistency`, or `all` |
| `--output` | path | stdout | Output file for the review findings |

**Examples**

```bash
# Full review of a triple
mda review triples/Task_VerifyIncome/

# Review only completeness
mda review triples/Gateway_CreditCheck/ --aspect completeness

# Save review to a file
mda review triples/Task_DocumentCollection/ --output reviews/doc-collection-review.yaml

# Review with JSON output
mda review triples/Task_AppraisalOrder/ --json
```

**Example Output**

```
Reviewing: triples/Task_VerifyIncome/
  Aspect: all

  Completeness: 8/10
    - Missing: capsule.business_rules[].exception_handling
    - Missing: contract.sla.response_time_ms

  Accuracy: 9/10
    - intent.preconditions references outdated policy (pre-2024 thresholds)

  Consistency: 10/10
    - All cross-references resolve correctly
    - Naming conventions followed

  Overall: 27/30 (90%)
  Recommendation: Address completeness gaps before binding
```

**Notes**
- Requires an LLM API key.
- Review findings are advisory. Use `mda validate` for schema-level enforcement.

---

### Documentation

#### `mda docs generate`

Generate MkDocs configuration and a documentation overlay from the current project state.

```
mda docs generate
```

**Examples**

```bash
# Generate docs config
mda docs generate

# Preview what would be generated
mda docs generate --dry-run
```

**Example Output**

```
Generating documentation...
  Created: mkdocs.yml
  Created: docs/index.md
  Created: docs/process-overview.md
  Created: docs/triples/
  Created: docs/graph/

Documentation ready. Run: mda docs build
```

---

#### `mda docs build`

Generate documentation and build a static site using MkDocs.

```
mda docs build
```

**Examples**

```bash
# Build the documentation site
mda docs build

# Build with verbose output
mda docs build -v
```

**Example Output**

```
Generating documentation...
Building static site...
  Output: site/

Site built successfully. Open site/index.html or run: mda docs serve
```

---

#### `mda docs serve`

Generate documentation and serve it locally with live reload.

```
mda docs serve [options]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--port` | int | `8000` | Port to serve the documentation site on |

**Examples**

```bash
# Serve on the default port
mda docs serve

# Serve on a custom port
mda docs serve --port 9090
```

**Example Output**

```
Generating documentation...
Serving at: http://localhost:8000
  Press Ctrl+C to stop
```

---

## Configuration

The `mda.config.yaml` file controls all pipeline behavior. It is auto-detected in the current directory or any parent directory, or specified explicitly with `--config`.

```yaml
# Process identity
process:
  id: "Process_LoanOrigination"
  name: "Loan Origination"
  version: "1.0"
  domain: "Mortgage Lending"
  owner_team: "Retail Lending"

# Source file locations
source:
  bpmn_file: "bpmn/loan-origination.bpmn"
  metadata_file: "bpmn/bpmn-metadata.yaml"

# Output directory paths
output:
  triples_dir: "triples"
  decisions_dir: "decisions"
  graph_dir: "graph"
  gaps_dir: "gaps"
  audit_dir: "audit"

# Pipeline settings
pipeline:
  version: "0.1.0-demo"
  mode: "demo"                # demo | full
  schema_validation: true
  schemas:
    capsule: "../../schemas/capsule.schema.json"
    intent: "../../schemas/intent.schema.json"
    contract: "../../schemas/contract.schema.json"
    triple_manifest: "../../schemas/triple-manifest.schema.json"
  element_mapping: "../../ontology/bpmn-element-mapping.yaml"

# Default values for generated artifacts
defaults:
  status: "draft"
  binding_status: "unbound"
  audit_retention_years: 7
  mda_layers:
    capsule: "CIM"
    intent: "PIM"
    contract: "PSM"

# Naming conventions
naming:
  id_prefix: "LO"
  capsule_pattern: "CAP-{prefix}-{code}-{seq}"
  intent_pattern: "INT-{prefix}-{code}-{seq}"
  contract_pattern: "ICT-{prefix}-{code}-{seq}"
```

### Configuration Sections

| Section | Description |
|---------|-------------|
| `process` | Process identity: id, name, version, domain, and owner team |
| `source` | Paths to the source BPMN file and optional metadata |
| `output` | Output directories for triples, decisions, graph, gaps, and audit logs |
| `pipeline` | Pipeline version, mode, schema validation toggle, schema paths, and ontology mapping |
| `defaults` | Default values applied to generated artifacts (status, binding, retention, MDA layers) |
| `naming` | ID prefix and naming patterns for capsule, intent, and contract artifacts |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `MDA_LLM_PROVIDER` | Override LLM provider (`anthropic`, `openai`, or `ollama`) |
| `MDA_LLM_MODEL` | Override LLM model (e.g. `claude-sonnet-4-20250514`, `gpt-4o`) |
| `ANTHROPIC_API_KEY` | API key for Anthropic Claude |
| `OPENAI_API_KEY` | API key for OpenAI models |
| `OLLAMA_BASE_URL` | Base URL for local Ollama instance (default: `http://localhost:11434`) |

Environment variables override values in `mda.config.yaml`. This is useful for CI/CD pipelines where secrets are injected at runtime.

```bash
# Example: run ingestion with Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
export MDA_LLM_PROVIDER="anthropic"
export MDA_LLM_MODEL="claude-sonnet-4-20250514"
mda ingest bpmn/loan-origination.bpmn

# Example: run with local Ollama
export MDA_LLM_PROVIDER="ollama"
export MDA_LLM_MODEL="llama3"
export OLLAMA_BASE_URL="http://localhost:11434"
mda ingest bpmn/income-verification.bpmn
```
