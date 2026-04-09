# Corpus Authoring Guide

This guide is for subject-matter experts (SMEs) who write and maintain knowledge corpus documents. The corpus is the foundation of the MDA Intent Layer -- everything an agent needs to know about how your business works starts here.

## What Is the Corpus?

The knowledge corpus is a collection of structured Markdown documents that capture your organization's procedures, policies, regulations, business rules, data definitions, system references, training materials, and terminology. Each document lives in the `corpus/` directory and follows a standard format.

When the MDA pipeline processes a BPMN diagram, it matches corpus documents to each task using metadata in the document frontmatter. The enrichment stage (Stage 2) reads your corpus documents and uses them to generate rich, accurate capsules. If a procedure is missing from the corpus, the generated capsule will have gaps -- incomplete or placeholder content that someone will need to fill in later.

**In short: the better your corpus, the better your generated artifacts.**

## The 8 Document Types

The corpus taxonomy defines eight document types. Each serves a distinct purpose. Use the right type for the content you are writing.

### procedure (PRC)

Step-by-step operational instructions for carrying out a specific business activity. Use this when documenting how to do something.

**Example**: `corpus/procedures/w2-income-verification.corpus.md` describes the full procedure for verifying W-2 wage income, from collecting documents through calculating monthly income.

**When to use**: You have a repeatable process with numbered steps that a person (or agent) follows from start to finish.

### policy (POL)

High-level organizational directives that establish rules, boundaries, and decision-making authority. Use this for the "what" and "why," not the "how."

**Example**: `corpus/policies/document-retention-policy.corpus.md` establishes that all income documents must be retained for 7 years and defines who authorizes destruction.

**When to use**: You are documenting organizational requirements, authority levels, or governance rules -- not step-by-step procedures.

### regulation (REG)

External regulatory requirements imposed by governing bodies. These are not your organization's rules -- they come from regulators, statutes, or agency guidelines.

**Example**: `corpus/regulations/tila-summary.corpus.md` summarizes the Truth in Lending Act requirements including TRID timing rules and fee tolerances.

**When to use**: You are summarizing a law, regulation, or agency guideline (Fannie Mae, FHA, CFPB) that your processes must comply with.

### rule (RUL)

Discrete, testable business logic statements that govern decisions, validations, calculations, or routing. Rules are precise enough to be implemented in code.

**Example**: `corpus/rules/employment-type-classification.corpus.md` defines a decision table that classifies borrowers as W-2 employees, self-employed, commissioned, part-time, military, etc.

**When to use**: You have a specific decision with clear conditions and outcomes -- something that could be expressed as "if X then Y."

### data-dictionary (DAT)

Definitions, formats, valid ranges, and lineage for data elements used in a process.

**Example**: `corpus/data-dictionary/income-verification-data.corpus.md` defines the `borrower_income`, `income_source`, and `verification_result` objects with every field, type, and constraint.

**When to use**: You need to define what data flows through a process, what each field means, what values are valid, and where data comes from and goes.

### system (SYS)

Technical documentation for systems, APIs, integrations, and infrastructure that support business processes.

**Example**: `corpus/systems/los-integration-guide.corpus.md` documents the Loan Origination System API endpoints, authentication, data formats, and event topics.

**When to use**: You are documenting a system that your processes interact with -- its capabilities, APIs, data formats, and SLAs.

### training (TRN)

Educational content used for onboarding, upskilling, or certification.

**Example**: `corpus/training/loan-processor-onboarding.corpus.md` is a comprehensive onboarding guide for new loan processors covering the mortgage lifecycle, systems, and compliance essentials.

**When to use**: You are writing material that teaches someone how to do their job, not documenting a specific procedure.

### glossary (GLO)

Domain-specific terminology definitions providing a shared vocabulary.

**Example**: `corpus/glossary/mortgage-lending-glossary.corpus.md` defines terms like "DTI," "LTV," "TRID," and "AUS" with context about where each term is used.

**When to use**: You need to establish consistent definitions for terms used across multiple documents.

## File Format

Every corpus document is a Markdown file with the extension `.corpus.md`. The file has two parts:

