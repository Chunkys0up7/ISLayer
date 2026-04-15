"""mda skills generate — Auto-generate SKILL.md per BPMN step."""

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
            print_info(f"  /{skill_name} → {p}")
    else:
        print_warning("No skills generated. Check that triples exist in the process repo.")
