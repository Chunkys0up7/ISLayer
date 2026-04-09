# MDA Intent Layer -- Complete Execution Specification

*This document specifies every artifact, schema, convention, and behavior needed to build the MDA Intent Layer from scratch. An agent receiving this spec should produce a functionally identical system.*

---

## 1. System Overview

### 1.1 Purpose

The MDA Intent Layer is a BPMN-to-Intent-Spec transformation pipeline. It ingests BPMN 2.0 process models and produces structured artifacts (called "triples") that AI agents consume to execute business tasks without UI interaction.

The system is MDA-aligned:

- **CIM (Computation Independent Model):** BPMN XML process definitions -- the business view
- **PIM (Platform Independent Model):** Intent Specifications -- what an agent must achieve, without prescribing how
- **PSM (Platform Specific Model):** Integration Contracts -- concrete system bindings (APIs, protocols, endpoints)

A **Knowledge Capsule** extends the MDA stack as a human+agent readable container of domain knowledge extracted from a curated corpus of procedures, policies, regulations, rules, data dictionaries, system guides, training materials, and glossaries.

### 1.2 Core Principles

1. **One BPMN Task = One Triple (strict 1:1).** Every BPMN task element that is capsule-eligible produces exactly one triple. A triple consists of a Knowledge Capsule (.cap.md), an Intent Specification (.intent.md), and an Integration Contract (.contract.md). No task produces zero triples; no task produces more than one.

2. **Anti-UI Principle.** Triples never describe browser automation, screen scraping, UI clicks, or RPA-style macros. If the only way to achieve an outcome is through a UI, the intent spec records a gap and stays in draft. All outcomes must be achievable through APIs, data operations, and system integrations.

3. **Conservative Enrichment.** The pipeline flags gaps rather than hallucinating data. If a procedure, owner, decision rule, data schema, regulatory context, or integration binding cannot be found, the system records a structured gap entry with severity and suggested resolution. It never fabricates information.

4. **Separation of Change Rates.** BPMN process models change annually. Knowledge capsules (corpus documents) change quarterly. Integration contracts change monthly. The architecture isolates these change rates so that updating an API endpoint does not require re-reviewing the entire process model.

5. **Artifacts for Agents.** Triples are consumed by AI agents at runtime, not just as documentation. The intent spec's goal, inputs, outputs, invariants, failure modes, and forbidden actions form an executable contract that an agent can interpret and fulfill.

6. **Governed Lifecycle.** Every artifact progresses through: draft -> review -> approved -> current -> deprecated -> archived. Status transitions are gated by validation checks, human review, and compliance requirements.

### 1.3 Architecture Layers

```
BPMN XML (CIM) --> Knowledge Corpus --> Pipeline --> Triples (PIM+PSM) --> Agent Runtime
```

Detailed data flow:

```
                    +------------------+
                    | BPMN 2.0 XML     |  (CIM)
                    +--------+---------+
                             |
                    Stage 1: BPMN Parser
                             |
                    +--------v---------+
                    | ParsedModel      |
                    +--------+---------+
                             |
              +--------------+----------+
              |                         |
     corpus/corpus.config.yaml    ontology/*.yaml
              |                         |
              +------+------------------+
                     |
            Stage 2: Corpus Enricher
                     |
              +------v---------+
              | EnrichedModel  |  (with per-node enrichments + gap list)
              +------+---------+
                     |
         +-----------+-----------+-----------+
         |                       |           |
   Stage 3: Capsule Gen   Stage 4: Intent Gen   Stage 5: Contract Gen
         |                       |           |
    .cap.md files          .intent.md    .contract.md
         |                       |           |
         +-----------+-----------+-----------+
                     |
            Stage 6: Triple Validator
                     |
              +------v---------+
              | ValidationReport |
              +----------------+
```

---

## 2. Project Structure

### 2.1 Complete Directory Layout

```
ISLayer/
+-- README.md
+-- METHODOLOGY.md
+-- CHANGELOG.md
+-- requirements.txt
+-- .gitignore
|
+-- cli/                                    # Python CLI (~35 .py files, ~7300 lines)
|   +-- mda.py                             # Entry point (Click CLI)
|   +-- requirements.txt                   # Same deps as root
|   +-- __init__.py
|   +-- config/
|   |   +-- __init__.py
|   |   +-- loader.py                      # Config discovery + loading (mda.config.yaml)
|   |   +-- defaults.py                    # Default configuration values
|   +-- llm/
|   |   +-- __init__.py
|   |   +-- provider.py                    # Abstract LLMProvider base class + factory
|   |   +-- anthropic_provider.py          # Claude API integration
|   |   +-- openai_provider.py             # OpenAI API integration
|   |   +-- ollama_provider.py             # Local Ollama integration
|   |   +-- prompts/
|   |       +-- __init__.py
|   |       +-- enrich.py                  # Enrichment prompts
|   |       +-- capsule.py                 # Capsule generation prompts
|   |       +-- intent.py                  # Intent generation prompts
|   |       +-- contract.py                # Contract generation prompts
|   |       +-- review.py                  # Review/validation prompts
|   +-- commands/
|   |   +-- __init__.py
|   |   +-- init_cmd.py                    # `mda init` -- scaffold new process repo
|   |   +-- config_cmd.py                  # `mda config` -- view/set configuration
|   |   +-- parse_cmd.py                   # `mda parse` -- Stage 1 BPMN parsing
|   |   +-- ingest_cmd.py                  # `mda ingest` -- full pipeline run
|   |   +-- corpus_cmd.py                  # `mda corpus` -- corpus management
|   |   +-- validate_cmd.py               # `mda validate` -- Stage 6 validation
|   |   +-- status_cmd.py                 # `mda status` -- show triple statuses
|   |   +-- gaps_cmd.py                   # `mda gaps` -- gap report
|   |   +-- graph_cmd.py                  # `mda graph` -- process graph output
|   |   +-- enrich_cmd.py                 # `mda enrich` -- Stage 2 enrichment
|   |   +-- generate_cmd.py              # `mda generate` -- Stages 3-5
|   |   +-- review_cmd.py                # `mda review` -- LLM-assisted review
|   |   +-- docs_cmd.py                  # `mda docs` -- MkDocs site generation
|   +-- pipeline/
|   |   +-- __init__.py
|   |   +-- stage1_parser.py              # BPMN XML to ParsedModel
|   |   +-- stage2_enricher.py            # Corpus matching + gap analysis
|   |   +-- stage3_capsule_gen.py         # Capsule file generation
|   |   +-- stage4_intent_gen.py          # Intent spec generation
|   |   +-- stage5_contract_gen.py        # Integration contract generation
|   |   +-- stage6_validator.py           # Triple + process validation
|   |   +-- orchestrator.py              # Pipeline stage orchestration
|   |   +-- docs_generator.py            # MkDocs site generation
|   +-- models/
|   |   +-- __init__.py
|   |   +-- bpmn.py                       # ParsedModel, BPMNNode, BPMNEdge, etc.
|   |   +-- enriched.py                   # EnrichedModel, Enrichment, Gap
|   |   +-- triple.py                     # Triple, Capsule, Intent, Contract models
|   |   +-- corpus.py                     # CorpusDocument, CorpusIndex models
|   +-- mda_io/
|   |   +-- __init__.py
|   |   +-- frontmatter.py               # YAML frontmatter read/write
|   |   +-- bpmn_xml.py                   # BPMN XML parsing helpers
|   |   +-- schema_validator.py           # JSON Schema validation
|   |   +-- yaml_io.py                    # YAML read/write utilities
|   +-- output/
|       +-- __init__.py
|       +-- console.py                    # Rich console output formatting
|       +-- json_output.py               # JSON output formatting
|
+-- schemas/                               # 5 JSON Schema files
|   +-- capsule.schema.json
|   +-- intent.schema.json
|   +-- contract.schema.json
|   +-- corpus-document.schema.json
|   +-- triple-manifest.schema.json
|
+-- ontology/                              # 5 YAML ontology files
|   +-- goal-types.yaml
|   +-- status-lifecycle.yaml
|   +-- bpmn-element-mapping.yaml
|   +-- id-conventions.yaml
|   +-- corpus-taxonomy.yaml
|
+-- corpus/                                # 46 .corpus.md files + index
|   +-- corpus.config.yaml                 # Corpus index (auto-generated)
|   +-- procedures/                        # 15 procedure documents
|   |   +-- loan-application-intake.corpus.md
|   |   +-- identity-verification-kyc.corpus.md
|   |   +-- credit-report-procedure.corpus.md
|   |   +-- dti-assessment-procedure.corpus.md
|   |   +-- document-request-procedure.corpus.md
|   |   +-- loan-file-packaging.corpus.md
|   |   +-- underwriting-submission.corpus.md
|   |   +-- w2-income-verification.corpus.md
|   |   +-- self-employment-income-verification.corpus.md
|   |   +-- qualifying-income-calculation.corpus.md
|   |   +-- appraisal-ordering-procedure.corpus.md
|   |   +-- appraisal-report-review.corpus.md
|   |   +-- property-value-assessment.corpus.md
|   |   +-- appraisal-revision-request.corpus.md
|   |   +-- appraisal-manual-review.corpus.md
|   +-- policies/                          # 6 policy documents
|   |   +-- credit-report-ordering-policy.corpus.md
|   |   +-- permissible-purpose-policy.corpus.md
|   |   +-- document-retention-policy.corpus.md
|   |   +-- w2-verification-policy.corpus.md
|   |   +-- appraisal-ordering-policy.corpus.md
|   |   +-- amc-selection-policy.corpus.md
|   +-- regulations/                       # 7 regulation documents
|   |   +-- fcra-summary.corpus.md
|   |   +-- tila-summary.corpus.md
|   |   +-- ecoa-summary.corpus.md
|   |   +-- fannie-mae-income-summary.corpus.md
|   |   +-- fha-income-requirements.corpus.md
|   |   +-- uspap-standards-summary.corpus.md
|   |   +-- appraiser-independence-requirements.corpus.md
|   +-- rules/                             # 7 rule documents
|   |   +-- loan-eligibility-matrix.corpus.md
|   |   +-- document-completeness-checklist.corpus.md
|   |   +-- dti-threshold-rules.corpus.md
|   |   +-- employment-type-classification.corpus.md
|   |   +-- income-variance-thresholds.corpus.md
|   |   +-- appraisal-completeness-checklist.corpus.md
|   |   +-- ltv-threshold-rules.corpus.md
|   +-- data-dictionary/                   # 4 data dictionary documents
|   |   +-- loan-application-data.corpus.md
|   |   +-- credit-report-data.corpus.md
|   |   +-- income-verification-data.corpus.md
|   |   +-- appraisal-report-data.corpus.md
|   +-- systems/                           # 5 system reference documents
|   |   +-- los-integration-guide.corpus.md
|   |   +-- docvault-integration-guide.corpus.md
|   |   +-- event-bus-guide.corpus.md
|   |   +-- ives-guide.corpus.md
|   |   +-- appraisal-portal-guide.corpus.md
|   +-- training/                          # 1 training document
|   |   +-- loan-processor-onboarding.corpus.md
|   +-- glossary/                          # 1 glossary document
|       +-- mortgage-lending-glossary.corpus.md
|
+-- templates/                             # 3 artifact templates + 8 MkDocs templates
|   +-- capsule.template.cap.md
|   +-- intent.template.intent.md
|   +-- contract.template.contract.md
|   +-- mkdocs/
|       +-- mkdocs.yml.j2
|       +-- index.md.j2
|       +-- triple-wrapper.md.j2
|       +-- flow.md.j2
|       +-- graph.md.j2
|       +-- gaps.md.j2
|       +-- audit.md.j2
|       +-- corpus-section.md.j2
|
+-- pipeline/                              # 7 pipeline stage documents
|   +-- README.md
|   +-- stage-1-parser.md
|   +-- stage-2-enricher.md
|   +-- stage-3-capsule-gen.md
|   +-- stage-4-intent-gen.md
|   +-- stage-5-contract-gen.md
|   +-- stage-6-validator.md
|
+-- examples/                              # 3 demo processes
|   +-- loan-origination/
|   |   +-- README.md
|   |   +-- mda.config.yaml
|   |   +-- bpmn/
|   |   |   +-- loan-origination.bpmn
|   |   |   +-- bpmn-metadata.yaml
|   |   +-- triples/
|   |   |   +-- _manifest.json
|   |   |   +-- receive-application/
|   |   |   |   +-- receive-application.cap.md
|   |   |   |   +-- receive-application.intent.md
|   |   |   |   +-- receive-application.contract.md
|   |   |   |   +-- triple.manifest.json
|   |   |   +-- verify-identity/
|   |   |   +-- pull-credit/
|   |   |   +-- assess-dti/
|   |   |   +-- request-docs/
|   |   |   +-- package-loan/
|   |   |   +-- submit-underwriting/
|   |   |   +-- timeout-no-response/
|   |   +-- decisions/
|   |   |   +-- loan-eligibility/
|   |   |   |   +-- loan-eligibility.cap.md
|   |   |   |   +-- loan-eligibility.intent.md
|   |   |   |   +-- loan-eligibility.contract.md
|   |   |   |   +-- triple.manifest.json
|   |   |   +-- docs-received/
|   |   +-- gaps/
|   |   |   +-- GAP-001.md
|   |   +-- graph/
|   |   |   +-- process-graph.yaml
|   |   |   +-- graph-visual.md
|   |   +-- audit/
|   |       +-- ingestion-log.yaml
|   |       +-- change-log.yaml
|   +-- income-verification/
|   |   +-- README.md
|   |   +-- mda.config.yaml
|   |   +-- bpmn/
|   |   |   +-- income-verification.bpmn
|   |   |   +-- bpmn-metadata.yaml
|   |   +-- triples/
|   |   |   +-- _manifest.json
|   |   |   +-- receive-request/
|   |   |   +-- classify-employment/
|   |   |   +-- verify-w2/
|   |   |   +-- verify-self-employment/
|   |   |   +-- calc-qualifying/
|   |   |   +-- emit-verified/
|   |   +-- decisions/
|   |   |   +-- employment-type/
|   |   |   +-- variance-threshold/
|   |   +-- gaps/
|   |   |   +-- GAP-001.md
|   |   +-- graph/
|   |   |   +-- process-graph.yaml
|   |   |   +-- graph-visual.md
|   |   +-- audit/
|   |       +-- ingestion-log.yaml
|   |       +-- change-log.yaml
|   +-- property-appraisal/
|       +-- README.md
|       +-- mda.config.yaml
|       +-- bpmn/
|       |   +-- property-appraisal.bpmn
|       |   +-- bpmn-metadata.yaml
|       +-- triples/
|       |   +-- _manifest.json
|       |   +-- order-appraisal/
|       |   +-- receive-report/
|       |   +-- validate-completeness/
|       |   +-- request-revision/
|       |   +-- assess-value/
|       |   +-- manual-review/
|       |   +-- emit-complete/
|       +-- decisions/
|       |   +-- completeness-check/
|       |   +-- ltv-check/
|       +-- gaps/
|       |   +-- GAP-001.md
|       +-- graph/
|       |   +-- process-graph.yaml
|       |   +-- graph-visual.md
|       +-- audit/
|           +-- ingestion-log.yaml
|           +-- change-log.yaml
|
+-- docs/                                  # 8 documentation files
    +-- getting-started.md
    +-- architecture.md
    +-- cli-reference.md
    +-- corpus-authoring.md
    +-- governance-model.md
    +-- lifecycle-management.md
    +-- process-owner-guide.md
    +-- triple-review.md
```

Each triple directory (e.g., `triples/receive-application/`) contains exactly 4 files:
- `{slug}.cap.md` -- Knowledge Capsule
- `{slug}.intent.md` -- Intent Specification
- `{slug}.contract.md` -- Integration Contract
- `triple.manifest.json` -- Triple manifest linking the three

Decision directories follow the same pattern but live under `decisions/` to distinguish gateway/decision triples from task triples.

---

## 3. JSON Schemas (Complete Specifications)

### 3.1 capsule.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mda-intent-engine.dev/schemas/capsule.schema.json",
  "title": "MDA Intent Layer Knowledge Capsule",
  "description": "Validates the YAML frontmatter of .cap.md (Knowledge Capsule) files in the MDA Intent Layer BPMN-to-Intent-Spec generation system.",
  "type": "object",
  "required": [
    "capsule_id",
    "bpmn_task_id",
    "bpmn_task_name",
    "bpmn_task_type",
    "process_id",
    "process_name",
    "version",
    "status",
    "generated_from",
    "generated_date",
    "generated_by",
    "last_modified",
    "last_modified_by",
    "intent_id",
    "contract_id"
  ],
  "additionalProperties": false,
  "properties": {
    "capsule_id": {
      "type": "string",
      "pattern": "^CAP-[A-Z]{2,3}-[A-Z]{3}-\\d{3}$",
      "description": "Unique identifier for this knowledge capsule."
    },
    "bpmn_task_id": {
      "type": "string",
      "description": "The BPMN task element ID this capsule was extracted from."
    },
    "bpmn_task_name": {
      "type": "string",
      "description": "Human-readable name of the BPMN task."
    },
    "bpmn_task_type": {
      "type": "string",
      "enum": [
        "userTask",
        "serviceTask",
        "businessRuleTask",
        "task",
        "sendTask",
        "receiveTask",
        "scriptTask",
        "manualTask",
        "callActivity",
        "subProcess"
      ],
      "description": "The BPMN task type."
    },
    "process_id": {
      "type": "string",
      "description": "The BPMN process ID containing this task."
    },
    "process_name": {
      "type": "string",
      "description": "Human-readable name of the BPMN process."
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+$",
      "description": "Semantic version in MAJOR.MINOR format."
    },
    "status": {
      "type": "string",
      "enum": ["draft", "review", "approved", "current", "deprecated", "archived"],
      "description": "Lifecycle status of this capsule."
    },
    "generated_from": {
      "type": "string",
      "description": "Source file or artifact this capsule was generated from."
    },
    "generated_date": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of when this capsule was generated."
    },
    "generated_by": {
      "type": "string",
      "description": "Tool or person that generated this capsule."
    },
    "last_modified": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of the last modification."
    },
    "last_modified_by": {
      "type": "string",
      "description": "Tool or person that last modified this capsule."
    },
    "owner_role": {
      "type": ["string", "null"],
      "description": "Role responsible for this capsule."
    },
    "owner_team": {
      "type": ["string", "null"],
      "description": "Team responsible for this capsule."
    },
    "reviewers": {
      "type": "array",
      "items": { "type": "string" },
      "description": "List of reviewer identifiers."
    },
    "domain": {
      "type": "string",
      "description": "Business domain classification."
    },
    "subdomain": {
      "type": "string",
      "description": "Business subdomain classification."
    },
    "regulation_refs": {
      "type": "array",
      "items": { "type": "string" },
      "description": "References to applicable regulations."
    },
    "policy_refs": {
      "type": "array",
      "items": { "type": "string" },
      "description": "References to applicable policies."
    },
    "intent_id": {
      "type": "string",
      "pattern": "^INT-[A-Z]{2,3}-[A-Z]{3}-\\d{3}$",
      "description": "Cross-reference to the corresponding Intent Specification."
    },
    "contract_id": {
      "type": "string",
      "pattern": "^ICT-[A-Z]{2,3}-[A-Z]{3}-\\d{3}$",
      "description": "Cross-reference to the corresponding Integration Contract."
    },
    "parent_capsule_id": {
      "type": ["string", "null"],
      "pattern": "^CAP-[A-Z]{2,3}-[A-Z]{3}-\\d{3}$",
      "description": "ID of the parent capsule, if this is a sub-task capsule."
    },
    "predecessor_ids": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^CAP-[A-Z]{2,3}-[A-Z]{3}-\\d{3}$"
      },
      "description": "Capsule IDs that precede this one in the process flow."
    },
    "successor_ids": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Capsule IDs that follow this one in the process flow."
    },
    "exception_ids": {
      "type": "array",
      "items": { "type": "string" },
      "description": "IDs of exception-handling capsules related to this one."
    },
    "gaps": {
      "type": "array",
      "items": { "$ref": "#/definitions/gap" },
      "description": "Known gaps or ambiguities in the capsule content."
    },
    "corpus_refs": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "corpus_id": {
            "type": "string",
            "pattern": "^CRP-[A-Z]{3}-[A-Z]{2,3}-\\d{3}$"
          },
          "section": { "type": "string" },
          "match_confidence": {
            "type": "string",
            "enum": ["high", "medium", "low"]
          }
        },
        "required": ["corpus_id", "section", "match_confidence"],
        "additionalProperties": false
      },
      "description": "References to corpus documents that informed this capsule."
    }
  },
  "definitions": {
    "gap": {
      "type": "object",
      "required": ["type", "description", "severity"],
      "additionalProperties": false,
      "properties": {
        "type": {
          "type": "string",
          "description": "Category of the gap."
        },
        "description": {
          "type": "string",
          "description": "Detailed description of the gap."
        },
        "severity": {
          "type": "string",
          "enum": ["critical", "high", "medium", "low"],
          "description": "Severity level of the gap."
        }
      }
    }
  }
}
```

**Key facts about this schema:**

- 15 required fields (the largest required set of any schema)
- `bpmn_task_type` enum has 10 values: `userTask`, `serviceTask`, `businessRuleTask`, `task`, `sendTask`, `receiveTask`, `scriptTask`, `manualTask`, `callActivity`, `subProcess`
- `status` enum has 6 values: `draft`, `review`, `approved`, `current`, `deprecated`, `archived`
- `capsule_id` pattern: `^CAP-[A-Z]{2,3}-[A-Z]{3}-\d{3}$`
- `intent_id` pattern: `^INT-[A-Z]{2,3}-[A-Z]{3}-\d{3}$`
- `contract_id` pattern: `^ICT-[A-Z]{2,3}-[A-Z]{3}-\d{3}$`
- `corpus_refs` items require `corpus_id`, `section`, `match_confidence` (enum: high/medium/low)
- `gap` items require `type`, `description`, `severity` (enum: critical/high/medium/low)
- `owner_role` and `owner_team` are nullable strings (not required)
- `version` pattern: `^\d+\.\d+$`
- `additionalProperties: false` on root and all sub-objects

### 3.2 intent.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mda-intent-engine.dev/schemas/intent.schema.json",
  "title": "MDA Intent Layer Intent Specification",
  "description": "Validates the YAML frontmatter of .intent.md (Intent Specification) files in the MDA Intent Layer BPMN-to-Intent-Spec generation system.",
  "type": "object",
  "required": [
    "intent_id",
    "capsule_id",
    "bpmn_task_id",
    "version",
    "status",
    "goal",
    "goal_type",
    "contract_ref",
    "generated_from",
    "generated_date",
    "generated_by"
  ],
  "additionalProperties": false,
  "properties": {
    "intent_id": {
      "type": "string",
      "pattern": "^INT-[A-Z]{2,3}-[A-Z]{3}-\\d{3}$",
      "description": "Unique identifier for this intent specification."
    },
    "capsule_id": {
      "type": "string",
      "pattern": "^CAP-[A-Z]{2,3}-[A-Z]{3}-\\d{3}$",
      "description": "Cross-reference to the source Knowledge Capsule."
    },
    "bpmn_task_id": {
      "type": "string",
      "description": "The BPMN task element ID this intent was derived from."
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+$",
      "description": "Semantic version in MAJOR.MINOR format."
    },
    "status": {
      "type": "string",
      "enum": ["draft", "review", "approved", "current", "deprecated", "archived"],
      "description": "Lifecycle status of this intent specification."
    },
    "goal": {
      "type": "string",
      "description": "The outcome statement describing what this task achieves."
    },
    "goal_type": {
      "type": "string",
      "enum": ["data_production", "decision", "notification", "state_transition", "orchestration"],
      "description": "Classification of the goal's nature."
    },
    "preconditions": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Conditions that must be true before execution."
    },
    "inputs": {
      "type": "array",
      "items": { "$ref": "#/definitions/input" },
      "description": "Data inputs required for execution."
    },
    "outputs": {
      "type": "array",
      "items": { "$ref": "#/definitions/output" },
      "description": "Data outputs produced by execution."
    },
    "invariants": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Conditions that must remain true throughout execution."
    },
    "success_criteria": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Criteria that define successful completion."
    },
    "failure_modes": {
      "type": "array",
      "items": { "$ref": "#/definitions/failure_mode" },
      "description": "Known failure modes and their handling."
    },
    "contract_ref": {
      "type": "string",
      "pattern": "^ICT-[A-Z]{2,3}-[A-Z]{3}-\\d{3}$",
      "description": "Reference to the associated Integration Contract."
    },
    "idempotency": {
      "type": "string",
      "enum": ["safe", "unsafe"],
      "description": "Whether this operation is idempotent."
    },
    "retry_policy": {
      "type": "string",
      "description": "Retry strategy description (e.g., exponential backoff)."
    },
    "timeout_seconds": {
      "type": "integer",
      "minimum": 1,
      "description": "Maximum allowed execution time in seconds."
    },
    "side_effects": {
      "type": "array",
      "items": { "type": "string" },
      "description": "External side effects produced by this operation."
    },
    "execution_hints": {
      "$ref": "#/definitions/execution_hints",
      "description": "Non-binding hints for the execution layer."
    },
    "generated_from": {
      "type": "string",
      "description": "Source artifact this intent was generated from."
    },
    "generated_date": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of when this intent was generated."
    },
    "generated_by": {
      "type": "string",
      "description": "Tool or person that generated this intent."
    },
    "mda_layer": {
      "type": "string",
      "const": "PIM",
      "description": "MDA layer designation; always PIM for intent specifications."
    },
    "gaps": {
      "type": "array",
      "items": { "$ref": "#/definitions/gap" },
      "description": "Known gaps or ambiguities in the intent specification."
    }
  },
  "definitions": {
    "input": {
      "type": "object",
      "required": ["name", "source"],
      "additionalProperties": false,
      "properties": {
        "name": {
          "type": "string",
          "description": "Name of the input data element."
        },
        "source": {
          "type": "string",
          "description": "Where this input comes from."
        },
        "schema_ref": {
          "type": "string",
          "description": "Reference to the schema defining this input's structure."
        },
        "required": {
          "type": "boolean",
          "description": "Whether this input is mandatory."
        }
      }
    },
    "output": {
      "type": "object",
      "required": ["name", "type", "sink"],
      "additionalProperties": false,
      "properties": {
        "name": {
          "type": "string",
          "description": "Name of the output data element."
        },
        "type": {
          "type": "string",
          "description": "Data type of the output."
        },
        "sink": {
          "type": "string",
          "description": "Where this output is sent."
        },
        "invariants": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Invariants that apply to this specific output."
        }
      }
    },
    "failure_mode": {
      "type": "object",
      "required": ["mode", "detection", "action"],
      "additionalProperties": false,
      "properties": {
        "mode": {
          "type": "string",
          "description": "Description of the failure mode."
        },
        "detection": {
          "type": "string",
          "description": "How this failure is detected."
        },
        "action": {
          "type": "string",
          "description": "What action to take when this failure occurs."
        }
      }
    },
    "execution_hints": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "preferred_agent": {
          "type": "string",
          "description": "Suggested agent or service to execute this intent."
        },
        "tool_access": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Tools the executing agent may need access to."
        },
        "forbidden_actions": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Actions the executing agent must not perform."
        }
      }
    },
    "gap": {
      "type": "object",
      "required": ["type", "description", "severity"],
      "additionalProperties": false,
      "properties": {
        "type": {
          "type": "string",
          "description": "Category of the gap."
        },
        "description": {
          "type": "string",
          "description": "Detailed description of the gap."
        },
        "severity": {
          "type": "string",
          "enum": ["critical", "high", "medium", "low"],
          "description": "Severity level of the gap."
        }
      }
    }
  }
}
```

