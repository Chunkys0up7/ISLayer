# MDA Intent Layer — Grounding Agent Specification

## Document Control

| Field              | Value                                              |
| ------------------ | -------------------------------------------------- |
| **Spec ID**        | GROUNDING-AGENT-SPEC-001                           |
| **Version**        | 1.0                                                |
| **Status**         | Draft                                              |
| **Author**         | MDA Intent Layer Team                              |
| **Created**        | 2026-04-14                                         |
| **Target**         | Inside-firewall reimplementation                   |
| **Related Specs**  | EXECUTION-SPEC.md, TEST-SPEC.md                    |

---

## 1. Executive Summary

This specification defines the architecture and implementation of a **zero-hallucination grounding system** for the MDA Intent Layer. The system ensures that every factual claim in generated triple artifacts (capsules, intent specs, integration contracts) is traceable to a specific section of a specific corpus document, with no LLM-invented content.

### 1.1 Problem Statement

The current pipeline suffers from three categories of grounding failures:

1. **Matching failures** — Corpus documents are matched to BPMN tasks using metadata-only scoring (tags, process IDs). Relevant documents with slightly different vocabulary are missed, while loosely related documents with one overlapping keyword are incorrectly included.

2. **Content injection failures** — Corpus document bodies are truncated to 2000 characters before injection into LLM prompts, losing critical procedure steps, business rules, and regulatory requirements. The LLM fills gaps from its training data, producing plausible but ungrounded content.

3. **Job aid disconnection** — Job aid decision tables (condition/action lookup rules) are never referenced during triple generation. They exist as separate artifacts with no integration into the capsule, intent, or contract generation pipeline.

### 1.2 Solution Overview

The grounding agent replaces the current LLM-centric generation approach with an **extraction-based architecture** where:

- The LLM acts as an **editor** (organizes extracted content) rather than an **author** (creates content)
- Corpus matching uses a **multi-signal weighted scoring algorithm** with configurable weights
- Corpus content is extracted at **section level** (no truncation) and injected into prompts by section type
- **Job aids** are injected as structured decision tables during capsule generation
- Every generated artifact undergoes **automated grounding verification** that checks citation completeness
- A **provenance chain** in frontmatter traces every field to its source (corpus document + section + item)

---

## 2. Architecture

### 2.1 Pipeline Overview

```
BPMN XML ──► Stage 1 (Parse) ──► ParsedModel
                                       │
                                       ▼
Corpus Index ──► Stage 2 (Enrich) ──► EnrichedModel
  ├─ .corpus.md files                  ├─ Multi-signal weighted matching
  ├─ .jobaid.yaml files                ├─ Section-level content extraction
  └─ corpus.config.yaml                ├─ Job aid discovery
                                       └─ Gap detection
                                       │
                                       ▼
                          Stage 3 (Capsule Generator)
                          ├─ Grounded content injection (by section)
                          ├─ Job aid injection (deterministic)
                          ├─ LLM edits (not authors)
                          └─ Post-generation verification
                                       │
                                       ▼
                          Stage 4 (Intent Generator)
                          ├─ Preconditions from capsule corpus refs
                          ├─ Invariants from capsule business rules
                          ├─ Failure modes from capsule exceptions
                          └─ Job aid dimensions as inputs/outputs
                                       │
                                       ▼
                          Stage 5 (Contract Generator)
                          ├─ Sources/sinks from intent inputs/outputs
                          └─ System docs from corpus
                                       │
                                       ▼
                          Stage 6 (Validator)
                          ├─ Schema validation
                          ├─ Cross-reference integrity
                          └─ Grounding verification check
```