1. **YAML frontmatter** between `---` fences at the top
2. **Markdown body** below the frontmatter

Here is the basic structure:

```markdown
---
corpus_id: "CRP-PRC-IV-001"
title: "W-2 Income Verification Procedure"
slug: "w2-income-verification"
doc_type: "procedure"
domain: "Mortgage Lending"
subdomain: "Income Verification"
tags:
  - "w-2"
  - "wage-income"
  - "income-verification"
applies_to:
  process_ids:
    - "Process_IncomeVerification"
  task_types:
    - "userTask"
    - "serviceTask"
  task_name_patterns:
    - "verify.*w-?2"
    - "verify.*wage"
  goal_types:
    - "data_production"
  roles:
    - "loan_processor"
    - "underwriter"
version: "1.0"
status: "draft"
effective_date: "2025-03-01"
review_date: "2026-03-01"
author: "Operations Standards Committee"
last_modified: "2025-02-15"
last_modified_by: "J. Whitfield"
source: "internal"
related_corpus_ids:
  - "CRP-RUL-IV-001"
regulation_refs:
  - "Fannie Mae Selling Guide B3-3.1-09"
policy_refs:
  - "POL-IV-004"
---

# W-2 Income Verification Procedure

## 1. Scope

This procedure governs the verification and calculation of...
```

## Creating a New Corpus Document

The fastest way to create a new corpus document is with the CLI:

```bash
mda corpus add <type> --title "<title>" --domain "<domain>"
```

For example, to create a new procedure document:

```bash
mda corpus add procedure --title "FHA Streamline Refinance Procedure" --domain "Mortgage Lending"
```

This creates a scaffolded file at `corpus/procedures/fha-streamline-refinance-procedure.corpus.md` with all required frontmatter fields pre-populated and body section templates based on the document type.

The available types are: `procedure`, `policy`, `regulation`, `rule`, `data-dictionary`, `system`, `training`, `glossary`.

Each type is placed in its own subdirectory automatically:

| Type | Directory | ID Prefix |
|------|-----------|-----------|
| procedure | `corpus/procedures/` | PRC |
| policy | `corpus/policies/` | POL |
| regulation | `corpus/regulations/` | REG |
| rule | `corpus/rules/` | RUL |
| data-dictionary | `corpus/data-dictionary/` | DAT |
| system | `corpus/systems/` | SYS |
| training | `corpus/training/` | TRN |
| glossary | `corpus/glossary/` | GLO |

## Frontmatter Fields Explained

### Identity fields

- **corpus_id**: A unique identifier following the pattern `CRP-<PREFIX>-<DOMAIN>-<SEQ>`. For example, `CRP-PRC-IV-001` is the first procedure in the Income Verification domain. The CLI generates this automatically.
- **title**: A human-readable title for the document.
- **slug**: A URL-friendly version of the title, used as the filename. Generated automatically from the title.
- **doc_type**: One of the 8 document types listed above.
- **domain**: The business domain this document belongs to (e.g., "Mortgage Lending").
- **subdomain**: A more specific area within the domain (e.g., "Income Verification").

### Matching fields (applies_to)

These fields control how the enrichment pipeline finds your document when generating capsules for BPMN tasks. See the "How applies_to Matching Works" section below for details.

- **process_ids**: List of BPMN process IDs this document applies to.
- **task_types**: List of BPMN task types (e.g., `userTask`, `serviceTask`, `businessRuleTask`).
- **task_name_patterns**: Regex patterns matched against BPMN task names. This is the most important matching field.
- **goal_types**: The type of work the task performs (e.g., `data_production`, `decision`, `compliance`).
- **roles**: Roles that perform this work (e.g., `loan_processor`, `underwriter`).

### Tagging and discovery

- **tags**: A list of keywords for search and discovery. Tags are matched during corpus search and also used by the enrichment pipeline. Be thorough -- tags drive discovery.

### Lifecycle fields