**Key facts about this schema:**

- 11 required fields
- `goal_type` enum has 5 values: `data_production`, `decision`, `notification`, `state_transition`, `orchestration`
- `input` items require `name` and `source`; optional `schema_ref` (string) and `required` (boolean)
- `output` items require `name`, `type`, and `sink`; optional `invariants` (string array)
- `failure_mode` items require `mode`, `detection`, and `action` (all strings)
- `execution_hints` has three optional fields: `preferred_agent` (string), `tool_access` (string[]), `forbidden_actions` (string[])
- `mda_layer` is a const: always `"PIM"`
- `idempotency` enum: `safe`, `unsafe`

### 3.3 contract.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mda-intent-engine.dev/schemas/contract.schema.json",
  "title": "MDA Intent Layer Integration Contract",
  "description": "Validates the YAML frontmatter of .contract.md (Integration Contract) files in the MDA Intent Layer BPMN-to-Intent-Spec generation system.",
  "type": "object",
  "required": [
    "contract_id",
    "intent_id",
    "version",
    "status",
    "binding_status",
    "generated_from",
    "generated_date",
    "generated_by"
  ],
  "additionalProperties": false,
  "properties": {
    "contract_id": {
      "type": "string",
      "pattern": "^ICT-[A-Z]{2,3}-[A-Z]{3}-\\d{3}$",
      "description": "Unique identifier for this integration contract."
    },
    "intent_id": {
      "type": "string",
      "pattern": "^INT-[A-Z]{2,3}-[A-Z]{3}-\\d{3}$",
      "description": "Cross-reference to the corresponding Intent Specification."
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+$",
      "description": "Semantic version in MAJOR.MINOR format."
    },
    "status": {
      "type": "string",
      "enum": ["draft", "review", "approved", "current", "deprecated", "archived"],
      "description": "Lifecycle status of this contract."
    },
    "sources": {
      "type": "array",
      "items": { "$ref": "#/definitions/source" },
      "description": "Data sources this contract integrates with."
    },
    "sinks": {
      "type": "array",
      "items": { "$ref": "#/definitions/sink" },
      "description": "Data sinks this contract writes to."
    },
    "events": {
      "type": "array",
      "items": { "$ref": "#/definitions/event" },
      "description": "Events produced or consumed by this contract."
    },
    "rule_engines": {
      "type": "array",
      "items": { "$ref": "#/definitions/rule_engine" },
      "description": "Rule engines used for business logic evaluation."
    },
    "audit": {
      "$ref": "#/definitions/audit",
      "description": "Audit trail configuration."
    },
    "generated_from": {
      "type": "string",
      "description": "Source artifact this contract was generated from."
    },
    "generated_date": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of when this contract was generated."
    },
    "generated_by": {
      "type": "string",
      "description": "Tool or person that generated this contract."
    },
    "mda_layer": {
      "type": "string",
      "const": "PSM",
      "description": "MDA layer designation; always PSM for integration contracts."
    },
    "binding_status": {
      "type": "string",
      "enum": ["unbound", "partial", "bound"],
      "description": "Whether all sources and sinks have been resolved to concrete endpoints."
    },
    "unbound_sources": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Names of sources that have not yet been bound to concrete endpoints."
    },
    "unbound_sinks": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Names of sinks that have not yet been bound to concrete endpoints."
    }
  },
  "definitions": {
    "source": {
      "type": "object",
      "required": ["name", "protocol", "endpoint"],
      "additionalProperties": false,
      "properties": {
        "name": {
          "type": "string",
          "description": "Logical name of this data source."
        },
        "protocol": {
          "type": "string",
          "enum": ["rest", "grpc", "graphql", "soap", "jdbc", "file", "message_queue"],
          "description": "Communication protocol."
        },
        "endpoint": {
          "type": "string",
          "description": "URI or connection string for the source."
        },
        "auth": {
          "type": "string",
          "description": "Authentication mechanism (e.g., oauth2, api_key, mtls)."
        },
        "schema_ref": {
          "type": "string",
          "description": "Reference to the schema defining the data structure."
        },
        "sla_ms": {
          "type": "integer",
          "description": "Expected response time SLA in milliseconds."
        }
      }
    },
    "sink": {
      "type": "object",
      "required": ["name", "protocol", "endpoint"],
      "additionalProperties": false,
      "properties": {
        "name": {
          "type": "string",
          "description": "Logical name of this data sink."
        },
        "protocol": {
          "type": "string",
          "enum": ["rest", "grpc", "graphql", "soap", "jdbc", "file", "message_queue"],
          "description": "Communication protocol."
        },
        "endpoint": {
          "type": "string",
          "description": "URI or connection string for the sink."
        },
        "auth": {
          "type": "string",
          "description": "Authentication mechanism."
        },
        "schema_ref": {
          "type": "string",
          "description": "Reference to the schema defining the data structure."
        },
        "sla_ms": {
          "type": "integer",
          "description": "Expected response time SLA in milliseconds."
        },
        "idempotency_key": {
          "type": "string",
          "description": "Field or expression used as the idempotency key for writes."
        }
      }
    },
    "event": {
      "type": "object",
      "required": ["topic"],
      "additionalProperties": false,
      "properties": {
        "topic": {
          "type": "string",
          "description": "Event topic or channel name."
        },
        "schema_ref": {
          "type": "string",
          "description": "Reference to the event payload schema."
        },
        "delivery": {
          "type": "string",
          "enum": ["at_least_once", "at_most_once", "exactly_once"],
          "description": "Delivery guarantee semantics."
        },
        "key_field": {
          "type": "string",
          "description": "Field used as the partition or ordering key."
        }
      }
    },
    "rule_engine": {
      "type": "object",
      "required": ["name"],
      "additionalProperties": false,
      "properties": {
        "name": {
          "type": "string",
          "description": "Name of the rule engine."
        },
        "version": {
          "type": "string",
          "description": "Version of the rule engine."
        },
        "endpoint": {
          "type": "string",
          "description": "Endpoint for rule engine access."
        }
      }
    },
    "audit": {
      "type": "object",
      "required": ["record_type", "retention_years", "sink"],
      "additionalProperties": false,
      "properties": {
        "record_type": {
          "type": "string",
          "description": "Type of audit record to produce."
        },
        "retention_years": {
          "type": "integer",
          "description": "Number of years audit records must be retained."
        },
        "fields_required": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Fields that must be present in every audit record."
        },
        "sink": {
          "type": "string",
          "description": "Destination for audit records."
        }
      }
    }
  }
}
```

**Key facts about this schema:**

- 8 required fields
- `protocol` enum (used in both source and sink): `rest`, `grpc`, `graphql`, `soap`, `jdbc`, `file`, `message_queue` (7 values)
- `delivery` enum (on event): `at_least_once`, `at_most_once`, `exactly_once` (3 values)
- `binding_status` enum: `unbound`, `partial`, `bound` (3 values)
- `mda_layer` is a const: always `"PSM"`
- `source` requires: `name`, `protocol`, `endpoint`; optional: `auth`, `schema_ref`, `sla_ms`
- `sink` has same required/optional as source, plus optional `idempotency_key`
- `event` requires only `topic`; optional: `schema_ref`, `delivery`, `key_field`
- `rule_engine` requires only `name`; optional: `version`, `endpoint`
- `audit` requires: `record_type`, `retention_years`, `sink`; optional: `fields_required`

### 3.4 corpus-document.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mda-intent-engine.dev/schemas/corpus-document.schema.json",
  "title": "MDA Intent Layer Corpus Document",
  "description": "Validates the YAML frontmatter of .corpus.md files in the MDA Intent Layer knowledge corpus.",
  "type": "object",
  "required": [
    "corpus_id",
    "title",
    "slug",
    "doc_type",
    "domain",
    "version",
    "status",
    "author",
    "last_modified",
    "last_modified_by",
    "source"
  ],
  "additionalProperties": false,
  "properties": {
    "corpus_id": {
      "type": "string",
      "pattern": "^CRP-[A-Z]{3}-[A-Z]{2,3}-\\d{3}$",
      "description": "Unique identifier for this corpus document."
    },
    "title": {
      "type": "string",
      "description": "Human-readable title of the corpus document."
    },
    "slug": {
      "type": "string",
      "description": "URL-friendly short name for the corpus document."
    },
    "doc_type": {
      "type": "string",
      "enum": [
        "procedure",
        "policy",
        "regulation",
        "rule",
        "data-dictionary",
        "system",
        "training",
        "glossary"
      ],
      "description": "The type of corpus document."
    },
    "domain": {
      "type": "string",
      "description": "Business domain this document belongs to."
    },
    "subdomain": {
      "type": "string",
      "description": "Business subdomain classification."
    },
    "tags": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Freeform tags for discovery and filtering."
    },
    "applies_to": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "process_ids": {
          "type": "array",
          "items": { "type": "string" },
          "description": "BPMN process IDs this document applies to."
        },
        "task_types": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": [
              "userTask",
              "serviceTask",
              "businessRuleTask",
              "task",
              "sendTask",
              "receiveTask",
              "scriptTask",
              "manualTask",
              "callActivity",
              "subProcess"
            ]
          },
          "description": "BPMN task types this document is relevant to."
        },
        "task_name_patterns": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Regex patterns matched against BPMN task names."
        },
        "goal_types": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": [
              "data_production",
              "decision",
              "notification",
              "state_transition",
              "orchestration"
            ]
          },
          "description": "Intent goal types this document applies to."
        },
        "roles": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Roles for which this document is relevant."
        }
      },
      "description": "Scoping rules that link this document to BPMN elements and intents."
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+$",
      "description": "Semantic version in MAJOR.MINOR format."
    },
    "status": {
      "type": "string",
      "enum": ["draft", "review", "current", "superseded", "archived"],
      "description": "Lifecycle status of this corpus document."
    },
    "effective_date": {
      "type": "string",
      "format": "date",
      "description": "Date this document becomes effective."
    },
    "review_date": {
      "type": "string",
      "format": "date",
      "description": "Next scheduled review date."
    },
    "supersedes": {
      "type": ["string", "null"],
      "pattern": "^CRP-[A-Z]{3}-[A-Z]{2,3}-\\d{3}$",
      "description": "Corpus ID of the document this one replaces."
    },
    "superseded_by": {
      "type": ["string", "null"],
      "pattern": "^CRP-[A-Z]{3}-[A-Z]{2,3}-\\d{3}$",
      "description": "Corpus ID of the document that replaces this one."
    },
    "author": {
      "type": "string",
      "description": "Original author of this document."
    },
    "last_modified": {
      "type": "string",
      "format": "date",
      "description": "Date of the last modification."
    },
    "last_modified_by": {
      "type": "string",
      "description": "Person or tool that last modified this document."
    },
    "source": {
      "type": "string",
      "enum": ["internal", "external", "regulatory"],
      "description": "Origin classification of this document."
    },
    "source_ref": {
      "type": ["string", "null"],
      "description": "External reference identifier for the source material."
    },
    "related_corpus_ids": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^CRP-[A-Z]{3}-[A-Z]{2,3}-\\d{3}$"
      },
      "description": "Cross-references to related corpus documents."
    },
    "regulation_refs": {
      "type": "array",
      "items": { "type": "string" },
      "description": "References to applicable regulations."
    },
    "policy_refs": {
      "type": "array",
      "items": { "type": "string" },
      "description": "References to applicable policies."
    }
  }
}
```

**Key facts about this schema:**

- 11 required fields
- `corpus_id` pattern: `^CRP-[A-Z]{3}-[A-Z]{2,3}-\d{3}$` (note: type prefix is 3 letters unlike CAP/INT/ICT which are 3 letters -- CRP is also 3)
- `doc_type` enum has 8 values: `procedure`, `policy`, `regulation`, `rule`, `data-dictionary`, `system`, `training`, `glossary`
- `status` enum has 5 values (different from triple status): `draft`, `review`, `current`, `superseded`, `archived`
- `source` enum has 3 values: `internal`, `external`, `regulatory`
- `applies_to` is an object with 5 optional arrays: `process_ids`, `task_types`, `task_name_patterns`, `goal_types`, `roles`
- `last_modified` uses `format: date` (not date-time, unlike triple schemas)
- `supersedes` and `superseded_by` are nullable strings with CRP pattern

### 3.5 triple-manifest.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mda-intent-engine.dev/schemas/triple-manifest.schema.json",
  "title": "MDA Intent Layer Triple Manifest",
  "description": "Validates the triple.manifest.json file that links a Knowledge Capsule, Intent Specification, and Integration Contract into a validated triple.",
  "type": "object",
  "required": [
    "triple_id",
    "capsule_id",
    "intent_id",
    "contract_id",
    "bpmn_task_id",
    "bpmn_process_id",
    "status",
    "version",
    "provenance"
  ],
  "additionalProperties": false,
  "properties": {
    "triple_id": {
      "type": "string",
      "pattern": "^[A-Z]{2,3}-[A-Z]{3}-\\d{3}$",
      "description": "Unique identifier for this triple (shared suffix across capsule, intent, and contract)."
    },
    "capsule_id": {
      "type": "string",
      "pattern": "^CAP-[A-Z]{2,3}-[A-Z]{3}-\\d{3}$",
      "description": "Reference to the Knowledge Capsule."
    },
    "intent_id": {
      "type": "string",
      "pattern": "^INT-[A-Z]{2,3}-[A-Z]{3}-\\d{3}$",
      "description": "Reference to the Intent Specification."
    },
    "contract_id": {
      "type": "string",
      "pattern": "^ICT-[A-Z]{2,3}-[A-Z]{3}-\\d{3}$",
      "description": "Reference to the Integration Contract."
    },
    "bpmn_task_id": {
      "type": "string",
      "description": "The BPMN task element ID this triple represents."
    },
    "bpmn_process_id": {
      "type": "string",
      "description": "The BPMN process ID containing the task."
    },
    "status": {
      "type": "string",
      "enum": ["draft", "review", "approved", "current", "deprecated", "archived"],
      "description": "Lifecycle status of this triple."
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+$",
      "description": "Semantic version in MAJOR.MINOR format."
    },
    "created": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of when this triple was created."
    },
    "last_validated": {
      "type": ["string", "null"],
      "format": "date-time",
      "description": "ISO 8601 timestamp of the last validation run, or null if never validated."
    },
    "validation_result": {
      "type": ["string", "null"],
      "enum": ["pass", "fail", "skipped", null],
      "description": "Result of the last validation run."
    },
    "provenance": {
      "$ref": "#/definitions/provenance",
      "description": "Provenance information linking back to the source BPMN file."
    }
  },
  "definitions": {
    "provenance": {
      "type": "object",
      "required": ["bpmn_file", "bpmn_file_hash", "pipeline_version"],
      "additionalProperties": false,
      "properties": {
        "bpmn_file": {
          "type": "string",
          "description": "Path or name of the source BPMN file."
        },
        "bpmn_file_hash": {
          "type": "string",
          "pattern": "^sha256:[a-f0-9]{64}$",
          "description": "SHA-256 hash of the source BPMN file for integrity verification."
        },
        "pipeline_version": {
          "type": "string",
          "description": "Version of the generation pipeline that produced this triple."
        }
      }
    }
  }
}
```

**Key facts about this schema:**

- 9 required fields
- `triple_id` pattern: `^[A-Z]{2,3}-[A-Z]{3}-\d{3}$` -- NO type prefix; this is the shared stem
- `validation_result` is nullable with enum: `pass`, `fail`, `skipped`, or `null`
- `provenance` requires: `bpmn_file`, `bpmn_file_hash`, `pipeline_version`
- `bpmn_file_hash` pattern: `^sha256:[a-f0-9]{64}$`
- `last_validated` is nullable date-time

---

## 4. Ontology Definitions (Complete)

### 4.1 goal-types.yaml

```yaml
# MDA Intent Layer -- Goal Type Ontology
# Defines the allowed values for goal_type in intent specifications

goal_types:
  - id: data_production
    name: Data Production
    description: "The intent produces new data or transforms existing data into a required output"
    examples:
      - "Calculate verified income from tax returns"
      - "Generate credit score summary"
      - "Extract borrower information from application"
    typical_bpmn_elements:
      - serviceTask
      - scriptTask
      - userTask
      - manualTask

  - id: decision
    name: Decision
    description: "The intent evaluates conditions and produces a routing decision or classification"
    examples:
      - "Determine loan eligibility based on DTI ratio"
      - "Classify employment type as W-2 or self-employed"
    typical_bpmn_elements:
      - businessRuleTask
      - exclusiveGateway
      - inclusiveGateway
      - eventBasedGateway

  - id: notification
    name: Notification
    description: "The intent sends a message, alert, or signal to another system or participant"
    examples:
      - "Notify underwriter of completed income verification"
      - "Send document request to borrower"
    typical_bpmn_elements:
      - sendTask
      - intermediateThrowEvent

  - id: state_transition
    name: State Transition
    description: "The intent moves a business entity from one state to another"
    examples:
      - "Move loan from 'application' to 'processing' state"
      - "Mark appraisal as 'received'"
    typical_bpmn_elements:
      - receiveTask
      - startEvent
      - endEvent
      - intermediateCatchEvent

  - id: orchestration
    name: Orchestration
    description: "The intent coordinates multiple sub-intents or manages parallel execution"
    examples:
      - "Coordinate parallel credit check and income verification"
      - "Manage sub-process for document collection"
    typical_bpmn_elements:
      - callActivity
      - subProcess
```

### 4.2 status-lifecycle.yaml

```yaml
# MDA Intent Layer -- Status Lifecycle
# Defines the lifecycle states for triples (capsule + intent + contract)

statuses:
  - id: draft
    name: Draft
    description: "Generated by pipeline, may have gaps, not yet reviewed"
    required_fields:
      - capsule_id / intent_id / contract_id
      - bpmn_task_id
      - generated_from, generated_date, generated_by
    allowed_transitions:
      - review
    entry_conditions:
      - "Pipeline generates new triple"
      - "Existing triple is modified (auto-resets to draft)"

  - id: review
    name: Under Review
    description: "PR opened, human reviewers assigned, being evaluated"
    required_fields:
      - capsule_id / intent_id / contract_id
      - bpmn_task_id
      - generated_from, generated_date, generated_by
      - owner_role or owner_team
      - All inputs and outputs defined (for intent specs)
    allowed_transitions:
      - approved
      - draft    # if changes requested
    entry_conditions:
      - "PR opened against main branch"
      - "Pipeline validation passes"

  - id: approved
    name: Approved
    description: "All required reviewers have approved, awaiting merge"
    required_fields:
      - capsule_id / intent_id / contract_id
      - bpmn_task_id
      - generated_from, generated_date, generated_by
      - owner_role or owner_team
      - All inputs and outputs defined (for intent specs)
      - No critical gaps remaining
      - All cross-references valid
    allowed_transitions:
      - current
      - draft    # if reopened
    entry_conditions:
      - "All required PR reviewers approved"

  - id: current
    name: Current
    description: "Live, agent-executable, invariants enforced at runtime"
    required_fields:
      - capsule_id / intent_id / contract_id
      - bpmn_task_id
      - generated_from, generated_date, generated_by
      - owner_role or owner_team
      - All inputs and outputs defined (for intent specs)
      - No critical gaps remaining
      - All cross-references valid
    allowed_transitions:
      - deprecated
      - draft    # if direct edit triggers re-review
    entry_conditions:
      - "PR merged to main"

  - id: deprecated
    name: Deprecated
    description: "Superseded by new version or BPMN task removed, kept for audit"
    allowed_transitions:
      - archived
    entry_conditions:
      - "New version of triple merged to main"
      - "BPMN task removed in re-ingestion"

  - id: archived
    name: Archived
    description: "Permanently stored, no longer referenced, retention policy applies"
    allowed_transitions: []
    entry_conditions:
      - "Retention period elapsed"
      - "Compliance sign-off received"
