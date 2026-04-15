"""Skill Generator — auto-generate a SKILL.md per BPMN step from triple data."""

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
            "procedure_content": procedure_content or "*(No procedure documented yet — see capsule for details)*",
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