### 2.2 Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Grounding Agent System                       │
│                                                                  │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ Multi-Signal  │  │ Section-Level    │  │ Grounding        │  │
│  │ Scorer        │  │ Extractor        │  │ Verifier         │  │
│  │               │  │                  │  │                  │  │
│  │ 7 weighted    │  │ Parses markdown  │  │ Checks citations │  │
│  │ factors +     │  │ into sections.   │  │ against provided │  │
│  │ 3-tier        │  │ Maps to capsule  │  │ corpus IDs.      │  │
│  │ matching      │  │ section types.   │  │ Flags uncited    │  │
│  │               │  │ No truncation.   │  │ sections.        │  │
│  └──────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                  │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ Job Aid      │  │ Editor Prompt    │  │ Provenance       │  │
│  │ Injector     │  │ Engine           │  │ Tracker          │  │
│  │               │  │                  │  │                  │  │
│  │ Discovers    │  │ LLM organizes    │  │ Records source   │  │
│  │ .jobaid.yaml │  │ extracted content│  │ corpus_id +      │  │
│  │ files. Renders│  │ NOT generates.  │  │ section + match  │  │
│  │ as markdown  │  │ All claims must  │  │ method + score   │  │
│  │ tables.      │  │ cite corpus IDs. │  │ for every field. │  │
│  └──────────────┘  └──────────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Multi-Signal Weighted Corpus Matching

### 3.1 Three-Tier Architecture

#### Tier 1: Deterministic Match (Score = 1.0)

Corpus documents whose `applies_to.process_ids` contains the BPMN process ID **AND** whose `applies_to.task_name_patterns` contains a regex matching the BPMN task name. This is the gold standard match.

If only `task_name_patterns` matches (no process ID match), score = 0.8.

#### Tier 2: Multi-Factor Weighted Score (Score = 0.0–1.0)

Seven factors, each with a configurable weight that sums to 1.0:

| Factor | Weight | Description | Scoring |
| --- | --- | --- | --- |
| **Subdomain match** | 0.25 | Corpus subdomain tokens overlap with process name tokens | `\|overlap\| / \|subdomain_tokens\|` |
| **Tag overlap ratio** | 0.20 | Corpus tags overlap with BPMN task name tokens | `\|overlap\| / \|task_name_tokens\|` (ratio, not binary) |
| **Doc type relevance** | 0.15 | Procedure > Rule > Policy > Regulation > Data-Dict > System > Training > Glossary | Lookup score from configurable table |
| **Role match** | 0.10 | Corpus `applies_to.roles` contains the BPMN lane name | Boolean (full weight or zero) |
| **Data object match** | 0.15 | BPMN data associations match corpus tags | `\|data_overlap\| / \|data_tokens\|` |
| **Related corpus bonus** | 0.10 | Corpus `related_corpus_ids` overlaps with previously matched corpus IDs | Boolean (context-aware sequential boost) |
| **Goal type match** | 0.05 | Corpus `applies_to.goal_types` contains the node's default goal type | Boolean |

**Key differences from previous system:**
- Tag overlap is a **ratio** (3/4 tags matching scores higher than 1/4), not binary
- **Data object matching** considers BPMN data associations, not just the task name
- **Related corpus bonus** provides workflow-context-aware matching: if the previous task matched CRP-PRC-IV-001, this task gets a boost for documents in the same `related_corpus_ids` family
- **Goal type matching** uses the `applies_to.goal_types` field that was previously defined but never used

#### Tier 3: LLM Disambiguation (Tie-Breaking Only)

When multiple documents score within the configurable `disambiguation_band` (default 0.1) of each other, the LLM is asked to evaluate which candidates are most relevant. The LLM **does not find new documents** — it only picks between pre-filtered candidates.

### 3.2 Configuration

All matching parameters are configurable via `mda.config.yaml`:

```yaml
enrichment:
  match_threshold: 0.4          # Minimum score to consider a match
  high_confidence: 0.8           # Score >= this is "high" confidence
  medium_confidence: 0.5         # Score >= this is "medium" confidence
  max_matches_per_type: 3        # Maximum corpus matches per doc_type per node
  disambiguation_band: 0.1       # LLM breaks ties within this score range
  weights:
    subdomain_match: 0.25
    tag_overlap_ratio: 0.20
    doc_type_relevance: 0.15
    role_match: 0.10
    data_object_match: 0.15
    related_corpus_bonus: 0.10
    goal_type_match: 0.05
  doc_type_relevance_scores:
    procedure: 1.0
    rule: 0.9
    policy: 0.8
    regulation: 0.8
    data-dictionary: 0.7
    system: 0.6
    training: 0.4
    glossary: 0.3
```

### 3.3 Match Result Structure

Each match produces a `CorpusMatch` with:

```python
@dataclass
class CorpusMatch:
    corpus_id: str           # e.g., "CRP-PRC-IV-001"
    match_confidence: str    # "high" | "medium" | "low"
    match_method: str        # "exact_id" | "name_pattern" | "weighted_multi_signal"
    match_score: float       # 0.0 to 1.0+
```

---

## 4. Section-Level Corpus Extraction

### 4.1 Problem: Truncation

The previous system truncated corpus documents to 2000 characters. A typical W-2 verification procedure has 8+ steps with sub-steps, each with regulatory citations. Truncation loses steps 4-8 and all regulatory context, forcing the LLM to invent content.

### 4.2 Solution: Section Extraction

Instead of injecting entire documents, the system:

1. **Parses** each corpus document's markdown body into sections (split on `##` headings)
2. **Maps** each section to a capsule section type using keyword matching:

| Capsule Section | Corpus Section Keywords |
| --- | --- |
| Procedure | procedure, steps, process, workflow, instructions, method |
| Business Rules | rule, business rule, threshold, limit, constraint, criteria, decision |
| Inputs/Outputs | input, output, data, field, schema, object, element |
| Exception Handling | exception, error, edge case, escalat, fallback, override |
| Regulatory Context | regulat, compliance, requirement, fannie, fha, va, usda, guideline, policy, mandate |

3. **Injects** only the relevant sections into the prompt, organized by capsule section type
4. **No truncation** — full section content is included. Token budget management prioritizes higher-confidence matches.

### 4.3 API

```python
def extract_corpus_sections(corpus_dir, corpus_id, section_filter=None) -> list[dict]:
    """Extract sections from a corpus document.
    Returns [{heading, content, corpus_id, doc_title, doc_type, level}]
    """

def extract_grounded_content(corpus_dir, enrichment, node_element_type) -> dict:
    """Extract section-level content from ALL matched corpus docs for a node.
    Returns dict keyed by capsule section name, each containing list of
    {corpus_id, doc_title, heading, content, match_confidence, match_score}
    """
```

---

## 5. Job Aid Integration

### 5.1 Problem: Disconnection

Job aids exist as standalone `.jobaid.yaml` files with structured condition/action rules. They are never referenced during triple generation. An agent consuming a triple has no awareness that parameterized decision tables exist for the task.

### 5.2 Solution: Three-Point Integration

#### Stage 2 (Enrichment): Discovery

The enricher scans for `.jobaid.yaml` files and matches them to BPMN nodes by capsule ID convention (e.g., `CAP-IV-W2V-001` links to `JA-IV-W2V-001`). Discovered job aids are attached to `NodeEnrichment.jobaid_refs`.

#### Stage 3 (Capsule Generation): Content Injection

Job aid data is rendered as **deterministic markdown** (zero LLM involvement) and injected into the capsule body:

```markdown
## Decision Parameters (Job Aid: JA-IV-W2V-001)

**Title**: W-2 Income Verification Thresholds

### Dimensions
| Dimension | Required at Resolution |
|-----------|----------------------|
| loan_program | Yes |
| employment_type | Yes |

### Action Fields
| Field | Type |
|-------|------|
| max_variance_pct | number |
| years_required | number |

### Decision Table
| loan_program | employment_type | -> max_variance_pct | -> years_required |
| --- | --- | --- | --- |
| conventional | w2 | 25 | 2 |
| fha | w2 | 15 | 2 |
| va | w2 | 20 | 1 |

**Total Rules**: 12
**Precedence**: most_specific
**Default Action**: {max_variance_pct: 10, years_required: 2}
```

