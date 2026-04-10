# MDA Intent Layer -- Skills Specification

*This document specifies all 18 Claude Code skills that wrap the MDA CLI commands. An agent receiving this spec can recreate all skill files.*

## 1. Overview

- 18 skills located in `.claude/skills/`
- Each skill wraps one MDA CLI command as a Claude Code slash command
- Invoked via `/mda-<command>` in Claude Code
- Skills provide: explanation of the command, dynamic context about current project state, CLI execution instructions, and output handling guidance

## 2. Skill File Format

- **Location**: `.claude/skills/<skill-name>/SKILL.md`
- **Format**: YAML frontmatter delimited by `---` lines, followed by a Markdown body
- **Dynamic context**: Uses `!`\``command`\` syntax for preprocessing -- Claude Code executes the backtick-wrapped shell commands before presenting the skill body, injecting live project state into the prompt

### Example structure

```
---
name: mda-example
description: One-line description of the skill
argument-hint: [arguments]
allowed-tools: Bash(python *)
---

# Title

Body content with dynamic context via !`shell commands`
```

## 3. Frontmatter Fields Used

| Field | Type | Used By | Purpose |
|-------|------|---------|---------|
| `name` | string | All 18 skills | Slash command name (invoked as `/name`) |
| `description` | string | All 18 skills | One-line description shown in command picker |
| `argument-hint` | string | 13 skills | Placeholder text showing expected arguments |
| `allowed-tools` | string | All 18 skills | Tools the skill is permitted to use |
| `disable-model-invocation` | boolean | 3 skills | Prevents Claude from making additional LLM API calls during execution |

### `allowed-tools` values used

| Value | Skills |
|-------|--------|
| `Bash(python *) Bash(mkdir *) Bash(ls *)` | mda-init |
| `Bash(python *) Read Edit` | mda-config |
| `Bash(python *) Edit` | mda-corpus-add |
| `Bash(python *)` | All other 15 skills |

### `disable-model-invocation` usage

| Value | Skills |
|-------|--------|
| `true` | mda-ingest, mda-reingest, mda-generate |
| (not set) | All other 15 skills |

## 4. Complete Skill Inventory

| # | Skill Name | Invocation | CLI Command | Arguments | disable-model-invocation | Description |
|---|-----------|------------|-------------|-----------|--------------------------|-------------|
| 1 | mda-init | `/mda-init` | `python cli/mda.py init` | `[process-name]` | -- | Scaffold a new MDA process repository |
| 2 | mda-config | `/mda-config` | `python cli/mda.py config` | (none) | -- | Show or edit the MDA process configuration |
| 3 | mda-parse | `/mda-parse` | `python cli/mda.py parse` | `[bpmn-file-path]` | -- | Parse a BPMN 2.0 XML file into a typed object model |
| 4 | mda-ingest | `/mda-ingest` | `python cli/mda.py ingest` | `[bpmn-file-path]` | `true` | Run the full BPMN-to-triples pipeline |
| 5 | mda-reingest | `/mda-reingest` | `python cli/mda.py reingest` | `[bpmn-file-path]` | `true` | Re-ingest an updated BPMN file with diff |
| 6 | mda-corpus-index | `/mda-corpus-index` | `python cli/mda.py corpus index` | (none) | -- | Regenerate the corpus index from .corpus.md files |
| 7 | mda-corpus-add | `/mda-corpus-add` | `python cli/mda.py corpus add` | `[type]` | -- | Create a new knowledge corpus document |
| 8 | mda-corpus-search | `/mda-corpus-search` | `python cli/mda.py corpus search` | `[search-query]` | -- | Search the knowledge corpus |
| 9 | mda-corpus-validate | `/mda-corpus-validate` | `python cli/mda.py corpus validate` | (none) | -- | Validate all corpus documents against schema |
| 10 | mda-validate | `/mda-validate` | `python cli/mda.py validate` | `[path]` | -- | Validate triples for schema compliance and integrity |
| 11 | mda-status | `/mda-status` | `python cli/mda.py status` | (none) | -- | Show status of all triples in the repository |
| 12 | mda-gaps | `/mda-gaps` | `python cli/mda.py gaps` | `[--severity level]` | -- | List all knowledge gaps in triples |
| 13 | mda-graph | `/mda-graph` | `python cli/mda.py graph` | `[--format fmt]` | -- | Generate a process flow graph |
| 14 | mda-test | `/mda-test` | `python cli/mda.py test` | `[--quick] [--bpmn] [--triples] [--corpus]` | -- | Run verification checks on the repository |
| 15 | mda-docs | `/mda-docs` | `python cli/mda.py docs` | `[generate\|build\|serve]` | -- | Generate and serve MkDocs documentation |
| 16 | mda-enrich | `/mda-enrich` | `python cli/mda.py enrich` | `[parsed-model-path]` | -- | Enrich parsed BPMN model with corpus matches |
| 17 | mda-generate | `/mda-generate` | `python cli/mda.py generate` | `[capsule\|intent\|contract\|all]` | `true` | Generate triple artifacts using LLM |
| 18 | mda-review | `/mda-review` | `python cli/mda.py review` | `[triple-path]` | -- | LLM-assisted quality review of a triple |

## 5. Skill Specifications

Each subsection below contains the complete, verbatim content of one SKILL.md file. To recreate a skill, create the directory `.claude/skills/<skill-name>/` and write the content below into `SKILL.md`.

---

### 5.1 mda-init

**Directory**: `.claude/skills/mda-init/SKILL.md`

```markdown
---
name: mda-init
description: Scaffold a new MDA process repository. Use when creating a new BPMN process project from scratch.
argument-hint: [process-name]
allowed-tools: Bash(python *) Bash(mkdir *) Bash(ls *)
---

