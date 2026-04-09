"""mda validate [path] -- Validate triples against schemas and consistency rules."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_validate(args, config):
    """Validate triples, decisions, or a specific path against schemas."""
    from pipeline.stage6_validator import run_validator
    from output.console import print_header, print_validation_report
    from output.json_output import output_json

    # Determine paths
    triples_dir = args.path or config.resolve_path("paths.triples")
    decisions_dir = config.resolve_path("paths.decisions") if not args.path else None
    schemas_dir = config.schemas_dir

    report = run_validator(triples_dir, decisions_dir, schemas_dir)

    if args.json:
        output_json(report.to_dict())
    else:
        print_header("Validation Report")
        print_validation_report(report.to_dict())

    # Exit code based on --fail-on severity threshold
    if args.fail_on:
        severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        threshold = severity_rank.get(args.fail_on, 99)
        has_failure = False

        for err in report.to_dict().get("errors", []):
            err_sev = severity_rank.get(err.get("severity", "low"), 99)
            if err_sev <= threshold:
                has_failure = True
                break

        if has_failure:
            sys.exit(1)
    elif report.overall_result.value == "fail":
        sys.exit(1)