This is **pure extraction** — the data comes directly from the job aid YAML. The LLM is instructed to include it verbatim.

#### Stage 4 (Intent Generation): Input/Output Mapping

Job aid dimensions become additional **inputs** on the intent spec:

```yaml
inputs:
  - name: loan_program
    source: "jobaid:JA-IV-W2V-001"
    required: true
  - name: employment_type
    source: "jobaid:JA-IV-W2V-001"
    required: true
```

Job aid action fields become additional **outputs**:

```yaml
outputs:
  - name: max_variance_pct
    type: jobaid_action
    sink: task_parameters
    invariants:
      - "max_variance_pct resolved from job aid JA-IV-W2V-001"
```

The `jobaid_refs` field in the intent frontmatter provides the link:

```yaml
jobaid_refs:
  - jobaid_id: JA-IV-W2V-001
    title: "W-2 Income Verification Thresholds"
    precedence: most_specific
```

---

## 6. Editor-Not-Author LLM Prompts

### 6.1 Core Principle

The LLM's role changes from **content creator** to **content organizer**. It receives pre-extracted corpus sections and organizes them into capsule/intent/contract structure. It does not create new content.

### 6.2 Capsule System Prompt

```
You are a knowledge capsule EDITOR for the MDA Intent Layer.
You ORGANIZE and FORMAT pre-extracted corpus content into structured Markdown sections.

ABSOLUTE RULES — violations will cause rejection:
1. Every factual sentence MUST end with a (CORPUS-ID) citation in parentheses.
2. You may ONLY use information from the SOURCE CONTENT provided below.
3. If a section has NO source content, write EXACTLY: "NO SOURCE CONTENT — GAP FLAGGED"
4. Do NOT paraphrase loosely. Preserve the original wording and structure from sources.
5. Do NOT add information, examples, explanations, or inferences not in the sources.
6. Do NOT invent procedures, rules, thresholds, or regulatory references.
7. You are an EDITOR — you organize, you do not create.
```

### 6.3 Intent System Prompt

```
You are an intent specification architect for the MDA Intent Layer.
...
CRITICAL RULES:
1. Every precondition, invariant, and failure mode MUST be traceable to the capsule
   content or BPMN structure provided. Cite (CORPUS-ID) where applicable.
2. Do NOT invent preconditions, invariants, or rules not present in the source material.
3. If information is missing, write "DERIVED FROM BPMN STRUCTURE" for BPMN-sourced items.
```

### 6.4 Prompt Structure

The capsule generation prompt is organized by section:

```
## SOURCE CONTENT (extracted from corpus — this is ALL you may use)

### Procedure Sources
**[CRP-PRC-IV-001] W-2 Income Verification** — Section: Procedure Steps (confidence: high)
[full section content, no truncation]

### Business Rules Sources
**[CRP-RUL-MTG-003] DTI Threshold Rules** — Section: Business Rules (confidence: high)
[full section content]

### Regulatory / Compliance Sources
**[CRP-REG-IV-001] Fannie Mae B3-3.1** — Section: Regulatory Requirements (confidence: high)
[full section content]

## JOB AID DATA (include verbatim — do not modify)
[pre-rendered decision table]

## ORGANIZE INTO THESE SECTIONS
[section requirements with citation mandate]
```

---

## 7. Post-Generation Grounding Verification

### 7.1 Verification Algorithm

After the LLM returns a capsule body, the system runs automated verification:

```python
def verify_grounding(llm_output, corpus_content, provided_corpus_ids) -> dict:
    """
    Returns:
      valid: bool
      invalid_citations: list — cited IDs not in provided set
      uncited_sections: list — sections without citations (excluding gap-flagged)
      gap_sections: list — sections correctly marked as gaps
      citation_count: int — total citations found
      cited_ids: list — all corpus IDs cited in output
    """
```