- **version**: The document version (e.g., "2.1").
- **status**: The lifecycle state (see "Document Lifecycle" below).
- **effective_date**: When the document becomes authoritative.
- **review_date**: When the document is due for periodic review.
- **supersedes**: The corpus_id of a document this one replaces (or null).
- **superseded_by**: The corpus_id of a document that replaces this one (or null).

### Authorship

- **author**: Who originally wrote the document.
- **last_modified**: Date of the most recent change.
- **last_modified_by**: Who made the most recent change.
- **source**: Where the content comes from (`internal`, `regulatory`, `vendor`, `external`).
- **source_ref**: A reference number for the original source document.

### Cross-references

- **related_corpus_ids**: Other corpus documents that are related to this one.
- **regulation_refs**: Specific regulatory citations (e.g., "Fannie Mae Selling Guide B3-3.1-09").
- **policy_refs**: Internal policy references.

## Body Section Templates

Each document type has expected body sections defined in the ontology. When you use `mda corpus add`, these sections are scaffolded automatically. Here are the expected sections for each type:

### procedure

1. **Purpose** -- Why this procedure exists
2. **Scope** -- What it covers and does not cover
3. **Prerequisites** -- What must be in place before starting
4. **Procedure Steps** -- Numbered steps to follow
5. **Exception Handling** -- What to do when things go wrong
6. **Related Documents** -- Links to related corpus docs

### policy

1. **Purpose** -- Why this policy exists
2. **Scope** -- What it covers
3. **Policy Statement** -- The actual policy directives
4. **Roles and Responsibilities** -- Who does what
5. **Compliance Requirements** -- How compliance is measured
6. **Exceptions** -- When exceptions are allowed
7. **Related Documents** -- Links to related corpus docs

### regulation

1. **Regulation Summary** -- Plain-language summary of the regulation
2. **Applicability** -- Who and what the regulation applies to
3. **Key Requirements** -- The specific requirements
4. **Compliance Obligations** -- What your organization must do
5. **Penalties and Enforcement** -- Consequences of non-compliance
6. **Source References** -- Citations to the actual regulation text

### rule

1. **Rule Statement** -- The business rule in plain language
2. **Conditions** -- When the rule applies
3. **Actions** -- What happens when conditions are met
4. **Exceptions** -- When the rule does not apply
5. **Examples** -- Concrete examples showing the rule in action
6. **Source Authority** -- Where the rule comes from

### data-dictionary

1. **Overview** -- What data domain this covers
2. **Field Definitions** -- Table of fields with types, constraints, and descriptions
3. **Valid Values** -- Enumerated values for coded fields
4. **Data Lineage** -- Where data comes from and where it goes
5. **Validation Rules** -- Rules for data quality
6. **Related Systems** -- Systems that produce or consume this data

### system

1. **System Overview** -- What the system does
2. **Capabilities** -- What functions it provides
3. **Interfaces and APIs** -- Endpoints, protocols, authentication
4. **Data Flows** -- What data moves in and out
5. **Dependencies** -- Other systems it depends on
6. **SLA and Availability** -- Performance and uptime expectations

### training

1. **Learning Objectives** -- What the learner will know or be able to do
2. **Prerequisites** -- Prior knowledge or access required
3. **Content** -- The actual training material
4. **Exercises** -- Practice activities
5. **Assessment Criteria** -- How competency is measured
6. **References** -- Additional reading and resources

### glossary

1. **Scope** -- What domain or area the glossary covers
2. **Terms and Definitions** -- The term table
3. **Abbreviations** -- Acronym and abbreviation list
4. **Related Glossaries** -- Links to other glossaries

## How applies_to Matching Works

When the MDA pipeline enriches a BPMN task, it searches the corpus for documents that are relevant to that task. The enricher scores each corpus document against the task based on the `applies_to` fields:

1. **process_ids**: Does the document's process_ids list include the BPMN process ID? This is a broad filter -- a document that applies to `Process_IncomeVerification` will be considered for every task in that process.

2. **task_types**: Does the document's task_types list include the BPMN task type (e.g., `userTask`, `serviceTask`)? This is another broad filter.

3. **task_name_patterns**: Does any regex pattern match the BPMN task name? This is the most specific and highest-weight match. A pattern like `verify.*w-?2` will match tasks named "Verify W-2 Income" or "Verify W2 Documents."