# MDA Init -- Scaffold a New Process Repository

This command creates a new MDA process repository with the standard directory structure, default configuration, and template files needed to begin modeling a BPMN process.

## Context

Current working directory: !`pwd`
Existing MDA config: !`test -f mda.config.yaml && echo "mda.config.yaml found" || echo "No mda.config.yaml in current directory"`

## Steps

1. Run the scaffolding command for the process named `$ARGUMENTS`:

```
python cli/mda.py init $ARGUMENTS
```

2. If the command asks for additional information (domain prefix, namespace, etc.), prompt the user for those values before re-running.

3. After successful scaffolding, list the created directory structure to confirm everything was set up:

```
ls -R $ARGUMENTS/
```

4. Show the user:
   - The created directory tree
   - The generated `mda.config.yaml` contents
   - Suggested next steps (add BPMN file, add corpus documents, run ingest)
```

**Dynamic context commands**:
- `pwd` -- shows current working directory
- `test -f mda.config.yaml && echo "mda.config.yaml found" || echo "No mda.config.yaml in current directory"` -- checks if config already exists

**CLI command executed**: `python cli/mda.py init $ARGUMENTS`

---

### 5.2 mda-config

**Directory**: `.claude/skills/mda-config/SKILL.md`

```markdown
---
name: mda-config
description: Show or edit the MDA process configuration (mda.config.yaml). Use when checking or changing project settings.
allowed-tools: Bash(python *) Read Edit
---

# MDA Config -- View or Edit Process Configuration

This command displays or modifies the MDA process configuration stored in `mda.config.yaml`. Configuration controls process metadata, pipeline settings, LLM parameters, and output paths.

## Context

Current working directory: !`pwd`
Config file exists: !`test -f mda.config.yaml && echo "YES -- $(wc -l < mda.config.yaml) lines" || echo "NO -- not found"`

## Steps

### Viewing Configuration

1. Run:

```
python cli/mda.py config
```

2. Present the configuration values to the user in a readable format, highlighting any non-default settings.

### Editing Configuration

If the user wants to change a setting:

1. Use the CLI setter:

```
python cli/mda.py config --set KEY VALUE
```

2. After setting, re-read the config to confirm the change took effect.

3. If the user wants to edit the file directly, read `mda.config.yaml` and use the Edit tool to make precise changes.

### Common Configuration Keys

- `process.name` -- The process display name
- `process.domain` -- Domain prefix for triple IDs
- `pipeline.skip_llm` -- Whether to skip LLM calls during ingestion
- `pipeline.model` -- LLM model to use for generation
- `output.triples_dir` -- Output directory for generated triples
```

**Dynamic context commands**:
- `pwd` -- shows current working directory
- `test -f mda.config.yaml && echo "YES -- $(wc -l < mda.config.yaml) lines" || echo "NO -- not found"` -- checks config existence and size

**CLI command executed**: `python cli/mda.py config` (view) or `python cli/mda.py config --set KEY VALUE` (edit)

---

### 5.3 mda-parse

**Directory**: `.claude/skills/mda-parse/SKILL.md`

```markdown
---
name: mda-parse
description: Parse a BPMN 2.0 XML file into a typed object model. Use when ingesting or analyzing a BPMN file.
argument-hint: [bpmn-file-path]
allowed-tools: Bash(python *)
---

# MDA Parse -- Parse a BPMN 2.0 XML File

This command parses a BPMN 2.0 XML file into MDA's typed object model, extracting all process elements (tasks, gateways, events, sequence flows, lanes, pools) into a structured representation.

## Context

Current working directory: !`pwd`
BPMN files in project: !`find . -name "*.bpmn" -o -name "*.bpmn20.xml" 2>/dev/null | head -5 || echo "None found"`

## Steps

1. Parse the BPMN file at `$ARGUMENTS`:

```
python cli/mda.py parse $ARGUMENTS
```

2. Display a summary of the parsed model:
   - Total number of process elements (tasks, gateways, events)
   - Number of sequence flows (edges)
   - Lanes and pools found
   - Any warnings or unsupported elements

3. If the file path is not provided or invalid, check for `.bpmn` files in the current project and suggest one to the user.

4. If parsing produces warnings about unsupported BPMN constructs, explain what they mean and whether they will affect downstream processing.
```

**Dynamic context commands**:
- `pwd` -- shows current working directory
- `find . -name "*.bpmn" -o -name "*.bpmn20.xml" 2>/dev/null | head -5 || echo "None found"` -- lists available BPMN files

**CLI command executed**: `python cli/mda.py parse $ARGUMENTS`

---

### 5.4 mda-ingest

**Directory**: `.claude/skills/mda-ingest/SKILL.md`

```markdown
---
name: mda-ingest
description: Run the full BPMN-to-triples pipeline. Parses BPMN, enriches from corpus, generates capsules/intents/contracts. Use when converting a BPMN process into agent-executable triples.
argument-hint: [bpmn-file-path]
disable-model-invocation: true
allowed-tools: Bash(python *)
---

