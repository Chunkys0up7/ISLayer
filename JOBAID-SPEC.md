# MDA Intent Layer -- Job Aid Specification

## 1. Overview

Job aids are structured condition/action lookup tables -- the fourth artifact type in the MDA Intent Layer alongside knowledge capsules, intent specs, and integration contracts. They parameterize how a task executes based on conditions without multiplying triples. One BPMN task = one triple + zero or more job aids.

**Problem solved:** A single task like "Verify W-2 Income" has different documentation requirements, calculation methods, and thresholds depending on loan program (FHA, Conventional, VA, USDA), income type (base salary, overtime, bonus, commission, tips), and employment duration. Without job aids, you would need 40 separate triples for one task. With job aids, you keep one triple and attach a 40-rule lookup table.

**Key principle:** Job aids are YAML data files, not prose documents. They are machine-queryable decision tables that an agent consults at runtime to determine the correct parameters for a given set of conditions.

---

## 2. Architecture

### File Format and Location

- Job aids are `.jobaid.yaml` files (YAML, not markdown -- they are data, not prose)
- They live alongside triples in the same directory (e.g., `triples/verify-w2/verify-w2.jobaid.yaml`)
- Referenced by intent specs via the `jobaid_refs` field in intent YAML frontmatter
- Have their own JSON schema at `schemas/jobaid.schema.json`

### Separation from BPMN Pipeline

Job aids have a **separate pipeline** from BPMN ingestion:

- BPMN pipeline: `.bpmn` XML --> parsed model --> enriched model --> triples
- Job aid pipeline: Excel/Word decision table --> `.jobaid.yaml` --> validated --> queryable at runtime

### Precedence Strategies

Three strategies control how multiple matching rules are resolved:

| Strategy | Behavior |
|---|---|
| `first_match` | Return only the first matching rule (rule order matters) |
| `most_specific` | Return the rule with the most non-wildcard conditions |
| `all_matching` | Return all matching rules (merge results) |

### Source Files

| File | Purpose |
|---|---|
| `schemas/jobaid.schema.json` | JSON Schema for `.jobaid.yaml` validation |
| `cli/models/jobaid.py` | Python dataclasses (Dimension, ActionField, Rule, JobAid) |
| `cli/pipeline/jobaid_processor.py` | Import, validate, query, list, write functions |
| `cli/commands/jobaid_cmd.py` | CLI command handler (import, validate, query, list) |
| `.claude/skills/mda-jobaid/SKILL.md` | Claude Code skill definition |

---

## 3. Job Aid Format (.jobaid.yaml)

### Complete YAML Structure

```yaml
# === Identity ===
jobaid_id: JA-IV-VW2-001          # Pattern: JA-{PROCESS}-{CATEGORY}-{SEQ}
capsule_id: CAP-IV-VW2-001        # Links to the parent knowledge capsule
title: W-2 Income Verification Decision Table
version: "1.0"                     # MAJOR.MINOR string
status: current                    # draft | review | current | superseded | archived

# === Metadata ===
description: >
  Condition/action lookup table for W-2 income verification. Determines
  required documentation, calculation method, thresholds, and regulatory
  references based on loan program, income type, and employment duration.
source_file: w2-decision-table.xlsx   # Original import source (null if hand-authored)
author: mda-cli
last_modified: "2025-01-15"
last_modified_by: mda-cli

# === Dimensions (condition variables) ===
dimensions:
  - name: loan_program
    values: [FHA, Conventional, VA, USDA]
    description: The loan program under which the application is being processed
    # required_at_resolution: true  (default)
  - name: income_type
    values: [base_salary, overtime, bonus, commission, tips]
    description: The category of income being verified from the W-2
  - name: employment_duration
    values: [less_than_2_years, 2_years_or_more]
    description: Length of time the borrower has been employed at the current employer

# === Action Fields (output columns) ===
# Optional. Defines the schema of what each rule's action object produces.
action_fields:
  - name: documentation_required
    type: string_array          # string | number | boolean | string_array | object
    description: List of documents the agent must collect
    # required: true  (default)
  - name: calculation_method
    type: string
    description: How to calculate qualifying income
  - name: threshold
    type: string
    description: Any threshold or constraint that applies
  - name: regulatory_ref
    type: string
    description: Regulatory citation for audit trail

# === Precedence Strategy ===
precedence: first_match           # first_match | most_specific | all_matching

# === Rules (condition -> action rows) ===
rules:
  - id: R-001                     # Unique within this job aid
    conditions:
      loan_program: FHA
      income_type: base_salary
      employment_duration: 2_years_or_more
    action:
      documentation_required:
        - Most recent W-2
        - Most recent paystub covering 30-day period
      calculation_method: current_annualized
      threshold: null
      regulatory_ref: FHA 4000.1 II.A.4.c.ii
    notes: Standard base salary verification     # Optional
    regulatory_ref: FHA 4000.1 II.A.4.c.ii       # Optional top-level ref
    effective_date: "2024-01-01"                  # Optional
    expiry_date: null                             # Optional

  - id: R-002
    conditions:
      loan_program: FHA
      income_type: base_salary
      employment_duration: less_than_2_years
    action:
      documentation_required:
        - Most recent W-2
        - Most recent paystub covering 30-day period
        - Prior employer verification or school transcripts if gap exists
      calculation_method: current_annualized
      threshold: null
      regulatory_ref: FHA 4000.1 II.A.4.c.iii
  # ... additional rules ...

# === Default Action (fallback) ===
default_action:
  documentation_required:
    - Contact supervisor for guidance
  calculation_method: manual_review
  threshold: "Requires underwriter approval"
  regulatory_ref: "N/A"
```

