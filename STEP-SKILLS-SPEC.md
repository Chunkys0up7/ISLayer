# MDA Intent Layer -- Step Skills Generator Specification

## 1. Overview

The Step Skills Generator auto-generates a `SKILL.md` per BPMN step from triple data. Each skill is a complete task briefing containing procedure, inputs, outputs, business rules, job aid conditions, system endpoints, failure modes, and process navigation.

This is the **last mile** of the MDA pipeline:

```
BPMN XML --> parse --> triples (capsule + intent + contract) --> step skills
```

A **step skill** (also called a "task skill") is fundamentally different from a **tool skill**:

| Aspect        | Tool Skill (e.g. `/mda-skills`) | Task Skill (e.g. `/verify-w2`) |
|---------------|----------------------------------|--------------------------------|
| Purpose       | Wraps a CLI command              | Briefs a user/agent on a task  |
| Content       | How to invoke a tool             | Full task context: procedure, rules, inputs, outputs, failure modes |
| Source        | Hand-authored                    | Auto-generated from triples    |
| Changes when  | CLI changes                      | Process knowledge changes      |
| Typical use   | Developer runs a pipeline step   | Agent executes a business task |

The generator reads the journey model (produced by `journey_builder`), iterates over every step, reads the corresponding capsule/intent/contract/job-aid files, and renders a Jinja2 template into `.claude/skills/{slug}/SKILL.md`.

---

## 2. Architecture

### Data Flow

```
mda.config.yaml
      |
      v
journey_builder.build_journey()  -->  ProcessJourney
      |                                     |
      |                              steps: [StepSummary]
      v                                     |
skill_generator.generate_step_skills()      |
      |                                     |
      |   For each step:                    |
      |     1. _find_triple_dir(slug)       |
      |     2. _read_md(.cap.md)            |
      |     3. _read_md(.intent.md)         |
      |     4. _read_md(.contract.md)       |
      |     5. Read .jobaid.yaml            |
      |     6. _extract_section(Procedure)  |
      |     7. _extract_section(Business Rules) |
      |     8. Build template context       |
      |     9. Render step-skill.md.j2      |
      v                                     |
.claude/skills/{slug}/SKILL.md              |
```

### Key Dependencies

- `cli/pipeline/journey_builder.py` -- provides `ProcessJourney` with ordered `StepSummary` list
- `cli/models/journey.py` -- `StepSummary` and `ProcessJourney` dataclasses
- `cli/mda_io/frontmatter.py` -- reads YAML frontmatter from triple markdown files
- `cli/mda_io/yaml_io.py` -- reads YAML job aid files
- `templates/skills/step-skill.md.j2` -- Jinja2 template for output
- `mda.config.yaml` -- project configuration (paths, process metadata)

### File Layout

```
project-repo/
  .claude/
    skills/
      verify-w2/
        SKILL.md          <-- generated task skill
      classify-employment-type/
        SKILL.md          <-- generated task skill
      mda-skills/
        SKILL.md          <-- hand-authored meta-skill (tool skill)
  triples/
    verify-w2/
      verify-w2.cap.md
      verify-w2.intent.md
      verify-w2.contract.md
      verify-w2.jobaid.yaml
```

---

## 3. CLI Command

### Argparse Registration (in `cli/mda.py`)

```python
# --- Skills ---
skills_parser = subparsers.add_parser("skills", help="Generate step-level skills from triples")
skills_sub = skills_parser.add_subparsers(dest="skills_command")
skills_gen = skills_sub.add_parser("generate", help="Generate a SKILL.md per BPMN step")
skills_gen.add_argument("--step", help="Generate for one specific step (capsule ID or name)")
skills_gen.add_argument("--output", type=Path, help="Output directory (default: .claude/skills/)")
```

### Dispatch (in `cli/mda.py`)

```python
elif args.command == "skills":
    from commands.skills_cmd import run_skills
    run_skills(args, config)
```

### Command Handler (`cli/commands/skills_cmd.py`)