# MDA Ingest -- Full BPMN-to-Triples Pipeline

This command runs the complete ingestion pipeline: parse BPMN, enrich with corpus knowledge, and generate all triple artifacts (capsules, intents, contracts). This is the primary workflow for converting a business process into agent-executable form.

## Context

Current working directory: !`pwd`
Config exists: !`test -f mda.config.yaml && echo "YES" || echo "NO"`
Corpus index: !`test -f corpus/corpus.config.yaml && echo "YES -- corpus indexed" || echo "NO -- corpus not indexed, consider running corpus index first"`

## Steps

1. Ask the user whether they want to run in `--skip-llm` mode (uses heuristic generation instead of LLM calls -- faster, no API key needed, but lower quality output).

2. Run the full ingestion pipeline on `$ARGUMENTS`:

```
python cli/mda.py ingest $ARGUMENTS
```

Or with skip-llm:

```
python cli/mda.py ingest $ARGUMENTS --skip-llm
```

3. The pipeline will:
   - Parse the BPMN file
   - Match corpus documents to tasks via multi-factor scoring
   - Generate capsule, intent, and contract triples for each task
   - Write output to the configured triples directory

4. After completion, report:
   - Number of triples generated (capsules, intents, contracts)
   - Any gaps or warnings flagged during generation
   - Suggested next steps (validate, review, fill gaps)
```

**Dynamic context commands**:
- `pwd` -- shows current working directory
- `test -f mda.config.yaml && echo "YES" || echo "NO"` -- checks config existence
- `test -f corpus/corpus.config.yaml && echo "YES -- corpus indexed" || echo "NO -- corpus not indexed, consider running corpus index first"` -- checks corpus index state

**CLI command executed**: `python cli/mda.py ingest $ARGUMENTS` or `python cli/mda.py ingest $ARGUMENTS --skip-llm`

---

### 5.5 mda-reingest

**Directory**: `.claude/skills/mda-reingest/SKILL.md`

```markdown
---
name: mda-reingest
description: Re-ingest an updated BPMN file, diff against existing triples, and propose changes. Use when the upstream BPMN has been modified.
argument-hint: [bpmn-file-path]
disable-model-invocation: true
allowed-tools: Bash(python *)
---

# MDA Reingest -- Re-ingest Updated BPMN with Diff

This command re-ingests a BPMN file that has been modified since the last ingestion. It diffs the new parse against existing triples and proposes additions, deletions, and modifications rather than regenerating everything from scratch.

## Context

Current working directory: !`pwd`
Existing triples: !`find . -path "*/triples/*" -name "*.yaml" 2>/dev/null | wc -l || echo "0"` files found

## Steps

1. Always start with a dry run to preview changes:

```
python cli/mda.py reingest $ARGUMENTS --dry-run
```

2. Present the diff summary to the user:
   - New tasks added in BPMN (will generate new triples)
   - Tasks removed from BPMN (triples to be archived)
   - Tasks modified (triples to be updated)
   - Unchanged tasks (no action needed)

3. Ask the user if they want to proceed with the actual re-ingestion.

4. If confirmed, run without dry-run:

```
python cli/mda.py reingest $ARGUMENTS
```

5. Report what changed and suggest reviewing the modified triples.
```

**Dynamic context commands**:
- `pwd` -- shows current working directory
- `find . -path "*/triples/*" -name "*.yaml" 2>/dev/null | wc -l || echo "0"` -- counts existing triple files

**CLI command executed**: `python cli/mda.py reingest $ARGUMENTS --dry-run` then `python cli/mda.py reingest $ARGUMENTS`

---

### 5.6 mda-corpus-index

**Directory**: `.claude/skills/mda-corpus-index/SKILL.md`

```markdown
---
name: mda-corpus-index
description: Regenerate the corpus index (corpus.config.yaml) from all .corpus.md files. Use after adding or modifying corpus documents.
allowed-tools: Bash(python *)
---

# MDA Corpus Index -- Rebuild the Corpus Index

This command scans all `.corpus.md` files in the corpus directory and regenerates `corpus.config.yaml`, which serves as the searchable index for the enrichment pipeline.

## Context

Current working directory: !`pwd`
Corpus documents: !`find . -name "*.corpus.md" 2>/dev/null | wc -l || echo "0"` files found
Current index: !`test -f corpus/corpus.config.yaml && echo "EXISTS -- last modified $(stat -c %y corpus/corpus.config.yaml 2>/dev/null || stat -f %Sm corpus/corpus.config.yaml 2>/dev/null)" || echo "NOT FOUND"`

## Steps

1. Run the corpus indexing command:

```
python cli/mda.py corpus index
```

2. Report:
   - Number of corpus documents indexed
   - Types of documents found (procedures, policies, regulations, etc.)
   - Any documents that failed validation during indexing
   - Any orphaned entries in the old index that no longer have matching files