### Field Reference

| Field | Type | Required | Description |
|---|---|---|---|
| `jobaid_id` | string | Yes | Pattern: `JA-{PROCESS}-{CATEGORY}-{SEQ}` (e.g., `JA-IV-VW2-001`) |
| `capsule_id` | string | Yes | Pattern: `CAP-{PROCESS}-{CATEGORY}-{SEQ}` -- links to parent capsule |
| `title` | string | Yes | Human-readable title |
| `version` | string | Yes | `MAJOR.MINOR` format (e.g., `"1.0"`) |
| `status` | enum | Yes | `draft`, `review`, `current`, `superseded`, `archived` |
| `description` | string | No | Extended description |
| `source_file` | string/null | No | Original file this was imported from |
| `author` | string | No | Who created it |
| `last_modified` | string | No | Date of last modification |
| `last_modified_by` | string | No | Who last modified it |
| `dimensions` | array | Yes | At least 1 dimension required |
| `action_fields` | array | No | Defines the output column schema |
| `rules` | array | Yes | At least 1 rule required |
| `default_action` | object | No | Fallback when no rules match |
| `precedence` | enum | No | Default: `first_match` |

### Condition Matching Semantics

Each rule's `conditions` object maps dimension names to expected values. Matching follows these rules:

| Condition Value | Match Behavior |
|---|---|
| `"FHA"` (exact string) | Query value must equal `"FHA"` |
| `["FHA", "VA"]` (list) | Query value must be in the list |
| `"*"` (wildcard) | Matches any query value |
| `null` | Treated as wildcard (matches anything) |
| Dimension absent from query | Rule condition for that dimension is skipped |

### ID Patterns

- **Job Aid ID:** `JA-{2-3 char process}-{3 char category}-{3 digit seq}`
  - Regex: `^JA-[A-Z0-9]{2,3}-[A-Z0-9]{3}-\d{3}$`
  - Example: `JA-IV-VW2-001`
- **Capsule ID:** `CAP-{2-3 char process}-{3 char category}-{3 digit seq}`
  - Regex: `^CAP-[A-Z0-9]{2,3}-[A-Z0-9]{3}-\d{3}$`
  - Example: `CAP-IV-VW2-001`

---

## 4. Schema (schemas/jobaid.schema.json)

The JSON Schema at `schemas/jobaid.schema.json` enforces the `.jobaid.yaml` structure.

### Required Fields

```json
"required": ["jobaid_id", "capsule_id", "title", "version", "status", "dimensions", "rules"]
```

### Key Pattern Constraints