```python
"""mda skills generate -- Auto-generate SKILL.md per BPMN step."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path


def run_skills(args, config):
    cmd = getattr(args, 'skills_command', None)
    if cmd == "generate":
        _skills_generate(args, config)
    else:
        from output.console import print_error
        print_error("Usage: mda skills generate [--step ID] [--output PATH]")


def _skills_generate(args, config):
    from pipeline.skill_generator import generate_step_skills
    from output.console import print_header, print_success, print_info, print_warning

    project_root = config.project_root
    output_dir = Path(args.output) if getattr(args, 'output', None) else None
    step_filter = getattr(args, 'step', None)

    print_header("Generating Step Skills")

    created = generate_step_skills(project_root, config, output_dir=output_dir, step_filter=step_filter)

    if created:
        print_success(f"Generated {len(created)} step skill(s)")
        for p in created:
            skill_name = p.parent.name
            print_info(f"  /{skill_name} -> {p}")
    else:
        print_warning("No skills generated. Check that triples exist in the process repo.")
```

### Usage

```bash
# Generate all step skills
python cli/mda.py skills generate

# Generate for one step only
python cli/mda.py skills generate --step verify-w2

# Generate to a custom directory
python cli/mda.py skills generate --output /tmp/skills/
```

---

## 4. Generator (`cli/pipeline/skill_generator.py`)

### Complete Source