3. If no corpus documents are found, suggest creating some with `/mda-corpus-add`.
```

**Dynamic context commands**:
- `pwd` -- shows current working directory
- `find . -name "*.corpus.md" 2>/dev/null | wc -l || echo "0"` -- counts corpus documents
- `test -f corpus/corpus.config.yaml && echo "EXISTS -- last modified $(stat -c %y corpus/corpus.config.yaml 2>/dev/null || stat -f %Sm corpus/corpus.config.yaml 2>/dev/null)" || echo "NOT FOUND"` -- checks index existence and last modified time

**CLI command executed**: `python cli/mda.py corpus index`

---

### 5.7 mda-corpus-add

**Directory**: `.claude/skills/mda-corpus-add/SKILL.md`

```markdown
---
name: mda-corpus-add
description: Create a new knowledge corpus document. Use when adding procedures, policies, regulations, rules, data dictionaries, system docs, training, or glossary entries.
argument-hint: [type] (procedure|policy|regulation|rule|data-dictionary|system|training|glossary)
allowed-tools: Bash(python *) Edit
---

# MDA Corpus Add -- Create a New Corpus Document

This command creates a new knowledge corpus document of a specific type. Corpus documents feed the enrichment pipeline, providing the domain knowledge that gets bound to BPMN tasks.

## Context

Current working directory: !`pwd`
Existing corpus types: !`find . -name "*.corpus.md" 2>/dev/null | sed 's/.*\///' | sed 's/\.corpus\.md//' | sort -u | head -10 || echo "None found"`

## Steps

1. The document type is `$0`. Valid types: procedure, policy, regulation, rule, data-dictionary, system, training, glossary.

2. If domain or title are not provided, ask the user for:
   - **Domain**: The business domain this document belongs to (e.g., "lending", "compliance", "onboarding")
   - **Title**: A descriptive title for the document

3. Create the corpus document:

```
python cli/mda.py corpus add $0 --domain "$1" --title "$2"
```

4. After creation, open the generated file for editing so the user can fill in the actual content. The template will have the required frontmatter and section structure.

5. Remind the user to run `/mda-corpus-index` after finishing edits to update the search index.
```

**Dynamic context commands**:
- `pwd` -- shows current working directory
- `find . -name "*.corpus.md" 2>/dev/null | sed 's/.*\///' | sed 's/\.corpus\.md//' | sort -u | head -10 || echo "None found"` -- lists existing corpus document types

**CLI command executed**: `python cli/mda.py corpus add $0 --domain "$1" --title "$2"`

---

### 5.8 mda-corpus-search

**Directory**: `.claude/skills/mda-corpus-search/SKILL.md`

```markdown
---
name: mda-corpus-search
description: Search the knowledge corpus by keyword, type, or domain. Use when looking for existing procedures, policies, or regulations.
argument-hint: [search-query]
allowed-tools: Bash(python *)
---

# MDA Corpus Search -- Search the Knowledge Corpus

This command searches the indexed corpus documents by keyword, type, or domain. Useful for finding existing knowledge before adding new documents or understanding what corpus coverage exists for a given topic.

## Context

Current working directory: !`pwd`
Corpus indexed: !`test -f corpus/corpus.config.yaml && echo "YES" || echo "NO -- run /mda-corpus-index first"`

## Steps

1. Search the corpus for `$ARGUMENTS`:

```
python cli/mda.py corpus search "$ARGUMENTS"
```

2. Present results showing:
   - Document title and type
   - Domain
   - Relevance score or match context
   - File path for each match

3. If no results found, suggest:
   - Trying broader search terms
   - Checking if the corpus index is up to date (`/mda-corpus-index`)
   - Adding new corpus documents (`/mda-corpus-add`)
```

**Dynamic context commands**:
- `pwd` -- shows current working directory
- `test -f corpus/corpus.config.yaml && echo "YES" || echo "NO -- run /mda-corpus-index first"` -- checks if corpus is indexed

**CLI command executed**: `python cli/mda.py corpus search "$ARGUMENTS"`

---

### 5.9 mda-corpus-validate

**Directory**: `.claude/skills/mda-corpus-validate/SKILL.md`

```markdown
---
name: mda-corpus-validate
description: Validate all corpus documents against the JSON schema. Use to check corpus document quality.
allowed-tools: Bash(python *)
---

# MDA Corpus Validate -- Validate Corpus Documents

This command validates all corpus documents (`.corpus.md` files) against the expected JSON schema, checking frontmatter completeness, required sections, and structural correctness.

## Context

Current working directory: !`pwd`
Corpus documents: !`find . -name "*.corpus.md" 2>/dev/null | wc -l || echo "0"` files found

## Steps

1. Run corpus validation:

```
python cli/mda.py corpus validate
```

2. Report results:
   - Number of documents validated
   - Number passing / failing
   - For each failure: file path, specific validation errors (missing fields, invalid types, structural issues)

3. If there are failures, suggest fixes for each. Common issues include:
   - Missing required frontmatter fields
   - Invalid document type values
   - Missing required content sections
   - Malformed YAML in frontmatter