### 7.2 Verification Steps

1. **Extract citations** — Find all `(CRP-XXX-YY-NNN)` patterns in the output
2. **Validate citations** — Check every cited ID exists in the provided corpus set
3. **Check section coverage** — Every non-trivial section (>50 chars) must have either:
   - At least one valid citation, OR
   - A gap marker ("NO SOURCE CONTENT — GAP FLAGGED")
4. **Flag hallucination suspects** — Sections with substantial content but no citations

### 7.3 Retry on Failure

If verification fails on the first attempt, the system retries **once** with a stricter prompt:

```
GROUNDING VERIFICATION FAILED on previous attempt.
Uncited sections: [list]
Invalid citations: [list]
Available corpus IDs: [list]
You MUST cite a (CORPUS-ID) for every factual statement.
```

If the retry also fails, the verification result is stored in the frontmatter as `grounding_verification` for reviewer attention. The capsule is still written but flagged.

---

## 8. Provenance Chain

### 8.1 Frontmatter Provenance

Every corpus reference in the frontmatter includes full provenance:

```yaml
corpus_refs:
  - corpus_id: "CRP-PRC-IV-001"
    section: "Procedure"
    match_confidence: "high"
    match_method: "exact_id"       # How the match was determined
    match_score: 1.0               # Numeric score from matching algorithm

jobaid_refs:
  - jobaid_id: "JA-IV-W2V-001"
    title: "W-2 Income Verification Thresholds"
    dimensions: ["loan_program", "employment_type"]
    rules_count: 12

grounding_verification:
  valid: true
  citation_count: 14
  cited_ids: ["CRP-PRC-IV-001", "CRP-REG-IV-001", "CRP-RUL-MTG-003"]
  uncited_sections: []
  gap_sections: ["Exception Handling"]
```

### 8.2 Inline Citations

Every factual claim in the body cites its source:

```markdown
## Procedure

1. Collect borrower's W-2 forms for the most recent two tax years. (CRP-PRC-IV-001)
2. Request IRS Form 4506-T for transcript verification. (CRP-PRC-IV-001)
3. Cross-reference W-2 Box 1 against 1040 Line 1 for each tax year. (CRP-PRC-IV-001)

## Business Rules

- W-2 Box 1 total MUST NOT exceed 1040 Line 1 for the same tax year. (CRP-REG-IV-001)
- If income declined >10% year-over-year, use the lower year or two-year average. (CRP-RUL-MTG-003)
```

---

## 9. Implementation Guide (Inside Firewall)

### 9.1 Prerequisites

| Requirement | Details |
| --- | --- |
| Python | 3.10+ |
| LLM Provider | Any provider supported by `cli/llm/provider.py` — Anthropic Claude (via API), OpenAI GPT, or Ollama (local) |
| Dependencies | pyyaml, jsonschema, rich, jinja2, and one LLM SDK |
| Corpus | Populated corpus directory with `corpus.config.yaml` index |
| BPMN | Valid BPMN 2.0 XML files |

### 9.2 Files Modified

| File | Change Type | Description |
| --- | --- | --- |
| `cli/config/defaults.py` | Modified | Added `enrichment` config block with weights, thresholds, doc_type scores |
| `cli/models/enriched.py` | Modified | Added `jobaid_refs` field to `NodeEnrichment` |
| `cli/pipeline/stage2_enricher.py` | **Rewritten** | Multi-signal weighted scoring, section extraction, job aid discovery, grounding verification |
| `cli/pipeline/stage3_capsule_gen.py` | **Rewritten** | Section-level content injection, job aid rendering, verification pipeline |
| `cli/pipeline/stage4_intent_gen.py` | Modified | Job aid dimensions as inputs/outputs, capsule content passthrough for grounding |
| `cli/llm/prompts/capsule.py` | **Rewritten** | Editor-not-author paradigm, section-organized prompt, citation mandate |
| `cli/llm/prompts/intent.py` | **Rewritten** | Extraction-based prompt, corpus citation requirement |