```

**Transition graph:**

```
draft --> review --> approved --> current --> deprecated --> archived
  ^         |           |           |
  |         +-----------+           |
  +--- (changes requested) ---------+
```

### 4.3 bpmn-element-mapping.yaml

```yaml
# MDA Intent Layer -- BPMN Element Mapping
# Defines how each BPMN 2.0 element maps to triples

mappings:
  # === TASKS (produce full triples) ===
  - bpmn_element: task
    xml_tag: "<task>"
    triple_type: standard
    default_goal_type: null    # must be manually classified
    generates_capsule: true
    generates_intent: true
    generates_contract: true
    notes: "Generic task -- goal type must be set manually"

  - bpmn_element: userTask
    xml_tag: "<userTask>"
    triple_type: standard
    default_goal_type: data_production
    generates_capsule: true
    generates_intent: true
    generates_contract: true
    notes: "Human-performed task, still gets intent spec for agent-assisted execution"

  - bpmn_element: serviceTask
    xml_tag: "<serviceTask>"
    triple_type: standard
    default_goal_type: data_production
    generates_capsule: true
    generates_intent: true
    generates_contract: true

  - bpmn_element: businessRuleTask
    xml_tag: "<businessRuleTask>"
    triple_type: standard
    default_goal_type: decision
    generates_capsule: true
    generates_intent: true
    generates_contract: true

  - bpmn_element: sendTask
    xml_tag: "<sendTask>"
    triple_type: standard
    default_goal_type: notification
    generates_capsule: true
    generates_intent: true
    generates_contract: true

  - bpmn_element: receiveTask
    xml_tag: "<receiveTask>"
    triple_type: standard
    default_goal_type: state_transition
    generates_capsule: true
    generates_intent: true
    generates_contract: true

  - bpmn_element: scriptTask
    xml_tag: "<scriptTask>"
    triple_type: standard
    default_goal_type: data_production
    generates_capsule: true
    generates_intent: true
    generates_contract: true

  - bpmn_element: manualTask
    xml_tag: "<manualTask>"
    triple_type: standard
    default_goal_type: data_production
    generates_capsule: true
    generates_intent: true
    generates_contract: true

  - bpmn_element: callActivity
    xml_tag: "<callActivity>"
    triple_type: reference
    default_goal_type: orchestration
    generates_capsule: true
    generates_intent: true
    generates_contract: true
    notes: "Points to sub-process repo via cross-reference"

  - bpmn_element: subProcess
    xml_tag: "<subProcess>"
    triple_type: container
    default_goal_type: orchestration
    generates_capsule: true
    generates_intent: true
    generates_contract: true
    notes: "Recursively generates triples for contained tasks"

  # === GATEWAYS ===
  - bpmn_element: exclusiveGateway
    xml_tag: "<exclusiveGateway>"
    triple_type: decision
    default_goal_type: decision
    generates_capsule: true
    generates_intent: true
    generates_contract: true
    notes: "XOR branching -- one path taken"

  - bpmn_element: inclusiveGateway
    xml_tag: "<inclusiveGateway>"
    triple_type: decision
    default_goal_type: decision
    generates_capsule: true
    generates_intent: true
    generates_contract: true
    notes: "OR branching -- one or more paths taken"

  - bpmn_element: parallelGateway
    xml_tag: "<parallelGateway>"
    triple_type: coordination
    default_goal_type: null
    generates_capsule: true
    generates_intent: false
    generates_contract: false
    notes: "Fork/join -- structural, not behavioral. Capsule only for documentation."

  - bpmn_element: eventBasedGateway
    xml_tag: "<eventBasedGateway>"
    triple_type: decision
    default_goal_type: decision
    generates_capsule: true
    generates_intent: true
    generates_contract: true

  # === EVENTS ===
  - bpmn_element: startEvent
    xml_tag: "<startEvent>"
    triple_type: process_boundary
    default_goal_type: state_transition
    generates_capsule: true
    generates_intent: true
    generates_contract: true
    notes: "Process entry point -- trigger documentation"

  - bpmn_element: endEvent
    xml_tag: "<endEvent>"
    triple_type: process_boundary
    default_goal_type: state_transition
    generates_capsule: true
    generates_intent: true
    generates_contract: true

  - bpmn_element: intermediateCatchEvent
    xml_tag: "<intermediateCatchEvent>"
    triple_type: standard
    default_goal_type: state_transition
    generates_capsule: true
    generates_intent: true
    generates_contract: true

  - bpmn_element: intermediateThrowEvent
    xml_tag: "<intermediateThrowEvent>"
    triple_type: standard
    default_goal_type: notification
    generates_capsule: true
    generates_intent: true
    generates_contract: true

  - bpmn_element: boundaryEvent
    xml_tag: "<boundaryEvent>"
    triple_type: exception
    default_goal_type: null
    generates_capsule: true
    generates_intent: true
    generates_contract: true
    notes: "Attached to parent task -- exception handling"

  # === NON-TRIPLE ELEMENTS (metadata extraction only) ===
  - bpmn_element: dataObject
    xml_tag: "<dataObject>"
    triple_type: none
    generates_capsule: false
    generates_intent: false
    generates_contract: false
    extraction: "Referenced as input/output in intent specs and source/sink in contracts"

  - bpmn_element: dataStoreReference
    xml_tag: "<dataStoreReference>"
    triple_type: none
    generates_capsule: false
    generates_intent: false
    generates_contract: false
    extraction: "Referenced as source/sink in contracts"

  - bpmn_element: lane
    xml_tag: "<lane>"
    triple_type: none
    generates_capsule: false
    generates_intent: false
    generates_contract: false
    extraction: "Sets owner_role on enclosed tasks"

  - bpmn_element: participant
    xml_tag: "<participant>"
    triple_type: none
    generates_capsule: false
    generates_intent: false
    generates_contract: false
    extraction: "Sets owner_team on enclosed tasks"

  - bpmn_element: messageFlow
    xml_tag: "<messageFlow>"
    triple_type: none
    generates_capsule: false
    generates_intent: false
    generates_contract: false
    extraction: "Becomes event definition in integration contracts"

  - bpmn_element: sequenceFlow
    xml_tag: "<sequenceFlow>"
    triple_type: none
    generates_capsule: false
    generates_intent: false
    generates_contract: false
    extraction: "Populates predecessor_ids and successor_ids in capsules"
```

**Summary:** 24 BPMN elements total. 19 produce capsules. 17 produce intent specs (parallelGateway and boundaryEvent excluded from intent in some cases, but boundaryEvent does generate intent). 17 produce contracts. 6 are metadata-only (no triples).

### 4.4 id-conventions.yaml

```yaml
# MDA Intent Layer -- ID Conventions
# Defines the naming rules for all identifiers

id_format:
  pattern: "{TYPE}-{PROCESS}-{CATEGORY}-{SEQ}"

  type_prefixes:
    CAP: "Knowledge Capsule"
    INT: "Intent Specification"
    ICT: "Integration Contract"
    GAP: "Unresolved Gap"
    CRP: "Corpus Document"

  process_codes:
    description: "2-3 uppercase letter code identifying the process"
    rules:
      - "Must be unique across all process repos"
      - "Derived from process name abbreviation"
      - "Registered in engine repo process catalog"
    examples:
      LO: "Loan Origination"
      IV: "Income Verification"
      PA: "Property Appraisal"
      UW: "Underwriting"
      DC: "Document Collection"
      CL: "Closing"

  category_codes:
    description: "3 uppercase letter code identifying the functional area within the process"
    rules:
      - "Derived from task name"
      - "Must be unique within a process"
      - "Reuse standard codes where applicable"
    standard_codes:
      APP: "Application"
      IDV: "Identity Verification"
      CRC: "Credit Check"
      INC: "Income"
      DTI: "Debt-to-Income"
      DOC: "Documentation"
      PKG: "Packaging"
      SUB: "Submission"
      DEC: "Decision"
      ESC: "Escalation"
      NTF: "Notification"
      REQ: "Request"
      CLS: "Classification"
      QAL: "Qualification"
      ORD: "Order"
      RCV: "Receive"
      VAL: "Validation"
      REV: "Revision"
      ASV: "Assessment"
      MRV: "Manual Review"
      TMO: "Timeout"
      REJ: "Rejection"
      W2V: "W-2 Verification"
      SEI: "Self-Employment Income"
      PRC: "Procedure (corpus doc type)"
      POL: "Policy (corpus doc type)"
      REG: "Regulation (corpus doc type)"
      RUL: "Rule (corpus doc type)"
      DAT: "Data Dictionary (corpus doc type)"
      SYS: "System Reference (corpus doc type)"
      TRN: "Training Material (corpus doc type)"
      GLO: "Glossary (corpus doc type)"

  sequence:
    description: "3-digit zero-padded sequential number"
    format: "\\d{3}"
    starts_at: "001"
    notes: "Sequence is unique within a process+category combination"

  triple_id:
    description: "The shared stem used in triple.manifest.json"
    format: "{PROCESS}-{CATEGORY}-{SEQ}"
    notes: "Same as the full ID minus the type prefix"

  cross_reference_rules:
    - "A capsule CAP-XX-YYY-NNN must have matching INT-XX-YYY-NNN and ICT-XX-YYY-NNN"
    - "All three files in a triple share the same PROCESS-CATEGORY-SEQ stem"
    - "predecessor_ids and successor_ids reference capsule IDs (CAP-...)"
    - "exception_ids reference capsule IDs of boundary event triples"
    - "intent_id in capsule frontmatter must match the paired intent spec's intent_id"
    - "contract_ref in intent spec must match the paired contract's contract_id"
```

### 4.5 corpus-taxonomy.yaml

```yaml
# MDA Intent Layer -- Corpus Document Taxonomy
# Defines the 8 document types and status lifecycle for .corpus.md files

doc_types:
  - id: procedure
    name: Procedure
    id_prefix: PRC
    description: >
      Step-by-step operational instructions describing how to carry out
      a specific business activity or process task.
    expected_body_sections:
      - Purpose
      - Scope
      - Prerequisites
      - Procedure Steps
      - Exception Handling
      - Related Documents
    change_cadence: quarterly

  - id: policy
    name: Policy
    id_prefix: POL
    description: >
      High-level organizational directives that establish rules, boundaries,
      and decision-making authority for a business domain.
    expected_body_sections:
      - Purpose
      - Scope
      - Policy Statement
      - Roles and Responsibilities
      - Compliance Requirements
      - Exceptions
      - Related Documents
    change_cadence: annual

  - id: regulation
    name: Regulation
    id_prefix: REG
    description: >
      External regulatory requirements, statutes, or mandates imposed by
      governing bodies that the organization must comply with.
    expected_body_sections:
      - Regulation Summary
      - Applicability
      - Key Requirements
      - Compliance Obligations
      - Penalties and Enforcement
      - Source References
    change_cadence: as-amended

  - id: rule
    name: Business Rule
    id_prefix: RUL
    description: >
      Discrete, testable business logic statements that govern decisions,
      validations, calculations, or routing within a process.
    expected_body_sections:
      - Rule Statement
      - Conditions
      - Actions
      - Exceptions
      - Examples
      - Source Authority
    change_cadence: quarterly

  - id: data-dictionary
    name: Data Dictionary
    id_prefix: DAT
    description: >
      Definitions, formats, valid ranges, and lineage for data elements
      used within a domain or process.
    expected_body_sections:
      - Overview
      - Field Definitions
      - Valid Values
      - Data Lineage
      - Validation Rules
      - Related Systems
    change_cadence: semi-annual

  - id: system
    name: System Reference
    id_prefix: SYS
    description: >
      Technical documentation for systems, APIs, integrations, and
      infrastructure that support business processes.
    expected_body_sections:
      - System Overview
      - Capabilities
      - Interfaces and APIs
      - Data Flows
      - Dependencies
      - SLA and Availability
    change_cadence: semi-annual

  - id: training
    name: Training Material
    id_prefix: TRN
    description: >
      Educational content, guides, and reference material used for
      onboarding, upskilling, or certification.
    expected_body_sections:
      - Learning Objectives
      - Prerequisites
      - Content
      - Exercises
      - Assessment Criteria
      - References
    change_cadence: annual

  - id: glossary
    name: Glossary
    id_prefix: GLO
    description: >
      Domain-specific terminology definitions providing a shared vocabulary
      across teams and documents.
    expected_body_sections:
      - Scope
      - Terms and Definitions
      - Abbreviations
      - Related Glossaries
    change_cadence: semi-annual

status_lifecycle:
  description: >
    Corpus documents progress through a linear lifecycle.
    Only 'current' documents are authoritative for intent generation.
  states:
    - id: draft
      description: Initial authoring; not yet reviewed or approved.
      allowed_transitions: [review]

    - id: review
      description: Under review by subject-matter experts or compliance.
      allowed_transitions: [draft, current]

    - id: current
      description: Active, authoritative version used in intent generation.
      allowed_transitions: [superseded, archived]

    - id: superseded
      description: Replaced by a newer version; retained for audit trail.
      allowed_transitions: [archived]

    - id: archived
      description: No longer in use; preserved for historical reference only.
      allowed_transitions: []

  flow: "draft -> review -> current -> superseded -> archived"
```

---

## 5. Knowledge Corpus Specification

### 5.1 Corpus Structure

- **Location:** `corpus/` directory in the engine repository
- **Index:** `corpus/corpus.config.yaml` -- auto-generated by scanning `corpus/**/*.corpus.md`
- **File format:** `.corpus.md` -- Markdown with YAML frontmatter conforming to `schemas/corpus-document.schema.json`

**8 subdirectories** (one per `doc_type`):

| Directory | doc_type | Count |
|-----------|----------|-------|
| `procedures/` | procedure | 15 |
| `policies/` | policy | 6 |
| `regulations/` | regulation | 7 |
| `rules/` | rule | 7 |
| `data-dictionary/` | data-dictionary | 4 |
| `systems/` | system | 5 |
| `training/` | training | 1 |
| `glossary/` | glossary | 1 |
| **Total** | | **46** |

### 5.2 Corpus Document Format

Every `.corpus.md` file has this structure:

```yaml
---
corpus_id: "CRP-{TYPE_PREFIX}-{DOMAIN}-{SEQ}"
title: "Human-Readable Title"
slug: "url-friendly-slug"
doc_type: "procedure"                    # one of 8 types
domain: "Mortgage Lending"
subdomain: "Loan Origination"
tags:
  - "tag-one"
  - "tag-two"
applies_to:
  process_ids:
    - "Process_LoanOrigination"
  task_types:
    - "userTask"
    - "serviceTask"
  task_name_patterns:
    - "receive.*application"
    - "intake.*loan"
  goal_types:
    - "data_production"
    - "state_transition"
  roles:
    - "loan_officer"
    - "loan_processor"
version: "1.0"
status: "current"                        # draft | review | current | superseded | archived
effective_date: "2025-06-01"
review_date: "2026-06-01"
supersedes: null
superseded_by: null
author: "Operations Standards Committee"
last_modified: "2025-05-20"
last_modified_by: "R. Caruso"
source: "internal"                       # internal | external | regulatory
source_ref: "SOP-LO-2025-001"
related_corpus_ids:
  - "CRP-PRC-MTG-002"
  - "CRP-RUL-MTG-002"
regulation_refs:
  - "TILA-RESPA Integrated Disclosure Rule (TRID)"
policy_refs:
  - "POL-LO-001"
---

# Document Title

## Purpose
...

## Scope
...

