"""mda status -- Show triple status summary."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_status(args, config):
    """Show status of all triples across triples/ and decisions/ directories."""
    from mda_io.frontmatter import read_frontmatter_file
    from output.console import print_header, print_status_table
    from output.json_output import output_json

    triples_dir = config.resolve_path("paths.triples")
    decisions_dir = config.resolve_path("paths.decisions")

    triples = []
    for base_dir in [triples_dir, decisions_dir]:
        if not base_dir.exists():
            continue
        for d in sorted(base_dir.iterdir()):
            if not d.is_dir() or d.name.startswith("_"):
                continue
            triple = {
                "name": d.name,
                "capsule": None,
                "intent": None,
                "contract": None,
                "gaps": 0,
            }
            for cap in d.glob("*.cap.md"):
                fm, _ = read_frontmatter_file(cap)
                triple["capsule"] = fm.get("status", "unknown")
                triple["capsule_id"] = fm.get("capsule_id", "")
                triple["gaps"] += len(fm.get("gaps", []))
            for intent in d.glob("*.intent.md"):
                fm, _ = read_frontmatter_file(intent)
                triple["intent"] = fm.get("status", "unknown")
            for contract in d.glob("*.contract.md"):
                fm, _ = read_frontmatter_file(contract)
                triple["contract"] = fm.get("status", "unknown")
                triple["binding"] = fm.get("binding_status", "unknown")
            triples.append(triple)

    if getattr(args, "json", False):
        output_json(triples)
    else:
        print_header(f"Triple Status ({len(triples)} triples)")
        print_status_table(triples)