```

**Dynamic context commands**:
- `pwd` -- shows current working directory
- `find . -name "*.corpus.md" 2>/dev/null | wc -l || echo "0"` -- counts corpus documents

**CLI command executed**: `python cli/mda.py corpus validate`

---

### 5.10 mda-validate

**Directory**: `.claude/skills/mda-validate/SKILL.md`

```markdown
---
name: mda-validate
description: Validate triples for schema compliance, cross-reference integrity, and consistency. Use to check triple quality before review.
argument-hint: [path]
allowed-tools: Bash(python *)
---

# MDA Validate -- Validate Triple Artifacts

This command validates generated triples (capsules, intents, contracts) for schema compliance, cross-reference integrity between related triples, and internal consistency.

## Context

Current working directory: !`pwd`
Triple files: !`find . -path "*/triples/*" -name "*.yaml" 2>/dev/null | wc -l || echo "0"` files found
Config exists: !`test -f mda.config.yaml && echo "YES" || echo "NO"`

## Steps

1. Run validation on the specified path (or all triples if no path given):

```
python cli/mda.py validate $ARGUMENTS
```

2. Report results organized by severity:
   - **Errors**: Schema violations, broken cross-references, missing required fields
   - **Warnings**: Incomplete sections, weak descriptions, missing optional enrichments
   - **Info**: Suggestions for improvement

3. For each issue found, include the file path and specific field so the user can locate and fix it.

4. If all triples pass validation, confirm they are ready for review (`/mda-review`).
```

**Dynamic context commands**:
- `pwd` -- shows current working directory
- `find . -path "*/triples/*" -name "*.yaml" 2>/dev/null | wc -l || echo "0"` -- counts triple files
- `test -f mda.config.yaml && echo "YES" || echo "NO"` -- checks config existence

**CLI command executed**: `python cli/mda.py validate $ARGUMENTS`

---

### 5.11 mda-status

**Directory**: `.claude/skills/mda-status/SKILL.md`

```markdown
---
name: mda-status
description: Show the status of all triples in the current process repository. Use to see draft/review/approved/current counts and binding status.
allowed-tools: Bash(python *)
---

# MDA Status -- Process Repository Status

This command shows a summary of all triples in the current process repository, including their lifecycle status (draft, review, approved, current) and corpus binding coverage.

## Context

Current working directory: !`pwd`
Config exists: !`test -f mda.config.yaml && echo "YES" || echo "NO"`
Triple files: !`find . -path "*/triples/*" -name "*.yaml" 2>/dev/null | wc -l || echo "0"` files

## Steps

1. Run the status command:

```
python cli/mda.py status
```

2. Present a clear summary showing:
   - Total triple count by type (capsules, intents, contracts)
   - Breakdown by lifecycle status (draft / in-review / approved / current)
   - Corpus binding coverage (how many capsules have bound corpus documents)
   - Any triples with gaps or missing dependencies

3. If the repository looks incomplete, suggest next actions:
   - Ungenerated triples: run `/mda-ingest`
   - Draft triples: run `/mda-review`
   - Gaps found: run `/mda-gaps`
```

**Dynamic context commands**:
- `pwd` -- shows current working directory
- `test -f mda.config.yaml && echo "YES" || echo "NO"` -- checks config existence
- `find . -path "*/triples/*" -name "*.yaml" 2>/dev/null | wc -l || echo "0"` -- counts triple files

**CLI command executed**: `python cli/mda.py status`

---

### 5.12 mda-gaps

**Directory**: `.claude/skills/mda-gaps/SKILL.md`

```markdown
---
name: mda-gaps
description: List all gaps across triples, filterable by severity and type. Use to see what knowledge is missing from capsules.
argument-hint: [--severity critical|high|medium|low]
allowed-tools: Bash(python *)
---

# MDA Gaps -- List Knowledge Gaps in Triples

This command identifies gaps in the generated triples -- missing corpus bindings, incomplete procedure steps, unresolved references, and other areas where human knowledge input is needed.

## Context

Current working directory: !`pwd`
Triple files: !`find . -path "*/triples/*" -name "*.yaml" 2>/dev/null | wc -l || echo "0"` files

## Steps

1. List all gaps, optionally filtered by severity:

```
python cli/mda.py gaps $ARGUMENTS
```

2. Present gaps organized by:
   - **Severity**: Critical, High, Medium, Low
   - **Type**: Missing corpus binding, incomplete steps, ambiguous gateway logic, missing error handling, etc.
   - **Location**: Which triple and field the gap appears in

3. For each gap, provide a brief summary of what knowledge is needed to fill it.

4. Suggest actions:
   - Add corpus documents to fill knowledge gaps (`/mda-corpus-add`)
   - Search existing corpus for relevant documents (`/mda-corpus-search`)
   - Manually edit triples to fill small gaps
```

**Dynamic context commands**:
- `pwd` -- shows current working directory
- `find . -path "*/triples/*" -name "*.yaml" 2>/dev/null | wc -l || echo "0"` -- counts triple files

**CLI command executed**: `python cli/mda.py gaps $ARGUMENTS`

---

### 5.13 mda-graph

**Directory**: `.claude/skills/mda-graph/SKILL.md`

```markdown
---
name: mda-graph
description: Generate a process flow graph from capsule predecessor/successor relationships. Use to visualize the process flow.
argument-hint: [--format yaml|mermaid|dot]
allowed-tools: Bash(python *)
---

