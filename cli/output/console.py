"""Rich terminal output helper for the MDA Intent Layer CLI."""

from typing import Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()
error_console = Console(stderr=True)


def print_header(title: str) -> None:
    """Print a styled header."""
    console.print(f"\n[bold blue]{title}[/bold blue]")
    console.print("\u2500" * min(len(title) + 4, 60))


def print_success(message: str) -> None:
    console.print(f"[green]OK[/green] {message}")


def print_warning(message: str) -> None:
    console.print(f"[yellow]WARN[/yellow] {message}")


def print_error(message: str) -> None:
    error_console.print(f"[red]ERROR[/red] {message}")


def print_info(message: str) -> None:
    console.print(f"[dim]{message}[/dim]")


def print_table(
    title: str,
    columns: list[str],
    rows: list[list[str]],
    styles: Optional[list[str]] = None,
) -> None:
    """Print a rich table."""
    table = Table(title=title, box=box.SIMPLE_HEAVY)
    for i, col in enumerate(columns):
        style = styles[i] if styles and i < len(styles) else None
        table.add_column(col, style=style)
    for row in rows:
        table.add_row(*row)
    console.print(table)


def print_validation_report(report: dict) -> None:
    """Print a structured validation report with colors.

    Expected report structure::

        {
            "file": str,
            "valid": bool,
            "errors": [{"path": str, "message": str, "severity": str}],
            "warnings": [{"path": str, "message": str}],
            "summary": {"total": int, "errors": int, "warnings": int},
        }
    """
    file_label = report.get("file", "unknown")
    valid = report.get("valid", False)

    if valid:
        print_success(f"{file_label} is valid")
    else:
        print_error(f"{file_label} has validation issues")

    errors = report.get("errors", [])
    warnings = report.get("warnings", [])

    if errors:
        table = Table(
            title="Errors",
            box=box.SIMPLE_HEAVY,
            title_style="bold red",
        )
        table.add_column("Severity", style="red")
        table.add_column("Path", style="cyan")
        table.add_column("Message")

        for err in errors:
            severity = err.get("severity", "error").upper()
            sev_color = _severity_color(severity.lower())
            table.add_row(
                f"[{sev_color}]{severity}[/{sev_color}]",
                err.get("path", ""),
                err.get("message", ""),
            )
        console.print(table)

    if warnings:
        table = Table(
            title="Warnings",
            box=box.SIMPLE_HEAVY,
            title_style="bold yellow",
        )
        table.add_column("Path", style="cyan")
        table.add_column("Message")
        for warn in warnings:
            table.add_row(warn.get("path", ""), warn.get("message", ""))
        console.print(table)

    summary = report.get("summary", {})
    if summary:
        total = summary.get("total", 0)
        err_count = summary.get("errors", 0)
        warn_count = summary.get("warnings", 0)
        console.print(
            f"\n  Total checks: {total}  "
            f"[red]Errors: {err_count}[/red]  "
            f"[yellow]Warnings: {warn_count}[/yellow]"
        )


def print_gap_summary(gaps: list[dict]) -> None:
    """Print gap summary table sorted by severity.

    Expected gap structure::

        {
            "id": str,
            "type": str,
            "severity": str,       # critical | high | medium | low
            "process": str,
            "description": str,
        }
    """
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    sorted_gaps = sorted(
        gaps, key=lambda g: severity_order.get(g.get("severity", "low"), 99)
    )

    table = Table(title="Gap Analysis", box=box.SIMPLE_HEAVY)
    table.add_column("Severity", width=10)
    table.add_column("Type", style="cyan")
    table.add_column("Process", style="dim")
    table.add_column("ID", style="dim")
    table.add_column("Description")

    for gap in sorted_gaps:
        severity = gap.get("severity", "low")
        sev_color = _severity_color(severity)
        table.add_row(
            f"[{sev_color}]{severity.upper()}[/{sev_color}]",
            gap.get("type", ""),
            gap.get("process", ""),
            gap.get("id", ""),
            gap.get("description", ""),
        )

    console.print(table)

    # Print counts by severity
    counts: dict[str, int] = {}
    for gap in gaps:
        sev = gap.get("severity", "low")
        counts[sev] = counts.get(sev, 0) + 1

    parts = []
    for sev in ("critical", "high", "medium", "low"):
        if sev in counts:
            color = _severity_color(sev)
            parts.append(f"[{color}]{sev}: {counts[sev]}[/{color}]")
    if parts:
        console.print(f"\n  Total gaps: {len(gaps)}  ({', '.join(parts)})")


def print_status_table(triples: list[dict]) -> None:
    """Print triple status table with colored status indicators.

    Expected triple structure::

        {
            "id": str,
            "name": str,
            "type": str,            # capsule | intent | contract
            "status": str,          # draft | review | approved | current | deprecated | archived
            "binding_status": str,  # bound | unbound | partial
            "process": str,
        }
    """
    table = Table(title="Triple Status", box=box.SIMPLE_HEAVY)
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("Type", style="cyan")
    table.add_column("Status")
    table.add_column("Binding")
    table.add_column("Process", style="dim")

    for triple in triples:
        status = triple.get("status", "draft")
        binding = triple.get("binding_status", "unbound")
        s_color = status_color(status)
        b_color = _binding_color(binding)

        table.add_row(
            triple.get("id", ""),
            triple.get("name", ""),
            triple.get("type", ""),
            f"[{s_color}]{status}[/{s_color}]",
            f"[{b_color}]{binding}[/{b_color}]",
            triple.get("process", ""),
        )

    console.print(table)

    # Summary counts
    status_counts: dict[str, int] = {}
    for t in triples:
        s = t.get("status", "draft")
        status_counts[s] = status_counts.get(s, 0) + 1

    parts = []
    for s, count in sorted(status_counts.items()):
        color = status_color(s)
        parts.append(f"[{color}]{s}: {count}[/{color}]")
    if parts:
        console.print(f"\n  Total triples: {len(triples)}  ({', '.join(parts)})")


def get_progress() -> Progress:
    """Get a progress bar context manager."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    )


def status_color(status: str) -> str:
    """Return Rich color markup for a status value."""
    colors = {
        "draft": "dim",
        "review": "yellow",
        "approved": "cyan",
        "current": "green",
        "deprecated": "red",
        "archived": "dim red",
    }
    return colors.get(status, "white")


def _severity_color(severity: str) -> str:
    """Return Rich color for a severity level."""
    colors = {
        "critical": "bold red",
        "high": "red",
        "medium": "yellow",
        "low": "dim",
        "error": "red",
    }
    return colors.get(severity.lower(), "white")


def _binding_color(binding: str) -> str:
    """Return Rich color for a binding status."""
    colors = {
        "bound": "green",
        "unbound": "dim",
        "partial": "yellow",
    }
    return colors.get(binding.lower(), "white")
