"""mda config -- Show or edit configuration."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_config(args, config):
    """Show, get, set, or validate configuration."""
    from mda_io.yaml_io import dump_yaml_string, write_yaml
    from output.console import print_header, print_success, print_error, print_info
    from output.json_output import output_json

    if args.get:
        value = config.get(args.get)
        if getattr(args, "json", False):
            output_json({"key": args.get, "value": value})
        else:
            print(f"{args.get} = {value}")

    elif args.set:
        key, value = args.set
        config.set(key, value)
        if config.config_path:
            write_yaml(config.config_path, config.to_dict())
            print_success(f"Set {key} = {value}")
        else:
            print_error(
                "No config file found. Run from a process directory or use --config."
            )

    elif args.validate:
        # Validate config paths resolve to existing locations
        issues = []
        for path_key in ["pipeline.schemas", "pipeline.ontology", "paths.corpus"]:
            resolved = config.resolve_path(path_key)
            if not resolved.exists():
                issues.append(f"{path_key}: {resolved} (not found)")
        if issues:
            print_error("Config validation failed:")
            for issue in issues:
                print_info(f"  {issue}")
        else:
            print_success("Config is valid")

    else:
        # Show full config
        if getattr(args, "json", False):
            output_json(config.to_dict())
        else:
            print_header("Configuration")
            if config.config_path:
                print_info(f"File: {config.config_path}")
            else:
                print_info("No config file found -- using defaults")
            print(dump_yaml_string(config.to_dict()))