# MDA Graph -- Generate Process Flow Graph

This command generates a visual process flow graph from the capsule predecessor/successor relationships, showing how tasks connect through the modeled process.

## Context

Current working directory: !`pwd`
Triple files: !`find . -path "*/triples/*" -name "*.yaml" 2>/dev/null | wc -l || echo "0"` files

## Steps

1. Generate the graph in the requested format (default: mermaid):

```
python cli/mda.py graph --format mermaid
```

If the user specified a different format via `$ARGUMENTS`, use that instead:

```
python cli/mda.py graph $ARGUMENTS
```

2. Supported formats:
   - **mermaid**: Mermaid.js flowchart syntax (can be rendered in Markdown)
   - **yaml**: Structured YAML adjacency list
   - **dot**: Graphviz DOT format

3. If the output is Mermaid format, present it in a fenced code block so it renders visually in supported viewers.

4. Highlight any disconnected nodes or unreachable paths in the graph.
```

**Dynamic context commands**:
- `pwd` -- shows current working directory
- `find . -path "*/triples/*" -name "*.yaml" 2>/dev/null | wc -l || echo "0"` -- counts triple files

**CLI command executed**: `python cli/mda.py graph --format mermaid` or `python cli/mda.py graph $ARGUMENTS`

---

### 5.14 mda-test

**Directory**: `.claude/skills/mda-test/SKILL.md`

```markdown
---
name: mda-test
description: Run verification checks on the current process repository. Checks BPMN parsing, triple integrity, corpus consistency. Use to validate your work before committing.
argument-hint: [--quick] [--bpmn] [--triples] [--corpus]
allowed-tools: Bash(python *)
---

# MDA Test -- Run Verification Checks

This command runs a suite of verification checks against the current process repository, covering BPMN parsing, triple schema integrity, corpus consistency, and cross-reference validation.

## Context

Current working directory: !`pwd`
Config exists: !`test -f mda.config.yaml && echo "YES" || echo "NO"`
BPMN files: !`find . -name "*.bpmn" -o -name "*.bpmn20.xml" 2>/dev/null | wc -l || echo "0"` found
Triple files: !`find . -path "*/triples/*" -name "*.yaml" 2>/dev/null | wc -l || echo "0"` found
Corpus files: !`find . -name "*.corpus.md" 2>/dev/null | wc -l || echo "0"` found

## Steps

1. Run the test suite. If no specific flags are given via `$ARGUMENTS`, run all checks:

```
python cli/mda.py test $ARGUMENTS
```

2. Available flags:
   - `--quick` -- Fast subset of checks, skips expensive validations
   - `--bpmn` -- Only check BPMN parsing
   - `--triples` -- Only check triple integrity
   - `--corpus` -- Only check corpus consistency

3. Report results:
   - Total checks run, passed, failed
   - Details for each failure with file path and description
   - Overall pass/fail status

4. If failures are found, suggest targeted fixes. If all pass, confirm the repository is ready for commit.
```

**Dynamic context commands**:
- `pwd` -- shows current working directory
- `test -f mda.config.yaml && echo "YES" || echo "NO"` -- checks config existence
- `find . -name "*.bpmn" -o -name "*.bpmn20.xml" 2>/dev/null | wc -l || echo "0"` -- counts BPMN files
- `find . -path "*/triples/*" -name "*.yaml" 2>/dev/null | wc -l || echo "0"` -- counts triple files
- `find . -name "*.corpus.md" 2>/dev/null | wc -l || echo "0"` -- counts corpus files

**CLI command executed**: `python cli/mda.py test $ARGUMENTS`

---

### 5.15 mda-docs

**Directory**: `.claude/skills/mda-docs/SKILL.md`

```markdown
---
name: mda-docs
description: Generate and serve the MkDocs documentation site for the current process. Use to browse triples, corpus, and process flow visually.
argument-hint: [generate|build|serve]
allowed-tools: Bash(python *)
---

# MDA Docs -- Generate and Serve Documentation

This command generates and optionally serves an MkDocs documentation site for the current process repository, providing a browsable view of triples, corpus documents, and process flow diagrams.

## Context

Current working directory: !`pwd`
Config exists: !`test -f mda.config.yaml && echo "YES" || echo "NO"`
Docs directory: !`test -d docs && echo "EXISTS" || echo "NOT FOUND"`

## Steps

1. Run the docs command. Default to `serve` if no subcommand is specified via `$ARGUMENTS`:

```
python cli/mda.py docs $ARGUMENTS
```

2. Available subcommands:
   - `generate` -- Generate Markdown documentation files from triples and corpus
   - `build` -- Build the static MkDocs site
   - `serve` -- Start the MkDocs dev server for local browsing

3. If serving, report the local URL (typically `http://localhost:8000`) so the user can open the docs in a browser.

4. If generating, report how many documentation pages were created and for which triples/corpus documents.
```

**Dynamic context commands**:
- `pwd` -- shows current working directory
- `test -f mda.config.yaml && echo "YES" || echo "NO"` -- checks config existence
- `test -d docs && echo "EXISTS" || echo "NOT FOUND"` -- checks if docs directory exists

**CLI command executed**: `python cli/mda.py docs $ARGUMENTS`

---

### 5.16 mda-enrich

**Directory**: `.claude/skills/mda-enrich/SKILL.md`

```markdown
---
name: mda-enrich
description: Enrich a parsed BPMN model with corpus matches. Runs the multi-factor scoring algorithm to find relevant knowledge documents for each task.
argument-hint: [parsed-model-path]
allowed-tools: Bash(python *)
---

