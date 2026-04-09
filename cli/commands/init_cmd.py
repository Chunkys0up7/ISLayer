"""mda init <name> -- Scaffold a new process repository."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_init(args, config):
    """Create a new process repository with standard directory structure."""
    from pathlib import Path
    from mda_io.yaml_io import write_yaml
    from output.console import print_header, print_success, print_info, print_error

    output_dir = args.output_dir or Path.cwd() / args.name

    if output_dir.exists():
        print_error(f"Directory already exists: {output_dir}")
        sys.exit(1)

    # Create directory structure
    dirs = [
        "bpmn",
        "triples",
        "decisions",
        "graph",
        "gaps",
        "audit",
    ]
    for d in dirs:
        (output_dir / d).mkdir(parents=True, exist_ok=True)

    # Create mda.config.yaml
    prefix = args.prefix or args.name[:2].upper()
    process_config = {
        "mda": {"version": "1.0.0"},
        "process": {
            "id": f"Process_{args.name.replace('-', '_').title().replace('_', '')}",
            "name": args.name.replace("-", " ").title(),
            "domain": args.domain or "Unspecified",
        },
        "paths": {
            "bpmn": "bpmn/",
            "triples": "triples/",
            "decisions": "decisions/",
            "graph": "graph/",
            "gaps": "gaps/",
            "audit": "audit/",
            "corpus": "../../corpus",
        },
        "naming": {"id_prefix": prefix},
        "llm": {
            "provider": "anthropic",
            "model": "claude-sonnet-4-20250514",
            "api_key_env": "ANTHROPIC_API_KEY",
        },
        "pipeline": {
            "schemas": "../../schemas/",
            "ontology": "../../ontology/",
        },
        "defaults": {
            "status": "draft",
            "binding_status": "unbound",
            "audit_retention_years": 7,
        },
    }
    write_yaml(output_dir / "mda.config.yaml", process_config)

    # Create empty manifests
    write_yaml(
        output_dir / "triples" / "_manifest.json",
        {"triples": [], "generated_date": "", "count": 0},
    )
    write_yaml(
        output_dir / "audit" / "ingestion-log.yaml",
        {"ingestions": []},
    )
    write_yaml(
        output_dir / "audit" / "change-log.yaml",
        {"changes": []},
    )

    # Create README
    readme = (
        f"# {args.name.replace('-', ' ').title()}\n\n"
        f"Process repository for the MDA Intent Layer.\n"
    )
    (output_dir / "README.md").write_text(readme, encoding="utf-8")

    if not getattr(args, "json", False):
        print_header(f"Initialized: {args.name}")
        print_success(f"Created at {output_dir}")
        for d in dirs:
            print_info(f"  {d}/")
        print_info("  mda.config.yaml")
        print_info("  README.md")
