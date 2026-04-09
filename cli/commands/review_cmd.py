"""mda review <triple_path> -- LLM-assisted quality review of a triple."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_review(args, config):
    """Run an LLM-assisted quality review on a triple directory."""
    from mda_io.frontmatter import read_frontmatter_file
    from llm.provider import get_provider
    from llm.prompts.review import REVIEW_SYSTEM, build_review_prompt, REVIEW_SCHEMA
    from output.console import print_header, print_success, print_info, print_warning, print_error, print_table
    from output.json_output import output_json

    triple_path = args.triple_path
    if not triple_path.exists() or not triple_path.is_dir():
        raise FileNotFoundError(f"Triple directory not found: {triple_path}")

    aspect = getattr(args, "aspect", "all")

    # Find the three files
    cap_files = list(triple_path.glob("*.cap.md"))
    intent_files = list(triple_path.glob("*.intent.md"))
    contract_files = list(triple_path.glob("*.contract.md"))

    if not cap_files or not intent_files or not contract_files:
        missing = []
        if not cap_files:
            missing.append("capsule (.cap.md)")
        if not intent_files:
            missing.append("intent (.intent.md)")
        if not contract_files:
            missing.append("contract (.contract.md)")
        raise FileNotFoundError(f"Incomplete triple -- missing: {', '.join(missing)}")

    # Read file contents
    cap_fm, cap_body = read_frontmatter_file(cap_files[0])
    int_fm, int_body = read_frontmatter_file(intent_files[0])
    con_fm, con_body = read_frontmatter_file(contract_files[0])

    # Reconstruct full content for review
    import yaml
    capsule_content = yaml.dump(cap_fm, default_flow_style=False)[:1500] + "\n" + cap_body
    intent_content = yaml.dump(int_fm, default_flow_style=False)[:1500] + "\n" + int_body
    contract_content = yaml.dump(con_fm, default_flow_style=False)[:1500] + "\n" + con_body

    # Get LLM provider
    llm_provider = get_provider(config)

    # Build and execute review prompt
    prompt = build_review_prompt(capsule_content, intent_content, contract_content, aspect)

    try:
        review_result = llm_provider.complete_structured(
            prompt,
            schema=REVIEW_SCHEMA,
            system_prompt=REVIEW_SYSTEM,
            max_tokens=4096,
        )
    except Exception:
        # Fall back to free-form if structured output fails
        response = llm_provider.complete(prompt, system_prompt=REVIEW_SYSTEM, max_tokens=4096)
        review_result = {
            "overall_rating": "unknown",
            "findings": [],
            "summary": response.content,
        }

    if getattr(args, "json", False):
        output_json(review_result)
        return

    # Display results
    print_header(f"Review: {triple_path.name}")

    rating = review_result.get("overall_rating", "unknown")
    rating_colors = {
        "pass": "[green]PASS[/green]",
        "pass_with_warnings": "[yellow]PASS (with warnings)[/yellow]",
        "needs_revision": "[red]NEEDS REVISION[/red]",
        "fail": "[bold red]FAIL[/bold red]",
    }
    from rich.console import Console
    console = Console()
    console.print(f"  Overall: {rating_colors.get(rating, rating)}")

    # Display findings
    findings = review_result.get("findings", [])
    if findings:
        rows = []
        for f in findings:
            sev = f.get("severity", "?")
            asp = f.get("aspect", "?")
            file_name = f.get("file", "?")
            finding = f.get("finding", "")
            # Truncate long findings for table display
            if len(finding) > 80:
                finding = finding[:77] + "..."
            rows.append([sev, asp, file_name, finding])

        print_table(
            f"Findings ({len(findings)})",
            ["Severity", "Aspect", "File", "Finding"],
            rows,
            styles=["bold", None, None, None],
        )

        # Show recommendations for critical/high findings
        critical_high = [f for f in findings if f.get("severity") in ("critical", "high")]
        if critical_high:
            print_info("\n  Recommendations:")
            for f in critical_high:
                rec = f.get("recommendation", "No recommendation")
                print_info(f"    [{f.get('severity')}] {rec}")

    # Summary
    summary = review_result.get("summary", "")
    if summary:
        print_info(f"\n  Summary: {summary}")

    # Write output if requested
    if hasattr(args, "output") and args.output:
        import json
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(review_result, f, indent=2, default=str)
        print_success(f"Review written to {args.output}")