4. **goal_types**: Does the task's inferred goal type match? Goal types like `data_production`, `decision`, and `compliance` help the enricher pick the right documents.

5. **roles**: Does the task's assigned role match any role in the document? This helps when multiple procedures exist for different roles.

Documents with more matching criteria rank higher and are more likely to be used by the enricher to populate the capsule.

## Writing Effective task_name_patterns

The `task_name_patterns` field uses Python regex syntax. Patterns are matched case-insensitively against the BPMN task name. Here are practical tips:

**Be specific enough to avoid false matches:**

```yaml
# Good - matches "Verify W-2 Income" and "Review W-2 Documents"
task_name_patterns:
  - "verify.*w-?2"
  - "review.*w-?2"

# Too broad - matches any task with "verify" in the name
task_name_patterns:
  - "verify"
```

**Use `.*` to match any characters between words:**

```yaml
# Matches "Calculate Qualifying Income" and "Calculate Total Qualifying Income"
task_name_patterns:
  - "calculate.*qualifying.*income"
```

**Use `?` for optional characters and `-?` for optional hyphens:**

```yaml
# Matches both "W-2" and "W2"
task_name_patterns:
  - "w-?2"
```

**Use `|` for alternatives:**

```yaml
# Matches tasks about either appraisal ordering or appraisal review
task_name_patterns:
  - "(order|review).*appraisal"
```

**Use word boundaries for precision when needed:**

```yaml
# Matches "DTI Assessment" but not "EditItem"
task_name_patterns:
  - "\\bdti\\b"
```

**Common patterns from the demo corpus:**

| Pattern | Matches |
|---------|---------|
| `verify.*w-?2` | Verify W-2 Income, Verify W2 Documents |
| `classify.*employment` | Classify Employment Type |
| `calculate.*qualifying` | Calculate Qualifying Income |
| `order.*appraisal` | Order Appraisal |
| `.*income.*` | Any task with "income" in the name |
| `.*document.*` | Any task with "document" in the name |

## Cross-Referencing

Corpus documents do not exist in isolation. Use the cross-reference fields to connect related documents:

**related_corpus_ids** -- Link to other corpus documents that are directly related. For example, a procedure document should reference the rules it applies and the data dictionary it uses:

```yaml
related_corpus_ids:
  - "CRP-RUL-IV-001"   # Employment Type Classification Rules
  - "CRP-RUL-IV-002"   # Income Variance Thresholds
  - "CRP-DAT-IV-001"   # Income Verification Data Objects
```

**regulation_refs** -- Cite the specific regulatory sections that govern this procedure:

```yaml
regulation_refs:
  - "Fannie Mae Selling Guide B3-3.1-09"
  - "FHA 4000.1 II.A.4.c.2"
  - "VA Pamphlet 26-7 Ch. 4"
```

**policy_refs** -- Reference internal policies that set the rules for this procedure:

```yaml
policy_refs:
  - "POL-IV-004"
  - "POL-DOC-001"
```

These references flow through to the generated capsules and intent specs, giving agents (and reviewers) a clear audit trail back to authoritative sources.

## Document Lifecycle

Corpus documents progress through a linear lifecycle. Only documents in `current` status are used as authoritative sources during intent generation.

```
draft -> review -> current -> superseded -> archived
```

| Status | Meaning | Used for Generation? |
|--------|---------|---------------------|
| `draft` | Initial authoring, not yet reviewed | No |
| `review` | Under review by SMEs or compliance | No |
| `current` | Active, authoritative version | Yes |
| `superseded` | Replaced by a newer version; kept for audit | No |
| `archived` | No longer in use; kept for history | No |

**Transitions:**
- `draft` can move to `review`
- `review` can move back to `draft` (needs rework) or forward to `current` (approved)
- `current` can move to `superseded` (when a new version replaces it) or `archived`
- `superseded` can move to `archived`
- `archived` is a terminal state

When you supersede a document, update both the old and new documents:

```yaml
# Old document (now superseded)
status: "superseded"
superseded_by: "CRP-PRC-IV-002"

# New document (now current)
status: "current"
supersedes: "CRP-PRC-IV-001"
```

## Validating Your Work

After writing or editing a corpus document, validate it against the schema:

```bash
mda corpus validate
```

This checks every `.corpus.md` file in the corpus directory against the corpus document schema. It verifies that:

- All required frontmatter fields are present
- Field values match expected types and formats
- Enumerated values (like `doc_type` and `status`) are valid
- The `applies_to` structure is correctly formed

Example output:

```
Corpus Validation (46 files)
  All 46 corpus documents pass schema validation
```

If there are errors, you will see specific messages:

```
Corpus Validation (46 files)
  procedures/new-procedure.corpus.md:
    applies_to.task_name_patterns: Expected array, got string
    status: Invalid value "active" (expected: draft, review, current, superseded, archived)
```

Fix the indicated issues and run validation again.

## Rebuilding the Index

The corpus index (`corpus/corpus.config.yaml`) is a summary file that lists all corpus documents with their metadata. The enrichment pipeline uses this index to quickly find relevant documents. Rebuild it after adding, removing, or renaming corpus documents:

```bash
mda corpus index
```

Example output:

```
Indexed 46 corpus documents -> corpus/corpus.config.yaml
```

You can also search the index to find documents:

```bash
mda corpus search "income verification"
```

```bash
mda corpus search "appraisal" --type procedure
```

```bash
mda corpus search "compliance" --domain "Mortgage Lending"
```

## Best Practices

### Write procedures as numbered steps

Procedures should be actionable. Use numbered steps with clear, imperative instructions. Each step should describe one action and its expected result.

```markdown
### Step 3: Calculate Base Income

3.1. If salaried: Use the annual salary stated on the VOE or offer letter,
     divided by 12.

3.2. If hourly: Multiply hourly rate by guaranteed weekly hours, then
     apply the frequency conversion:
     - Weekly: multiply by 52, divide by 12
     - Bi-weekly: multiply by 26, divide by 12
     - Semi-monthly: multiply by 24, divide by 12
```

### Include regulatory citations

When a step or rule is driven by a regulation, cite the specific section. This gives agents and reviewers a traceable path to the authoritative source.

```markdown
- Overtime must have a documented two-year history to be used as
  qualifying income (Fannie Mae Selling Guide B3-3.1-01).
```

### Use consistent terminology

Refer to the glossary for standard terms. If your domain has a glossary corpus document (like `CRP-GLO-MTG-001`), use the defined terms consistently. Write "DTI" not "debt ratio." Write "URLA" not "loan application form."

### Keep documents focused

One procedure per file. One regulation summary per file. Do not combine the W-2 verification procedure and the self-employment verification procedure in a single document -- they apply to different BPMN tasks and should be matched independently.

### Tag thoroughly

Tags drive discovery. Include:
- The specific subject (`w-2`, `appraisal`, `credit-report`)
- Related concepts (`wage-income`, `employment-income`)
- Relevant roles (`loan_processor`, `underwriter`)
- Loan programs if applicable (`fha`, `va`, `conventional`)

The more relevant tags you add, the more likely the enricher will find your document for the right tasks.

### Include quality checks and common pitfalls

Procedures benefit greatly from a "Quality Checks" table and a "Common Pitfalls" section. These translate directly into invariants and failure modes in the generated intent specs.

### Use tables for structured information

Decision tables, field definitions, retention schedules, and checklists are far more useful in table format than in prose. Tables are easier for the LLM to parse and translate into structured artifacts.

### Document exception handling

Every procedure should address what happens when things go wrong. What if a document is missing? What if data does not match? What if a threshold is exceeded? These exceptions become failure modes in the intent spec.

### Keep revision history

Maintain a revision history table at the bottom of the document. This is especially important for procedures and policies where auditors may need to know what changed and when.

```markdown
## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.1 | 2025-02-15 | J. Whitfield | Updated trending thresholds |
| 2.0 | 2024-06-01 | J. Whitfield | Major revision |
| 1.0 | 2022-01-10 | Operations Standards | Initial release |
```
