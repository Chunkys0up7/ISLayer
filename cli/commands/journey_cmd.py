"""mda journey — Display process journey traceability: step summaries, data lineage, critical path."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_journey(args, config):
    """Entry point for the mda journey command."""
    from pipeline.journey_builder import build_journey
    from output.console import console, print_header, print_info, print_table, print_warning
    from output.json_output import output_json

    project_root = config.project_root
    journey = build_journey(project_root, config)

    if not journey or not journey.steps:
        print_warning("No journey data found. Run mda ingest first.")
        return

    step_id = getattr(args, "step", None)
    data_name = getattr(args, "data", None)
    fmt = getattr(args, "format", None)
    critical = getattr(args, "critical_path", False)

    if step_id:
        _show_step_detail(journey, step_id)
    elif data_name:
        _show_data_lineage(journey, data_name)
    elif fmt:
        _output_formatted(journey, fmt)
    elif critical:
        _show_critical_path(journey)
    else:
        _show_journey_summary(journey)


# ---------------------------------------------------------------------------
# Journey summary table
# ---------------------------------------------------------------------------


def _show_journey_summary(journey):
    """Print the full journey as a Rich table."""
    from output.console import console, print_header
    from rich.table import Table
    from rich import box

    print_header(f"Process Journey: {journey.process_name}")
    console.print(f"  Process ID: [bold]{journey.process_id}[/bold]  |  Steps: [bold]{journey.total_steps}[/bold]")

    hs = journey.health_summary
    if hs:
        console.print(
            f"  Avg Health: [bold]{hs.get('avg_health', 0)}[/bold]  |  "
            f"Gaps: [bold]{hs.get('total_gaps', 0)}[/bold]  |  "
            f"With Job Aid: [bold]{hs.get('steps_with_jobaid', 0)}[/bold]"
        )
    console.print()

    table = Table(title="Step Journey Map", box=box.SIMPLE_HEAVY, show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Name", style="bold")
    table.add_column("Type", style="dim")
    table.add_column("Owner")
    table.add_column("Inputs", width=14)
    table.add_column("Outputs", width=14)
    table.add_column("Systems")
    table.add_column("Binding", width=10)
    table.add_column("Health", width=8)
    table.add_column("Gaps", width=6)

    for step in journey.steps:
        inputs_str = ", ".join(i.name for i in step.required_inputs[:3])
        if len(step.required_inputs) > 3:
            inputs_str += f" +{len(step.required_inputs) - 3}"

        outputs_str = ", ".join(o.name for o in step.outputs[:3])
        if len(step.outputs) > 3:
            outputs_str += f" +{len(step.outputs) - 3}"

        systems = sorted(set(step.sources + step.sinks))
        systems_str = ", ".join(systems[:3])
        if len(systems) > 3:
            systems_str += f" +{len(systems) - 3}"

        binding_color = {
            "approved": "green", "bound": "green", "active": "green",
            "review": "yellow", "in_review": "yellow",
            "draft": "dim",
        }.get(step.binding_status, "red")
        binding_str = f"[{binding_color}]{step.binding_status}[/{binding_color}]"

        health_val = step.health_score
        if health_val >= 80:
            health_str = f"[green]{health_val}[/green]"
        elif health_val >= 50:
            health_str = f"[yellow]{health_val}[/yellow]"
        elif health_val > 0:
            health_str = f"[red]{health_val}[/red]"
        else:
            health_str = "[dim]--[/dim]"

        gaps_str = str(len(step.gaps)) if step.gaps else "[dim]0[/dim]"

        table.add_row(
            str(step.step_number),
            step.name,
            step.task_type,
            step.owner or "[dim]--[/dim]",
            inputs_str or "[dim]--[/dim]",
            outputs_str or "[dim]--[/dim]",
            systems_str or "[dim]--[/dim]",
            binding_str,
            health_str,
            gaps_str,
        )

    console.print(table)

    # Branch points
    if journey.branch_points:
        console.print(f"\n[bold]Branch Points:[/bold] {len(journey.branch_points)}")
        for bp in journey.branch_points:
            targets = ", ".join(b.get("target_name", "?") for b in bp.branches)
            console.print(f"  {bp.gateway_name} -> {targets}")

    # Critical path
    if journey.critical_path:
        path_names = []
        for cid in journey.critical_path:
            step = journey.get_step(cid)
            path_names.append(step.name if step else cid)
        console.print(f"\n[bold]Critical Path ({len(journey.critical_path)} steps):[/bold]")
        console.print("  " + " -> ".join(path_names))


# ---------------------------------------------------------------------------
# Step detail view
# ---------------------------------------------------------------------------


def _show_step_detail(journey, step_id):
    """Show detailed view of a single step."""
    from output.console import console, print_header, print_warning
    from rich.panel import Panel
    from rich.table import Table
    from rich import box

    step = journey.get_step(step_id)
    if not step:
        # Try matching by name substring
        matches = [s for s in journey.steps if step_id.lower() in s.name.lower() or step_id.lower() in s.capsule_id.lower()]
        if len(matches) == 1:
            step = matches[0]
        elif matches:
            print_warning(f"Ambiguous step ID '{step_id}'. Matches:")
            for m in matches:
                console.print(f"  {m.capsule_id}  {m.name}")
            return
        else:
            print_warning(f"Step '{step_id}' not found.")
            return

    lines = []
    lines.append(f"[bold]Step {step.step_number}:[/bold] {step.name}")
    lines.append(f"Capsule ID: {step.capsule_id}")
    lines.append(f"Type: {step.task_type}  |  Owner: {step.owner or '--'}  |  Binding: {step.binding_status}")
    lines.append(f"Health Score: {step.health_score}  |  Gaps: {len(step.gaps)}")

    if step.preconditions:
        lines.append(f"\n[bold]Preconditions:[/bold]")
        for pc in step.preconditions:
            lines.append(f"  - {pc}")

    if step.required_inputs:
        lines.append(f"\n[bold]Inputs ({len(step.required_inputs)}):[/bold]")
        for inp in step.required_inputs:
            req = "required" if inp.required else "optional"
            schema = f"  schema: {inp.schema_ref}" if inp.schema_ref else ""
            lines.append(f"  - {inp.name}  (source: {inp.source}, {req}){schema}")

    if step.outputs:
        lines.append(f"\n[bold]Outputs ({len(step.outputs)}):[/bold]")
        for out in step.outputs:
            inv = f"  invariants: {', '.join(out.invariants)}" if out.invariants else ""
            lines.append(f"  - {out.name}  (type: {out.type}, sink: {out.sink}){inv}")

    if step.invariants:
        lines.append(f"\n[bold]Invariants:[/bold]")
        for inv in step.invariants:
            lines.append(f"  - {inv}")

    if step.events_emitted:
        lines.append(f"\n[bold]Events Emitted:[/bold]")
        for ev in step.events_emitted:
            lines.append(f"  - {ev}")

    if step.predecessor_steps:
        lines.append(f"\n[bold]Predecessors:[/bold] {', '.join(step.predecessor_steps)}")
    if step.successor_steps:
        lines.append(f"[bold]Successors:[/bold] {', '.join(step.successor_steps)}")

    if step.sources or step.sinks:
        lines.append(f"\n[bold]External Systems:[/bold]")
        if step.sources:
            lines.append(f"  Sources: {', '.join(step.sources)}")
        if step.sinks:
            lines.append(f"  Sinks: {', '.join(step.sinks)}")

    if step.jobaid_id:
        lines.append(f"\n[bold]Job Aid:[/bold] {step.jobaid_id}")
        lines.append(f"  Dimensions: {', '.join(step.jobaid_dimensions) if step.jobaid_dimensions else '--'}")
        lines.append(f"  Rules: {step.jobaid_rule_count}")

    if step.gaps:
        lines.append(f"\n[bold]Gaps ({len(step.gaps)}):[/bold]")
        for gap in step.gaps[:10]:
            sev = gap.get("severity", "?")
            desc = gap.get("description", gap.get("message", str(gap)))
            lines.append(f"  [{sev}] {desc}")

    console.print(Panel("\n".join(lines), title=f"Step Detail: {step.capsule_id}", border_style="blue"))


# ---------------------------------------------------------------------------
# Data lineage view
# ---------------------------------------------------------------------------


def _show_data_lineage(journey, data_name):
    """Show data lineage for a specific data object."""
    from output.console import console, print_header, print_warning

    dl = journey.get_data(data_name)
    if not dl:
        # Show all available data objects
        print_warning(f"Data object '{data_name}' not found.")
        if journey.data_lineage:
            console.print("\n[bold]Available data objects:[/bold]")
            for d in journey.data_lineage:
                console.print(f"  {d.data_name}  (source: {d.source_name}, consumers: {len(d.consumers)})")
        return

    print_header(f"Data Lineage: {dl.data_name}")
    console.print(f"  Source: [bold]{dl.source_name}[/bold] ({dl.source})")

    if dl.consumers:
        console.print(f"\n  [bold]Consumed by ({len(dl.consumers)}):[/bold]")
        for c in dl.consumers:
            console.print(f"    -> {c.get('name', '?')}  ({c.get('capsule_id', '?')})")
    else:
        console.print("  [dim]No consumers found.[/dim]")

    # Show flow diagram
    console.print(f"\n  [bold]Flow:[/bold]")
    flow_parts = [f"[{dl.source_name}]"]
    flow_parts.append(f" -- {dl.data_name} -->")
    if dl.consumers:
        consumer_names = [c.get("name", "?") for c in dl.consumers]
        flow_parts.append(" | ".join(f"[{n}]" for n in consumer_names))
    else:
        flow_parts.append("[no consumers]")
    console.print("  " + " ".join(flow_parts))


# ---------------------------------------------------------------------------
# Critical path view
# ---------------------------------------------------------------------------


def _show_critical_path(journey):
    """Highlight critical path steps."""
    from output.console import console, print_header
    from rich.table import Table
    from rich import box

    print_header(f"Critical Path: {journey.process_name}")

    if not journey.critical_path:
        console.print("  [dim]No critical path computed (no predecessor/successor data).[/dim]")
        return

    console.print(f"  Length: [bold]{len(journey.critical_path)}[/bold] steps out of {journey.total_steps} total\n")

    table = Table(title="Critical Path Steps", box=box.SIMPLE_HEAVY)
    table.add_column("#", style="dim", width=4)
    table.add_column("Capsule ID")
    table.add_column("Name", style="bold")
    table.add_column("Type")
    table.add_column("Owner")
    table.add_column("Binding")

    cp_set = set(journey.critical_path)
    for step in journey.steps:
        if step.capsule_id in cp_set:
            table.add_row(
                str(step.step_number),
                step.capsule_id,
                step.name,
                step.task_type,
                step.owner or "--",
                step.binding_status,
            )

    console.print(table)

    # Path sequence
    path_names = []
    for cid in journey.critical_path:
        step = journey.get_step(cid)
        path_names.append(step.name if step else cid)
    console.print(f"\n[bold]Sequence:[/bold]")
    console.print("  " + " -> ".join(path_names))


# ---------------------------------------------------------------------------
# Formatted output (JSON, YAML, Mermaid)
# ---------------------------------------------------------------------------


def _output_formatted(journey, fmt):
    """Output journey in a structured format."""
    from output.console import console

    data = journey.to_dict()

    if fmt == "json":
        import json
        print(json.dumps(data, indent=2, default=str))

    elif fmt == "yaml":
        try:
            import yaml
            print(yaml.dump(data, default_flow_style=False, sort_keys=False))
        except ImportError:
            from output.json_output import output_json
            output_json(data)

    elif fmt == "mermaid":
        _print_mermaid(journey)

    else:
        import json
        print(json.dumps(data, indent=2, default=str))


def _print_mermaid(journey):
    """Generate a Mermaid diagram with data flow annotations."""
    lines = ["graph TD"]

    # Nodes
    for step in journey.steps:
        nid = step.capsule_id.replace("-", "_")
        label = step.name
        if "gateway" in step.task_type.lower() or "Gateway" in step.task_type:
            lines.append(f'    {nid}{{{{{label}}}}}')
        elif "event" in step.task_type.lower() or "Event" in step.task_type:
            lines.append(f'    {nid}(("{label}"))')
        else:
            lines.append(f'    {nid}["{label}"]')

    # Edges from successor relationships
    seen_edges = set()
    for step in journey.steps:
        for succ_name in step.successor_steps:
            # Find the successor step by name
            succ_step = None
            for s in journey.steps:
                if s.name == succ_name or s.capsule_id == succ_name:
                    succ_step = s
                    break
            if succ_step:
                edge_key = (step.capsule_id, succ_step.capsule_id)
                if edge_key not in seen_edges:
                    src = step.capsule_id.replace("-", "_")
                    tgt = succ_step.capsule_id.replace("-", "_")
                    lines.append(f'    {src} --> {tgt}')
                    seen_edges.add(edge_key)

    # Data flow annotations as comments
    if journey.data_lineage:
        lines.append("")
        lines.append("    %% Data Flow")
        for dl in journey.data_lineage:
            src = dl.source.replace("-", "_") if dl.source != "external" else "ext"
            for c in dl.consumers:
                tgt = c.get("capsule_id", "").replace("-", "_")
                if src and tgt:
                    lines.append(f'    %% {dl.data_name}: {src} -> {tgt}')

    # Style
    lines.append("")
    lines.append("    classDef task fill:#e1f5fe,stroke:#01579b")
    lines.append("    classDef gateway fill:#fff3e0,stroke:#e65100")
    lines.append("    classDef event fill:#e8f5e9,stroke:#1b5e20")
    lines.append("    classDef critical fill:#ffcdd2,stroke:#b71c1c")

    cp_set = set(journey.critical_path)
    for step in journey.steps:
        nid = step.capsule_id.replace("-", "_")
        if step.capsule_id in cp_set:
            lines.append(f"    class {nid} critical")
        elif "gateway" in step.task_type.lower() or "Gateway" in step.task_type:
            lines.append(f"    class {nid} gateway")
        elif "event" in step.task_type.lower() or "Event" in step.task_type:
            lines.append(f"    class {nid} event")
        else:
            lines.append(f"    class {nid} task")

    print("\n".join(lines))