(body sections per doc_type's expected_body_sections from corpus-taxonomy.yaml)
```

### 5.3 Corpus Index Format (corpus.config.yaml)

```yaml
# MDA Intent Layer -- Knowledge Corpus Index
# Auto-generated from corpus document frontmatter
# Regenerate by scanning corpus/**/*.corpus.md

version: "1.0"
generated_date: "2026-04-09"
document_count: 46

documents:
  - corpus_id: "CRP-PRC-MTG-001"
    title: "Loan Application Intake Procedure"
    doc_type: "procedure"
    domain: "Mortgage Lending"
    subdomain: "Loan Origination"
    path: "procedures/loan-application-intake.corpus.md"
    tags:
      - "loan-application"
      - "intake"
    applies_to:
      process_ids:
        - "Process_LoanOrigination"
      task_name_patterns:
        - "receive.*application"
      task_types:
        - "userTask"
      goal_types:
        - "data_production"
      roles:
        - "loan_officer"
    status: "current"

  # ... (one entry per document, 46 total)
```

Each entry in the `documents` array mirrors the frontmatter of the corresponding `.corpus.md` file, plus a `path` field indicating the relative path within `corpus/`.

### 5.4 Enrichment Matching Algorithm

The corpus enricher uses a multi-factor scoring algorithm to match BPMN nodes to corpus documents. For each node, every corpus document is scored independently.

**Scoring factors (applied in order, highest score wins):**

| Factor | Score | Condition |
|--------|-------|-----------|
| Exact ID match | 1.0 | `applies_to.process_ids` contains the current `process_id` AND at least one `applies_to.task_name_patterns` regex matches the node's `bpmn_task_name` |
| Name pattern match | 0.8 | `applies_to.task_name_patterns` regex matches `bpmn_task_name`, regardless of `process_id` |
| Domain + task type match | 0.5 | Corpus doc's `domain` matches the process domain AND `applies_to.task_types` includes the node's element type |
| Tag intersection | 0.3 | Tokens extracted from the node's `bpmn_task_name` (split on spaces, hyphens, underscores, lowercased) overlap with the corpus doc's `tags` array |
| Role match (bonus) | +0.1 | The node's lane name (resolved to `owner_role`) appears in `applies_to.roles`. This is additive on top of any other score. |

**Threshold:** A document is considered a match if its total score is >= 0.3.

**Confidence mapping:**
- Score >= 0.8: `high`
- Score >= 0.5: `medium`
- Score >= 0.3: `low`

**Match method recording:**
- Score 1.0: `"exact_id"`
- Score 0.8: `"name_pattern"`
- Score 0.5: `"domain_type"`
- Score 0.3: `"tag_intersection"`

### 5.5 Demo Corpus Inventory

All 46 corpus documents organized by type:

**Procedures (15 documents):**

| corpus_id | Title | Processes |
|-----------|-------|-----------|
| CRP-PRC-MTG-001 | Loan Application Intake Procedure | Loan Origination |
| CRP-PRC-MTG-002 | Identity Verification Procedure (KYC/BSA) | Loan Origination |
| CRP-PRC-MTG-003 | Credit Report Ordering and Review Procedure | Loan Origination |
| CRP-PRC-MTG-004 | DTI Ratio Assessment Procedure | Loan Origination |
| CRP-PRC-MTG-005 | Document Request and Follow-Up Procedure | Loan Origination |
| CRP-PRC-MTG-006 | Loan File Packaging Procedure | Loan Origination |
| CRP-PRC-MTG-007 | Underwriting Submission Procedure | Loan Origination |
| CRP-PRC-IV-001 | W-2 Income Verification Procedure | Income Verification |
| CRP-PRC-IV-002 | Self-Employment Income Verification Procedure | Income Verification |
| CRP-PRC-IV-003 | Qualifying Income Calculation Procedure | Income Verification |
| CRP-PRC-PA-001 | Appraisal Ordering Procedure | Property Appraisal |
| CRP-PRC-PA-002 | Appraisal Report Review Procedure | Property Appraisal |
| CRP-PRC-PA-003 | Property Value Assessment Procedure | Property Appraisal |
| CRP-PRC-PA-004 | Appraisal Revision Request Procedure | Property Appraisal |
| CRP-PRC-PA-005 | Appraisal Manual Review Procedure | Property Appraisal |

**Policies (6 documents):**

| corpus_id | Title | Processes |
|-----------|-------|-----------|
| CRP-POL-MTG-001 | Credit Report Ordering Policy | Loan Origination |
| CRP-POL-MTG-002 | Permissible Purpose Policy (FCRA Compliance) | Loan Origination |
| CRP-POL-MTG-010 | General Document Retention Policy | All processes |
| CRP-POL-IV-001 | W-2 Income Verification Policy | Income Verification |
| CRP-POL-PA-001 | Appraisal Ordering Policy | Property Appraisal |
| CRP-POL-PA-002 | AMC Selection and Rotation Policy | Property Appraisal |

**Regulations (7 documents):**

| corpus_id | Title | Processes |
|-----------|-------|-----------|
| CRP-REG-MTG-001 | Fair Credit Reporting Act (FCRA) / Regulation V Summary | Loan Origination |
| CRP-REG-MTG-002 | Truth in Lending Act (TILA) / Regulation Z Summary | Loan Origination |
| CRP-REG-MTG-003 | Equal Credit Opportunity Act (ECOA) / Regulation B Summary | Loan Origination, Income Verification |
| CRP-REG-IV-001 | Fannie Mae Selling Guide B3-3.1 (Income Assessment) Summary | Income Verification |
| CRP-REG-IV-002 | FHA 4000.1 Income Requirements Summary | Income Verification |
| CRP-REG-PA-001 | USPAP Standards Summary | Property Appraisal |
| CRP-REG-PA-002 | Appraiser Independence Requirements (Dodd-Frank Section 1472) | Property Appraisal |

**Rules (7 documents):**

| corpus_id | Title | Processes |
|-----------|-------|-----------|
| CRP-RUL-MTG-001 | Loan Eligibility Decision Matrix | Loan Origination |
| CRP-RUL-MTG-002 | Document Completeness Checklist | Loan Origination |
| CRP-RUL-MTG-003 | DTI Threshold Rules by Loan Program | Loan Origination |
| CRP-RUL-IV-001 | Employment Type Classification Rules | Income Verification |
| CRP-RUL-IV-002 | Income Variance Threshold Rules | Income Verification |
| CRP-RUL-PA-001 | Appraisal Completeness Checklist | Property Appraisal |
| CRP-RUL-PA-002 | LTV Threshold Rules by Loan Program | Property Appraisal |

**Data Dictionaries (4 documents):**

| corpus_id | Title | Processes |
|-----------|-------|-----------|
| CRP-DAT-MTG-001 | Loan Application Data Object | Loan Origination |
| CRP-DAT-MTG-002 | Credit Report Data Object | Loan Origination |
| CRP-DAT-IV-001 | Income Verification Data Objects | Income Verification |
| CRP-DAT-PA-001 | Appraisal Report Data Object | Property Appraisal |

**Systems (5 documents):**

| corpus_id | Title | Processes |
|-----------|-------|-----------|
| CRP-SYS-MTG-001 | LOS (Loan Origination System) Integration Guide | All processes |
| CRP-SYS-MTG-002 | DocVault Integration Guide | Income Verification, Property Appraisal |
| CRP-SYS-MTG-003 | Event Bus Integration Guide | All processes |
| CRP-SYS-IV-002 | IVES (IRS Income Verification Express Service) Guide | Income Verification |
| CRP-SYS-PA-001 | Appraisal Portal Integration Guide | Property Appraisal |

**Training (1 document):**

| corpus_id | Title | Processes |
|-----------|-------|-----------|
| CRP-TRN-MTG-001 | Loan Processor Onboarding Guide | All processes |

**Glossary (1 document):**

| corpus_id | Title | Processes |
|-----------|-------|-----------|
| CRP-GLO-MTG-001 | Mortgage Lending Glossary | All processes |

---

## 6. Pipeline Stages (Complete)

### 6.1 Stage 1: BPMN Parser

**Input:** BPMN 2.0 XML file
**Output:** ParsedModel (structured YAML or JSON)

#### BPMN Namespace

```
http://www.omg.org/spec/BPMN/20100524/MODEL
```

The parser must validate the XML against this namespace. If the namespace is missing or the XML is malformed, halt with error `PARSE_ERR_MALFORMED_XML` and include the parser error message.

#### Process Metadata Extraction

For each `<bpmn:process>` or `<bpmn:participant>` element, extract:

| Field | Source |
|-------|--------|
| `process_id` | `<process id="...">` attribute |
| `process_name` | `<process name="...">` attribute |
| `is_executable` | `<process isExecutable="...">` attribute |
| `participant_id` | `<participant id="...">` in the collaboration |
| `participant_name` | `<participant name="...">` in the collaboration |

If a collaboration element exists, map participants to their processes via `processRef`.

#### Node Extraction

For every element listed in `ontology/bpmn-element-mapping.yaml`, extract:

| Field | Description |
|-------|-------------|
| `id` | The element's `id` attribute |
| `name` | The element's `name` attribute (may be null) |
| `type` | The BPMN element type (e.g., `userTask`, `exclusiveGateway`, `startEvent`) |
| `lane` | The lane ID containing this element (resolved from `<laneSet>`) |
| `incoming` | Array of incoming sequence flow IDs |
| `outgoing` | Array of outgoing sequence flow IDs |
| `boundary_events` | Array of boundary event IDs attached to this element (`attachedToRef`) |
| `documentation` | Contents of any `<bpmn:documentation>` child element |
| `attributes` | Map of additional element-specific attributes (e.g., `implementation`, `scriptFormat`, `calledElement`) |

For gateways, also extract:
- `gateway_direction` (converging, diverging, mixed, unspecified)
- `default` flow ID if present

For events, also extract:
- `event_definitions` -- array of event definition types (e.g., `timerEventDefinition`, `errorEventDefinition`, `messageEventDefinition`) with their attributes

#### Edge Extraction

For each `<bpmn:sequenceFlow>`:

| Field | Description |
|-------|-------------|
| `id` | The flow's `id` attribute |
| `name` | The flow's `name` attribute (may be null) |
| `source` | `sourceRef` attribute -- the originating node ID |
| `target` | `targetRef` attribute -- the destination node ID |
| `condition_expression` | Contents of `<bpmn:conditionExpression>` child, if present |

#### Lane Extraction

From each `<bpmn:laneSet>`:

| Field | Description |
|-------|-------------|
| `lane_id` | The lane's `id` attribute |
| `lane_name` | The lane's `name` attribute |
| `flow_node_refs` | Array of node IDs belonging to this lane |

#### Data Object and Data Store Extraction

For each `<bpmn:dataObjectReference>` and `<bpmn:dataStoreReference>`:

| Field | Description |
|-------|-------------|
| `id` | Reference ID |
| `name` | Reference name |
| `type` | `dataObject` or `dataStore` |
| `item_subject_ref` | The `itemSubjectRef` if defined |

Also extract `<bpmn:dataInputAssociation>` and `<bpmn:dataOutputAssociation>` to build data flow connections between tasks and data objects.

#### Message Flow Extraction

For each `<bpmn:messageFlow>` (from the collaboration):

| Field | Description |
|-------|-------------|
| `id` | Flow ID |
| `name` | Flow name |
| `source` | `sourceRef` -- may be a task or participant |
| `target` | `targetRef` -- may be a task or participant |
| `message_ref` | Reference to a `<bpmn:message>` element if present |

#### Output Shape

```yaml
mda_parsed_model:
  source_file: "<filename>"
  parse_date: "<ISO 8601 timestamp>"
  bpmn_version: "2.0"

  processes:
    - process_id: "..."
      process_name: "..."
      is_executable: true
      participant_id: "..."
      participant_name: "..."

  nodes:
    - id: "..."
      name: "..."
      type: "userTask"
      lane: "..."
      incoming: ["flow_1"]
      outgoing: ["flow_2"]
      boundary_events: []
      documentation: "..."
      attributes: {}

  edges:
    - id: "..."
      name: null
      source: "..."
      target: "..."
      condition_expression: null

  lanes:
    - lane_id: "..."
      lane_name: "..."
      flow_node_refs: ["node_1", "node_2"]

  data_objects:
    - id: "..."
      name: "..."
      type: "dataObject"
      item_subject_ref: null

  data_stores:
    - id: "..."
      name: "..."
      type: "dataStore"

  data_associations:
    - task_id: "..."
      data_ref: "..."
      direction: "input"    # or "output"

  message_flows:
    - id: "..."
      name: "..."
      source: "..."
      target: "..."
      message_ref: null
```

#### Error Handling

| Condition | Action |
|-----------|--------|
| XML is not well-formed | Halt. Report `PARSE_ERR_MALFORMED_XML` with line/column. |
| XML is well-formed but not valid BPMN 2.0 | Halt. Report `PARSE_ERR_INVALID_BPMN` with details. |
| Element has no `id` attribute | Generate a synthetic ID (`_synthetic_{type}_{n}`), add a warning. |
| Element has no `name` attribute | Set `name` to `null`. Not an error. |
| Unknown element type not in the mapping table | Include it with `type: "unknown"` and add a warning. Do not halt. |
| Sequence flow references a non-existent node | Include the edge but add a warning with the dangling reference. |
| Multiple processes in one file | Parse all processes. Downstream stages handle them individually. |

#### Output Validation

Before completing, verify:

1. Every node ID referenced by an edge exists in the nodes array (warn if not)
2. Every node has at least one incoming or outgoing flow (except start/end events)
3. Lane references resolve to actual node IDs
4. No duplicate IDs exist in any array

### 6.2 Stage 2: Corpus Enricher

**Input:** ParsedModel (from Stage 1) + corpus index (`corpus/corpus.config.yaml`)
**Output:** EnrichedModel with per-node enrichments + consolidated gap list

#### Enrichment Process

For each node in the parsed model's `nodes` array, perform the following enrichment checks and attach the results as an `enrichment` object on the node.

#### Enrichment Categories

**1. Procedure Lookup**

Search the knowledge corpus for procedure documents matching the node using the multi-factor scoring algorithm (Section 5.4). Filter corpus documents where `doc_type` is `procedure`.

Record:
```yaml
enrichment:
  procedure:
    found: true | false
    corpus_refs:
      - corpus_id: "CRP-PRC-INC-001"
        match_confidence: high | medium | low
        match_score: 0.9
    match_method: "exact_id" | "name_pattern" | "domain_type" | "tag_intersection"
```

**2. Ownership Resolution**

Determine task ownership from (in priority order):
1. Lane assignment from parsed model (`node.lane` -> resolve lane name)
2. Participant from process/collaboration metadata
3. Organizational mapping in the KB (department -> role)

Record:
```yaml
enrichment:
  ownership:
    resolved: true | false
    owner_role: "Senior Underwriter"
    owner_team: "Credit Risk"
    source: "lane" | "participant" | "kb_mapping"
```

**3. Decision Rule Resolution**

For gateway nodes and `businessRuleTask` nodes. Sources:
1. Condition expressions on outgoing sequence flows
2. DMN references in BPMN element attributes
3. Business rule documents in the KB

Record:
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

**4. Data Schema Resolution**

For each data object/store referenced by the node via `data_associations`. Sources:
1. `itemSubjectRef` from the BPMN data object
2. Enterprise data catalog
3. Schema files in the repository

Record:
```yaml
enrichment:
  data_schemas:
    - data_ref: "DataObject_1"
      schema_found: true | false
      schema_ref: "schemas/loan-application.json"
      direction: "input" | "output"
```

**5. Regulatory Context**

Check for applicable regulations and policies using the same multi-factor scoring algorithm, filtering on `doc_type` values of `regulation` and `policy`.

Record:
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

**6. Integration Binding Check**

Check for known system integrations. Sources:
1. BPMN element `implementation` attribute
2. Enterprise API registry
3. Integration documentation in the KB

Record:
```yaml
enrichment:
  integration:
    has_binding: true | false
    system_name: "LOS"
    protocol: "rest"
    endpoint_hint: "/api/v2/applications/{id}/income"
```

#### Gap Types

For every missing or incomplete enrichment result, create a gap record:

| gap_type | Default severity | Trigger |
|----------|-----------------|---------|
| `missing_procedure` | high | No procedure found for an executable task |
| `missing_owner` | high | No lane assignment and no ownership mapping |
| `missing_decision_rules` | critical | Gateway has no condition expressions or rule references |
| `missing_data_schema` | medium | Data object referenced but no schema exists |
| `missing_regulatory_context` | low | Domain suggests regulation but no refs found |
| `missing_integration_binding` | medium | Service/send/receive task with no integration info |
| `ambiguous_name` | low | Task name is generic (e.g., "Process", "Handle", "Check") |
| `unnamed_element` | medium | Element has `name: null` |

Severity may be adjusted based on context (e.g., `missing_procedure` on a `manualTask` in a non-critical lane may be downgraded to `medium`).

Each gap record includes:

| Field | Description |
|-------|-------------|
| `gap_id` | Auto-generated: `GAP-{node_id}-{n}` |
| `node_id` | The BPMN node this gap applies to |
| `gap_type` | Category from table above |
| `severity` | `critical`, `high`, `medium`, or `low` |
| `description` | Human-readable explanation of what is missing |
| `suggested_resolution` | Recommended action to resolve the gap |

#### Output Shape

```yaml
mda_enriched_model:
  source_model: "<reference to Stage 1 output>"
  enrichment_date: "<ISO 8601 timestamp>"
  enriched_by: "<tool or person>"

  # Original parsed model fields preserved unchanged
  # Each node now has an enrichment object attached

  gaps:
    - gap_id: "GAP-Task_1-001"
      node_id: "Task_1"
      gap_type: "missing_procedure"
      severity: "high"
      description: "No procedure document found for 'Verify Borrower Income'"
      suggested_resolution: "Create work instruction covering income verification steps"

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

**Important notes:**
- Gaps are informational, not blocking. Downstream stages use them to populate the `gaps` array in generated triples.
- The enricher reads the corpus index for candidate filtering, then loads the full `.corpus.md` file only for matched documents.

### 6.3 Stage 3: Capsule Generator

**Input:** EnrichedModel (from Stage 2) + corpus documents
**Output:** `.cap.md` files (one per capsule-eligible BPMN element)

#### Capsule Eligibility

Consult `ontology/bpmn-element-mapping.yaml`. Elements with `generates_capsule: true` produce capsules. This includes:
- All 10 task types
- 4 gateway types (exclusive, inclusive, parallel, event-based)
- 5 event types (start, end, intermediate catch, intermediate throw, boundary)

#### ID Generation

```
CAP-{process_code}-{category_code}-{sequence_number}
```

The same stem (`{process_code}-{category_code}-{sequence_number}`) is reused for the paired intent spec (`INT-...`) and contract (`ICT-...`).

Category code derivation: Map keywords in the task name to 3-letter codes using the standard_codes table from `ontology/id-conventions.yaml`.

#### Frontmatter Population

| Frontmatter field | Source |
|-------------------|--------|
| `capsule_id` | Generated ID |
| `bpmn_task_id` | `node.id` |
| `bpmn_task_name` | `node.name` |
| `bpmn_task_type` | `node.type` |
| `process_id` | From process metadata |
| `process_name` | From process metadata |
| `version` | `"1.0"` (initial generation) |
| `status` | `"draft"` |
| `generated_from` | Source BPMN filename |
| `generated_date` | Current ISO 8601 timestamp |
| `generated_by` | Tool or agent identifier |
| `last_modified` | Same as `generated_date` |
| `last_modified_by` | Same as `generated_by` |
| `owner_role` | `enrichment.ownership.owner_role` (or null) |
| `owner_team` | `enrichment.ownership.owner_team` (or null) |
| `domain` | Derived from process/lane context |
| `subdomain` | Derived from task functional area |
| `regulation_refs` | `enrichment.regulatory.regulation_refs` (or empty array) |
| `policy_refs` | `enrichment.regulatory.policy_refs` (or empty array) |
| `intent_id` | `INT-{same stem}` |
| `contract_id` | `ICT-{same stem}` |
| `parent_capsule_id` | Set if this node is inside a sub-process |
| `predecessor_ids` | Capsule IDs of nodes connected via incoming sequence flows |
| `successor_ids` | Capsule IDs of nodes connected via outgoing sequence flows |
| `exception_ids` | Capsule IDs of boundary event capsules attached to this node |
| `gaps` | Gap entries from enrichment that apply to this node |
| `corpus_refs` | Corpus document references with section and match confidence |

#### Markdown Body Sections

1. **Purpose** -- Derived from task name and process position
2. **Procedure** -- From highest-confidence `doc_type: procedure` corpus match; placeholder with gap note if none found
3. **Business Rules** -- From `enrichment.decision_rules` and matched `doc_type: rule` corpus docs; "No business rules apply" if not a decision node
4. **Inputs Required** -- Table of data inputs from BPMN data associations and predecessor outputs
5. **Outputs Produced** -- Table of data outputs
6. **Exception Handling** -- From boundary events; "No boundary events attached" if none
7. **Regulatory Context** -- From matched `doc_type: regulation` corpus docs
8. **Notes** -- Lower-confidence matches listed as "See also"

#### Corpus-to-Capsule Content Flow

1. **Procedure section:** Highest-confidence `procedure` match -> extract numbered steps
2. **Business Rules section:** Matched `rule` corpus docs -> extract decision tables
3. **Regulatory Context section:** Matched `regulation` corpus docs -> extract key requirements, cite corpus_id
4. **Inputs/Outputs tables:** Matched `data-dictionary` corpus docs -> resolve field names and types
5. **Exception Handling:** BPMN boundary events + procedural exception handling from corpus

#### LLM Mode vs Skip-LLM Mode

- **LLM mode:** Reads matched corpus documents, generates body sections via LLM call
- **Skip-LLM mode:** Template stubs with TODO markers in each section

#### Special Cases

**Sub-Process Handling:**
1. Create parent capsule for the sub-process with `bpmn_task_type: subProcess`
2. Create child capsules for each task inside
3. Set `parent_capsule_id` on each child
4. Parent's procedure section describes overall sub-process flow
5. Child `predecessor_ids`/`successor_ids` reference other children (internal flow)

**Parallel Gateway Handling:**
- Capsule only (no intent spec per `bpmn-element-mapping.yaml`)
- Purpose describes fork/join semantics
- `successor_ids` lists all parallel branches

**Boundary Event Handling:**
- Produces exception capsules
- `parent_capsule_id` is the task the event is attached to
- Parent's `exception_ids` includes the exception capsule's ID

**Gateway-Only Capsules (exclusive/inclusive):**
- Business Rules section populated with condition expressions from outgoing flows
- No procedure section (replaced with "Decision logic is defined in Business Rules below")

#### Output File Naming

```
triples/{process_id}/{capsule_id}.cap.md
```

#### Validation Before Output

1. `capsule_id` matches `^CAP-[A-Z]{2,3}-[A-Z]{3}-\d{3}$`
2. All required frontmatter fields present per `schemas/capsule.schema.json`
3. `intent_id` and `contract_id` use the same ID stem
4. `predecessor_ids` and `successor_ids` reference valid capsule IDs
5. YAML frontmatter parses without error

### 6.4 Stage 4: Intent Generator

**Input:** EnrichedModel (from Stage 2) + capsules (from Stage 3)
**Output:** `.intent.md` files (one per intent-eligible BPMN element)

#### Intent Eligibility

Elements with `generates_intent: true` in `bpmn-element-mapping.yaml`. Notably, `parallelGateway` has `generates_intent: false`.

#### ID Generation

Same stem as paired capsule: `INT-{process_code}-{category_code}-{sequence_number}`

#### Goal Derivation

The `goal` field is a single sentence describing the outcome. Derived from:
1. Task name (primary)
2. Process context (predecessors and successors)
3. Capsule's Purpose section

#### Goal Type Assignment

Look up `default_goal_type` from `bpmn-element-mapping.yaml`:

| goal_type | Typical elements |
|-----------|-----------------|
| `data_production` | serviceTask, scriptTask, userTask, manualTask |
| `decision` | businessRuleTask, exclusiveGateway, inclusiveGateway, eventBasedGateway |
| `notification` | sendTask, intermediateThrowEvent |
| `state_transition` | receiveTask, startEvent, endEvent, intermediateCatchEvent |
| `orchestration` | callActivity, subProcess |

Override if enrichment data clearly indicates a different type.

#### Mandatory Forbidden Actions

Every intent spec must include in `execution_hints.forbidden_actions`:

```yaml
execution_hints:
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"
```

Additional forbidden actions may be added per context (e.g., `"direct_database_write"`).

#### Execution Boundaries

| Field | Default value |
|-------|---------------|
| `contract_ref` | `ICT-{same stem}` |
| `idempotency` | `"safe"` if re-execution produces same result; `"unsafe"` otherwise |
| `retry_policy` | `"exponential_backoff_3x"` (adjust per task type) |
| `timeout_seconds` | 300 for service tasks, 86400 for user tasks |
| `mda_layer` | Always `"PIM"` |

#### Markdown Body Sections

1. **Outcome Statement** -- Paragraph describing what successful execution looks like
2. **Outcome Contract** -- Prose summary of inputs, outputs, and invariants
3. **Reasoning Guidance** -- Step-by-step logical guidance for the executing agent
4. **Anti-Patterns** -- Explicit list of what the agent must NOT do (always includes Anti-UI)
5. **Paired Capsule** -- Reference to the capsule
6. **Paired Integration Contract** -- Reference to the contract

#### Special Cases

**Blocked Intent Specs:** If a task requires UI interaction and no API exists:
- Set `status: "draft"` with a critical gap
- Gap type: `"missing_integration_binding"`, severity: `"critical"`
- Reasoning Guidance: "This intent is blocked pending API availability. See gaps."

**Gateway Intent Specs:**
- `goal_type: "decision"`
- Inputs are the data points the decision evaluates
- Outputs are the decision result and selected path

**Sub-Process Intent Specs:**
- `goal_type: "orchestration"`
- Inputs/outputs are sub-process boundary data
- Reasoning Guidance describes coordination of child tasks

#### Output File Naming

```
triples/{process_id}/{intent_id}.intent.md
```

#### Validation Before Output

1. `intent_id` matches `^INT-[A-Z]{2,3}-[A-Z]{3}-\d{3}$`
2. All required frontmatter fields present per `schemas/intent.schema.json`
3. `capsule_id` references an existing capsule from Stage 3
4. `contract_ref` uses the same ID stem
5. `goal_type` is one of the five allowed values
6. At least one input and one output defined (or gaps recorded)
7. `forbidden_actions` includes the four mandatory anti-UI entries
8. YAML frontmatter parses without error

### 6.5 Stage 5: Contract Generator

**Input:** EnrichedModel (from Stage 2) + intent specs (from Stage 4)
**Output:** `.contract.md` files (one per contract-eligible BPMN element)

#### Contract Eligibility

Every node that produced an intent spec in Stage 4 also produces a contract.

#### ID Generation

Same stem: `ICT-{process_code}-{category_code}-{sequence_number}`

#### Source Resolution

For each `input` in the paired intent spec, attempt to bind to a concrete data source:

```yaml
sources:
  - name: "Tax Return Data"
    protocol: rest            # rest | grpc | graphql | soap | jdbc | file | message_queue
    endpoint: "https://api.internal/v2/tax-returns/{ssn}"
    auth: "oauth2"
    schema_ref: "schemas/tax-return-response.json"
    sla_ms: 2000
```

If not found, add the input name to `unbound_sources`.

#### Sink Resolution

For each `output` in the paired intent spec, attempt to bind to a concrete data sink:

```yaml
sinks:
  - name: "Verified Income Record"
    protocol: rest
    endpoint: "https://api.internal/v2/income-verification"
    auth: "oauth2"
    schema_ref: "schemas/income-record.json"
    sla_ms: 1000
    idempotency_key: "application_id + verification_date"
```

If not found, add to `unbound_sinks`.

#### Event Definition

For notifications, state changes, and inter-process signals:

```yaml
events:
  - topic: "loan.income.verified"
    schema_ref: "schemas/events/income-verified.json"
    delivery: at_least_once     # at_least_once | at_most_once | exactly_once
    key_field: "application_id"
```

#### Rule Engine Definition

If the paired intent involves decision logic and a rule engine is available:

```yaml
rule_engines:
  - name: "DTI Threshold Engine"
    version: "2.1"
    endpoint: "https://rules.internal/v1/dti-check"
```

#### Audit Requirements

Default retention periods by domain:

| Domain | Default retention |
|--------|------------------|
| Financial / lending | 7 years |
| Healthcare | 10 years |
| General business | 3 years |
| Compliance-critical | 10 years |

```yaml
audit:
  record_type: "income_verification_audit"
  retention_years: 7
  fields_required:
    - "application_id"
    - "agent_id"
    - "timestamp"
    - "input_hash"
    - "output_hash"
    - "decision_rationale"
  sink: "https://audit.internal/v1/records"
```

#### Binding Status

| Status | Condition |
|--------|-----------|
| `bound` | All sources and sinks resolved to concrete endpoints |
| `partial` | Some resolved, others in `unbound_*` arrays |
| `unbound` | No sources or sinks resolved |

#### Markdown Body Sections

1. **Binding Rationale** -- Explains integration decisions and lists unbound integrations
2. **Change Protocol** -- How changes to this contract should be managed (endpoint changes, schema changes, protocol changes, SLA changes)
3. **Decommissioning** -- Steps before decommissioning (verify no active references, ensure audit retention, notify consumers, deprecate then archive)

#### Demo / Greenfield Mode

When no enterprise API catalog exists:
1. Generate plausible REST endpoints based on task domain
2. Set `binding_status: "unbound"` regardless
3. Add a note in Binding Rationale that all endpoints are illustrative placeholders

#### Output File Naming

```
triples/{process_id}/{contract_id}.contract.md
```

#### Validation Before Output

1. `contract_id` matches `^ICT-[A-Z]{2,3}-[A-Z]{3}-\d{3}$`
2. All required frontmatter fields present per `schemas/contract.schema.json`
3. `intent_id` references an existing intent spec from Stage 4
4. ID stem matches across the triple (CAP/INT/ICT)
5. Every source and sink has at minimum `name`, `protocol`, `endpoint`
6. `binding_status` accurately reflects `unbound_sources`/`unbound_sinks` state
7. `mda_layer` is set to `"PSM"`
8. YAML frontmatter parses without error

### 6.6 Stage 6: Triple Validator

**Input:** Complete set of triples from Stages 3-5 + ParsedModel from Stage 1
**Output:** ValidationReport (pass/fail per triple, per process)

#### Per-Triple Checks (10 checks)

**Check 1: Triple Completeness**
All three files (capsule, intent, contract) must exist for each ID stem.
Exception: `parallelGateway` may have capsule only (PASS).

**Check 2: ID Convention Conformance**
Each ID must match its expected regex:
- Capsule: `^CAP-[A-Z]{2,3}-[A-Z]{3}-\d{3}$`
- Intent: `^INT-[A-Z]{2,3}-[A-Z]{3}-\d{3}$`
- Contract: `^ICT-[A-Z]{2,3}-[A-Z]{3}-\d{3}$`

**Check 3: ID Stem Consistency**
The process code, category code, and sequence number must be identical across the triple.

**Check 4: Cross-Reference Integrity**
Verify bidirectional consistency:
- `capsule.intent_id == intent.intent_id`
- `capsule.contract_id == contract.contract_id`
- `intent.capsule_id == capsule.capsule_id`
- `intent.contract_ref == contract.contract_id`
- `contract.intent_id == intent.intent_id`

**Check 5: Status Consistency**
All three files must have the same `status` value.

**Check 6: Version Consistency**
All three files must have the same `version` value.

**Check 7: Required Fields for Status**
Cross-reference current `status` against `ontology/status-lifecycle.yaml`. Verify all `required_fields` for that status level are populated.

**Check 8: Schema Validation**
Parse YAML frontmatter; validate against the corresponding JSON Schema:
- `.cap.md` -> `schemas/capsule.schema.json`
- `.intent.md` -> `schemas/intent.schema.json`
- `.contract.md` -> `schemas/contract.schema.json`

**Check 9: Gap Entry Completeness**
For every entry in the `gaps` array, verify:
- `type` is a non-empty string
- `description` is a non-empty string
- `severity` is one of: `critical`, `high`, `medium`, `low`

**Check 10: Anti-UI Compliance**
Verify that every intent spec's `execution_hints.forbidden_actions` includes the four mandatory entries: `browser_automation`, `screen_scraping`, `ui_click`, `rpa_style_macros`.

#### Per-Process Checks (7 checks)

**Check 11: BPMN Coverage**
Every capsule-eligible BPMN task must have exactly one triple. FAIL on missing or duplicate.

**Check 12: Process Graph Connectivity**
All capsules must be reachable from the start event capsule via `predecessor_ids`/`successor_ids`. FAIL on orphans.

**Check 13: Predecessor/Successor Reference Validity**
Every ID in `predecessor_ids` and `successor_ids` must reference an existing capsule ID. FAIL on dangling references.

**Check 14: Exception Reference Validity**
Every ID in `exception_ids` must reference an existing capsule ID.

**Check 15: Start and End Event Triples**
At least one triple must correspond to a start event and at least one to an end event for each process.

**Check 16: Circular Dependency Detection**
Walk the predecessor/successor graph and detect cycles. The capsule dependency graph must be a DAG. BPMN loops should be modeled with distinct capsules for each iteration entry, not as circular references.

**Check 17: Gap Tracking Completeness**
Every gap from the Stage 2 enriched model must appear in at least one triple's `gaps` array. No gap should be silently dropped.

#### Output Format

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
          result: PASS
        - check: "status_consistency"
          result: PASS
        - check: "version_consistency"
          result: PASS
        - check: "required_fields_for_status"
          result: PASS
        - check: "schema_validation"
          result: PASS
        - check: "gap_entry_completeness"
          result: PASS
        - check: "anti_ui_compliance"
          result: PASS

  per_process_results:
    - process_id: "Process_1"
      process_name: "Mortgage Origination"
      result: PASS | FAIL
      checks:
        - check: "bpmn_coverage"
          result: PASS
        - check: "graph_connectivity"
          result: PASS
        - check: "predecessor_successor_validity"
          result: PASS
        - check: "exception_reference_validity"
          result: PASS
        - check: "start_end_event_triples"
          result: PASS
        - check: "circular_dependency_detection"
          result: PASS
        - check: "gap_tracking_completeness"
          result: PASS

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
      description: "Resolve missing_decision_rules on exclusive gateway before advancing past draft"
    - severity: high
      description: "4 tasks lack ownership assignment. Review lane mappings in BPMN model"
```

#### Result Determination

- **Overall PASS:** All per-triple checks pass AND all per-process checks pass
- **Overall FAIL:** Any check fails

A FAIL result is not necessarily a broken pipeline -- gaps and draft status are expected on initial ingestion. The report prioritizes what needs human attention.

The validator is idempotent and can be re-run after addressing failures.

---

*Sections 7-12 (CLI Implementation, MkDocs Integration, Demo Data, Configuration, LLM Integration, File Formats) are specified in the second half of this document.*

## 7. CLI Specification

### 7.1 Entry Point

- **File**: `cli/mda.py`
- **Invocation**: `python cli/mda.py <command> [options]`
- **Global flags** (available on every command):

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--json` | bool flag | `false` | Emit all output as JSON (for machine consumption) |
| `-v` / `--verbose` | bool flag | `false` | Enable verbose/debug output |
| `--dry-run` | bool flag | `false` | Show what would be done without writing files |
| `--config <path>` | `Path` | auto-discovered | Explicit path to `mda.config.yaml` |

When `--json` is set, all output (success, error, status) is serialized through `output/json_output.py`. When unset, human-readable output goes through `output/console.py`.

Error handling: all command handlers are wrapped in a `try/except` in `main()`. Exceptions are routed to `output_json_error()` or `print_error()` depending on the `--json` flag. With `--verbose`, the full traceback is printed. `KeyboardInterrupt` exits with code 130.

### 7.2 Command Reference

---

#### 7.2.1 `init`

**Syntax**:
```
mda init <name> [--domain DOMAIN] [--prefix PREFIX] [--output-dir DIR]
```

| Argument/Option | Type | Required | Default | Description |
|-----------------|------|----------|---------|-------------|
| `name` | `str` | yes | -- | Process name (e.g., `income-verification`) |
| `--domain` | `str` | no | `None` | Business domain (e.g., `Mortgage Lending`) |
| `--prefix` | `str` | no | derived from name | 2-3 letter ID prefix (e.g., `IV`) |
| `--output-dir` | `Path` | no | `./<name>/` | Output directory for scaffolded repo |

**Behavior**: Creates a new process repository directory structure with `bpmn/`, `triples/`, `decisions/`, `graph/`, `gaps/`, `audit/` subdirectories, a starter `mda.config.yaml`, and a `README.md`. Does not use LLM.

**Uses LLM**: No

---

#### 7.2.2 `config`

**Syntax**:
```
mda config [--show] [--set KEY VALUE] [--get KEY] [--validate]
```

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--show` | bool flag | no | `true` (default action) | Display current merged config |
| `--set` | `(str, str)` | no | -- | Set a dotted key to a value (e.g., `llm.provider openai`) |
| `--get` | `str` | no | -- | Get a single dotted key value |
| `--validate` | bool flag | no | `false` | Validate config structure and paths |

**Behavior**: Reads the discovered `mda.config.yaml`, merges with defaults, applies env overrides. `--show` prints the full merged config. `--set` writes to the config file. `--get` prints a single value. `--validate` checks that all referenced paths exist and the LLM provider is recognized. Does not use LLM.

**Uses LLM**: No

---

#### 7.2.3 `parse`

**Syntax**:
```
mda parse <bpmn-file> [--output FILE] [--format {yaml,json}]
```

| Argument/Option | Type | Required | Default | Description |
|-----------------|------|----------|---------|-------------|
| `bpmn_file` | `Path` | yes | -- | Path to a BPMN 2.0 XML file |
| `--output` | `Path` | no | stdout | Output file for the parsed model |
| `--format` | `str` | no | `yaml` | Choices: `yaml`, `json` |

**Behavior**: Parses the BPMN XML using `mda_io/bpmn_xml.py::parse_bpmn()`, producing a `ParsedModel`. Serializes to YAML or JSON. This is Stage 1 only -- no enrichment, no LLM calls.

**Uses LLM**: No

---

#### 7.2.4 `ingest`

**Syntax**:
```
mda ingest <bpmn-file> [--skip-llm] [--stages STAGES] [--no-validate]
```

| Argument/Option | Type | Required | Default | Description |
|-----------------|------|----------|---------|-------------|
| `bpmn_file` | `Path` | yes | -- | Path to a BPMN 2.0 XML file |
| `--skip-llm` | bool flag | no | `false` | Skip all LLM calls; produce template stubs |
| `--stages` | `str` | no | `"1,2,3,4,5,6"` | Comma-separated stage numbers to run |
| `--no-validate` | bool flag | no | `false` | Skip Stage 6 validation |

**Behavior**: Runs the full 6-stage pipeline orchestrated by `pipeline/orchestrator.py`:
1. Parse BPMN XML into `ParsedModel`
2. Enrich with corpus matches, gap analysis (LLM-assisted disambiguation)
3. Generate knowledge capsules (LLM body generation)
4. Generate intent specifications (LLM frontmatter + body)
5. Generate integration contracts (LLM frontmatter + body)
6. Validate all artifacts against JSON schemas

When `--skip-llm` is set, stages 2-5 produce stub templates with empty body sections and minimal frontmatter. When `--stages` is provided, only those stages run (e.g., `--stages 1,2` runs parse + enrich only). `--no-validate` is equivalent to omitting stage 6 from `--stages`.

**Uses LLM**: Yes (stages 2-5, unless `--skip-llm`)

---

#### 7.2.5 `reingest`

**Syntax**:
```
mda reingest <bpmn-file> [--dry-run] [--force]
```

| Argument/Option | Type | Required | Default | Description |
|-----------------|------|----------|---------|-------------|
| `bpmn_file` | `Path` | yes | -- | Path to updated BPMN XML |
| `--force` | bool flag | no | `false` | Force full regeneration without diff analysis |

**Behavior**: Compares the new BPMN against the previously ingested model (stored in `audit/ingestion-log.yaml`). Identifies added, removed, and modified elements. Only regenerates triples for changed elements. With `--force`, regenerates everything. With `--dry-run` (global flag), shows the diff without writing files.

**Uses LLM**: Yes (for regenerated elements)

---

#### 7.2.6 `corpus index`

**Syntax**:
```
mda corpus index
```

No additional arguments.

**Behavior**: Scans all `.corpus.md` files under the configured corpus directory (`paths.corpus`). Reads frontmatter from each file and regenerates `corpus/corpus.config.yaml` with a `CorpusIndex` containing one `CorpusIndexEntry` per document.

**Uses LLM**: No

---

#### 7.2.7 `corpus add`

**Syntax**:
```
mda corpus add <type> [--domain DOMAIN] [--title TITLE]
```

| Argument/Option | Type | Required | Default | Description |
|-----------------|------|----------|---------|-------------|
| `type` | `str` | yes | -- | Choices: `procedure`, `policy`, `regulation`, `rule`, `data-dictionary`, `system`, `training`, `glossary` |
| `--domain` | `str` | no | from config `process.domain` | Document domain |
| `--title` | `str` | no | prompted interactively | Document title |

**Behavior**: Scaffolds a new `.corpus.md` file in the corpus directory with pre-populated frontmatter matching the chosen `doc_type`. Generates a `corpus_id` using the pattern `CRP-{DOMAIN_CODE}-{TYPE_CODE}-{SEQ}`. Writes body section guidance appropriate to the document type.

**Uses LLM**: No

---

#### 7.2.8 `corpus search`

**Syntax**:
```
mda corpus search <query> [--type TYPE] [--domain DOMAIN] [--tags TAGS] [--limit N]
```

| Argument/Option | Type | Required | Default | Description |
|-----------------|------|----------|---------|-------------|
| `query` | `str` | yes | -- | Search query (matched against title, corpus_id, domain, tags) |
| `--type` | `str` | no | `None` | Filter by `doc_type` |
| `--domain` | `str` | no | `None` | Filter by domain |
| `--tags` | `str` | no | `None` | Comma-separated tag filter (all must match) |
| `--limit` | `int` | no | `10` | Maximum results to return |

**Behavior**: Loads the corpus index from `corpus.config.yaml` and calls `CorpusIndex.search()`. Filters are applied as hard constraints; the query string is matched case-insensitively against `corpus_id`, `title`, `domain`, `subdomain`, and `tags`.

**Uses LLM**: No

---

#### 7.2.9 `corpus validate`

**Syntax**:
```
mda corpus validate
```

No additional arguments.

**Behavior**: Validates all `.corpus.md` files against `corpus-document.schema.json`. Reports validation errors per file.

**Uses LLM**: No

---

#### 7.2.10 `validate`

**Syntax**:
```
mda validate [path] [--fail-on {critical,high,medium,low}]
```

| Argument/Option | Type | Required | Default | Description |
|-----------------|------|----------|---------|-------------|
| `path` | `Path` | no | project root | Path to validate (file or directory) |
| `--fail-on` | `str` | no | `None` | Exit non-zero if any gap matches this severity or higher |

**Behavior**: Runs Stage 6 validation. If `path` is a directory, validates all triples and decisions within it. If `path` is a file, validates that single artifact. Checks:
- Frontmatter against JSON schemas (capsule, intent, contract, triple-manifest)
- Cross-reference consistency (capsule_id in intent matches, intent_id in contract matches)
- ID pattern compliance (`CAP-XX-XXX-NNN`, `INT-XX-XXX-NNN`, `ICT-XX-XXX-NNN`)
- Predecessor/successor chain integrity

When `--fail-on` is set, the CLI exits with code 1 if any validation finding has the specified severity or higher.

**Uses LLM**: No

---

#### 7.2.11 `status`

**Syntax**:
```
mda status [--process PROCESS_ID]
```

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--process` | `str` | no | from config | Filter by process ID |

**Behavior**: Scans `triples/` and `decisions/` directories and reads capsule frontmatter to produce a summary table showing each triple's name, BPMN type, status, binding status, and gap count. Displays aggregate statistics: total triples, counts by status, binding coverage percentage.

**Uses LLM**: No

---

#### 7.2.12 `gaps`

**Syntax**:
```
mda gaps [--severity {critical,high,medium,low}] [--type TYPE] [--process PROCESS_ID]
```

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--severity` | `str` | no | `None` | Filter gaps by severity |
| `--type` | `str` | no | `None` | Filter by gap type (e.g., `missing_procedure`) |
| `--process` | `str` | no | from config | Filter by process ID |

**Behavior**: Collects all gaps from two sources: (1) `gaps` arrays embedded in capsule frontmatter, and (2) standalone `GAP-*.md` files in the `gaps/` directory. Displays a sorted table (critical first). Shows aggregate counts by severity and type.

**Uses LLM**: No

---

#### 7.2.13 `graph`

**Syntax**:
```
mda graph [--format {yaml,mermaid,dot}] [--output FILE]
```

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--format` | `str` | no | `yaml` | Output format |
| `--output` | `Path` | no | stdout / `graph/` directory | Output file |

**Behavior**: Reads the parsed model (from previous ingestion or from BPMN file in config) and generates a process graph. The YAML format produces `process-graph.yaml`. The `mermaid` format produces a `graph-visual.md` with a fenced Mermaid flowchart. The `dot` format produces Graphviz DOT. Node shapes vary by element type: `(("..."))` for events, `["..."]` for tasks, `{"..."}` for gateways, `[("...")]` for data objects.

**Uses LLM**: No

---

#### 7.2.14 `enrich`

**Syntax**:
```
mda enrich <model> [--corpus-path DIR] [--output FILE]
```

| Argument/Option | Type | Required | Default | Description |
|-----------------|------|----------|---------|-------------|
| `model` | `Path` | yes | -- | Path to parsed model YAML or JSON |
| `--corpus-path` | `Path` | no | from config `paths.corpus` | Path to corpus directory |
| `--output` | `Path` | no | stdout | Output file for enriched model |

**Behavior**: Runs Stage 2 enrichment. Loads the parsed model, loads the corpus index, matches corpus documents to nodes using `applies_to` rules (process_ids, task_types, task_name_patterns, goal_types, roles). For ambiguous matches, calls the LLM with `build_disambiguation_prompt()` using `complete_structured()` against `DISAMBIGUATION_SCHEMA`. Produces an `EnrichedModel` with `NodeEnrichment` records and `Gap` records.

**Uses LLM**: Yes (for corpus disambiguation)

---

#### 7.2.15 `generate`

**Syntax**:
```
mda generate <type> [--enriched-model FILE] [--nodes NODE_IDS] [--force]
```

| Argument/Option | Type | Required | Default | Description |
|-----------------|------|----------|---------|-------------|
| `type` | `str` | yes | -- | Choices: `capsule`, `intent`, `contract`, `all` |
| `--enriched-model` | `Path` | no | auto-discovered | Path to enriched model file |
| `--nodes` | `str` | no | all nodes | Comma-separated BPMN node IDs to generate for |
| `--force` | bool flag | no | `false` | Overwrite existing triple files |

**Behavior**: Runs stages 3, 4, and/or 5 depending on `type`. When `type` is `all`, runs 3 then 4 then 5 in sequence. For each node:
- **capsule**: Generates frontmatter from enrichment data, calls LLM with `build_capsule_body_prompt()` for body, writes `{slug}.cap.md`
- **intent**: Calls LLM with `build_intent_frontmatter_prompt()` + `INTENT_FRONTMATTER_SCHEMA` for structured frontmatter, then `build_intent_body_prompt()` for body, writes `{slug}.intent.md`
- **contract**: Calls LLM with `build_contract_frontmatter_prompt()` + `CONTRACT_FRONTMATTER_SCHEMA` for structured frontmatter, then `build_contract_body_prompt()` for body, writes `{slug}.contract.md`

Also generates `triple.manifest.json` per triple and updates `triples/_manifest.json`. Skips nodes that already have files unless `--force` is set.

**Uses LLM**: Yes

---

#### 7.2.16 `review`

**Syntax**:
```
mda review <triple-path> [--aspect {completeness,accuracy,consistency,all}] [--output FILE]
```

| Argument/Option | Type | Required | Default | Description |
|-----------------|------|----------|---------|-------------|
| `triple_path` | `Path` | yes | -- | Path to a triple directory (e.g., `triples/verify-w2/`) |
| `--aspect` | `str` | no | `all` | Review aspect to focus on |
| `--output` | `Path` | no | stdout | Output file for findings |

**Behavior**: Reads all three files from the triple directory (`.cap.md`, `.intent.md`, `.contract.md`). Sends their content to the LLM with `build_review_prompt()` and receives structured findings via `complete_structured()` against `REVIEW_SCHEMA`. Reports findings with severity, aspect, file, and recommendation.

**Uses LLM**: Yes

---

#### 7.2.17 `docs`

**Syntax**:
```
mda docs generate
mda docs build
mda docs serve [--port N]
```

| Subcommand | Options | Description |
|------------|---------|-------------|
| `generate` | none | Create `mkdocs.yml` + `docs/` overlay |
| `build` | none | Generate + run `mkdocs build` for static HTML |
| `serve` | `--port` (int, default `8000`) | Generate + run `mkdocs serve` with live reload |

**Behavior**: See Section 9 for full docs generator specification.

**Uses LLM**: No

---

### 7.3 CLI Module Architecture

The CLI is organized into 7 packages under `cli/`:

```
cli/
├── mda.py                     # Entry point: argparse + dispatch
├── __init__.py
├── config/                    # Configuration loading
│   ├── __init__.py
│   ├── defaults.py            # DEFAULTS dict, SCHEMA_NAMES, ONTOLOGY_NAMES
│   └── loader.py              # Config class, find_config(), load_config()
├── llm/                       # LLM provider abstraction
│   ├── __init__.py
│   ├── provider.py            # LLMProvider ABC, LLMResponse, get_provider()
│   ├── anthropic_provider.py  # AnthropicProvider
│   ├── openai_provider.py     # OpenAIProvider
│   ├── ollama_provider.py     # OllamaProvider
│   └── prompts/               # Prompt templates per stage
│       ├── __init__.py
│       ├── enrich.py
│       ├── capsule.py
│       ├── intent.py
│       ├── contract.py
│       └── review.py
├── commands/                  # One module per CLI command
│   ├── __init__.py
│   ├── init_cmd.py            # run_init(args, config)
│   ├── config_cmd.py          # run_config(args, config)
│   ├── parse_cmd.py           # run_parse(args, config)
│   ├── ingest_cmd.py          # run_ingest(args, config), run_reingest(args, config)
│   ├── corpus_cmd.py          # run_corpus(args, config)
│   ├── validate_cmd.py        # run_validate(args, config)
│   ├── status_cmd.py          # run_status(args, config)
│   ├── gaps_cmd.py            # run_gaps(args, config)
│   ├── graph_cmd.py           # run_graph(args, config)
│   ├── enrich_cmd.py          # run_enrich(args, config)
│   ├── generate_cmd.py        # run_generate(args, config)
│   ├── review_cmd.py          # run_review(args, config)
│   └── docs_cmd.py            # run_docs(args, config)
├── pipeline/                  # Stage implementations
│   ├── __init__.py
│   ├── orchestrator.py        # PipelineOrchestrator: run_all(), run_stages()
│   ├── stage1_parser.py
│   ├── stage2_enricher.py
│   ├── stage3_capsule_gen.py
│   ├── stage4_intent_gen.py
│   ├── stage5_contract_gen.py
│   ├── stage6_validator.py
│   └── docs_generator.py      # MkDocs site generation
├── models/                    # Dataclass definitions
│   ├── __init__.py
│   ├── bpmn.py                # ParsedModel, BpmnNode, BpmnEdge, BpmnLane, etc.
│   ├── enriched.py            # EnrichedModel, NodeEnrichment, Gap, etc.
│   ├── triple.py              # CapsuleFrontmatter, IntentFrontmatter, ContractFrontmatter, etc.
│   └── corpus.py              # CorpusDocument, CorpusIndex, CorpusIndexEntry, AppliesTo
├── mda_io/                    # I/O utilities (named to avoid shadowing stdlib io)
│   ├── __init__.py
│   ├── frontmatter.py         # parse_frontmatter(), read/write/update frontmatter files
│   ├── bpmn_xml.py            # parse_bpmn(), BPMN_NS, ALL_NODE_TAGS
│   ├── schema_validator.py    # SchemaValidator class
│   └── yaml_io.py             # read_yaml(), write_yaml(), etc.
└── output/                    # Output formatting
    ├── __init__.py
    ├── console.py             # print_error(), print_success(), print_table()
    └── json_output.py         # output_json_error(), output_json_success()
```

**Import pattern for `mda_io`**: Because `mda_io` shadows nothing but was named to avoid confusion with Python's stdlib `io`, pipeline stages that need to import from it at runtime use `importlib.util.spec_from_file_location()`:

```python
import importlib.util, os

def _load_io(name):
    spec = importlib.util.spec_from_file_location(
        name,
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "mda_io",
            f"{name}.py",
        ),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

frontmatter_mod = _load_io("frontmatter")
yaml_io = _load_io("yaml_io")
```

### 7.4 Data Models

All data models are defined as Python `dataclass` classes with `to_dict()` and `from_dict()` serialization methods.

#### 7.4.1 BPMN Models (`models/bpmn.py`)

**Enums**:

```python
class BpmnTaskType(str, Enum):
    TASK = "task"
    USER_TASK = "userTask"
    SERVICE_TASK = "serviceTask"
    BUSINESS_RULE_TASK = "businessRuleTask"
    SEND_TASK = "sendTask"
    RECEIVE_TASK = "receiveTask"
    SCRIPT_TASK = "scriptTask"
    MANUAL_TASK = "manualTask"
    CALL_ACTIVITY = "callActivity"
    SUB_PROCESS = "subProcess"

class BpmnGatewayType(str, Enum):
    EXCLUSIVE = "exclusiveGateway"
    INCLUSIVE = "inclusiveGateway"
    PARALLEL = "parallelGateway"
    EVENT_BASED = "eventBasedGateway"

class BpmnEventType(str, Enum):
    START = "startEvent"
    END = "endEvent"
    INTERMEDIATE_CATCH = "intermediateCatchEvent"
    INTERMEDIATE_THROW = "intermediateThrowEvent"
    BOUNDARY = "boundaryEvent"

class BpmnElementType(str, Enum):
    # Union of all task, gateway, and event types (19 values total)
    ...
```

**Dataclasses**:

| Class | Fields | Description |
|-------|--------|-------------|
| `BpmnNode` | `id: str`, `name: Optional[str]`, `element_type: str`, `lane_id: Optional[str]`, `lane_name: Optional[str]`, `incoming: list[str]`, `outgoing: list[str]`, `boundary_event_ids: list[str]`, `attached_to: Optional[str]`, `documentation: Optional[str]`, `attributes: dict`, `event_definitions: list[dict]`, `gateway_direction: Optional[str]`, `default_flow: Optional[str]` | A single BPMN element (task, gateway, or event) |
| `BpmnEdge` | `id: str`, `source_id: str`, `target_id: str`, `name: Optional[str]`, `condition_expression: Optional[str]` | A sequence flow between two nodes |
| `BpmnLane` | `id: str`, `name: Optional[str]`, `node_ids: list[str]` | A swim lane with its contained node IDs |
| `BpmnProcess` | `id: str`, `name: Optional[str]`, `is_executable: bool` | A BPMN process definition |
| `BpmnDataObject` | `id: str`, `name: Optional[str]`, `item_subject_ref: Optional[str]` | A data object or data store reference |
| `BpmnDataAssociation` | `id: str`, `source_ref: str`, `target_ref: str` | A data input or output association |
| `BpmnMessageFlow` | `id: str`, `source_ref: str`, `target_ref: str`, `name: Optional[str]` | A message flow from a collaboration element |
| `ParsedModel` | `processes: list[BpmnProcess]`, `nodes: list[BpmnNode]`, `edges: list[BpmnEdge]`, `lanes: list[BpmnLane]`, `data_objects: list[BpmnDataObject]`, `data_associations: list[BpmnDataAssociation]`, `message_flows: list[BpmnMessageFlow]`, `source_file: Optional[str]` | Complete Stage 1 output |

`ParsedModel` helper methods:
- `get_node(node_id) -> Optional[BpmnNode]`
- `get_edge(edge_id) -> Optional[BpmnEdge]`
- `get_predecessors(node_id) -> list[BpmnNode]`
- `get_successors(node_id) -> list[BpmnNode]`
- `get_lane_for_node(node_id) -> Optional[BpmnLane]`

#### 7.4.2 Enrichment Models (`models/enriched.py`)

**Enums**:

```python
class GapSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class GapType(str, Enum):
    MISSING_PROCEDURE = "missing_procedure"
    MISSING_OWNER = "missing_owner"
    MISSING_DECISION_RULES = "missing_decision_rules"
    MISSING_DATA_SCHEMA = "missing_data_schema"
    MISSING_REGULATORY_CONTEXT = "missing_regulatory_context"
    MISSING_INTEGRATION_BINDING = "missing_integration_binding"
    AMBIGUOUS_NAME = "ambiguous_name"
    UNNAMED_ELEMENT = "unnamed_element"
```

**Dataclasses**:

| Class | Fields | Description |
|-------|--------|-------------|
| `CorpusMatch` | `corpus_id: str`, `match_confidence: str` (high/medium/low), `match_method: str` (exact_id/name_pattern/domain_type/tag_intersection), `match_score: float` | A single corpus-to-node match |
| `ProcedureEnrichment` | `found: bool`, `corpus_refs: list[CorpusMatch]` | Whether procedural knowledge was found |
| `OwnershipEnrichment` | `resolved: bool`, `owner_role: Optional[str]`, `owner_team: Optional[str]`, `source: Optional[str]` (lane/participant/kb_mapping) | Ownership resolution from lanes or corpus |
| `DecisionRuleEnrichment` | `defined: bool`, `rule_type: Optional[str]` (condition_expression/dmn_ref/kb_document/none), `rule_ref: Optional[str]`, `conditions: list[dict]` | Decision rules for gateways |
| `DataSchemaEnrichment` | `data_ref: str`, `schema_found: bool`, `schema_ref: Optional[str]`, `direction: Optional[str]` (input/output) | Data schema discovery per data association |
| `RegulatoryEnrichment` | `applicable: bool`, `corpus_refs: list[CorpusMatch]`, `regulation_refs: list[str]`, `policy_refs: list[str]` | Regulatory context from corpus |
| `IntegrationEnrichment` | `has_binding: bool`, `system_name: Optional[str]`, `protocol: Optional[str]`, `endpoint_hint: Optional[str]` | Integration binding hints |
| `Gap` | `gap_id: str`, `node_id: str`, `gap_type: GapType`, `severity: GapSeverity`, `description: str`, `suggested_resolution: Optional[str]` | A discovered knowledge or binding gap |
| `NodeEnrichment` | `node_id: str`, `procedure: ProcedureEnrichment`, `ownership: OwnershipEnrichment`, `decision_rules: Optional[DecisionRuleEnrichment]`, `data_schemas: list[DataSchemaEnrichment]`, `regulatory: RegulatoryEnrichment`, `integration: IntegrationEnrichment` | All enrichment data for a single node |
| `EnrichedModel` | `parsed_model: ParsedModel`, `enrichment_date: str`, `enriched_by: str`, `node_enrichments: dict[str, NodeEnrichment]`, `gaps: list[Gap]` | Complete Stage 2 output |

`EnrichedModel` helper methods:
- `get_enrichment(node_id) -> Optional[NodeEnrichment]`
- `gap_summary() -> dict` -- returns `{"total": N, "by_severity": {...}, "by_type": {...}}`

#### 7.4.3 Triple Models (`models/triple.py`)

**Enums**:

```python
class TripleStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    CURRENT = "current"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

class GoalType(str, Enum):
    DATA_PRODUCTION = "data_production"
    DECISION = "decision"
    NOTIFICATION = "notification"
    STATE_TRANSITION = "state_transition"
    ORCHESTRATION = "orchestration"

class BindingStatus(str, Enum):
    UNBOUND = "unbound"
    PARTIAL = "partial"
    BOUND = "bound"
```

**Frontmatter Dataclasses**:

| Class | Key Fields | Description |
|-------|------------|-------------|
| `CapsuleFrontmatter` | `capsule_id`, `bpmn_task_id`, `bpmn_task_name`, `bpmn_task_type`, `process_id`, `process_name`, `version`, `status: TripleStatus`, `lane_id`, `lane_name`, `owner_role`, `owner_team`, `corpus_refs: list[CorpusRef]`, `predecessor_ids: list[str]`, `successor_ids: list[str]`, `boundary_events: list[str]`, `documentation`, `tags: list[str]` | Capsule YAML frontmatter |
| `IntentFrontmatter` | `intent_id`, `capsule_id`, `bpmn_task_id`, `version`, `status: TripleStatus`, `goal`, `goal_type: GoalType`, `inputs: list[IntentInput]`, `outputs: list[IntentOutput]`, `preconditions: list[str]`, `postconditions: list[str]`, `failure_modes: list[FailureMode]`, `execution_hints: ExecutionHints`, `corpus_refs: list[CorpusRef]`, `decision_rules: list[dict]`, `regulatory_refs: list[str]`, `tags: list[str]` | Intent spec YAML frontmatter |
| `ContractFrontmatter` | `contract_id`, `intent_id`, `version`, `status: TripleStatus`, `binding_status: BindingStatus`, `sources: list[ContractSource]`, `sinks: list[ContractSink]`, `events_published: list[ContractEvent]`, `events_consumed: list[ContractEvent]`, `audit: Optional[AuditConfig]`, `sla_ms: Optional[int]`, `retry_policy: Optional[dict]`, `idempotency: Optional[dict]`, `tags: list[str]` | Contract YAML frontmatter |
| `TripleManifest` | `triple_id`, `capsule_id`, `intent_id`, `contract_id`, `bpmn_task_id`, `bpmn_process_id`, `status: TripleStatus`, `version`, `created`, `last_validated: Optional[str]`, `validation_result: Optional[str]`, `provenance: dict` | The linking manifest for one triple |

**Supporting Dataclasses**:

| Class | Fields |
|-------|--------|
| `CorpusRef` | `corpus_id: str`, `section: str`, `match_confidence: str` |
| `IntentInput` | `name: str`, `source: str`, `schema_ref: Optional[str]`, `required: bool = True` |
| `IntentOutput` | `name: str`, `type: str`, `sink: str`, `invariants: list[str]` |
| `FailureMode` | `mode: str`, `detection: str`, `action: str` |
| `ExecutionHints` | `preferred_agent: Optional[str]`, `tool_access: list[str]`, `forbidden_actions: list[str]` |
| `ContractSource` | `name: str`, `protocol: str`, `endpoint: str`, `auth: Optional[str]`, `schema_ref: Optional[str]`, `sla_ms: Optional[int]` |
| `ContractSink` | `name: str`, `protocol: str`, `endpoint: str`, `auth: Optional[str]`, `schema_ref: Optional[str]`, `sla_ms: Optional[int]`, `idempotency_key: Optional[str]` |
| `ContractEvent` | `topic: str`, `schema_ref: Optional[str]`, `delivery: Optional[str]`, `key_field: Optional[str]` |
| `AuditConfig` | `record_type: str`, `retention_years: int`, `fields_required: list[str]`, `sink: str` |

#### 7.4.4 Corpus Models (`models/corpus.py`)

**Enums**:

```python
class CorpusDocType(str, Enum):
    PROCEDURE = "procedure"
    POLICY = "policy"
    REGULATION = "regulation"
    RULE = "rule"
    DATA_DICTIONARY = "data-dictionary"
    SYSTEM = "system"
    TRAINING = "training"
    GLOSSARY = "glossary"

class CorpusStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    CURRENT = "current"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"
```

**Dataclasses**:

| Class | Fields |
|-------|--------|
| `AppliesTo` | `process_ids: list[str]`, `task_types: list[str]`, `task_name_patterns: list[str]`, `goal_types: list[str]`, `roles: list[str]` |
| `CorpusDocument` | `corpus_id: str`, `title: str`, `slug: str`, `doc_type: CorpusDocType`, `domain: str`, `subdomain: Optional[str]`, `tags: list[str]`, `applies_to: AppliesTo`, `version: str`, `status: CorpusStatus`, `author: Optional[str]`, `last_reviewed: Optional[str]`, `supersedes: Optional[str]`, `body: str`, `file_path: Optional[str]` |
| `CorpusIndexEntry` | `corpus_id: str`, `title: str`, `doc_type: str`, `domain: str`, `subdomain: Optional[str]`, `path: str`, `tags: list[str]`, `applies_to: AppliesTo`, `status: str` |
| `CorpusIndex` | `version: str`, `generated_date: str`, `document_count: int`, `documents: list[CorpusIndexEntry]` |

`CorpusIndex.search(query, doc_type=None, domain=None, tags=None) -> list[CorpusIndexEntry]`:
Performs case-insensitive keyword search across `corpus_id`, `title`, `domain`, `subdomain`, and `tags`. Applies `doc_type`, `domain`, and `tags` as hard filters before keyword matching.

### 7.5 I/O Modules

#### 7.5.1 `mda_io/frontmatter.py`

```python
def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter delimited by --- lines.
    Returns (frontmatter_dict, body_text).
    If no frontmatter found, returns ({}, full_content)."""

def read_frontmatter_file(path: Path) -> tuple[dict, str]:
    """Read a file and parse its frontmatter."""

def write_frontmatter_file(path: Path, frontmatter: dict, body: str) -> None:
    """Write a file with YAML frontmatter + markdown body.
    Creates parent directories. Uses yaml.dump with
    default_flow_style=False, sort_keys=False, width=120."""

def update_frontmatter(path: Path, updates: dict) -> None:
    """Read, merge updates into frontmatter, write back. Preserves body."""
```

#### 7.5.2 `mda_io/bpmn_xml.py`

```python
BPMN_NS = "http://www.omg.org/spec/BPMN/20100524/MODEL"
BPMNDI_NS = "http://www.omg.org/spec/BPMN/20100524/DI"

TASK_TAGS = [
    "task", "userTask", "serviceTask", "businessRuleTask",
    "sendTask", "receiveTask", "scriptTask", "manualTask",
    "callActivity", "subProcess",
]

GATEWAY_TAGS = [
    "exclusiveGateway", "inclusiveGateway",
    "parallelGateway", "eventBasedGateway",
]

EVENT_TAGS = [
    "startEvent", "endEvent", "intermediateCatchEvent",
    "intermediateThrowEvent", "boundaryEvent",
]

ALL_NODE_TAGS = TASK_TAGS + GATEWAY_TAGS + EVENT_TAGS  # 19 tags

def parse_bpmn(path: Path) -> ParsedModel:
    """Parse a BPMN 2.0 XML file into a ParsedModel.
    Steps:
    1. Parse XML and validate BPMN namespace
    2. Extract process definitions
    3. Extract all nodes (tasks, gateways, events) per process
    4. Extract sequence flows as edges
    5. Extract lane sets and assign nodes to lanes
    6. Extract data objects and data store references
    7. Extract data associations (input/output) from within task elements
    8. Extract message flows from collaboration elements
    9. Post-process: assign lane info to nodes
    10. Post-process: link boundary events to parent tasks via attachedToRef
    11. Post-process: populate incoming/outgoing edge IDs on nodes
    """
```

Event definition extraction handles these event definition types:
`timerEventDefinition`, `messageEventDefinition`, `signalEventDefinition`, `errorEventDefinition`, `escalationEventDefinition`, `compensateEventDefinition`, `conditionalEventDefinition`, `linkEventDefinition`, `terminateEventDefinition`, `cancelEventDefinition`.

Synthetic IDs are generated for elements lacking an `id` attribute using a global counter with prefix-based naming (e.g., `synth_1`, `process_2`).

#### 7.5.3 `mda_io/schema_validator.py`

```python
@dataclass
class SchemaError:
    path: str        # JSON pointer path to the failing field
    message: str
    schema_path: str # Which schema rule failed

class SchemaValidator:
    def __init__(self, schemas_dir: Path):
        """Load all *.schema.json files from the directory."""

    @property
    def available_schemas(self) -> list[str]:
        """Names of loaded schemas (e.g., ['capsule', 'intent', 'contract', ...])."""

    def validate_capsule(self, frontmatter: dict) -> list[SchemaError]
    def validate_intent(self, frontmatter: dict) -> list[SchemaError]
    def validate_contract(self, frontmatter: dict) -> list[SchemaError]
    def validate_corpus_document(self, frontmatter: dict) -> list[SchemaError]
    def validate_triple_manifest(self, manifest: dict) -> list[SchemaError]
```

Uses `jsonschema.Draft7Validator` for validation. Errors are sorted by JSON pointer path.

#### 7.5.4 `mda_io/yaml_io.py`

```python
def read_yaml(path: Path) -> Any:
    """Read a YAML file via yaml.safe_load."""

def write_yaml(path: Path, data: Any) -> None:
    """Write data to YAML. Creates parent dirs. Uses
    default_flow_style=False, sort_keys=False, width=120."""

def read_yaml_string(content: str) -> Any:
    """Parse a YAML string via yaml.safe_load."""

def dump_yaml_string(data: Any) -> str:
    """Dump data to a YAML string."""
```

---

## 8. LLM Provider Specification

### 8.1 Abstract Interface

```python
class LLMProvider(ABC):
    @abstractmethod
    def complete(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.2,
        stop_sequences: Optional[list[str]] = None,
    ) -> LLMResponse:
        """Free-form text completion."""
        ...

    @abstractmethod
    def complete_structured(
        self,
        prompt: str,
        schema: dict,
        system_prompt: str = "",
        max_tokens: int = 4096,
    ) -> dict:
        """Structured output completion.
        Returns a dict validated against the provided JSON Schema."""
        ...

    @abstractmethod
    def name(self) -> str:
        """Provider name for logging/audit trail."""
        ...
```

### 8.2 LLMResponse

```python
@dataclass
class LLMResponse:
    content: str          # The generated text
    model: str            # Model identifier (e.g., "claude-sonnet-4-20250514")
    usage: dict           # {"input_tokens": N, "output_tokens": N}
    raw: Any = None       # Provider-specific raw response object
```

### 8.3 Provider Implementations

#### 8.3.1 AnthropicProvider

- **SDK**: `anthropic` Python SDK
- **`complete()`**: Calls `client.messages.create()` with role `"user"` for the prompt and `system` parameter for the system prompt.
- **`complete_structured()`**: Uses Anthropic's tool-use feature. Defines a single tool named `structured_output` whose input schema matches the provided JSON schema. The prompt instructs the model to call this tool. Extracts the tool call's input as the structured result.
- **Authentication**: Reads API key from config (`llm.api_key_env` environment variable, default `ANTHROPIC_API_KEY`).

#### 8.3.2 OpenAIProvider

- **SDK**: `openai` Python SDK
- **`complete()`**: Calls `client.chat.completions.create()` with messages `[{"role": "system", ...}, {"role": "user", ...}]`.
- **`complete_structured()`**: Uses OpenAI's `response_format={"type": "json_schema", "json_schema": {...}}` parameter to enforce structured output.
- **Authentication**: Reads API key from `OPENAI_API_KEY` environment variable.

#### 8.3.3 OllamaProvider

- **SDK**: `requests` library for REST calls to Ollama's local API.
- **Base URL**: `OLLAMA_BASE_URL` environment variable, default `http://localhost:11434`.
- **`complete()`**: `POST /api/generate` with `model`, `prompt`, `system`, and generation parameters.
- **`complete_structured()`**: Uses Ollama's JSON mode (`format: "json"`) and embeds the JSON schema in the prompt with instructions to conform. Parses the JSON response and validates against the schema.
- **Authentication**: None (local service).

### 8.4 Factory

```python
def get_provider(config) -> LLMProvider:
    """Factory: create provider from config.
    Reads config.llm_provider: 'anthropic' | 'openai' | 'ollama'.
    Raises ValueError for unknown providers."""
```

Resolution order for provider selection:
1. `MDA_LLM_PROVIDER` environment variable (if set)
2. `llm.provider` in `mda.config.yaml`
3. Default: `"anthropic"`

Resolution order for model selection:
1. `MDA_LLM_MODEL` environment variable (if set)
2. `llm.model` in `mda.config.yaml`
3. Default: `"claude-sonnet-4-20250514"`

### 8.5 Prompt Templates

Each stage has a dedicated prompt module in `cli/llm/prompts/`.

#### 8.5.1 `prompts/enrich.py` (Stage 2)

```python
DISAMBIGUATION_SYSTEM = """You are a knowledge corpus matching specialist for the MDA Intent Layer.
Your job is to judge whether a corpus document is relevant to a specific BPMN task.
Be precise. A document is relevant only if it directly provides procedural knowledge,
business rules, or regulatory context that would populate a knowledge capsule for this task."""

def build_disambiguation_prompt(
    node_context: dict,   # {id, name, element_type, lane_name, process_name, domain}
    candidates: list[dict] # [{corpus_id, title, doc_type, tags, snippet}]
) -> str

DISAMBIGUATION_SCHEMA = {
    "type": "object",
    "properties": {
        "assessments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "corpus_id": {"type": "string"},
                    "relevant": {"type": "boolean"},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                    "reason": {"type": "string"}
                },
                "required": ["corpus_id", "relevant", "confidence", "reason"]
            }
        }
    },
    "required": ["assessments"]
}
```

#### 8.5.2 `prompts/capsule.py` (Stage 3)

```python
CAPSULE_SYSTEM = """You are a knowledge capsule author for the MDA Intent Layer.
You produce knowledge capsules -- structured Markdown documents that capture procedural
knowledge, business rules, and domain context for a specific BPMN task.

Capsules are consumed by AI agents as domain knowledge. Be precise, factual, and thorough.
Draw from the provided corpus documents. Cite corpus IDs where appropriate.
Do not fabricate procedures or rules -- if information is missing, leave the section empty
and note the gap."""

def build_capsule_body_prompt(
    node_context: dict,       # BPMN node details
    corpus_content: list[dict], # [{corpus_id, title, doc_type, body_text}]
    enrichment: dict           # Enrichment data for this node
) -> str
```

The capsule body prompt requests 8 sections: Purpose, Procedure, Business Rules, Inputs Required, Outputs Produced, Exception Handling, Regulatory Context, Notes. Uses `complete()` (free-form), not `complete_structured()`.

#### 8.5.3 `prompts/intent.py` (Stage 4)

```python
INTENT_SYSTEM = """You are an intent specification architect for the MDA Intent Layer.
...
ANTI-UI PRINCIPLE: Intent specs must NEVER be satisfied through browser automation,
screen scraping, or UI clicks. forbidden_actions MUST always include:
- browser_automation
- screen_scraping
- ui_click
- rpa_style_macros"""

def build_intent_frontmatter_prompt(
    node_context: dict,   # {name, element_type, default_goal_type}
    capsule_content: str,  # Raw capsule markdown (truncated to 3000 chars)
    enrichment: dict
) -> str

def build_intent_body_prompt(
    node_context: dict,
    frontmatter: dict  # Already-generated frontmatter (JSON, truncated to 2000 chars)
) -> str

INTENT_FRONTMATTER_SCHEMA = {
    "type": "object",
    "required": ["goal", "inputs", "outputs", "invariants",
                  "success_criteria", "failure_modes", "execution_hints"],
    "properties": {
        "goal": {"type": "string"},
        "preconditions": {"type": "array", "items": {"type": "string"}},
        "inputs": {"type": "array", "items": {
            "type": "object",
            "properties": {"name": {}, "source": {}, "schema_ref": {}, "required": {}},
            "required": ["name", "source"]
        }},
        "outputs": {"type": "array", "items": {
            "type": "object",
            "properties": {"name": {}, "type": {}, "sink": {}, "invariants": {}},
            "required": ["name", "type", "sink"]
        }},
        "invariants": {"type": "array", "items": {"type": "string"}},
        "success_criteria": {"type": "array", "items": {"type": "string"}},
        "failure_modes": {"type": "array", "items": {
            "type": "object",
            "required": ["mode", "detection", "action"]
        }},
        "execution_hints": {"type": "object", "properties": {
            "preferred_agent": {}, "tool_access": {}, "forbidden_actions": {}
        }}
    }
}
```

Intent generation is a two-call process:
1. `complete_structured()` with `INTENT_FRONTMATTER_SCHEMA` for frontmatter fields
2. `complete()` with `build_intent_body_prompt()` for the markdown body

The body prompt requests 6 sections: Outcome Statement, Outcome Contract, Reasoning Guidance, Anti-Patterns, Paired Capsule, Paired Integration Contract.

#### 8.5.4 `prompts/contract.py` (Stage 5)

```python
CONTRACT_SYSTEM = """You are an integration architect for the MDA Intent Layer.
...
Contracts are the ONLY artifacts that contain technology-specific detail.
When real system information is unavailable, generate plausible REST endpoint
patterns and set binding_status to 'unbound'."""

def build_contract_frontmatter_prompt(
    intent_frontmatter: dict,
    system_docs: list[dict],   # [{corpus_id, title, body_text}]
    config_systems: list[dict]  # System configs from mda.config.yaml
) -> str

def build_contract_body_prompt(contract_frontmatter: dict) -> str

CONTRACT_FRONTMATTER_SCHEMA = {
    "type": "object",
    "required": ["sources", "sinks", "binding_status"],
    "properties": {
        "sources": {"type": "array", "items": {
            "required": ["name", "protocol", "endpoint"]
        }},
        "sinks": {"type": "array", "items": {
            "required": ["name", "protocol", "endpoint"]
        }},
        "events": {"type": "array"},
        "audit": {"type": "object", "required": ["record_type", "retention_years"]},
        "binding_status": {"type": "string", "enum": ["bound", "partial", "unbound"]},
        "unbound_sources": {"type": "array"},
        "unbound_sinks": {"type": "array"}
    }
}
```

Protocol enum values accepted in schemas: `rest`, `grpc`, `graphql`, `soap`, `jdbc`, `file`, `message_queue`. The `amqp` protocol appears in demo data but is not in the schema enum -- it is used in examples where the specific broker protocol is known.

Contract body prompt requests 3 sections: Binding Rationale, Change Protocol, Decommissioning.

#### 8.5.5 `prompts/review.py` (Quality Review)

```python
REVIEW_SYSTEM = """You are a quality reviewer for MDA Intent Layer triples.
Review the capsule, intent spec, and integration contract for completeness,
accuracy, consistency, and anti-UI compliance.
Be specific in your findings. Reference exact fields and sections.
Assign severity: critical (must fix), high (should fix), medium (consider fixing), low (minor)."""

def build_review_prompt(
    capsule_content: str,   # Raw markdown (truncated to 3000 chars)
    intent_content: str,    # Raw markdown (truncated to 3000 chars)
    contract_content: str,  # Raw markdown (truncated to 3000 chars)
    aspect: str = "all"     # "completeness" | "accuracy" | "consistency" | "all"
) -> str

REVIEW_SCHEMA = {
    "type": "object",
    "required": ["overall_rating", "findings", "summary"],
    "properties": {
        "overall_rating": {
            "type": "string",
            "enum": ["pass", "pass_with_warnings", "needs_revision", "fail"]
        },
        "findings": {"type": "array", "items": {
            "type": "object",
            "required": ["severity", "aspect", "file", "finding", "recommendation"],
            "properties": {
                "severity": {"enum": ["critical", "high", "medium", "low"]},
                "aspect": {"enum": ["completeness", "accuracy", "consistency", "anti_ui"]},
                "file": {"enum": ["capsule", "intent", "contract"]},
                "field_or_section": {"type": "string"},
                "finding": {"type": "string"},
                "recommendation": {"type": "string"}
            }
        }},
        "summary": {"type": "string"}
    }
}
```

### 8.6 Environment Variables

| Variable | Provider | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic | -- | API key for Anthropic Claude |
| `OPENAI_API_KEY` | OpenAI | -- | API key for OpenAI |
| `OLLAMA_BASE_URL` | Ollama | `http://localhost:11434` | Base URL for local Ollama server |
| `MDA_LLM_PROVIDER` | all | -- | Override provider selection (bypasses config file) |
| `MDA_LLM_MODEL` | all | -- | Override model selection (bypasses config file) |

The `llm.api_key_env` config key controls which environment variable is read for the API key. Default: `ANTHROPIC_API_KEY`. This allows a single config to point at a custom env var (e.g., `MY_CLAUDE_KEY`).

---

## 9. MkDocs Process Navigator

### 9.1 Purpose

The docs system auto-generates a per-process MkDocs site from existing triple files, corpus documents, graph data, and gap records. It provides a navigable, interlinked documentation hub for each process repository. The site is generated entirely from the process repo's on-disk artifacts -- no database, no API.

### 9.2 CLI Commands

| Command | Description | Subprocess |
|---------|-------------|------------|
| `mda docs generate` | Creates `mkdocs.yml` + `docs/` overlay in the project root | None |
| `mda docs build` | Runs `generate`, then `mkdocs build` | `mkdocs build` |
| `mda docs serve [--port N]` | Runs `generate`, then `mkdocs serve --dev-addr 0.0.0.0:N` | `mkdocs serve` |

The `generate` step always runs fresh -- it deletes and recreates the `docs/` directory to avoid stale content.

### 9.3 Generated Site Structure

```
{project_root}/
├── mkdocs.yml                    # Generated MkDocs configuration
└── docs/
    ├── index.md                  # Status dashboard + README content
    ├── flow/
    │   ├── diagram.md            # Mermaid BPMN visualization
    │   └── graph.md              # Process graph YAML dump
    ├── tasks/{slug}/
    │   ├── capsule.md            # Wrapped .cap.md with metadata table
    │   ├── intent.md             # Wrapped .intent.md with metadata table
    │   └── contract.md           # Wrapped .contract.md with metadata table
    ├── decisions/{slug}/
    │   ├── capsule.md
    │   ├── intent.md
    │   └── contract.md
    ├── corpus/
    │   ├── {doc_type}.md         # Index page per corpus type (e.g., procedures.md)
    │   └── {corpus_id}.md        # Individual corpus docs with metadata
    ├── gaps/
    │   └── index.md              # Aggregated gap tracker sorted by severity
    └── audit/
        └── index.md              # Ingestion + change logs
```

### 9.4 MkDocs Configuration

The generated `mkdocs.yml` uses:

- **Theme**: Material for MkDocs with `indigo` primary color and `white` accent
- **Extensions**:
  - `admonition` -- for callout boxes
  - `pymdownx.details` -- for collapsible sections
  - `pymdownx.superfences` -- with custom fence for `mermaid` code blocks
- **Plugins**: `search` (built-in)
- **Navigation**: Auto-generated from discovered triples and decisions. Structure:
  ```yaml
  nav:
    - Home: index.md
    - Flow:
        - Diagram: flow/diagram.md
        - Graph: flow/graph.md
    - Tasks:
        - {Task Name}:
            - Capsule: tasks/{slug}/capsule.md
            - Intent: tasks/{slug}/intent.md
            - Contract: tasks/{slug}/contract.md
    - Decisions:
        - {Decision Name}:
            - Capsule: decisions/{slug}/capsule.md
            - Intent: decisions/{slug}/intent.md
            - Contract: decisions/{slug}/contract.md
    - Corpus:
        - {Type Name}: corpus/{type}.md
    - Gaps: gaps/index.md
    - Audit: audit/index.md
  ```

### 9.5 Jinja2 Templates (8 files in `templates/mkdocs/`)

All templates are Jinja2 `.j2` files rendered by `pipeline/docs_generator.py::_render_template()`.

#### 9.5.1 `mkdocs.yml.j2`

**Variables**: `process_name: str`, `site_name: str`, `nav_tasks: list[{slug, name}]`, `nav_decisions: list[{slug, name}]`, `has_corpus: bool`, `corpus_sections: list[{type, type_name}]`

**Output**: The `mkdocs.yml` configuration file.

#### 9.5.2 `index.md.j2`

**Variables**: `process_name: str`, `readme_content: str`, `summary: {total, by_status, gap_count, unbound_count}`, `status_table: list[{name, slug, type, status, binding, gaps, section}]`

**Output**: Dashboard page with summary statistics and a status table for all triples.

#### 9.5.3 `flow.md.j2`

**Variables**: `process_name: str`, `mermaid_content: str`

**Output**: Embeds the Mermaid flowchart from `graph/graph-visual.md`.

#### 9.5.4 `graph.md.j2`

**Variables**: `process_name: str`, `graph_yaml: str`

**Output**: Displays the raw `process-graph.yaml` in a fenced YAML code block.

#### 9.5.5 `gaps.md.j2`

**Variables**: `gaps: list[{id, severity, type, triple, description}]`, `summary: {critical, high, medium, low}`

**Output**: Gap tracker with severity counts and a detailed table.

#### 9.5.6 `audit.md.j2`

**Variables**: `ingestion_log: str`, `change_log: str`

**Output**: Displays ingestion and change logs in fenced YAML code blocks.

#### 9.5.7 `corpus-section.md.j2`

**Variables**: `type_name: str`, `documents: list[{corpus_id, title, slug, path, status, tags}]`

**Output**: Index page for a corpus document type with links to individual docs.

#### 9.5.8 `triple-wrapper.md.j2`

**Variables**: `task_name: str`, `triple_type: str`, `content: str`, `capsule_link: {name, url}`, `intent_link: {name, url}`, `contract_link: {name, url}`, `predecessor_links: list[{name, url}]`, `successor_links: list[{name, url}]`

**Output**: Wraps a triple file with navigation breadcrumbs (Capsule / Intent / Contract links), predecessor/successor links, and the artifact content with a metadata table extracted from frontmatter.

### 9.6 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `mkdocs` | `>=1.6` | Static site generator |
| `mkdocs-material` | `>=9.5` | Material theme with Mermaid support |
| `jinja2` | `>=3.1` | Template engine (also a dependency of MkDocs) |

---

## 10. Configuration System

### 10.1 `mda.config.yaml` Format

The canonical configuration file format with all supported keys:

```yaml
# ---- Top-Level Metadata ----
mda:
  version: "1.0.0"                    # Config schema version
  project: "income-verification-demo"  # Optional project identifier

# ---- Process Identity ----
process:
  id: "Process_IncomeVerification"     # BPMN process ID
  name: "Income Verification"         # Human-readable process name
  domain: "mortgage-underwriting"      # Business domain
  subdomain: "income-verification"     # Business subdomain
  owner_team: "Income Verification"    # Owning team
  version: "1.0"                       # Process version

# ---- Path Configuration (Standard Pattern) ----
paths:
  bpmn: "bpmn/"                        # BPMN source files
  triples: "triples/"                  # Generated triple artifacts
  decisions: "decisions/"              # Decision gateway triples
  graph: "graph/"                      # Process graph files
  gaps: "gaps/"                        # Gap analysis documents
  audit: "audit/"                      # Audit trail files
  corpus: "../../corpus"               # Path to shared corpus (relative to project root)

# ---- BPMN Source Configuration ----
bpmn:
  source: "bpmn/income-verification.bpmn"  # Primary BPMN file
  metadata: "bpmn/bpmn-metadata.yaml"      # BPMN metadata supplement

# ---- Naming Conventions ----
naming:
  id_prefix: "IV"                      # 2-3 letter prefix for generated IDs
  capability_prefix: "ICT-IV"          # Full capability ID prefix
  gap_prefix: "GAP"                    # Gap ID prefix
  capsule_pattern: "CAP-{prefix}-{code}-{seq}"   # Optional: custom ID patterns
  intent_pattern: "INT-{prefix}-{code}-{seq}"
  contract_pattern: "ICT-{prefix}-{code}-{seq}"

# ---- LLM Configuration ----
llm:
  provider: "anthropic"                # Choices: "anthropic", "openai", "ollama"
  model: "claude-sonnet-4-20250514"    # Model identifier
  api_key_env: "ANTHROPIC_API_KEY"     # Env var holding the API key
  temperature: 0.2                     # Generation temperature
  max_tokens: 4096                     # Max output tokens per call

# ---- Pipeline Configuration ----
pipeline:
  schemas: "../../schemas/"            # Path to JSON schema files
  ontology: "../../ontology/"          # Path to ontology YAML files
  version: "0.1.0-demo"               # Pipeline version string
  mode: "demo"                         # Optional mode indicator
  schema_validation: true              # Enable/disable schema validation

# ---- Ingestion Behavior ----
ingestion:
  auto_generate_triples: true          # Auto-generate triples during ingest
  auto_generate_graph: true            # Auto-generate process graph
  gap_analysis: true                   # Run gap analysis during enrichment
  binding_status_default: "unbound"    # Default binding status for new contracts

# ---- Default Values ----
defaults:
  status: "draft"                      # Default lifecycle status
  binding_status: "unbound"            # Default binding status
  audit_retention_years: 7             # Default audit record retention
  mda_layers:                          # MDA layer designations
    capsule: "CIM"
    intent: "PIM"
    contract: "PSM"

# ---- Integration Systems (optional) ----
integrations:
  systems:
    - id: "LOS"
      name: "Loan Origination System"
      type: "rest"
      description: "Core loan application management system"
    - id: "DocVault"
      name: "Document Vault"
      type: "rest"
      description: "Document storage and extraction service"

# ---- Validation Rules (optional) ----
validation:
  require_all_triples: true            # All BPMN tasks must have triples
  require_cross_references: true       # IDs must cross-reference correctly
  require_predecessor_successor_match: true
  require_data_flow_consistency: true
```

### 10.2 Config Resolution Order

Values are resolved in this precedence (highest wins):

1. **CLI flags** (`--config`, `--json`, `--verbose`, `--dry-run`)
2. **Environment variables** (`MDA_LLM_PROVIDER`, `MDA_LLM_MODEL`, API key vars)
3. **`mda.config.yaml`** (file discovered or specified)
4. **Built-in defaults** (`cli/config/defaults.py::DEFAULTS`)

The `Config` class implements this via:
- `DEFAULTS` is deep-merged with file data at load time
- Properties like `llm_provider` check `os.environ` before returning config values
- CLI flags are applied by the command handlers after config loading

### 10.3 Config Discovery

`find_config()` implements git-style upward directory walking:

1. Start from the current working directory (or the directory specified by `--config`)
2. Look for `mda.config.yaml` in the current directory
3. If not found, move to the parent directory
4. Repeat until found or the filesystem root is reached
5. If not found, return `None` (defaults apply)

The directory containing the discovered config file becomes the `project_root`. All relative paths in the config are resolved against this root.

### 10.4 Alternate Config Key Patterns

The Loan Origination demo uses a different config structure than the standard one:

| Standard Key | Alternate Key | Used By |
|-------------|---------------|---------|
| `paths.triples` | `output.triples_dir` | LO demo |
| `paths.decisions` | `output.decisions_dir` | LO demo |
| `paths.graph` | `output.graph_dir` | LO demo |
| `paths.gaps` | `output.gaps_dir` | LO demo |
| `paths.audit` | `output.audit_dir` | LO demo |
| `pipeline.schemas` | `pipeline.schemas.capsule` (per-schema paths) | LO demo |

The docs generator and other consumers handle both patterns by checking the standard key first, then falling back to the alternate key:

```python
triples_path = config.get("paths.triples") or config.get("output.triples_dir") or "triples"
```

---

## 11. Demo Data Specification

### 11.1 Process Repository Structure

Each demo process lives in `examples/{slug}/` with this directory structure:

```
examples/{slug}/
├── bpmn/
│   ├── {slug}.bpmn              # BPMN 2.0 XML source file
│   └── bpmn-metadata.yaml       # Supplemental metadata not in the XML
├── triples/
│   ├── _manifest.json           # Process manifest listing all triples
│   └── {task-slug}/
│       ├── {task-slug}.cap.md        # Knowledge Capsule
│       ├── {task-slug}.intent.md     # Intent Specification
│       ├── {task-slug}.contract.md   # Integration Contract
│       └── triple.manifest.json      # Per-triple manifest
├── decisions/
│   └── {gateway-slug}/
│       ├── {gateway-slug}.cap.md
│       ├── {gateway-slug}.intent.md
│       ├── {gateway-slug}.contract.md
│       └── triple.manifest.json
├── graph/
│   ├── process-graph.yaml       # Structured process graph
│   └── graph-visual.md          # Mermaid flowchart visualization
├── gaps/
│   └── GAP-001.md               # Standalone gap documents
├── audit/
│   ├── ingestion-log.yaml       # Pipeline ingestion history
│   └── change-log.yaml          # Change tracking
├── mda.config.yaml              # Process-specific configuration
└── README.md                    # Process overview
```

### 11.2 Demo Process 1: Loan Origination (LO)

**Config**: `examples/loan-origination/mda.config.yaml`
- Process ID: `Process_LoanOrigination`
- Process Name: Loan Origination
- Domain: Mortgage Lending
- ID Prefix: `LO`

**Tasks (7 triples in `triples/`)**:

| Triple ID | Directory | BPMN Element ID | Element Type | BPMN Task Name |
|-----------|-----------|-----------------|--------------|----------------|
| `LO-APP-001` | `receive-application` | `Task_ReceiveApplication` | `receiveTask` | Receive Loan Application |
| `LO-IDV-001` | `verify-identity` | `Task_VerifyIdentity` | `serviceTask` | Verify Borrower Identity |
| `LO-CRC-001` | `pull-credit` | `Task_PullCredit` | `serviceTask` | Pull Credit Report |
| `LO-DTI-001` | `assess-dti` | `Task_AssessDTI` | `businessRuleTask` | Assess Debt-to-Income Ratio |
| `LO-DOC-001` | `request-docs` | `Task_RequestDocs` | `sendTask` | Request Additional Documentation |
| `LO-PKG-001` | `package-loan` | `Task_PackageLoan` | `task` | Package Loan File |
| `LO-SUB-001` | `submit-underwriting` | `Task_SubmitUW` | `sendTask` | Submit to Underwriting |

**Boundary Event (1 triple in `triples/`)**:

| Triple ID | Directory | BPMN Element ID | Element Type | BPMN Task Name |
|-----------|-----------|-----------------|--------------|----------------|
| `LO-TMO-001` | `timeout-no-response` | `Boundary_Timeout` | `boundaryEvent` | Timeout - No Response |

**Decisions (2 triples in `decisions/`)**:

| Triple ID | Directory | BPMN Element ID | Element Type | BPMN Task Name |
|-----------|-----------|-----------------|--------------|----------------|
| `LO-DEC-001` | `loan-eligibility` | `Gateway_Eligible` | `exclusiveGateway` | Eligible? |
| `LO-DEC-002` | `docs-received` | `Gateway_DocsReceived` | `exclusiveGateway` | Docs Received? |

**Total**: 10 triples (7 tasks + 1 boundary event + 2 decisions)

### 11.3 Demo Process 2: Income Verification (IV)

**Config**: `examples/income-verification/mda.config.yaml`
- Process ID: `Process_IncomeVerification`
- Process Name: Income Verification
- Domain: mortgage-underwriting
- ID Prefix: `IV`
- Capability Prefix: `ICT-IV`

**Tasks (6 triples in `triples/`)**:

| Triple ID | Directory | BPMN Element ID | Element Type | BPMN Task Name |
|-----------|-----------|-----------------|--------------|----------------|
| `IV-REQ-001` | `receive-request` | `Task_ReceiveRequest` | `receiveTask` | Receive Verification Request |
| `IV-CLS-001` | `classify-employment` | `Task_ClassifyEmployment` | `businessRuleTask` | Classify Employment Type |
| `IV-W2V-001` | `verify-w2` | `Task_VerifyW2` | `serviceTask` | Verify W-2 Income |
| `IV-SEI-001` | `verify-self-employment` | `Task_VerifySelfEmployment` | `serviceTask` | Verify Self-Employment Income |
| `IV-QAL-001` | `calc-qualifying` | `Task_CalcQualifying` | `businessRuleTask` | Calculate Qualifying Income |
| `IV-NTF-001` | `emit-verified` | `Task_EmitVerified` | `sendTask` | Emit Income Verified Event |

**Decisions (2 triples in `decisions/`)**:

| Triple ID | Directory | BPMN Element ID | Element Type | BPMN Task Name |
|-----------|-----------|-----------------|--------------|----------------|
| `IV-DEC-001` | `employment-type` | `Gateway_EmploymentType` | `exclusiveGateway` | W-2 or Self-Employed? |
| `IV-DEC-002` | `variance-threshold` | `Gateway_Variance` | `exclusiveGateway` | Variance Exceeds Threshold? |

**Total**: 8 triples (6 tasks + 2 decisions)

**Process Graph Nodes** (from `graph/process-graph.yaml`):
- `Start_Requested` (startEvent) -> `Task_ReceiveRequest` -> `Task_ClassifyEmployment` -> `Gateway_EmploymentType`
- `Gateway_EmploymentType` branches to `Task_VerifyW2` (W-2) or `Task_VerifySelfEmployment` (Self-Employed)
- Both converge at `Task_CalcQualifying` -> `Gateway_Variance`
- `Gateway_Variance` branches to `Task_EmitVerified` (Within Threshold) -> `End_Verified` or `End_VarianceException` (Exceeds Threshold)

**Data Objects**: `borrower_profile`, `tax_returns`, `w2_documents`, `income_result`

**Integration Systems**: LOS, DocVault, RuleEngine, EventBus, IVES

### 11.4 Demo Process 3: Property Appraisal (PA)

**Config**: `examples/property-appraisal/mda.config.yaml`
- Process ID: `Process_PropertyAppraisal`
- Process Name: Property Appraisal
- Domain: Mortgage
- Subdomain: Property Appraisal
- ID Prefix: `PA`

**Tasks (7 triples in `triples/`)**:

| Triple ID | Directory | BPMN Element ID | Element Type | BPMN Task Name |
|-----------|-----------|-----------------|--------------|----------------|
| `PA-ORD-001` | `order-appraisal` | `Task_OrderAppraisal` | `task` | Order Appraisal |
| `PA-RCV-001` | `receive-report` | `Task_ReceiveReport` | `task` | Receive Appraisal Report |
| `PA-VAL-001` | `validate-completeness` | `Task_ValidateCompleteness` | `task` | Validate Appraisal Completeness |
| `PA-REV-001` | `request-revision` | `Task_RequestRevision` | `task` | Request Appraisal Revision |
| `PA-ASV-001` | `assess-value` | `Task_AssessValue` | `task` | Assess Property Value |
| `PA-MRV-001` | `manual-review` | `Task_ManualReview` | `task` | Flag for Manual Review |
| `PA-NTF-001` | `emit-complete` | `Task_EmitComplete` | `task` | Emit Appraisal Complete Event |

**Decisions (2 triples in `decisions/`)**:

| Triple ID | Directory | BPMN Element ID | Element Type | BPMN Task Name |
|-----------|-----------|-----------------|--------------|----------------|
| `PA-DEC-001` | `completeness-check` | `Gateway_Complete` | decision | Complete? |
| `PA-DEC-002` | `ltv-check` | `Gateway_LTV` | decision | Value Within LTV? |

**Total**: 9 triples (7 tasks + 2 decisions)

**Regulatory Context**:
- USPAP (Uniform Standards of Professional Appraisal Practice)
- AIR (Appraiser Independence Requirements - Dodd-Frank Section 1472)
- ECOA (Equal Credit Opportunity Act)
- TRID (TILA-RESPA Integrated Disclosure)
- Fannie Mae Selling Guide B4-1
- FHA Handbook 4000.1 Sections D4-D5

**Integration Systems**: LOS, Appraisal Portal, Document Management System, Payment Gateway, Event Bus, MLS Data Provider, Disclosure System

### 11.5 BPMN XML Requirements

All demo BPMN files must be valid BPMN 2.0 XML with:

1. **Root element**: `<definitions>` with namespace `xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"`
2. **Required child elements**:
   - `<collaboration>` with at least one `<participant>` referencing the process
   - `<process>` with `id` and `name` attributes
   - `<laneSet>` with at least one `<lane>`, each containing `<flowNodeRef>` elements
   - At least one `<startEvent>` and one `<endEvent>`
   - At least one task element (from `TASK_TAGS`)
   - `<sequenceFlow>` elements connecting all nodes
3. **Optional elements**:
   - `<exclusiveGateway>`, `<inclusiveGateway>`, `<parallelGateway>`, `<eventBasedGateway>`
   - `<boundaryEvent>` with `attachedToRef` attribute
   - `<dataObject>`, `<dataObjectReference>`, `<dataStoreReference>`
   - `<dataInputAssociation>`, `<dataOutputAssociation>` nested inside task elements
   - `<messageFlow>` inside `<collaboration>`
   - Event definitions: `<timerEventDefinition>`, `<messageEventDefinition>`, etc.
   - `<conditionExpression>` inside sequence flows
   - `<documentation>` inside any element
4. **Diagram layer**: `<bpmndi:BPMNDiagram>` is optional and ignored by the parser (only the semantic model is used).

---

## 12. File Format Reference

### 12.1 Knowledge Capsule (`.cap.md`)

**File naming**: `{task-slug}.cap.md` (e.g., `receive-request.cap.md`)

**Frontmatter** (validated against `capsule.schema.json`):

```yaml
---
capsule_id: "CAP-IV-REQ-001"              # Pattern: CAP-{PREFIX}-{CODE}-{SEQ}
bpmn_task_id: "Task_ReceiveRequest"        # BPMN element ID
bpmn_task_name: "Receive Verification Request"
bpmn_task_type: "receiveTask"              # Enum: userTask, serviceTask, businessRuleTask,
                                           #   task, sendTask, receiveTask, scriptTask,
                                           #   manualTask, callActivity, subProcess
process_id: "Process_IncomeVerification"
process_name: "Income Verification"
version: "1.0"                             # Pattern: MAJOR.MINOR
status: "draft"                            # Enum: draft, review, approved, current,
                                           #   deprecated, archived
generated_from: "income-verification.bpmn"
generated_date: "2026-04-09T00:00:00Z"     # ISO 8601
generated_by: "MDA Demo"
last_modified: "2026-04-09T00:00:00Z"
last_modified_by: "MDA Demo"
owner_role: "Underwriter"                  # Nullable
owner_team: "Income Verification"          # Nullable
reviewers: []                              # Optional string array
domain: "Mortgage Lending"                 # Optional
subdomain: "Income Verification"           # Optional
regulation_refs:                           # Optional string array
  - "Fannie Mae Selling Guide B3-3.1"
policy_refs:                               # Optional string array
  - "POL-IV-001 Income Verification Request Acceptance Policy"
intent_id: "INT-IV-REQ-001"                # Cross-ref pattern: INT-{PREFIX}-{CODE}-{SEQ}
contract_id: "ICT-IV-REQ-001"              # Cross-ref pattern: ICT-{PREFIX}-{CODE}-{SEQ}
parent_capsule_id: null                    # Nullable, pattern: CAP-{PREFIX}-{CODE}-{SEQ}
predecessor_ids:                           # Array of capsule IDs
  - "CAP-IV-XXX-001"
successor_ids:
  - "CAP-IV-CLS-001"
exception_ids: []                          # Related exception-handling capsule IDs
gaps:                                      # Inline gap records
  - type: "missing_detail"
    description: "Co-borrower handling not specified"
    severity: "medium"                     # Enum: critical, high, medium, low
corpus_refs:                               # Corpus document references
  - corpus_id: "CRP-INC-PRO-001"          # Pattern: CRP-{DOMAIN}-{TYPE}-{SEQ}
    section: "Income Verification Intake"
    match_confidence: "high"               # Enum: high, medium, low
---
```

**Body sections** (markdown below the closing `---`):

```markdown
# {Task Name}

## Purpose
One paragraph describing what this task accomplishes in the process flow.

## Procedure
1. **Step Name**: Step description. (CRP-XXX-XXX-001)
2. **Step Name**: Step description.

## Business Rules
- **Rule Name**: Rule description with thresholds/constraints. (CRP-XXX-XXX-002)

## Inputs Required
| Input | Source | Description |
|-------|--------|-------------|
| loanApplicationId | LOS | Unique loan identifier |

## Outputs Produced
| Output | Destination | Description |
|--------|-------------|-------------|
| borrower_profile | Process Context | Full borrower data |

## Exception Handling
- **ExceptionName**: Description of what triggers it and how to handle it.

## Regulatory Context
Applicable regulations with specific section citations. (CRP-XXX-XXX-003)

## Notes
Additional context, warnings, or tips.
```

### 12.2 Intent Specification (`.intent.md`)

**File naming**: `{task-slug}.intent.md` (e.g., `receive-request.intent.md`)

**Frontmatter** (validated against `intent.schema.json`):

```yaml
---
intent_id: "INT-IV-REQ-001"               # Pattern: INT-{PREFIX}-{CODE}-{SEQ}
capsule_id: "CAP-IV-REQ-001"              # Cross-ref to Knowledge Capsule
bpmn_task_id: "Task_ReceiveRequest"
version: "1.0"                             # Pattern: MAJOR.MINOR
status: "draft"                            # Same enum as capsule
goal: "Accept and validate an income verification request so that only well-formed requests enter the pipeline."
goal_type: "state_transition"              # Enum: data_production, decision, notification,
                                           #   state_transition, orchestration
preconditions:                             # Observable state conditions
  - "The message broker channel is active and accessible."
  - "The LOS has submitted a request with a valid loanApplicationId."
inputs:
  - name: "loanApplicationId"
    source: "LOS"
    schema_ref: "schemas/verification-request.json"
    required: true
  - name: "borrowerId"
    source: "LOS"
    schema_ref: "schemas/verification-request.json"
    required: true
outputs:
  - name: "borrower_profile"
    type: "object"
    sink: "Process Context"
    invariants:
      - "borrower_profile contains employment history and stated income"
  - name: "acknowledgement"
    type: "object"
    sink: "LOS"
    invariants:
      - "acknowledgement contains correlationId"
invariants:                                # Conditions that must hold at completion
  - "Every accepted request MUST have a non-empty loanApplicationId."
success_criteria:                          # Conditions confirming success
  - "A valid request is accepted and borrower_profile is populated."
failure_modes:
  - mode: "Required fields missing"
    detection: "Schema validation returns errors"
    action: "Reject request with error code ERR_INVALID_REQUEST"
  - mode: "LOS API unreachable"
    detection: "HTTP 5xx or connection timeout"
    action: "Retry with exponential backoff, max 3 attempts"
contract_ref: "ICT-IV-REQ-001"             # Cross-ref to Integration Contract
idempotency: "safe"                        # Optional. Enum: safe, unsafe
retry_policy: "exponential_backoff_3x"     # Optional string
timeout_seconds: 30                        # Optional integer >= 1
side_effects:                              # Optional string array
  - "Audit log entry created for PII access"
execution_hints:
  preferred_agent: "income-verification-agent"
  tool_access:
    - "los_api"
    - "docvault_api"
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"
generated_from: "CAP-IV-REQ-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PIM"                           # Always "PIM" for intent specs
gaps:
  - type: "missing_timeout_config"
    description: "Timeout duration not specified for document retrieval"
    severity: "low"
---
```

**Body sections**:

```markdown
# Intent: {Task Name}

## Outcome Statement
2-3 sentences describing what must be achieved (not how).

## Outcome Contract
When is this intent satisfied? References the invariants and success criteria.

## Reasoning Guidance
1. Check preconditions.
2. Validate input schema.
3. Retrieve required data from sources.
4. Verify data completeness against invariants.
5. Produce outputs to designated sinks.

## Anti-Patterns
- **Never use browser automation** to interact with the LOS.
- **Never scrape screens** for data extraction.
- **Never click UI elements** in any web interface.
- **Never use RPA-style macros** to simulate human interaction.

## Paired Capsule
See [CAP-IV-REQ-001](../capsule.md) for procedural knowledge.

## Paired Integration Contract
See [ICT-IV-REQ-001](../contract.md) for system bindings.
```

### 12.3 Integration Contract (`.contract.md`)

**File naming**: `{task-slug}.contract.md` (e.g., `receive-request.contract.md`)

**Frontmatter** (validated against `contract.schema.json`):

```yaml
---
contract_id: "ICT-IV-REQ-001"             # Pattern: ICT-{PREFIX}-{CODE}-{SEQ}
intent_id: "INT-IV-REQ-001"               # Cross-ref to Intent Specification
version: "1.0"                             # Pattern: MAJOR.MINOR
status: "draft"                            # Same lifecycle enum
binding_status: "unbound"                  # Enum: unbound, partial, bound
sources:
  - name: "Income Verification Request Queue"
    protocol: "rest"                       # Enum: rest, grpc, graphql, soap, jdbc,
                                           #   file, message_queue
    endpoint: "income.verification.requests"
    auth: "service_account"                # Optional: oauth2, api_key, mtls, etc.
    schema_ref: "schemas/verification-request.json"
    sla_ms: 1000                           # Optional integer
  - name: "LOS Borrower Profile API"
    protocol: "rest"
    endpoint: "https://los.example.com/api/v2/borrowers/{borrowerId}/profile"
    auth: "oauth2"
    schema_ref: "schemas/borrower-profile.json"
    sla_ms: 5000
sinks:
  - name: "Verification Acknowledgement Channel"
    protocol: "rest"
    endpoint: "income.verification.acknowledgements"
    auth: "service_account"
    schema_ref: "schemas/verification-ack.json"
    sla_ms: 1000
    idempotency_key: "loanApplicationId"   # Optional
events:
  - topic: "income.verification.acknowledged"
    schema_ref: "schemas/events/verification-acknowledged.json"
    delivery: "at_least_once"              # Enum: at_least_once, at_most_once, exactly_once
    key_field: "loanApplicationId"
rule_engines:                              # Optional
  - name: "Underwriting Rule Engine"
    version: "2.1"
    endpoint: "https://rules.example.com/api/v1/evaluate"
audit:
  record_type: "verification_request_intake"
  retention_years: 7
  fields_required:
    - "loanApplicationId"
    - "borrowerId"
    - "requestedBy"
    - "timestamp"
    - "agent_id"
  sink: "https://audit.example.com/api/v1/records"
generated_from: "INT-IV-REQ-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PSM"                           # Always "PSM" for contracts
unbound_sources:                           # Names of unresolved sources
  - "Message broker implementation not yet determined"
unbound_sinks:                             # Names of unresolved sinks
  - "Acknowledgement channel broker not yet determined"
---
```

**Body sections**:

```markdown
# Integration Contract: {Task Name}

## Binding Rationale
Why these specific systems/APIs were chosen for each source and sink.

## Source Details
### {Source Name}
- Protocol, endpoint, auth details, schema reference, SLA.

## Sink Details
### {Sink Name}
- Protocol, endpoint, auth details, schema reference, SLA.

## Event Details
### {Event Topic}
- Delivery semantics, key field, payload schema.

## Change Protocol
Rules for updating this contract:
- **Non-breaking**: Adding optional fields, increasing SLA budget.
- **Breaking**: Changing endpoint paths, removing fields, changing auth.

## Decommissioning
What happens when a source or sink is retired. Migration path requirements.
```

### 12.4 Corpus Document (`.corpus.md`)

**File naming**: `{slug}.corpus.md` (e.g., `income-verification-procedure.corpus.md`)

**Frontmatter** (validated against `corpus-document.schema.json`):

```yaml
---
corpus_id: "CRP-INC-PRO-001"              # Pattern: CRP-{DOMAIN}-{TYPE}-{SEQ}
title: "Income Verification Standard Procedure"
slug: "income-verification-procedure"
doc_type: "procedure"                      # Enum: procedure, policy, regulation, rule,
                                           #   data-dictionary, system, training, glossary
domain: "Mortgage Lending"
subdomain: "Income Verification"           # Optional
tags:                                      # Freeform discovery tags
  - "income"
  - "verification"
  - "w2"
applies_to:
  process_ids:                             # BPMN process IDs
    - "Process_IncomeVerification"
  task_types:                              # BPMN task type filter
    - "serviceTask"
    - "businessRuleTask"
  task_name_patterns:                      # Regex patterns for task names
    - ".*[Ii]ncome.*"
    - ".*[Vv]erif.*"
  goal_types:                              # Intent goal type filter
    - "data_production"
  roles:                                   # Role-based scoping
    - "Underwriter"
version: "1.0"                             # Pattern: MAJOR.MINOR
status: "current"                          # Enum: draft, review, current, superseded, archived
effective_date: "2024-01-15"               # Optional ISO date
review_date: "2025-01-15"                  # Optional ISO date
supersedes: null                           # Nullable corpus ID
superseded_by: null                        # Nullable corpus ID
author: "Compliance Team"
last_modified: "2024-06-01"               # ISO date
last_modified_by: "J. Smith"
source: "internal"                         # Enum: internal, external, regulatory
source_ref: null                           # Optional external reference
related_corpus_ids:                        # Cross-references
  - "CRP-INC-POL-001"
regulation_refs:                           # Applicable regulation identifiers
  - "Fannie Mae Selling Guide B3-3.1"
policy_refs:                               # Applicable policy identifiers
  - "POL-IV-001"
---
```

**Body guidance by `doc_type`**:

| `doc_type` | Expected Body Content |
|------------|----------------------|
| `procedure` | Numbered step-by-step procedure with inputs, outputs, and exception handling |
| `policy` | Policy statement, scope, applicability, enforcement, and exceptions |
| `regulation` | Regulation citation, effective date, key requirements, and compliance obligations |
| `rule` | Business rule name, condition logic (if/then), thresholds, and edge cases |
| `data-dictionary` | Field definitions table with name, type, constraints, and descriptions |
| `system` | System overview, API endpoints, authentication, data models, and SLAs |
| `training` | Training objectives, prerequisites, procedures, and assessment criteria |
| `glossary` | Term definitions in alphabetical order with context and usage examples |

### 12.5 Triple Manifest (`triple.manifest.json`)

One file per triple directory, linking the three artifacts:

```json
{
  "triple_id": "IV-REQ-001",
  "capsule_id": "CAP-IV-REQ-001",
  "intent_id": "INT-IV-REQ-001",
  "contract_id": "ICT-IV-REQ-001",
  "bpmn_task_id": "Task_ReceiveRequest",
  "bpmn_process_id": "Process_IncomeVerification",
  "status": "draft",
  "version": "1.0",
  "created": "2026-04-09T00:00:00Z",
  "last_validated": null,
  "validation_result": null,
  "provenance": {
    "bpmn_file": "income-verification.bpmn",
    "bpmn_file_hash": "sha256:a1b2c3d4e5f6...",
    "pipeline_version": "0.1.0-demo"
  }
}
```

**Field descriptions**:

| Field | Type | Required | Pattern / Enum | Description |
|-------|------|----------|----------------|-------------|
| `triple_id` | string | yes | `{PREFIX}-{CODE}-{SEQ}` | Shared suffix across capsule, intent, contract |
| `capsule_id` | string | yes | `CAP-{PREFIX}-{CODE}-{SEQ}` | Reference to Knowledge Capsule |
| `intent_id` | string | yes | `INT-{PREFIX}-{CODE}-{SEQ}` | Reference to Intent Specification |
| `contract_id` | string | yes | `ICT-{PREFIX}-{CODE}-{SEQ}` | Reference to Integration Contract |
| `bpmn_task_id` | string | yes | -- | BPMN element ID |
| `bpmn_process_id` | string | yes | -- | BPMN process ID |
| `status` | string | yes | draft/review/approved/current/deprecated/archived | Lifecycle status |
| `version` | string | yes | `MAJOR.MINOR` | Version |
| `created` | string | no | ISO 8601 datetime | Creation timestamp |
| `last_validated` | string/null | no | ISO 8601 datetime | Last validation timestamp |
| `validation_result` | string/null | no | pass/fail/skipped/null | Last validation outcome |
| `provenance` | object | yes | -- | Source traceability |
| `provenance.bpmn_file` | string | yes | -- | Source BPMN filename |
| `provenance.bpmn_file_hash` | string | yes | `sha256:{hex64}` | SHA-256 hash for integrity |
| `provenance.pipeline_version` | string | yes | -- | Pipeline version that generated this |

### 12.6 Process Manifest (`triples/_manifest.json`)

The master index listing all triples and decisions in a process:

```json
{
  "process_id": "Process_IncomeVerification",
  "process_name": "Income Verification",
  "version": "1.0.0",
  "generated_date": "2026-04-09T00:00:00Z",
  "generated_by": "MDA Demo",
  "pipeline_version": "0.1.0-demo",
  "triple_count": 8,
  "triples": [
    {
      "capability_id": "ICT-IV-REQ-001",
      "directory": "receive-request",
      "bpmn_element_id": "Task_ReceiveRequest",
      "element_type": "receiveTask",
      "binding_status": "unbound"
    }
  ],
  "decisions": [
    {
      "capability_id": "ICT-IV-DEC-001",
      "directory": "../decisions/employment-type",
      "bpmn_element_id": "Gateway_EmploymentType",
      "element_type": "exclusiveGateway",
      "binding_status": "unbound"
    }
  ],
  "stats": {
    "total_triples": 8,
    "bound": 0,
    "unbound": 8,
    "binding_coverage": "0%"
  }
}
```

**Field descriptions**:

| Field | Type | Description |
|-------|------|-------------|
| `process_id` | string | BPMN process ID |
| `process_name` | string | Human-readable name |
| `version` | string | Process version |
| `generated_date` | string | ISO 8601 timestamp |
| `generated_by` | string | Generator identity |
| `pipeline_version` | string | Pipeline version |
| `triple_count` | integer | Total triples + decisions |
| `triples[].capability_id` | string | Capability ID (`ICT-{PREFIX}-{CODE}-{SEQ}`) |
| `triples[].directory` | string | Relative path to triple directory |
| `triples[].bpmn_element_id` | string | BPMN element ID |
| `triples[].element_type` | string | BPMN element type |
| `triples[].binding_status` | string | unbound/partial/bound |
| `decisions[]` | array | Same structure as triples, for gateway elements |
| `stats.total_triples` | integer | Sum of triples + decisions |
| `stats.bound` | integer | Count with binding_status "bound" |
| `stats.unbound` | integer | Count with binding_status "unbound" |
| `stats.binding_coverage` | string | Percentage bound (e.g., "0%") |

### 12.7 Corpus Index (`corpus/corpus.config.yaml`)

The searchable index generated by `mda corpus index`:

```yaml
version: "1.0"
generated_date: "2026-04-09T00:00:00Z"
document_count: 12
documents:
  - corpus_id: "CRP-INC-PRO-001"
    title: "Income Verification Standard Procedure"
    doc_type: "procedure"
    domain: "Mortgage Lending"
    subdomain: "Income Verification"
    path: "mortgage-lending/procedures/income-verification-procedure.corpus.md"
    tags:
      - "income"
      - "verification"
      - "w2"
    applies_to:
      process_ids:
        - "Process_IncomeVerification"
      task_types:
        - "serviceTask"
      task_name_patterns:
        - ".*[Ii]ncome.*"
      goal_types:
        - "data_production"
      roles:
        - "Underwriter"
    status: "current"
```

Each entry in `documents[]` mirrors the frontmatter of the corresponding `.corpus.md` file, plus a `path` field giving the relative path from the corpus root to the file.

### 12.8 Process Graph (`graph/process-graph.yaml`)

Structured representation of the process flow:

```yaml
process:
  id: "Process_IncomeVerification"
  name: "Income Verification"
  version: "1.0.0"

nodes:
  - id: "Start_Requested"
    type: "startEvent"                     # BPMN element type
    name: "Verification Requested"
    successors: ["Task_ReceiveRequest"]

  - id: "Task_ReceiveRequest"
    type: "receiveTask"
    name: "Receive Verification Request"
    capability_id: "ICT-IV-REQ-001"        # Link to triple
    lane: "Lane_UnderwritingSystem"
    predecessors: ["Start_Requested"]
    successors: ["Task_ClassifyEmployment"]
    data_outputs: ["borrower_profile"]

  - id: "Gateway_EmploymentType"
    type: "exclusiveGateway"
    name: "W-2 or Self-Employed?"
    capability_id: "ICT-IV-DEC-001"
    predecessors: ["Task_ClassifyEmployment"]
    successors: ["Task_VerifyW2", "Task_VerifySelfEmployment"]
    branches:
      - condition: "${employmentType == 'W2'}"
        target: "Task_VerifyW2"
      - condition: "${employmentType == 'SELF_EMPLOYED'}"
        target: "Task_VerifySelfEmployment"

  - id: "End_Verified"
    type: "endEvent"
    name: "Income Verified"
    predecessors: ["Task_EmitVerified"]

  - id: "End_VarianceException"
    type: "endEvent"
    name: "Variance Exception"
    error_code: "ERR_VARIANCE_001"
    predecessors: ["Gateway_Variance"]

edges:
  - id: "Flow_StartToReceive"
    source: "Start_Requested"
    target: "Task_ReceiveRequest"

  - id: "Flow_GatewayToW2"
    source: "Gateway_EmploymentType"
    target: "Task_VerifyW2"
    label: "W-2 Employee"
    condition: "${employmentType == 'W2'}"

data_objects:
  - id: "borrower_profile"
    produced_by: "Task_ReceiveRequest"
    consumed_by: ["Task_ClassifyEmployment"]

  - id: "tax_returns"
    produced_by: "external"
    consumed_by: ["Task_VerifyW2", "Task_VerifySelfEmployment"]
```

**Node fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | BPMN element ID |
| `type` | string | yes | BPMN element type |
| `name` | string | yes | Human-readable name |
| `capability_id` | string | no | Link to the triple's capability ID |
| `lane` | string | no | Lane ID |
| `predecessors` | string[] | no | Predecessor node IDs |
| `successors` | string[] | no | Successor node IDs |
| `data_inputs` | string[] | no | Data object IDs consumed |
| `data_outputs` | string[] | no | Data object IDs produced |
| `branches` | object[] | no | Gateway-only: condition/target pairs |
| `error_code` | string | no | End event error code |

**Edge fields**: `id`, `source`, `target`, `label` (optional), `condition` (optional).

**Data object fields**: `id`, `produced_by` (node ID or "external"), `consumed_by` (node ID array).

### 12.9 Graph Visualization (`graph/graph-visual.md`)

Mermaid flowchart format with typed node shapes:

```markdown
# {Process Name} Process Graph

```mermaid
flowchart TD
    %% Events use double-circle notation
    Start_Requested(("Verification\nRequested"))
    End_Verified(("Income\nVerified"))

    %% Tasks use rectangle notation with type annotation
    Task_ReceiveRequest["Receive Verification\nRequest\n<i>receiveTask</i>"]
    Task_ClassifyEmployment["Classify Employment\nType\n<i>businessRuleTask</i>"]

    %% Gateways use diamond notation
    Gateway_EmploymentType{"W-2 or\nSelf-Employed?"}

    %% Data objects use cylinder notation
    borrower_profile[(borrower_profile)]

    %% Sequence flows (solid arrows)
    Start_Requested --> Task_ReceiveRequest
    Task_ReceiveRequest --> Task_ClassifyEmployment

    %% Conditional flows (labeled arrows)
    Gateway_EmploymentType -->|"W-2 Employee"| Task_VerifyW2

    %% Data flows (dashed arrows)
    Task_ReceiveRequest -.-> borrower_profile
    borrower_profile -.-> Task_ClassifyEmployment

    %% Style classes
    classDef startEnd fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
    classDef task fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef gateway fill:#fce4ec,stroke:#c62828,stroke-width:2px
    classDef data fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px,stroke-dasharray: 5

    class Start_Requested,End_Verified startEnd
    class Task_ReceiveRequest,Task_ClassifyEmployment task
    class Gateway_EmploymentType gateway
    class borrower_profile data
`` `
```

**Node shape conventions**:

| Element Category | Mermaid Shape | Example |
|-----------------|---------------|---------|
| Start/End Events | `(("label"))` | Double circle |
| Tasks (all types) | `["label\n<i>type</i>"]` | Rectangle with type annotation |
| Gateways | `{"label"}` | Diamond |
| Data Objects | `[("label")]` | Cylinder |

**Arrow conventions**:

| Connection Type | Mermaid Syntax | Description |
|----------------|----------------|-------------|
| Sequence flow | `-->` | Solid arrow |
| Conditional flow | `-->|"label"|` | Solid arrow with label |
| Data flow | `-.->` | Dashed arrow |

**Style classes**:

| Class | Fill | Stroke | Applied To |
|-------|------|--------|-----------|
| `startEnd` | `#e1f5fe` (light blue) | `#0288d1` (blue) | Start and end events |
| `task` | `#fff3e0` (light orange) | `#f57c00` (orange) | All task types |
| `gateway` | `#fce4ec` (light pink) | `#c62828` (red) | All gateway types |
| `data` | `#e8f5e9` (light green) | `#2e7d32` (green), dashed | Data objects |

Below the Mermaid diagram, the file includes:
- **Lane Assignments** table: Lane name to task list mapping
- **Data Flow Summary** table: Data object to producer/consumer mapping