### 9.3 New Functions

| Function | Location | Purpose |
| --- | --- | --- |
| `extract_corpus_sections()` | `stage2_enricher.py` | Parse markdown into sections, filter by keywords |
| `extract_grounded_content()` | `stage2_enricher.py` | Extract section-level content for all matched docs |
| `verify_grounding()` | `stage2_enricher.py` | Post-generation citation verification |
| `_discover_jobaids()` | `stage2_enricher.py` | Find and index `.jobaid.yaml` files |
| `_parse_markdown_sections()` | `stage2_enricher.py` | Split markdown body by heading levels |
| `_get_node_data_refs()` | `stage2_enricher.py` | Extract data object names from BPMN associations |
| `_preload_corpus_bodies()` | `stage2_enricher.py` | Pre-load corpus previews for matching context |
| `_format_jobaid_section()` | `stage3_capsule_gen.py` | Render job aid as deterministic markdown table |

### 9.4 Configuration Changes

Add to `mda.config.yaml`:

```yaml
enrichment:
  match_threshold: 0.4
  high_confidence: 0.8
  medium_confidence: 0.5
  max_matches_per_type: 3
  disambiguation_band: 0.1
  weights:
    subdomain_match: 0.25
    tag_overlap_ratio: 0.20
    doc_type_relevance: 0.15
    role_match: 0.10
    data_object_match: 0.15
    related_corpus_bonus: 0.10
    goal_type_match: 0.05
  doc_type_relevance_scores:
    procedure: 1.0
    rule: 0.9
    policy: 0.8
    regulation: 0.8
    data-dictionary: 0.7
    system: 0.6
    training: 0.4
    glossary: 0.3
```

### 9.5 Deployment Steps

1. **Update code** — Pull latest changes from this branch
2. **Update config** — Add `enrichment` block to `mda.config.yaml`
3. **Reindex corpus** — Run `mda corpus index` to regenerate `corpus.config.yaml`
4. **Test matching** — Run `mda enrich <model.yaml>` and inspect match scores in output
5. **Tune weights** — Adjust `enrichment.weights` based on your corpus characteristics:
   - If too many irrelevant matches: increase `match_threshold`
   - If too few matches: decrease `match_threshold`, increase `tag_overlap_ratio` weight
   - If wrong doc types matched: adjust `doc_type_relevance_scores`
   - If job aids not discovered: check capsule ID naming convention matches
6. **Generate triples** — Run `mda generate --type all` and review `grounding_verification` in frontmatter
7. **Review gaps** — Run `mda gaps` to see which sections were flagged as "NO SOURCE CONTENT"

---

## 10. Verification Checks

### 10.1 Grounding-Specific Checks (New)

| Check ID | Name | Severity | Description |
| --- | --- | --- | --- |
| G01 | Citation completeness | CRITICAL | Every non-gap section has at least one valid (CORPUS-ID) citation |
| G02 | Citation validity | CRITICAL | Every cited CORPUS-ID exists in the corpus index |
| G03 | No hallucinated content | HIGH | No section contains >100 words without a citation |
| G04 | Job aid linkage | MEDIUM | If a job aid exists for a capsule, it must appear in `jobaid_refs` |
| G05 | Match score threshold | MEDIUM | All corpus_refs have `match_score >= match_threshold` |
| G06 | Provenance completeness | MEDIUM | All corpus_refs include `match_method` and `match_score` |
| G07 | Gap acknowledgment | LOW | Sections with no source content are marked "GAP FLAGGED" |

### 10.2 Regression Checks (Existing)

All existing B01-B08, T01-T11, and C01-C06 checks continue to apply. The grounding system is additive — it does not break existing schema or cross-reference validation.

---

## 11. Data Flow Diagrams

### 11.1 Corpus Matching Flow