```python
"""Skill Generator -- auto-generate a SKILL.md per BPMN step from triple data."""

import os, sys, re
from pathlib import Path
from datetime import datetime
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib.util
def _load_io(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mda_io", f"{name}.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
frontmatter_mod = _load_io("frontmatter")
yaml_io = _load_io("yaml_io")

from jinja2 import Environment, FileSystemLoader


def generate_step_skills(project_root: Path, config, output_dir: Optional[Path] = None,
                          step_filter: Optional[str] = None, engine_root: Optional[Path] = None) -> list[Path]:
    """Generate a SKILL.md for each BPMN step in the process.

    Returns list of created skill file paths.
    """
    # Resolve paths
    if output_dir is None:
        output_dir = project_root / ".claude" / "skills"
    output_dir.mkdir(parents=True, exist_ok=True)

    if engine_root is None:
        schemas_val = config.get("pipeline.schemas") if hasattr(config, 'get') and callable(getattr(config, 'get')) else None
        if isinstance(schemas_val, str):
            engine_root = (project_root / schemas_val).resolve().parent
        elif isinstance(schemas_val, dict):
            first = next(iter(schemas_val.values()), "../../schemas/capsule.schema.json")
            engine_root = (project_root / first).resolve().parent.parent
        else:
            engine_root = project_root.parent.parent

    # Set up Jinja2
    templates_dir = engine_root / "templates" / "skills"
    if not templates_dir.exists():
        raise FileNotFoundError(f"Skill templates not found at {templates_dir}")
    env = Environment(loader=FileSystemLoader(str(templates_dir)), keep_trailing_newline=True)

    # Build journey for step ordering and context
    _jb_spec = importlib.util.spec_from_file_location("journey_builder",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "journey_builder.py"))
    _jb_mod = importlib.util.module_from_spec(_jb_spec)
    _jb_spec.loader.exec_module(_jb_mod)
    journey = _jb_mod.build_journey(project_root, config)

    if not journey or not journey.steps:
        return []

    # Build step lookup for names
    step_lookup = {s.capsule_id: s for s in journey.steps}

    # Resolve paths for triples
    triples_path = _get_config(config, "paths.triples", "output.triples_dir", "triples")
    decisions_path = _get_config(config, "paths.decisions", "output.decisions_dir", "decisions")

    created = []

    for step in journey.steps:
        if step_filter and step_filter not in step.capsule_id and step_filter.lower() not in step.name.lower():
            continue

        # Find the triple directory
        triple_dir = _find_triple_dir(project_root, triples_path, decisions_path, step.slug)
        if not triple_dir:
            continue

        # Read triple files
        cap_fm, cap_body = _read_md(triple_dir, ".cap.md")
        int_fm, int_body = _read_md(triple_dir, ".intent.md")
        con_fm, con_body = _read_md(triple_dir, ".contract.md")

        # Read job aid if exists
        jobaid = None
        jobaid_path = None
        for ja_file in triple_dir.glob("*.jobaid.yaml"):
            jobaid = yaml_io.read_yaml(ja_file)
            jobaid_path = str(ja_file.relative_to(project_root))
            break

        # Extract body sections from capsule
        procedure_content = _extract_section(cap_body, "Procedure")
        business_rules = _extract_section(cap_body, "Business Rules")

        # Get predecessor/successor names
        predecessor_names = [step_lookup[pid].name for pid in step.predecessor_steps
                           if pid in step_lookup] if isinstance(step.predecessor_steps, list) else []
        successor_names = [step_lookup[sid].name for sid in step.successor_steps
                         if sid in step_lookup] if isinstance(step.successor_steps, list) else []
        # If successor_steps contains names instead of IDs, use directly
        if not successor_names and step.successor_steps:
            successor_names = [s for s in step.successor_steps if s]
        if not predecessor_names and step.predecessor_steps:
            predecessor_names = [s for s in step.predecessor_steps if s]

        # Build template context
        slug = step.slug or step.name.lower().replace(" ", "-")
        slug = re.sub(r'[^a-z0-9-]', '', slug)

        # Parse inputs/outputs from intent
        inputs = int_fm.get("inputs", []) or []
        outputs = int_fm.get("outputs", []) or []
        preconditions = int_fm.get("preconditions", []) or []
        failure_modes = int_fm.get("failure_modes", []) or []
        sources = con_fm.get("sources", []) or []

        # Collect all output invariants
        output_invariants = []
        for out in outputs:
            if isinstance(out, dict):
                for inv in out.get("invariants", []):
                    output_invariants.append(inv)
        # Add top-level invariants
        output_invariants.extend(int_fm.get("invariants", []) or [])

        context = {
            "slug": slug,
            "step": step.to_dict(),
            "step_number": step.step_number,
            "total_steps": journey.total_steps,
            "process_name": journey.process_name,
            "capsule_fm": cap_fm,
            "capsule_body": cap_body,
            "intent_fm": int_fm,
            "contract_fm": con_fm,
            "goal": int_fm.get("goal", ""),
            "preconditions": preconditions,
            "inputs": [i if isinstance(i, dict) else {"name": str(i)} for i in inputs],
            "outputs": [o if isinstance(o, dict) else {"name": str(o)} for o in outputs],
            "output_invariants": output_invariants,
            "sources": [s if isinstance(s, dict) else {"name": str(s)} for s in sources],
            "failure_modes": [fm if isinstance(fm, dict) else {"mode": str(fm)} for fm in failure_modes],
            "regulation_refs": cap_fm.get("regulation_refs", []) or [],
            "policy_refs": cap_fm.get("policy_refs", []) or [],
            "gaps": cap_fm.get("gaps", []) or [],
            "procedure_content": procedure_content or "*(No procedure documented yet -- see capsule for details)*",
            "business_rules": business_rules or "",
            "jobaid": jobaid,
            "jobaid_path": jobaid_path,
            "predecessor_names": predecessor_names,
            "successor_names": successor_names,
        }

        # Render template
        template = env.get_template("step-skill.md.j2")
        content = template.render(**context)

        # Write skill file
        skill_dir = output_dir / slug
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_path = skill_dir / "SKILL.md"
        skill_path.write_text(content, encoding="utf-8")
        created.append(skill_path)

    return created


def _get_config(config, key1, key2, default):
    """Get config value trying multiple key patterns."""
    if hasattr(config, 'get') and callable(getattr(config, 'get')):
        return config.get(key1) or config.get(key2) or default
    return default


def _find_triple_dir(project_root, triples_path, decisions_path, slug):
    """Find the triple directory for a step by slug."""
    for base in [triples_path, decisions_path]:
        candidate = project_root / base / slug
        if candidate.exists():
            return candidate
    return None


def _read_md(triple_dir, suffix):
    """Read a .md file from a triple directory."""
    files = list(triple_dir.glob(f"*{suffix}"))
    if files:
        return frontmatter_mod.read_frontmatter_file(files[0])
    return {}, ""


def _extract_section(body: str, section_name: str) -> str:
    """Extract a markdown section from the capsule body."""
    if not body:
        return ""
    pattern = rf"## {re.escape(section_name)}\s*\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, body, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""
```

### Function-by-Function Specification

#### `generate_step_skills(project_root, config, output_dir=None, step_filter=None, engine_root=None) -> list[Path]`

Main entry point. Orchestrates the full generation pipeline.

**Parameters:**

| Parameter      | Type            | Default                   | Description |
|----------------|-----------------|---------------------------|-------------|
| `project_root` | `Path`          | (required)                | Root of the process repository (where `mda.config.yaml` lives) |
| `config`       | config object   | (required)                | Parsed MDA config with `.get(key)` accessor |
| `output_dir`   | `Optional[Path]`| `project_root/.claude/skills/` | Where to write generated `SKILL.md` files |
| `step_filter`  | `Optional[str]` | `None`                    | If set, only generate for steps whose `capsule_id` contains this string or whose `name` matches (case-insensitive) |
| `engine_root`  | `Optional[Path]`| auto-resolved from config | Root of the MDA engine (parent of `templates/`) |

