"""mda gaps -- List all gaps across triples."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_gaps(args, config):
    """Collect and display gaps from capsule frontmatter and the gaps/ directory."""
    from mda_io.frontmatter import read_frontmatter_file
    from output.console import print_header, print_gap_summary
    from output.json_output import output_json

    triples_dir = config.resolve_path("paths.triples")
    decisions_dir = config.resolve_path("paths.decisions")

    all_gaps = []

    # Collect gaps embedded in capsule frontmatter
    for base_dir in [triples_dir, decisions_dir]:
        if not base_dir.exists():
            continue
        for d in sorted(base_dir.iterdir()):
            if not d.is_dir() or d.name.startswith("_"):
                continue
            for cap in d.glob("*.cap.md"):
                fm, _ = read_frontmatter_file(cap)
                gaps = fm.get("gaps", [])
                for gap in gaps:
                    if isinstance(gap, dict):
                        gap["source_triple"] = d.name
                        gap["source_file"] = str(cap.name)
                        all_gaps.append(gap)

    # Also check standalone gaps/ directory
    gaps_path = config.get("paths.gaps")
    if gaps_path:
        gaps_dir = config.resolve_path("paths.gaps")
        if gaps_dir.exists():
            for gap_file in sorted(gaps_dir.glob("GAP-*.md")):
                fm, _body = read_frontmatter_file(gap_file)
                if fm:
                    fm["source_file"] = str(gap_file.name)
                    all_gaps.append(fm)

    # Apply filters
    if args.severity:
        all_gaps = [g for g in all_gaps if g.get("severity") == args.severity]
    if args.type:
        all_gaps = [g for g in all_gaps if g.get("type") == args.type]

    if getattr(args, "json", False):
        output_json(all_gaps)
    else:
        print_header(f"Gaps ({len(all_gaps)} found)")
        print_gap_summary(all_gaps)