# MDA Enrich -- Enrich Parsed Model with Corpus Knowledge

This command runs the multi-factor scoring algorithm to match corpus documents to parsed BPMN tasks. It produces enrichment scores showing which knowledge documents are most relevant to each task, forming the basis for triple generation.

## Context

Current working directory: !`pwd`
Corpus indexed: !`test -f corpus/corpus.config.yaml && echo "YES" || echo "NO -- run /mda-corpus-index first"`
Corpus documents: !`find . -name "*.corpus.md" 2>/dev/null | wc -l || echo "0"` files

## Steps

1. Run enrichment on the parsed model at `$ARGUMENTS`:

```
python cli/mda.py enrich $ARGUMENTS
```

2. Report enrichment results:
   - For each BPMN task, show the top-matched corpus documents and their scores
   - Highlight tasks with no corpus matches (these will produce gaps in generation)
   - Show the scoring factors used (keyword overlap, domain match, type relevance)

3. If tasks have low or no matches, suggest:
   - Adding more corpus documents (`/mda-corpus-add`)
   - Checking corpus index is current (`/mda-corpus-index`)
   - Reviewing task naming for better keyword alignment
```

**Dynamic context commands**:
- `pwd` -- shows current working directory
- `test -f corpus/corpus.config.yaml && echo "YES" || echo "NO -- run /mda-corpus-index first"` -- checks corpus index
- `find . -name "*.corpus.md" 2>/dev/null | wc -l || echo "0"` -- counts corpus documents

**CLI command executed**: `python cli/mda.py enrich $ARGUMENTS`

---

### 5.17 mda-generate

**Directory**: `.claude/skills/mda-generate/SKILL.md`

```markdown
---
name: mda-generate
description: Generate triple artifacts (capsule, intent, contract) using LLM. Use after enrichment to produce draft triples from corpus knowledge.
argument-hint: [capsule|intent|contract|all]
disable-model-invocation: true
allowed-tools: Bash(python *)
---

# MDA Generate -- Generate Triple Artifacts

This command generates triple artifacts (capsules, intents, contracts) using LLM-based generation from enriched corpus knowledge. Run this after enrichment to produce draft triples.

## Context

Current working directory: !`pwd`
Config exists: !`test -f mda.config.yaml && echo "YES" || echo "NO"`
Enrichment data: !`find . -path "*enrichment*" -name "*.yaml" -o -path "*enrichment*" -name "*.json" 2>/dev/null | wc -l || echo "0"` files

## Steps

1. If no artifact type is specified via `$ARGUMENTS`, ask the user which type to generate:
   - `capsule` -- Task capsules (what the agent does, step-by-step procedures)
   - `intent` -- Intent declarations (what triggers the task, input/output schemas)
   - `contract` -- Contracts (pre/post conditions, SLAs, error handling)
   - `all` -- Generate all three types

2. Run the generation command:

```
python cli/mda.py generate $ARGUMENTS
```

3. Report:
   - Number of artifacts generated by type
   - Any generation failures or skipped tasks
   - Quality warnings (low corpus coverage, ambiguous procedures)

4. Suggest running `/mda-validate` to check the generated triples, then `/mda-review` for quality review.
```

**Dynamic context commands**:
- `pwd` -- shows current working directory
- `test -f mda.config.yaml && echo "YES" || echo "NO"` -- checks config existence
- `find . -path "*enrichment*" -name "*.yaml" -o -path "*enrichment*" -name "*.json" 2>/dev/null | wc -l || echo "0"` -- counts enrichment data files

**CLI command executed**: `python cli/mda.py generate $ARGUMENTS`

---

### 5.18 mda-review

**Directory**: `.claude/skills/mda-review/SKILL.md`

```markdown
---
name: mda-review
description: LLM-assisted quality review of a triple. Checks completeness, accuracy, consistency, and anti-UI compliance. Use before approving a triple.
argument-hint: [triple-path]
allowed-tools: Bash(python *)
---

# MDA Review -- LLM-Assisted Triple Quality Review

This command performs an LLM-assisted quality review of a triple artifact, checking completeness, accuracy, internal consistency, and anti-UI compliance (ensuring the triple describes agent behavior, not UI interactions).

## Context

Current working directory: !`pwd`
Triple files: !`find . -path "*/triples/*" -name "*.yaml" 2>/dev/null | head -10 || echo "None found"`

## Steps

1. Run the review on the specified triple at `$ARGUMENTS`:

```
python cli/mda.py review $ARGUMENTS
```

2. Present the review results organized by dimension:
   - **Completeness**: Are all required fields populated? Are procedures fully specified?
   - **Accuracy**: Do the steps match the bound corpus knowledge?
   - **Consistency**: Are cross-references valid? Do input/output schemas align?
   - **Anti-UI Compliance**: Does the triple describe agent actions, not user interface interactions?

3. For each finding, show severity (critical/high/medium/low) and a specific recommendation.