**Returns:** `list[Path]` -- paths to all created `SKILL.md` files.

**Algorithm:**

1. Resolve `output_dir` (default: `project_root/.claude/skills/`), create if needed.
2. Resolve `engine_root` from config's `pipeline.schemas` path, walking up to find the engine root.
3. Set up Jinja2 `Environment` with `templates/skills/` as the loader path.
4. Call `journey_builder.build_journey()` to get the full `ProcessJourney`.
5. Build a `step_lookup` dict mapping `capsule_id` to `StepSummary` for name resolution.
6. For each step in `journey.steps`:
   - Apply `step_filter` if set (skip non-matching steps).
   - Call `_find_triple_dir()` to locate the step's triple directory.
   - Read capsule, intent, and contract frontmatter+body via `_read_md()`.
   - Read job aid YAML if a `.jobaid.yaml` file exists.
   - Extract `Procedure` and `Business Rules` sections from capsule body via `_extract_section()`.
   - Resolve predecessor/successor names from the step lookup.
   - Build the template context dict from all collected data.
   - Render `step-skill.md.j2` with the context.
   - Write to `output_dir/{slug}/SKILL.md`.
7. Return list of all created file paths.

#### `_get_config(config, key1, key2, default)`

Tries two config key patterns, returns the first non-None value or the default.

| Parameter | Type   | Description |
|-----------|--------|-------------|
| `config`  | object | Config with `.get()` method |
| `key1`    | `str`  | Primary key (e.g. `"paths.triples"`) |
| `key2`    | `str`  | Fallback key (e.g. `"output.triples_dir"`) |
| `default` | `str`  | Default value if both keys miss |

#### `_find_triple_dir(project_root, triples_path, decisions_path, slug) -> Path | None`

Locates the triple directory for a step by checking both the `triples/` and `decisions/` directories.

| Parameter        | Type   | Description |
|------------------|--------|-------------|
| `project_root`   | `Path` | Project root |
| `triples_path`   | `str`  | Relative path to triples directory (e.g. `"triples"`) |
| `decisions_path` | `str`  | Relative path to decisions directory (e.g. `"decisions"`) |
| `slug`           | `str`  | Step slug (directory name, e.g. `"verify-w2"`) |

**Returns:** `Path` to the triple directory, or `None` if not found.

#### `_read_md(triple_dir, suffix) -> tuple[dict, str]`

Reads a markdown file with YAML frontmatter from a triple directory.

| Parameter    | Type   | Description |
|--------------|--------|-------------|
| `triple_dir` | `Path` | Directory containing triple files |
| `suffix`     | `str`  | File suffix to match (e.g. `".cap.md"`, `".intent.md"`, `".contract.md"`) |

**Returns:** `(frontmatter_dict, body_string)`. Returns `({}, "")` if no matching file found.

#### `_extract_section(body, section_name) -> str`

Regex extraction of a `## Section Name` block from capsule markdown body.

| Parameter      | Type  | Description |
|----------------|-------|-------------|
| `body`         | `str` | Full markdown body (after frontmatter) |
| `section_name` | `str` | Section heading to extract (e.g. `"Procedure"`, `"Business Rules"`) |

**Returns:** The section content (stripped), or `""` if not found.

**Regex pattern:** `## {section_name}\s*\n(.*?)(?=\n## |\Z)` with `re.DOTALL`.

### Template Context Dictionary

The following variables are passed to the Jinja2 template:

| Variable              | Type          | Source                                  |
|-----------------------|---------------|-----------------------------------------|
| `slug`                | `str`         | Step slug, sanitized to `[a-z0-9-]`     |
| `step`                | `dict`        | `StepSummary.to_dict()` -- full step data |
| `step_number`         | `int`         | 1-based position in journey             |
| `total_steps`         | `int`         | Total steps in the process              |
| `process_name`        | `str`         | Human-readable process name             |
| `capsule_fm`          | `dict`        | Capsule YAML frontmatter                |
| `capsule_body`        | `str`         | Capsule markdown body                   |
| `intent_fm`           | `dict`        | Intent YAML frontmatter                 |
| `contract_fm`         | `dict`        | Contract YAML frontmatter               |
| `goal`                | `str`         | From `intent_fm.goal`                   |
| `preconditions`       | `list[str]`   | From `intent_fm.preconditions`          |
| `inputs`              | `list[dict]`  | Each: `{name, source, schema_ref, required}` |
| `outputs`             | `list[dict]`  | Each: `{name, type, sink, invariants}` |
| `output_invariants`   | `list[str]`   | Merged from per-output + top-level invariants |
| `sources`             | `list[dict]`  | Each: `{name, protocol, endpoint, sla_ms}` |
| `failure_modes`       | `list[dict]`  | Each: `{mode, detection, action}`       |
| `regulation_refs`     | `list[str]`   | From `capsule_fm.regulation_refs`       |
| `policy_refs`         | `list[str]`   | From `capsule_fm.policy_refs`           |
| `gaps`                | `list[dict]`  | Each: `{type, description, severity}`   |
| `procedure_content`   | `str`         | Extracted `## Procedure` section body   |
| `business_rules`      | `str`         | Extracted `## Business Rules` section body |
| `jobaid`              | `dict or None`| Parsed `.jobaid.yaml` contents          |
| `jobaid_path`         | `str or None` | Relative path to job aid file           |
| `predecessor_names`   | `list[str]`   | Human-readable predecessor step names   |
| `successor_names`     | `list[str]`   | Human-readable successor step names     |

---

## 5. Template (`templates/skills/step-skill.md.j2`)

### Complete Template

```jinja2
---
name: {{ slug }}
description: "Step {{ step_number }}/{{ total_steps }} in {{ process_name }}: {{ step.name }}. {{ goal | default('Execute this task with the procedure, inputs, and business rules below.') }}"
allowed-tools: Bash(python *) Read
user-invocable: true
---

# Step {{ step_number }}: {{ step.name }}

**Type**: {{ step.task_type }} | **Owner**: {{ step.owner | default("Unassigned") }} | **Status**: {{ capsule_fm.status | default("draft") }}

---

## Where You Are in the Process

**Process**: {{ process_name }} (Step {{ step_number }} of {{ total_steps }})

{% if predecessor_names %}
**Previous**: {{ predecessor_names | join(", ") }}
{% else %}
**Previous**: *(Start of process)*
{% endif %}

{% if successor_names %}
**Next**: {{ successor_names | join(", ") }}
{% else %}
**Next**: *(End of process)*
{% endif %}

---

{% if preconditions %}
## Preconditions

Before starting this step, these must be true:

{% for pc in preconditions %}
- {{ pc }}
{% endfor %}
{% endif %}

{% if inputs %}
## Required Inputs

| Input | Source | Required |
|-------|--------|----------|
{% for inp in inputs %}
| {{ inp.name }} | {{ inp.source }} | {{ "Yes" if inp.required else "No" }} |
{% endfor %}
{% endif %}

## Procedure

{{ procedure_content }}

{% if business_rules %}
## Business Rules

{{ business_rules }}
{% endif %}

{% if jobaid %}
## Job Aid: {{ jobaid.title }}

This step has a **decision table** with **{{ jobaid.rules | length }} rules** across {{ jobaid.dimensions | length }} condition dimensions:

{% for dim in jobaid.dimensions %}
- **{{ dim["name"] }}**: {{ dim.get("values", []) | join(", ") }}
{% endfor %}

To look up conditions for a specific case:

```
python cli/mda.py jobaid query {{ jobaid_path }} -c "{{ jobaid.dimensions[0]["name"] }}=VALUE"
```
{% endif %}

{% if outputs %}
## Expected Outputs

| Output | Type | Destination |
|--------|------|-------------|
{% for out in outputs %}
| {{ out.name }} | {{ out.type }} | {{ out.sink }} |
{% endfor %}

{% if output_invariants %}
### Output Invariants

{% for inv in output_invariants %}
- {{ inv }}
{% endfor %}
{% endif %}
{% endif %}

{% if sources %}
## Systems Called

| System | Protocol | Endpoint | SLA |
|--------|----------|----------|-----|
{% for src in sources %}
| {{ src.name }} | {{ src.protocol }} | {{ src.endpoint }} | {{ src.sla_ms | default("-") }}ms |
{% endfor %}
{% endif %}

{% if failure_modes %}
## Failure Modes

| Mode | Detection | Action |
|------|-----------|--------|
{% for fm in failure_modes %}
| {{ fm.mode }} | {{ fm.detection }} | {{ fm.action }} |
{% endfor %}
{% endif %}

{% if regulation_refs or policy_refs %}
## Regulatory Context

{% for ref in regulation_refs %}
- {{ ref }}
{% endfor %}
{% for ref in policy_refs %}
- Policy: {{ ref }}
{% endfor %}
{% endif %}

{% if gaps %}
## Known Gaps

{% for gap in gaps %}
- **{{ gap.severity | upper }}**: {{ gap.description }} *({{ gap.type }})*
{% endfor %}
{% endif %}

---

## Validation

```
python cli/mda.py test --triples
python cli/mda.py report --format yaml
```

{% if successor_names %}
## What's Next

After completing this step, proceed to: **{{ successor_names[0] }}**
{% endif %}
```