```json
"jobaid_id": {
  "type": "string",
  "pattern": "^JA-[A-Z0-9]{2,3}-[A-Z0-9]{3}-\\d{3}$"
}
"capsule_id": {
  "type": "string",
  "pattern": "^CAP-[A-Z0-9]{2,3}-[A-Z0-9]{3}-\\d{3}$"
}
"version": {
  "type": "string",
  "pattern": "^\\d+\\.\\d+$"
}
```

### Status Enum

```json
"status": {
  "type": "string",
  "enum": ["draft", "review", "current", "superseded", "archived"]
}
```

### Precedence Enum

```json
"precedence": {
  "type": "string",
  "enum": ["first_match", "most_specific", "all_matching"],
  "default": "first_match"
}
```

### Action Field Type Enum

```json
"type": {
  "type": "string",
  "enum": ["string", "number", "boolean", "string_array", "object"]
}
```

### Dimensions Array

- Minimum 1 item
- Each dimension requires `name`
- Optional: `description`, `values` (allowed value list), `required_at_resolution` (boolean, default true)
- `additionalProperties: false`

### Rules Array

- Minimum 1 item
- Each rule requires `id`, `conditions`, `action`
- `conditions`: object with `additionalProperties` of type `string | array | null`
- `action`: object with `additionalProperties: true` (free-form action payload)
- Optional: `notes`, `regulatory_ref`, `effective_date`, `expiry_date`
- `additionalProperties: false`

### Default Action

```json
"default_action": {
  "type": "object",
  "description": "Fallback action when no rules match",
  "additionalProperties": true
}
```

---

## 5. Data Models (cli/models/jobaid.py)

### Enums

```python
class JobAidStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    CURRENT = "current"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"

class Precedence(str, Enum):
    FIRST_MATCH = "first_match"
    MOST_SPECIFIC = "most_specific"
    ALL_MATCHING = "all_matching"
```

### Dimension Dataclass

```python
@dataclass
class Dimension:
    name: str
    description: str = ""
    values: list[str] = field(default_factory=list)
    required_at_resolution: bool = True
```

- `name`: The dimension variable name (e.g., `loan_program`)
- `values`: Allowed values (e.g., `["FHA", "Conventional", "VA", "USDA"]`)
- `required_at_resolution`: Whether the agent must supply this dimension when querying

### ActionField Dataclass

```python
@dataclass
class ActionField:
    name: str
    type: str       # string | number | boolean | string_array | object
    description: str = ""
    required: bool = True
```

### Rule Dataclass

```python
@dataclass
class Rule:
    id: str
    conditions: dict[str, Any]      # dimension_name -> value or list or "*"
    action: dict[str, Any]          # action_field_name -> value
    notes: Optional[str] = None
    regulatory_ref: Optional[str] = None
    effective_date: Optional[str] = None
    expiry_date: Optional[str] = None
```

#### Rule.matches(query: dict[str, str]) -> bool

Determines whether a rule matches a given set of conditions:

1. For each dimension in the rule's conditions:
   - If the rule expects `"*"` or `None` --> skip (wildcard, always matches)
   - If the query does not include this dimension --> skip (dimension not specified, do not filter)
   - If the rule expects a **list** --> query value must be **in** the list
   - If the rule expects a **string** --> query value must **equal** the string
   - If any condition fails --> return `False`
2. If all conditions pass --> return `True`

#### Rule.specificity() -> int

Counts the number of non-wildcard conditions. Used by `most_specific` precedence to rank rules:

```python
def specificity(self) -> int:
    return sum(1 for v in self.conditions.values() if v != "*" and v is not None)
```

A rule with `loan_program=FHA, income_type=base_salary, employment_duration=2_years_or_more` has specificity 3. A rule with `loan_program=FHA, income_type=*, employment_duration=*` has specificity 1.

### JobAid Dataclass

```python
@dataclass
class JobAid:
    jobaid_id: str
    capsule_id: str
    title: str
    version: str = "1.0"
    status: JobAidStatus = JobAidStatus.DRAFT
    description: str = ""
    source_file: Optional[str] = None
    author: str = ""
    last_modified: str = ""
    last_modified_by: str = ""
    dimensions: list[Dimension] = field(default_factory=list)
    action_fields: list[ActionField] = field(default_factory=list)
    rules: list[Rule] = field(default_factory=list)
    default_action: Optional[dict] = None
    precedence: Precedence = Precedence.FIRST_MATCH
    file_path: Optional[str] = None
```

