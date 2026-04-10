"""mda report — Generate GAP analysis report with health scoring."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path


def run_report(args, config):
    """Generate GAP analysis report with health scoring."""
    from pipeline.health_scorer import score_process
    from pipeline.report_generator import generate_xml, generate_json, generate_yaml, write_report
    from output.console import console, print_header, print_success, print_info
    from output.json_output import output_json

    project_root = config.project_root
    schemas_dir = config.schemas_dir
    corpus_dir = config.corpus_dir

    # Score the process
    report = score_process(project_root, config, schemas_dir, corpus_dir)

    fmt = getattr(args, 'format', 'xml') or 'xml'
    output_path = getattr(args, 'output', None)

    if output_path:
        write_report(report, Path(output_path), fmt)
        print_success(f"Report written to {output_path}")
    else:
        # Console display: show summary + write to stdout
        _print_console_report(report)

        # Also output in requested format if not already shown
        if fmt == "xml":
            print(generate_xml(report))
        elif fmt == "json":
            print(generate_json(report))
        elif fmt == "yaml":
            print(generate_yaml(report))


def _print_console_report(report):
    """Print Rich-formatted report summary."""
    from output.console import console
    from rich.table import Table
    from rich import box

    # Grade coloring
    grade_colors = {"A": "green", "B": "blue", "C": "yellow", "D": "red", "F": "bold red"}
    color = grade_colors.get(report.grade.value, "white")

    console.print(f"\n[bold]Process:[/bold] {report.process_name}")
    console.print(f"[bold]Health Score:[/bold] [{color}]{report.health_score:.1f} ({report.grade.value} — {report.grade_label})[/{color}]")
    console.print(f"[bold]Gaps:[/bold] {report.gap_summary.total} (critical: {report.gap_summary.critical}, high: {report.gap_summary.high}, medium: {report.gap_summary.medium}, low: {report.gap_summary.low})")
    console.print(f"[bold]Graph:[/bold] connected={report.graph_integrity.connected}, cycles={report.graph_integrity.cycles}")
    console.print()

    # Triple scores table
    table = Table(title="Triple Health Scores", box=box.SIMPLE_HEAVY)
    table.add_column("Triple", style="bold")
    table.add_column("Type", style="dim")
    table.add_column("Score", justify="right")
    table.add_column("Grade", justify="center")
    table.add_column("Gaps", justify="right")
    table.add_column("Comp", justify="right", style="dim")
    table.add_column("Cons", justify="right", style="dim")
    table.add_column("Schema", justify="right", style="dim")
    table.add_column("Know", justify="right", style="dim")
    table.add_column("AntiUI", justify="right", style="dim")

    for ts in report.triple_scores:
        gc = grade_colors.get(ts.grade.value, "white")
        dims = {d.name: d.score for d in ts.dimensions}
        table.add_row(
            ts.triple_name[:30],
            ts.bpmn_task_type,
            f"[{gc}]{ts.health_score:.0f}[/{gc}]",
            f"[{gc}]{ts.grade.value}[/{gc}]",
            str(len(ts.gaps)),
            f"{dims.get('completeness', 0):.0f}",
            f"{dims.get('consistency', 0):.0f}",
            f"{dims.get('schema_compliance', 0):.0f}",
            f"{dims.get('knowledge_coverage', 0):.0f}",
            f"{dims.get('anti_ui_compliance', 0):.0f}",
        )

    console.print(table)