### Template Sections Explained

| Section | Condition | Source Data |
|---------|-----------|-------------|
| **Frontmatter** | Always | `slug`, `step_number`, `total_steps`, `process_name`, `goal` |
| **Header** | Always | `step.name`, `step.task_type`, `step.owner`, `capsule_fm.status` |
| **Process Position** | Always | `process_name`, `step_number`, `total_steps`, `predecessor_names`, `successor_names` |
| **Preconditions** | `preconditions` non-empty | `intent_fm.preconditions` |
| **Required Inputs** | `inputs` non-empty | `intent_fm.inputs` (name, source, required) |
| **Procedure** | Always | Extracted `## Procedure` from capsule body; fallback placeholder |
| **Business Rules** | `business_rules` non-empty | Extracted `## Business Rules` from capsule body |
| **Job Aid** | `jobaid` is not None | `.jobaid.yaml` (title, rules count, dimensions, query command) |
| **Expected Outputs** | `outputs` non-empty | `intent_fm.outputs` (name, type, sink) |
| **Output Invariants** | `output_invariants` non-empty | Per-output invariants + top-level `intent_fm.invariants` |
| **Systems Called** | `sources` non-empty | `contract_fm.sources` (name, protocol, endpoint, sla_ms) |
| **Failure Modes** | `failure_modes` non-empty | `intent_fm.failure_modes` (mode, detection, action) |
| **Regulatory Context** | refs exist | `capsule_fm.regulation_refs` + `capsule_fm.policy_refs` |
| **Known Gaps** | `gaps` non-empty | `capsule_fm.gaps` (severity, description, type) |
| **Validation** | Always | Static commands |
| **What's Next** | `successor_names` non-empty | First successor name |

---

## 6. Meta-Skill (`/mda-skills`)

The meta-skill at `.claude/skills/mda-skills/SKILL.md` is a **tool skill** that wraps the `mda skills generate` CLI command. It is hand-authored, not generated.

### Complete SKILL.md Content