#### JobAid.query(conditions: dict[str, str]) -> list[Rule]

Finds rules matching the given conditions, applying the precedence strategy:

1. Collect all rules where `rule.matches(conditions)` is `True`
2. Apply precedence:
   - **first_match:** Return `[matches[0]]` (first matching rule only)
   - **most_specific:** Sort by `rule.specificity()` descending, return `[matches[0]]` (highest specificity wins)
   - **all_matching:** Return all matching rules
3. If no matches, return `[]`

#### JobAid.get_rule(rule_id: str) -> Optional[Rule]

Look up a specific rule by its ID string.

#### Properties

- `dimension_names -> list[str]`: Returns `[d.name for d in self.dimensions]`
- `rule_count -> int`: Returns `len(self.rules)`

#### Serialization

- `to_dict() -> dict`: Converts to a dictionary suitable for YAML output
- `from_dict(d: dict) -> JobAid`: Constructs a JobAid from a parsed YAML dictionary

---

## 6. Processor (cli/pipeline/jobaid_processor.py)

### import_from_excel()

```python
def import_from_excel(
    excel_path: Path,
    capsule_id: str,
    title: Optional[str] = None,
    dimension_columns: Optional[list[str]] = None,
    sheet_name: Optional[str] = None,
) -> JobAid:
```

Converts an Excel decision table into a JobAid object.

**Excel file expectations:**
- Column headers in row 1
- Each subsequent row is one rule
- `dimension_columns` specifies which columns are conditions; remaining columns become action fields

**Auto-detection of dimension columns** (when `dimension_columns` is None):
1. Count unique values per column across all data rows
2. Columns with fewer than 20 unique values (and at least 1) are classified as dimensions
3. Fallback: if no columns qualify, use the first 3 columns

**Comma-separated list parsing:**
- Action cell values containing commas (but not starting with `{`) are split into string arrays
- Example: `"W-2, Paystub, VOE"` becomes `["W-2", "Paystub", "VOE"]`

**Rule ID generation:**
- Auto-generated as `R001`, `R002`, ... based on row number

**Job Aid ID derivation:**
- Strips `CAP-` from the capsule_id and prepends `JA-`
- Example: `CAP-IV-VW2-001` becomes `JA-IV-VW2-001`

**Metadata defaults:**
- `version`: `"1.0"`
- `author`: `"mda-cli"`
- `last_modified`: UTC date at import time
- `precedence`: `first_match`
- `description`: `"Imported from {filename}"`

**Dependency:** Requires `openpyxl` (`pip install openpyxl`).

### validate_jobaid()

```python
def validate_jobaid(jobaid_path: Path, schemas_dir: Optional[Path] = None) -> list[dict]:
```

Validates a `.jobaid.yaml` file. Returns a list of error dicts (empty list = valid).

**Validation layers:**

1. **YAML parse check:** File must be valid, non-empty YAML
2. **JSON Schema validation:** Validates against `schemas/jobaid.schema.json` (if `schemas_dir` provided)
3. **Internal consistency checks:**
   - All dimension names used in rule conditions must be defined in the `dimensions` array
   - No duplicate rule IDs
   - Condition values must be in the dimension's allowed `values` list (if `values` is defined)
   - Wildcard (`"*"`) and null values are exempt from the allowed-values check
   - List conditions: each value in the list is checked individually

**Error format:**

```python
{"path": "rules/R-001/conditions/loan_program", "error": "Value 'JUMBO' not in dimension 'loan_program' allowed values"}
```

### query_jobaid()

```python
def query_jobaid(jobaid_path: Path, conditions: dict[str, str]) -> list[dict]:
```

Loads a `.jobaid.yaml`, constructs a JobAid, calls `jobaid.query(conditions)`, and returns matching rules as dicts.

### list_jobaids()

```python
def list_jobaids(triples_dir: Path, decisions_dir: Optional[Path] = None) -> list[dict]:
```

Recursively finds all `*.jobaid.yaml` files under `triples_dir` and `decisions_dir`. Returns a summary list:

```python
{
    "jobaid_id": "JA-IV-VW2-001",
    "capsule_id": "CAP-IV-VW2-001",
    "title": "W-2 Income Verification Decision Table",
    "rules": 40,
    "dimensions": 3,
    "status": "current",
    "path": "triples/verify-w2/verify-w2.jobaid.yaml"
}
```

### write_jobaid()

```python
def write_jobaid(jobaid: JobAid, output_path: Path) -> None:
```

Serializes a JobAid to YAML and writes to disk. Creates parent directories if needed.

---

## 7. CLI Commands

All commands are accessed via `python cli/mda.py jobaid {subcommand}`.

### mda jobaid import

Import a decision table from Excel into a `.jobaid.yaml` file.

```
python cli/mda.py jobaid import <excel-file> \
    --capsule-id CAP-XX-YYY-NNN \
    [--title "My Job Aid"] \
    [--dimensions "col1,col2,col3"] \
    [--output path/to/output.jobaid.yaml]
```

| Argument | Required | Description |
|---|---|---|
| `file` | Yes | Path to the Excel file (.xlsx) |
| `--capsule-id` | Yes | Capsule ID to link the job aid to |
| `--title` | No | Human-readable title (default: auto-generated from capsule ID) |
| `--dimensions` | No | Comma-separated list of column names that are conditions (default: auto-detect) |
| `--output` | No | Output file path (default: auto-placed in triples directory) |

**Output:** Creates the `.jobaid.yaml` file and prints summary (rule count, dimensions, output path).

### mda jobaid validate

Validate job aid files against the schema and internal consistency rules.

```
python cli/mda.py jobaid validate [path/to/specific.jobaid.yaml]
```

| Argument | Required | Description |
|---|---|---|
| `path` | No | Path to a specific `.jobaid.yaml` file. If omitted, validates all job aids in triples/ and decisions/ |

**Output:** Reports validation errors or confirms all files pass. Supports `--json` for machine-readable output.

### mda jobaid query

Query a job aid with specific conditions and return matching rules.

```
python cli/mda.py jobaid query <jobaid-file> \
    --conditions "key1=val1,key2=val2"
```

| Argument | Required | Description |
|---|---|---|
| `jobaid_file` | Yes | Path to the `.jobaid.yaml` file to query |
| `--conditions` / `-c` | No | Comma-separated key=value pairs (e.g., `"loan_program=FHA,income_type=overtime"`) |

**Output:** Prints matching rules with their conditions and action fields. Supports `--json`.

**Example:**

```
python cli/mda.py jobaid query triples/verify-w2/verify-w2.jobaid.yaml \
    -c "loan_program=FHA,income_type=overtime,employment_duration=2_years_or_more"
```

### mda jobaid list

List all job aids found in the process repository.

```
python cli/mda.py jobaid list
```

**Output:** Table showing ID, title, rule count, dimension count, and status for each job aid. Supports `--json`.

---

## 8. Intent Spec Integration

### The jobaid_refs Field

Intent specifications (`.intent.md` YAML frontmatter) reference job aids through the `jobaid_refs` array. This field is defined in `schemas/intent.schema.json`:

```yaml
# In an intent spec's YAML frontmatter:
jobaid_refs:
  - jobaid_id: JA-IV-VW2-001
    applies_when: "Task involves W-2 income verification"
    resolution: agent
  - jobaid_id: JA-IV-VW2-002
    applies_when: "Borrower has multiple employers"
    resolution: pre_filtered
```

### jobaid_refs Schema

```json
"jobaid_refs": {
  "type": "array",
  "items": {
    "type": "object",
    "required": ["jobaid_id"],
    "properties": {
      "jobaid_id": {
        "type": "string",
        "pattern": "^JA-[A-Z0-9]{2,3}-[A-Z0-9]{3}-\\d{3}$"
      },
      "applies_when": {
        "type": "string",
        "default": "always"
      },
      "resolution": {
        "type": "string",
        "enum": ["agent", "pre_filtered", "human"],
        "default": "agent"
      }
    },
    "additionalProperties": false
  }
}
```

### Field Definitions

| Field | Required | Default | Description |
|---|---|---|---|
| `jobaid_id` | Yes | -- | The ID of the referenced job aid (must match a `.jobaid.yaml` file) |
| `applies_when` | No | `"always"` | Condition under which this job aid is relevant |
| `resolution` | No | `"agent"` | How the job aid is resolved at runtime |

