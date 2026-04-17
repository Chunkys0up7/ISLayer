"""Click-based CLI entry point.

Commands:
    triple_flow_sim inventory --corpus-config <path> [--bpmn <path>] [--out <dir>]
    triple_flow_sim load --corpus-config <path>
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import click

from triple_flow_sim import TAXONOMY_VERSION, __version__
from triple_flow_sim.components.c01_loader import TripleLoader
from triple_flow_sim.components.c02_inventory import TripleInventory
from triple_flow_sim.components.c03_graph import JourneyGraph
from triple_flow_sim.components.c11_classifier import FindingClassifier
from triple_flow_sim.components.c12_store import FindingStore
from triple_flow_sim.config import load_config
from triple_flow_sim.logging_setup import get_logger, setup_logging
from triple_flow_sim.reports.inventory_report import write_reports


@click.group()
@click.version_option(__version__, prog_name="triple_flow_sim")
def cli():
    """Triple Flow Simulator — diagnostic harness for MDA triple handoffs."""
    pass


@cli.command()
@click.option(
    "--corpus-config",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to loader config YAML",
)
@click.option(
    "--bpmn",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to BPMN 2.0 XML file (optional; graph checks deferred if omitted)",
)
@click.option(
    "--out",
    type=click.Path(path_type=Path),
    default=Path("./reports"),
    help="Output directory for reports and findings.db",
)
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
)
def inventory(corpus_config: Path, bpmn: Path, out: Path, log_level: str):
    """Run the inventory generator and emit the report."""
    setup_logging(log_level)
    log = get_logger("cli.inventory")

    run_id = (
        datetime.utcnow().strftime("%Y%m%dT%H%M%S") + "-" + str(uuid4())[:8]
    )
    run_dir = Path(out) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load triples
    config = load_config(Path(corpus_config))
    loader = TripleLoader(config)
    triple_set, load_report = loader.load()
    src = config.get("source.path") or config.get("source.ssh_url") or "?"
    log.info(f"Loaded {len(triple_set)} triples from {src}")
    log.info(
        f"Load failures: {len(load_report.failed_loads)}, "
        f"identity failures: {len(load_report.identity_failures)}"
    )

    # 2. Build graph (if BPMN provided)
    graph = None
    bpmn_hash = ""
    if bpmn is not None:
        try:
            graph = JourneyGraph.from_bpmn_file(Path(bpmn), triple_set)
            bpmn_hash = graph.bpmn_data.source_hash
            log.info(
                f"Graph built: {len(graph.start_events())} starts, "
                f"{len(graph.end_events())} ends, "
                f"{len(graph.pairs_to_check())} edges"
            )
        except Exception as exc:  # noqa: BLE001
            log.error(f"Failed to build graph from {bpmn}: {exc}")
            graph = None
    else:
        log.warning(
            "No BPMN file provided — graph-dependent invariants will run "
            "in best-effort mode"
        )

    # 3. Start run in store
    db_path = run_dir / "findings.db"
    store = FindingStore(db_path)
    store.start_run(
        run_id=run_id,
        corpus_version_hash=triple_set.corpus_version_hash,
        bpmn_version_hash=bpmn_hash,
        generator="inventory",
        simulator_version=__version__,
        taxonomy_version=TAXONOMY_VERSION,
        config=config.to_dict(),
    )

    # 4. Run inventory
    inv = TripleInventory(triple_set, graph=graph)
    report = inv.run()
    log.info(f"Inventory produced {len(report.raw_detections)} raw detections")

    # 5. Classify + emit
    classifier = FindingClassifier(strict=False)
    findings = []
    for det in report.raw_detections:
        try:
            finding = classifier.classify(det, run_id)
            store.emit_finding(finding, run_id)
            findings.append(finding)
        except Exception as e:  # noqa: BLE001
            log.error(f"Failed to classify detection {det.signal_type}: {e}")

    # 6. Complete run
    store.complete_run(
        run_id,
        metrics={
            "total_triples": report.total_triples,
            "total_findings": len(findings),
            "excluded_triples": len(report.exclusions),
        },
    )
    store.close()

    # 7. Write reports
    paths = write_reports(report, findings, run_id, run_dir)
    log.info(
        f"Reports written: {paths['markdown_path']} | {paths['json_path']}"
    )
    log.info(f"SQLite db: {db_path}")

    # Summary to stdout
    click.echo(f"\n{'=' * 60}")
    click.echo(f"Run ID:            {run_id}")
    click.echo(f"Triples loaded:    {len(triple_set)}")
    click.echo(f"Findings emitted:  {len(findings)}")
    click.echo(
        f"Triples excluded:  {len(report.exclusions)} (not simulatable)"
    )
    click.echo(f"Reports:           {run_dir}")
    click.echo(f"{'=' * 60}\n")

    return 0


@cli.command()
@click.option(
    "--corpus-config",
    type=click.Path(exists=True, path_type=Path),
    required=True,
)
def load(corpus_config: Path):
    """Load triples to cache and print summary (no inventory)."""
    setup_logging("INFO")
    config = load_config(Path(corpus_config))
    loader = TripleLoader(config)
    triple_set, load_report = loader.load()
    click.echo(f"Loaded {len(triple_set)} triples")
    click.echo(f"corpus_version_hash: {triple_set.corpus_version_hash}")
    click.echo(f"Failures: {len(load_report.failed_loads)}")
    click.echo(f"Identity failures: {len(load_report.identity_failures)}")


def main():
    """Entry point for `python -m triple_flow_sim` and console_scripts."""
    try:
        return cli(standalone_mode=False) or 0
    except click.exceptions.Abort:
        return 1
    except click.exceptions.ClickException as e:
        e.show()
        return e.exit_code


if __name__ == "__main__":
    sys.exit(main())