```markdown
---
name: mda-skills
description: Generate step-level skills from process triples. Creates a SKILL.md for each BPMN step containing the complete briefing packet (procedure, inputs, outputs, business rules, job aid conditions, systems, failure modes). Use to create actionable task skills from your process.
argument-hint: [generate] [--step <name>] [--output <path>]
allowed-tools: Bash(python *)
disable-model-invocation: true
---

# MDA Skills -- Generate Task Skills from Triples

Auto-generate a skill per BPMN step. Each skill gives the user/agent everything needed to execute that task.

## Context

Current working directory: !`pwd`
Triples: !`find . -name "*.cap.md" 2>/dev/null | wc -l || echo "0"` steps found
Existing step skills: !`ls .claude/skills/*/SKILL.md 2>/dev/null | wc -l || echo "0"` skills

## Steps

1. Generate skills for all steps:

```
python cli/mda.py skills generate $ARGUMENTS
```

2. Options:
   - `--step "verify-w2"` -- generate for one step only
   - `--output /custom/path/` -- write to a custom directory

3. After generation, the user can invoke any step skill by name:
   - `/verify-w2-income` -- W-2 income verification briefing
   - `/classify-employment-type` -- employment classification briefing

4. Each generated skill includes:
   - Process position (step N of M, predecessor/successor)
   - Preconditions, required inputs, procedure steps
   - Business rules, job aid conditions (if any)
   - Expected outputs with invariants
   - Systems to call (from contract)
   - Failure modes with detection and action
   - Regulatory context and known gaps
```

---

## 7. Example Output

The following is the complete generated skill for `verify-w2`, produced from the example triples in `examples/income-verification/triples/verify-w2/`. This shows what correct output looks like when all triple layers are populated.

### Generated `.claude/skills/verify-w2/SKILL.md`

```markdown
---
name: verify-w2
description: "Step 3/7 in Income Verification: Verify W-2 Income. Verify the borrower's W-2 wage income by cross-referencing W-2 forms against IRS tax return transcripts and computing a reliable monthly income figure for qualifying income calculation."
allowed-tools: Bash(python *) Read
user-invocable: true
---

# Step 3: Verify W-2 Income

**Type**: serviceTask | **Owner**: Verification Agent | **Status**: draft

---

## Where You Are in the Process

**Process**: Income Verification (Step 3 of 7)

**Previous**: Classify Employment Type

**Next**: Calculate Qualifying Income

---

## Preconditions

Before starting this step, these must be true:

- The borrower has been classified as a W-2 employee (employmentType = W2).
- W-2 documents for the most recent 2 tax years are available in DocVault with status AVAILABLE or VERIFIED.
- IRS Form 1040 transcripts for the corresponding years are available.
- The DocVault extraction service has parsed structured data from the W-2 images/PDFs.

## Required Inputs

| Input | Source | Required |
|-------|--------|----------|
| borrower_profile | Process Context | Yes |
| w2_documents | DocVault | Yes |
| tax_returns | DocVault | Yes |
| loanProgram | Process Context | Yes |

## Procedure

1. **Retrieve W-2 Documents**: Fetch the borrower's W-2 documents from DocVault for the most recent two tax years. Extract Box 1 (Wages, tips, other compensation) and Box 5 (Medicare wages) from each W-2.

2. **Retrieve Tax Return Transcripts**: Fetch IRS Form 1040 data for the same tax years. Extract Line 1 (Wages, salaries, tips) from each return.

3. **Cross-Reference W-2 to 1040**: For each tax year, compare the sum of all W-2 Box 1 amounts to the corresponding 1040 Line 1 amount. They should match or the W-2 total should be less than or equal to 1040 Line 1 (since 1040 may include additional wage sources).

4. **Validate Employer Information**: Confirm the employer name and EIN on the W-2 match the employment record in the borrower profile. Flag discrepancies for manual review.

5. **Calculate Year-over-Year Trend**: Compare the two years of W-2 income:
   - If income is stable or increasing, use the most recent year as the base.
   - If income declined by more than 10%, use the lower of the two years or the average, per Fannie Mae B3-3.1-01 guidance.

6. **Identify Additional Compensation**: Review W-2 boxes for overtime (if separately documented), bonuses, commissions, and tips. If these represent more than 25% of base pay, they require a 2-year history of receipt to be included in qualifying income.

7. **Compute Monthly Gross Income**: Calculate the verified monthly gross W-2 income:
   `verifiedMonthlyIncome = verifiedAnnualIncome / 12`

8. **Record Verification Result**: Store the verified income figure, supporting calculations, and any flags in the process context for the downstream qualifying income calculation.

## Business Rules

- Fannie Mae Selling Guide B3-3.1-01: Salary and wage income must be verified with W-2s and pay stubs covering the most recent 30 days plus the most recent two years.
- FHA 4000.1 II.A.4.c.2.a: W-2 income for the most recent two years is required. Declining income requires use of the lower figure.
- Conventional loans may use a 2-year average if income is stable or increasing.
- W-2 documents have been OCR-processed and structured data is available in DocVault.
- IRS transcript data is available through IVES or has been manually obtained and uploaded.

## Job Aid: W-2 Income Verification Decision Table

This step has a **decision table** with **40 rules** across 3 condition dimensions:

- **loan_program**: FHA, Conventional, VA, USDA
- **income_type**: base_salary, overtime, bonus, commission, tips
- **employment_duration**: less_than_2_years, 2_years_or_more

To look up conditions for a specific case:

```
python cli/mda.py jobaid query triples/verify-w2/verify-w2.jobaid.yaml -c "loan_program=VALUE"
```

## Expected Outputs

| Output | Type | Destination |
|--------|------|-------------|
| verifiedAnnualIncome | decimal | Process Context |
| verifiedMonthlyIncome | decimal | Process Context |
| incomeComponents | object | Process Context |
| incomeTrend | string | Process Context |
| w2_1040_matchResult | object | Process Context |
| verificationFlags | array | Process Context |

### Output Invariants

- verifiedAnnualIncome is derived from W-2 and 1040 cross-reference, never from stated income
- verifiedMonthlyIncome equals verifiedAnnualIncome / 12
- incomeTrend is one of STABLE, INCREASING, DECLINING
- W-2 Box 1 totals MUST NOT exceed 1040 Line 1 for the same tax year (unless additional W-2s from other employers are missing).
- If income declined year-over-year by more than 10%, the verified income MUST use the lower year or the 2-year average, whichever is less.
- Variable income (overtime, bonus, commission) exceeding 25% of base MUST have a 2-year receipt history to be included.
- Employer EIN on W-2 MUST match the employment record in borrower_profile or be flagged for review.

## Systems Called

| System | Protocol | Endpoint | SLA |
|--------|----------|----------|-----|
| DocVault W-2 Retrieval API | rest | https://docvault.example.com/api/v1/documents/borrower/{borrowerId}/w2 | 5000ms |
| DocVault Tax Return Retrieval API | rest | https://docvault.example.com/api/v1/documents/borrower/{borrowerId}/1040 | 5000ms |
| IRS IVES Transcript Service | rest | https://ives.example.com/api/v1/irs/ives/request-transcript | 30000ms |

## Failure Modes

| Mode | Detection | Action |
|------|-----------|--------|
| W-2 document parse failure | Structured data extraction failed or confidence below threshold | Re-queue for manual extraction; flag for underwriter |
| Missing tax year | W-2 or 1040 missing for one of the required tax years | Request document from borrower; cannot proceed without both years |
| EIN mismatch | Employer EIN on W-2 does not match borrower profile | Flag for manual review; may indicate unreported employer change |
| Amount mismatch | W-2 total significantly exceeds 1040 Line 1 | Halt; possible fraudulent W-2 or missing 1040 data |

## Regulatory Context

- Fannie Mae Selling Guide B3-3.1-01 (Salary and Wage Income)
- FHA 4000.1 II.A.4.c.2.a (W-2 Income Requirements)
- Policy: POL-IV-004 W-2 Income Verification Policy

## Known Gaps

- **LOW**: OCR extraction confidence threshold for auto-acceptance not yet defined (suggested: 0.95) *(missing_detail)*

---

## Validation

```
python cli/mda.py test --triples
python cli/mda.py report --format yaml
```

## What's Next

After completing this step, proceed to: **Calculate Qualifying Income**
```

---

## 8. Verification

### Verify the feature works end-to-end

```bash
# 1. From the example process repo, generate all skills
cd examples/income-verification
python ../../cli/mda.py skills generate

# 2. Check that SKILL.md files were created
ls -la .claude/skills/*/SKILL.md