### Resolution Strategies

| Strategy | Behavior |
|---|---|
| `agent` | The executing agent queries the job aid at runtime using case-specific conditions |
| `pre_filtered` | The orchestrator pre-filters the job aid before passing it to the agent (reduces the lookup to applicable rules only) |
| `human` | A human must select the applicable rule; the agent presents options but does not decide |

---

## 9. Agent Runtime Behavior

When an agent executes a task that has `jobaid_refs`, it follows these steps:

### Step 1: Load the Intent Spec

The agent reads the intent spec and identifies all `jobaid_refs` entries.

### Step 2: Evaluate applies_when

For each job aid reference, the agent checks whether the `applies_when` condition is met for the current case. If `applies_when` is `"always"` (default), the job aid is always consulted.

### Step 3: Gather Dimension Values

The agent extracts the current values for each dimension from the case data. For example:
- `loan_program` = value from the loan application
- `income_type` = value from the income document being verified
- `employment_duration` = calculated from employment start date

### Step 4: Query the Job Aid

The agent calls `jobaid.query(conditions)` with the gathered dimension values. The precedence strategy determines which rules are returned.

### Step 5: Apply the Action

The agent uses the matching rule's action fields to parameterize its execution:
- `documentation_required` --> which documents to collect/verify
- `calculation_method` --> which formula to apply
- `threshold` --> any constraints to enforce
- `regulatory_ref` --> citation for the audit trail

### Step 6: Handle No Match

If no rules match and a `default_action` is defined, the agent uses the default action. If no `default_action` exists, the agent escalates to a human reviewer.

### Resolution Strategy Variations

- **agent resolution:** Steps 3-5 are performed autonomously by the agent.
- **pre_filtered resolution:** The orchestrator performs Step 4 before the agent starts, passing only matching rules. The agent skips the query step.
- **human resolution:** The agent presents the matching rules to a human, who selects the applicable one. The agent then applies the selected rule's action.

---

## 10. Skill

The `/mda-jobaid` skill is defined at `.claude/skills/mda-jobaid/SKILL.md`.

### Skill Frontmatter

```yaml
---
name: mda-jobaid
description: Import, validate, query, and manage job aids. Job aids are structured condition/action lookup tables that parameterize how a task executes based on conditions like loan program, income type, and state. Use when working with decision tables, lookup matrices, or conditional business rules.
argument-hint: [import|validate|query|list]
allowed-tools: Bash(python *) Read Edit
---
```

### Skill Commands

| Command | Usage |
|---|---|
| Import | `python cli/mda.py jobaid import <excel-file> --capsule-id CAP-XX-YYY-NNN [--title "..."] [--dimensions "col1,col2"]` |
| Validate | `python cli/mda.py jobaid validate [path-to-jobaid.yaml]` |
| Query | `python cli/mda.py jobaid query <jobaid.yaml> --conditions "key1=val1,key2=val2"` |
| List | `python cli/mda.py jobaid list` |

### Skill Workflow

1. Determine which subcommand the user needs based on `$ARGUMENTS`
2. Run the appropriate command
3. If importing, suggest running validate afterward
4. If querying, explain the matching results

---

## 11. Demo Data

The repository includes a complete 40-rule W-2 income verification job aid at:

```
examples/income-verification/triples/verify-w2/verify-w2.jobaid.yaml
```

### Coverage Matrix

The job aid covers the full cross-product of:

| Dimension | Values | Count |
|---|---|---|
| `loan_program` | FHA, Conventional, VA, USDA | 4 |
| `income_type` | base_salary, overtime, bonus, commission, tips | 5 |
| `employment_duration` | less_than_2_years, 2_years_or_more | 2 |

**Total rules:** 4 x 5 x 2 = **40 rules** (R-001 through R-040)

### Rule ID to Program Mapping

| Rules | Program |
|---|---|
| R-001 to R-010 | FHA |
| R-011 to R-020 | Conventional |
| R-021 to R-030 | VA |
| R-031 to R-040 | USDA |

Within each program, income types cycle in order: base_salary, overtime, bonus, commission, tips. Each income type has two rules (one per employment duration).