```
BPMN Node
  │
  ├── name: "Verify W-2 Income"
  ├── element_type: "serviceTask"
  ├── lane_name: "Verification Agent"
  └── data_associations: [W2Documents, TaxReturns]
  │
  ▼
Multi-Signal Scorer
  │
  ├── Tier 1: Check applies_to.process_ids + task_name_patterns
  │   └── CRP-PRC-IV-001: process_match=YES, pattern_match=YES → 1.0 (exact_id)
  │
  ├── Tier 2: Weighted scoring for remaining candidates
  │   ├── CRP-POL-IV-001: subdomain=0.25, tags=0.15, type=0.12, role=0.10 → 0.62
  │   ├── CRP-REG-IV-001: subdomain=0.25, tags=0.10, type=0.12, goal=0.05 → 0.52
  │   └── CRP-DAT-IV-001: data_obj=0.15, tags=0.10, type=0.105 → 0.355
  │
  └── Result: [CRP-PRC-IV-001 (1.0), CRP-POL-IV-001 (0.62), CRP-REG-IV-001 (0.52)]
```

### 11.2 Section Extraction Flow

```
CRP-PRC-IV-001 (W-2 Income Verification Procedure)
  │
  ├── ## Scope                    → (not matched to any capsule section)
  ├── ## Prerequisites            → exception_handling
  ├── ## Procedure Steps          → procedure ✓
  ├── ## Business Rules           → business_rules ✓
  ├── ## Exception Handling       → exception_handling ✓
  └── ## Regulatory Requirements  → regulatory_context ✓
  │
  ▼
grounded_content = {
    "procedure": [{corpus_id, heading: "Procedure Steps", content: "1. Collect..."}],
    "business_rules": [{corpus_id, heading: "Business Rules", content: "- W-2 Box 1..."}],
    "exception_handling": [{...}],
    "regulatory_context": [{...}],
    "inputs_outputs": [],  # → GAP
}
```

### 11.3 Capsule Generation Flow

```
grounded_content + jobaid_content + node_context
  │
  ▼
build_capsule_body_prompt()
  │  ├── Procedure Sources: [full sections from CRP-PRC-IV-001]
  │  ├── Business Rules Sources: [from CRP-RUL-MTG-003]
  │  ├── Regulatory Sources: [from CRP-REG-IV-001]
  │  ├── Job Aid Data: [rendered decision table from JA-IV-W2V-001]
  │  └── Instructions: "ORGANIZE, don't CREATE. CITE every statement."
  │
  ▼
LLM (temperature=0.15)
  │
  ▼
verify_grounding(output, corpus_content, provided_ids)
  │
  ├── Pass → write capsule with grounding_verification.valid=true
  └── Fail → retry once with stricter prompt
         │
         ├── Pass → write with verification result
         └── Fail → write with grounding_verification.valid=false (flagged for review)
```

---

## 12. Anti-Hallucination Guarantees

### 12.1 Layer Defense Model

| Layer | Mechanism | What It Catches |
| --- | --- | --- |
| **L1: Input filtering** | Only matched corpus sections enter the prompt | Prevents irrelevant information from being available |
| **L2: Prompt engineering** | Editor-not-author paradigm with citation mandate | Instructs the LLM to organize, not create |
| **L3: Temperature control** | 0.15 for capsule, 0.10 for structured output | Reduces creative variation |
| **L4: Post-generation verification** | Automated citation checking | Catches uncited sections and invalid IDs |
| **L5: Retry mechanism** | Stricter prompt on verification failure | Gives the LLM a second chance with explicit ID list |
| **L6: Provenance tracking** | `grounding_verification` in frontmatter | Flags ungrounded content for human review |
| **L7: Gap acknowledgment** | "NO SOURCE CONTENT — GAP FLAGGED" | Makes missing information visible rather than hidden |

### 12.2 What This Does NOT Prevent