4. If the triple passes review, suggest approving it. If not, suggest specific edits to address each finding.
```

**Dynamic context commands**:
- `pwd` -- shows current working directory
- `find . -path "*/triples/*" -name "*.yaml" 2>/dev/null | head -10 || echo "None found"` -- lists existing triple files

**CLI command executed**: `python cli/mda.py review $ARGUMENTS`

---

## 6. Design Decisions

### Why `disable-model-invocation: true` on ingest, reingest, and generate

These three skills trigger external LLM API calls through the Python CLI (`python cli/mda.py ingest/reingest/generate`). The `disable-model-invocation: true` flag prevents Claude Code from making *additional* LLM calls on top of the ones the CLI already makes. Without this flag, Claude Code might attempt to further process or regenerate the output, doubling API costs and potentially conflicting with the CLI's own generation logic. These are the only skills with side effects that involve external LLM invocations.

### Why `allowed-tools: Bash(python *)` on all skills

Every skill needs to execute `python cli/mda.py <command>`, so `Bash(python *)` is the universal baseline. The glob pattern `python *` permits any Python command invocation while blocking arbitrary shell commands. This provides a security boundary -- skills cannot run arbitrary bash commands, only Python-based CLI invocations.

### Why `Edit` is added to corpus-add and config

- **mda-corpus-add**: After creating a corpus document from a template, the user needs to fill in the actual content. The `Edit` tool allows Claude to open and modify the generated `.corpus.md` file inline without leaving the skill flow.
- **mda-config**: The `Edit` tool allows direct editing of `mda.config.yaml` when the CLI `--set` interface is insufficient for complex changes (e.g., editing nested YAML structures, adding new sections).

### Why `Read` is added to config

The **mda-config** skill includes `Read` so Claude can read `mda.config.yaml` directly to show its contents to the user, independent of the CLI `config` command output format.

### Why `Bash(mkdir *) Bash(ls *)` is added to init

The **mda-init** skill needs `mkdir` to create directory structures if the CLI scaffolding requires it, and `ls` to display the created directory tree to the user after scaffolding completes.

### Why dynamic context via `!`\``backtick`\` syntax

Dynamic context commands run *before* Claude sees the skill body. This means Claude always knows the current project state (which files exist, whether config is present, how many triples/corpus docs exist) before deciding what to do. This eliminates a round trip -- without dynamic context, Claude would need to first run diagnostic commands, then decide on the action. With dynamic context, the skill body already contains current state information, allowing Claude to give relevant guidance immediately.

## 7. Verification

To verify that all 18 skills have been correctly recreated:

### Structural checks

1. Confirm 18 directories exist under `.claude/skills/`:
   ```
   ls -d .claude/skills/mda-*/  | wc -l
   # Expected: 18
   ```

2. Confirm each directory contains a `SKILL.md` file:
   ```
   ls .claude/skills/mda-*/SKILL.md | wc -l
   # Expected: 18
   ```

3. Confirm each `SKILL.md` has valid YAML frontmatter (starts with `---`, has a closing `---`):
   ```
   for f in .claude/skills/mda-*/SKILL.md; do
     head -1 "$f" | grep -q "^---$" && echo "OK: $f" || echo "FAIL: $f"
   done
   ```

### Content checks

4. Verify all 18 skill names are present:
   ```
   grep -h "^name:" .claude/skills/mda-*/SKILL.md | sort
   ```
   Expected output (one per line): mda-config, mda-corpus-add, mda-corpus-index, mda-corpus-search, mda-corpus-validate, mda-docs, mda-enrich, mda-gaps, mda-generate, mda-graph, mda-ingest, mda-init, mda-parse, mda-reingest, mda-review, mda-status, mda-test, mda-validate

5. Verify `disable-model-invocation: true` appears in exactly 3 skills:
   ```
   grep -l "disable-model-invocation: true" .claude/skills/mda-*/SKILL.md
   # Expected: mda-ingest, mda-reingest, mda-generate
   ```

6. Verify all skills have `allowed-tools` containing `Bash(python *)`:
   ```
   grep -L "Bash(python \*)" .claude/skills/mda-*/SKILL.md
   # Expected: no output (all files contain it)
   ```

### Functional checks

7. Each skill can be invoked via `/mda-<name>` in Claude Code. Test by typing `/mda-status` in a Claude Code session and confirming the skill activates.

8. Dynamic context commands should resolve -- when a skill is invoked, the `!`\``command`\` blocks should be replaced with actual shell output showing current project state.

### Complete directory listing

```
.claude/skills/
  mda-init/SKILL.md
  mda-config/SKILL.md
  mda-parse/SKILL.md
  mda-ingest/SKILL.md
  mda-reingest/SKILL.md
  mda-corpus-index/SKILL.md
  mda-corpus-add/SKILL.md
  mda-corpus-search/SKILL.md
  mda-corpus-validate/SKILL.md
  mda-validate/SKILL.md
  mda-status/SKILL.md
  mda-gaps/SKILL.md
  mda-graph/SKILL.md
  mda-test/SKILL.md
  mda-docs/SKILL.md
  mda-enrich/SKILL.md
  mda-generate/SKILL.md
  mda-review/SKILL.md
```