# 3. Generate for a single step
python ../../cli/mda.py skills generate --step verify-w2

# 4. Inspect the output
cat .claude/skills/verify-w2/SKILL.md

# 5. Verify the generated skill has all expected sections
grep -c "^## " .claude/skills/verify-w2/SKILL.md
# Expected: 10+ sections (varies by step)

# 6. Verify frontmatter is valid
head -5 .claude/skills/verify-w2/SKILL.md
# Should show: ---\nname: verify-w2\ndescription: "Step ..."\n...

# 7. Run the full test suite to confirm nothing broke
python ../../cli/mda.py test --triples

# 8. Generate a report to check process health
python ../../cli/mda.py report --format yaml
```

### Verify template rendering

```bash
# Check that all sections render when data is present
python -c "
from pathlib import Path
skill = Path('.claude/skills/verify-w2/SKILL.md').read_text()
required = ['Preconditions', 'Required Inputs', 'Procedure', 'Business Rules',
            'Job Aid', 'Expected Outputs', 'Output Invariants', 'Systems Called',
            'Failure Modes', 'Regulatory Context', 'Known Gaps', 'Validation']
missing = [s for s in required if s not in skill]
print(f'Missing sections: {missing}' if missing else 'All sections present')
"
```

### Verify skills are invocable

After generation, each skill appears as a slash command in Claude Code:

```
/verify-w2                  -- W-2 income verification briefing
/classify-employment-type   -- employment classification briefing
/calculate-qualifying-income -- qualifying income calculation briefing
```

The skill frontmatter sets `user-invocable: true` and `allowed-tools: Bash(python *) Read`, enabling the agent to both read the briefing and execute validation commands.