### Action Fields per Rule

| Field | Type | Description |
|---|---|---|
| `documentation_required` | string_array | Documents the agent must collect |
| `calculation_method` | string | One of: `current_annualized`, `2_year_average`, `ytd_annualized_if_trending_upward`, `not_eligible_unless_same_field` |
| `threshold` | string/null | Constraint or eligibility note (null means no threshold) |
| `regulatory_ref` | string | Regulatory citation (e.g., `FHA 4000.1 II.A.4.c.ii`, `FNMA B3-3.1-01`, `VA Pamphlet 26-7 Ch. 4`, `USDA HB-1-3555 Ch. 9.3`) |

### Example Query

Query: FHA + overtime + 2 years or more employment

```
python cli/mda.py jobaid query examples/income-verification/triples/verify-w2/verify-w2.jobaid.yaml \
    -c "loan_program=FHA,income_type=overtime,employment_duration=2_years_or_more"
```

Expected match: **R-003**
- Documentation: 2 years W-2s, recent paystub, written VOE confirming overtime continues
- Calculation: 2-year average
- Regulatory ref: FHA 4000.1 II.A.4.c.viii

---

## 12. Verification

### Verify Schema Validation

```bash
python cli/mda.py jobaid validate examples/income-verification/triples/verify-w2/verify-w2.jobaid.yaml
```

Expected: All validation passes (no errors).

### Verify Query Matching

```bash
# Exact match -- should return 1 rule (R-001)
python cli/mda.py jobaid query examples/income-verification/triples/verify-w2/verify-w2.jobaid.yaml \
    -c "loan_program=FHA,income_type=base_salary,employment_duration=2_years_or_more"

# Partial query -- omit employment_duration, should match both FHA base_salary rules (R-001 and R-002)
# Note: with first_match precedence, only R-001 is returned
python cli/mda.py jobaid query examples/income-verification/triples/verify-w2/verify-w2.jobaid.yaml \
    -c "loan_program=FHA,income_type=base_salary"

# Cross-program query -- VA commission
python cli/mda.py jobaid query examples/income-verification/triples/verify-w2/verify-w2.jobaid.yaml \
    -c "loan_program=VA,income_type=commission,employment_duration=less_than_2_years"
# Expected: R-028
```

### Verify List Command

```bash
python cli/mda.py jobaid list
```

Expected: Table showing the W-2 job aid with 40 rules, 3 dimensions, status "current".

### Verify Import from Excel

```bash
# Create a test Excel file and import it:
python cli/mda.py jobaid import test-decision-table.xlsx \
    --capsule-id CAP-IV-VW2-001 \
    --title "Test Import" \
    --dimensions "Program,Income Type,Duration" \
    --output test-output.jobaid.yaml

# Then validate the output:
python cli/mda.py jobaid validate test-output.jobaid.yaml
```

### Verify Intent Spec Integration

Check that an intent spec with `jobaid_refs` validates against the intent schema:

```yaml
# In a .intent.md frontmatter:
jobaid_refs:
  - jobaid_id: JA-IV-VW2-001
    applies_when: always
    resolution: agent
```

The `jobaid_id` pattern must match `^JA-[A-Z0-9]{2,3}-[A-Z0-9]{3}-\d{3}$` and the `resolution` must be one of `agent`, `pre_filtered`, or `human`.

### Verify Data Model Round-Trip

```python
from cli.models.jobaid import JobAid
from cli.mda_io.yaml_io import read_yaml, write_yaml

# Load
data = read_yaml("examples/income-verification/triples/verify-w2/verify-w2.jobaid.yaml")
jobaid = JobAid.from_dict(data)

# Verify properties
assert jobaid.rule_count == 40
assert jobaid.dimension_names == ["loan_program", "income_type", "employment_duration"]

# Query
matches = jobaid.query({"loan_program": "FHA", "income_type": "overtime", "employment_duration": "2_years_or_more"})
assert len(matches) == 1
assert matches[0].id == "R-003"
assert matches[0].specificity() == 3

# Round-trip
d = jobaid.to_dict()
jobaid2 = JobAid.from_dict(d)
assert jobaid2.rule_count == 40
```