- **Subtle paraphrasing drift** — The LLM may slightly rephrase corpus content while citing it. This is acceptable as long as the meaning is preserved. Reviewers should spot-check citations against source documents.
- **Incorrect section assignment** — The LLM may put a business rule in the regulatory context section or vice versa. This is a formatting issue, not a hallucination.
- **Missing corpus documents** — If the corpus itself is incomplete, the system will correctly flag gaps but cannot fill them. The gap is visible; the fix is to author the missing corpus document.

---

## 13. Performance Considerations

### 13.1 Token Usage

Section-level extraction sends more corpus content to the LLM than the previous truncation approach. Expect:

- **Capsule generation**: ~4000-8000 input tokens (was ~2000-3000 with truncation)
- **Intent generation**: ~3000-5000 input tokens (unchanged)
- **Contract generation**: ~2000-4000 input tokens (unchanged)

### 13.2 Corpus Pre-Loading

The enricher pre-loads 500-char previews of all corpus documents at startup. For a 46-document corpus, this is <25KB of memory and <1 second of I/O. For larger corpora (500+ documents), consider:

- Lazy loading (only load on match)
- Caching the pre-loaded previews in a pickle file
- Indexing by doc_type for faster filtering

### 13.3 Job Aid Discovery

Job aid discovery scans the project directory tree for `.jobaid.yaml` files on every enrichment run. For large projects, consider:

- Caching the jobaid index
- Adding a `jobaids` section to `mda.config.yaml` with explicit paths

---

## 14. Testing Strategy

### 14.1 Unit Tests

| Test | File | Validates |
| --- | --- | --- |
| `test_weighted_scoring` | `tests/unit/test_enricher_scoring.py` | All 7 factors produce expected scores |
| `test_section_extraction` | `tests/unit/test_section_extraction.py` | Markdown parsed into correct sections |
| `test_grounding_verification` | `tests/unit/test_grounding_verification.py` | Citations detected, invalids flagged |
| `test_jobaid_injection` | `tests/unit/test_jobaid_injection.py` | Job aids rendered as correct markdown |
| `test_tag_overlap_ratio` | `tests/unit/test_enricher_scoring.py` | Ratio scoring vs binary |

### 14.2 Integration Tests

| Test | Validates |
| --- | --- |
| `test_full_pipeline_grounded` | End-to-end: BPMN → enrichment → grounded capsule with citations |
| `test_capsule_verification_pass` | Well-grounded capsule passes verification |
| `test_capsule_verification_fail` | Ungrounded capsule fails and retries |
| `test_jobaid_end_to_end` | Job aid discovered → injected → appears in capsule body and intent inputs |

### 14.3 Acceptance Criteria

1. **Zero hallucination**: Every factual statement in a generated capsule has a valid (CORPUS-ID) citation
2. **No truncation**: Full procedure steps from corpus documents appear in capsules
3. **Job aid visibility**: Decision tables appear in capsule body; dimensions appear as intent inputs
4. **Provenance**: Every corpus_ref in frontmatter includes match_method and match_score
5. **Gap clarity**: Missing information is explicitly flagged, not silently invented

---

## 15. Glossary

| Term | Definition |
| --- | --- |
| **Grounding** | Ensuring every generated claim traces to a specific source document |
| **Hallucination** | LLM-generated content that does not originate from the provided source material |
| **Triple** | A set of three artifacts (capsule, intent spec, integration contract) for one BPMN task |
| **Corpus** | The knowledge base of procedures, policies, regulations, rules, and data dictionaries |
| **Job Aid** | A structured condition/action decision table parameterizing task execution |
| **Provenance** | The chain of evidence from a generated field back to its source document and section |
| **Editor-not-author** | The principle that the LLM organizes extracted content rather than creating new content |
| **Section extraction** | Parsing corpus markdown into sections and matching them to capsule section types |
| **Multi-signal scoring** | Using multiple weighted factors to score corpus-to-task relevance |
| **Verification** | Automated post-generation check that all citations are valid and all sections are cited |
