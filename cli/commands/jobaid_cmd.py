"""mda jobaid — Import, validate, query, and manage job aids."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path


def run_jobaid(args, config):
    cmd = args.jobaid_command
    if cmd == "import":
        _jobaid_import(args, config)
    elif cmd == "validate":
        _jobaid_validate(args, config)
    elif cmd == "query":
        _jobaid_query(args, config)
    elif cmd == "list":
        _jobaid_list(args, config)
    else:
        from output.console import print_error
        print_error("Usage: mda jobaid {import|validate|query|list}")


def _jobaid_import(args, config):
    """Import job aid from Excel."""
    from pipeline.jobaid_processor import import_from_excel, write_jobaid
    from output.console import print_success, print_info, print_error

    excel_path = Path(args.file)
    capsule_id = args.capsule_id
    title = getattr(args, 'title', None)
    dims = getattr(args, 'dimensions', None)
    dim_list = dims.split(",") if dims else None

    if not excel_path.exists():
        print_error(f"File not found: {excel_path}")
        sys.exit(1)

    jobaid = import_from_excel(excel_path, capsule_id, title=title, dimension_columns=dim_list)

    # Determine output path
    output = getattr(args, 'output', None)
    if output:
        out_path = Path(output)
    else:
        # Auto-place next to the capsule's triple directory
        triples_path = config.get("paths.triples") or config.get("output.triples_dir") or "triples"
        triples_dir = config.project_root / triples_path
        # Find the triple dir for this capsule
        slug = capsule_id.lower().replace("cap-", "").replace("-", "_")
        out_path = triples_dir / f"{jobaid.jobaid_id.lower()}.jobaid.yaml"

    write_jobaid(jobaid, out_path)
    print_success(f"Imported {jobaid.rule_count} rules from {excel_path.name}")
    print_info(f"  Job Aid ID: {jobaid.jobaid_id}")
    print_info(f"  Dimensions: {', '.join(jobaid.dimension_names)}")
    print_info(f"  Written to: {out_path}")


def _jobaid_validate(args, config):
    """Validate job aid files."""
    from pipeline.jobaid_processor import validate_jobaid
    from output.console import print_header, print_success, print_error, print_warning, get_progress
    from output.json_output import output_json

    path = getattr(args, 'path', None)
    schemas_dir = config.schemas_dir

    if path:
        files = [Path(path)]
    else:
        # Find all .jobaid.yaml files
        triples_path = config.get("paths.triples") or config.get("output.triples_dir") or "triples"
        decisions_path = config.get("paths.decisions") or config.get("output.decisions_dir") or "decisions"
        triples_dir = config.project_root / triples_path
        decisions_dir = config.project_root / decisions_path
        files = list(triples_dir.rglob("*.jobaid.yaml")) + list(decisions_dir.rglob("*.jobaid.yaml"))

    if not files:
        print_warning("No job aid files found.")
        return

    print_header(f"Validating {len(files)} job aid(s)")
    all_errors = {}
    for f in files:
        errors = validate_jobaid(f, schemas_dir)
        if errors:
            all_errors[str(f)] = errors

    if getattr(args, 'json', False):
        output_json({"files": len(files), "errors": all_errors})
    elif all_errors:
        for file_path, errors in all_errors.items():
            print_error(f"{file_path}:")
            for e in errors:
                print_warning(f"  {e.get('path', '')}: {e.get('error', '')}")
    else:
        print_success(f"All {len(files)} job aid(s) pass validation")


def _jobaid_query(args, config):
    """Query a job aid with conditions."""
    from pipeline.jobaid_processor import query_jobaid
    from output.console import print_header, print_info, print_table
    from output.json_output import output_json

    jobaid_path = Path(args.jobaid_file)
    if not jobaid_path.exists():
        from output.console import print_error
        print_error(f"File not found: {jobaid_path}")
        sys.exit(1)

    # Parse conditions string: "key1=val1,key2=val2"
    conditions = {}
    if args.conditions:
        for pair in args.conditions.split(","):
            if "=" in pair:
                k, v = pair.split("=", 1)
                conditions[k.strip()] = v.strip()

    results = query_jobaid(jobaid_path, conditions)

    if getattr(args, 'json', False):
        output_json(results)
    else:
        print_header(f"Query results ({len(results)} matching rules)")
        for r in results:
            print_info(f"\n  Rule {r['id']}:")
            print_info(f"    Conditions: {r['conditions']}")
            for k, v in r['action'].items():
                print_info(f"    {k}: {v}")


def _jobaid_list(args, config):
    """List all job aids."""
    from pipeline.jobaid_processor import list_jobaids
    from output.console import print_header, print_table
    from output.json_output import output_json

    triples_path = config.get("paths.triples") or config.get("output.triples_dir") or "triples"
    decisions_path = config.get("paths.decisions") or config.get("output.decisions_dir") or "decisions"
    triples_dir = config.project_root / triples_path
    decisions_dir = config.project_root / decisions_path

    results = list_jobaids(triples_dir, decisions_dir)

    if getattr(args, 'json', False):
        output_json(results)
    else:
        print_header(f"Job Aids ({len(results)} found)")
        if results:
            rows = [[r.get("jobaid_id", ""), r.get("title", ""), str(r.get("rules", 0)), str(r.get("dimensions", 0)), r.get("status", "")] for r in results]
            print_table("Job Aids", ["ID", "Title", "Rules", "Dimensions", "Status"], rows)
