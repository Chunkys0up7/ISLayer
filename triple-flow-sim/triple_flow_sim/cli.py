"""Click-based CLI entry point.

Commands:
    triple_flow_sim inventory --corpus-config <path> [--bpmn <path>] [--out <dir>]
    triple_flow_sim load --corpus-config <path>
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

import click

from triple_flow_sim import TAXONOMY_VERSION, __version__
from triple_flow_sim.components.c01_loader import TripleLoader
from triple_flow_sim.components.c02_inventory import TripleInventory
from triple_flow_sim.components.c03_graph import JourneyGraph
from triple_flow_sim.components.c04_static_handoff.checker import (
    StaticHandoffChecker,
)
from triple_flow_sim.components.c05_llm import build_default_client
from triple_flow_sim.components.c06_persona import PersonaGenerator
from triple_flow_sim.components.c07_isolation import IsolationHarness
from triple_flow_sim.components.c08_grounded import SequenceRunner
from triple_flow_sim.components.c09_boundary import BranchBoundaryHarness
from triple_flow_sim.components.c11_classifier import FindingClassifier
from triple_flow_sim.components.c12_store import FindingStore
from triple_flow_sim.components.c13_reports import ReportBuilder
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
    help="Path to loader config YAML",
)
@click.option(
    "--bpmn",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to BPMN 2.0 XML file (required for static handoff checks)",
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
def static(corpus_config: Path, bpmn: Path, out: Path, log_level: str):
    """Run inventory + Phase 2 static handoff checker.

    Emits all Phase 1 inventory findings plus Phase 2 C1-C6 pair-check and
    G1-G3 gateway-check findings.
    """
    setup_logging(log_level)
    log = get_logger("cli.static")

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

    # 2. Build graph
    graph = JourneyGraph.from_bpmn_file(Path(bpmn), triple_set)
    bpmn_hash = graph.bpmn_data.source_hash
    log.info(
        f"Graph built: {len(graph.start_events())} starts, "
        f"{len(graph.end_events())} ends, "
        f"{len(graph.pairs_to_check())} edges"
    )

    # 3. Start run in store
    db_path = run_dir / "findings.db"
    store = FindingStore(db_path)
    store.start_run(
        run_id=run_id,
        corpus_version_hash=triple_set.corpus_version_hash,
        bpmn_version_hash=bpmn_hash,
        generator="static_handoff",
        simulator_version=__version__,
        taxonomy_version=TAXONOMY_VERSION,
        config=config.to_dict(),
    )

    # 4. Run inventory (Phase 1) + Phase 2 graph-level detections
    inv = TripleInventory(triple_set, graph=graph)
    inv_report = inv.run()

    extra_detections = []
    extra_detections.extend(graph.derive_topology_detections())
    extra_detections.extend(graph.cross_validate_against_derived())
    extra_detections.extend(graph.find_unbounded_loops())

    # 5. Run static handoff checker
    checker = StaticHandoffChecker(graph)
    check_report = checker.check_all()
    log.info(
        f"Static checker: {check_report.pairs_checked} pairs, "
        f"{check_report.gateways_checked} gateways"
    )

    all_detections = (
        list(inv_report.raw_detections) + extra_detections
        + check_report.all_detections()
    )
    log.info(
        f"Total detections: {len(all_detections)} "
        f"(inventory={len(inv_report.raw_detections)}, "
        f"graph={len(extra_detections)}, "
        f"static={len(check_report.all_detections())})"
    )

    # 6. Classify + emit
    classifier = FindingClassifier(strict=False)
    findings = []
    for det in all_detections:
        try:
            finding = classifier.classify(det, run_id)
            store.emit_finding(finding, run_id)
            findings.append(finding)
        except Exception as e:  # noqa: BLE001
            log.error(f"Failed to classify detection {det.signal_type}: {e}")

    store.complete_run(
        run_id,
        metrics={
            "total_triples": inv_report.total_triples,
            "total_findings": len(findings),
            "pairs_checked": check_report.pairs_checked,
            "gateways_checked": check_report.gateways_checked,
        },
    )
    store.close()

    # 7. Write reports (reuse inventory renderer — full static report in Phase 4)
    paths = write_reports(inv_report, findings, run_id, run_dir)
    log.info(
        f"Reports written: {paths['markdown_path']} | {paths['json_path']}"
    )

    click.echo(f"\n{'=' * 60}")
    click.echo(f"Run ID:            {run_id}")
    click.echo(f"Triples loaded:    {len(triple_set)}")
    click.echo(f"Pairs checked:     {check_report.pairs_checked}")
    click.echo(f"Gateways checked:  {check_report.gateways_checked}")
    click.echo(f"Findings emitted:  {len(findings)}")
    click.echo(f"Reports:           {run_dir}")
    click.echo(f"{'=' * 60}\n")
    return 0


@cli.command()
@click.option(
    "--corpus-config",
    type=click.Path(exists=True, path_type=Path),
    required=True,
)
@click.option(
    "--bpmn",
    type=click.Path(exists=True, path_type=Path),
    required=True,
)
@click.option(
    "--out",
    type=click.Path(path_type=Path),
    default=Path("./reports"),
)
@click.option(
    "--driver",
    type=click.Choice(["fake", "anthropic", "auto"]),
    default="fake",
    help="LLM driver. 'fake' is deterministic and offline.",
)
@click.option(
    "--seed", type=int, default=0,
)
@click.option(
    "--calibration-only",
    is_flag=True,
    default=False,
    help=(
        "Run context isolation in calibration mode — record divergences "
        "without emitting findings (Risk R4)."
    ),
)
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
)
def grounded(
    corpus_config: Path,
    bpmn: Path,
    out: Path,
    driver: str,
    seed: int,
    calibration_only: bool,
    log_level: str,
):
    """Phase 3: run grounded execution + context isolation + boundary probes.

    With --driver=fake (default) the run is deterministic and offline.
    Real LLM drivers activate with --driver=anthropic when ANTHROPIC_API_KEY
    is set.
    """
    setup_logging(log_level)
    log = get_logger("cli.grounded")

    run_id = (
        datetime.utcnow().strftime("%Y%m%dT%H%M%S") + "-" + str(uuid4())[:8]
    )
    run_dir = Path(out) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    config = load_config(Path(corpus_config))
    loader = TripleLoader(config)
    triple_set, load_report = loader.load()
    graph = JourneyGraph.from_bpmn_file(Path(bpmn), triple_set)
    bpmn_hash = graph.bpmn_data.source_hash
    llm = build_default_client(driver=driver, seed=seed)
    log.info(
        f"Loaded {len(triple_set)} triples; driver={driver}; "
        f"model={getattr(llm, 'model', '?')}"
    )

    db_path = run_dir / "findings.db"
    store = FindingStore(db_path)
    store.start_run(
        run_id=run_id,
        corpus_version_hash=triple_set.corpus_version_hash,
        bpmn_version_hash=bpmn_hash,
        generator="grounded_pair",
        simulator_version=__version__,
        taxonomy_version=TAXONOMY_VERSION,
        config=config.to_dict(),
    )

    all_detections = []

    # Phase 1/2 static findings so the grounded report is self-contained.
    inv = TripleInventory(triple_set, graph=graph)
    inv_report = inv.run()
    all_detections.extend(inv_report.raw_detections)
    all_detections.extend(graph.derive_topology_detections())
    all_detections.extend(graph.cross_validate_against_derived())
    all_detections.extend(graph.find_unbounded_loops())
    static = StaticHandoffChecker(graph).check_all()
    all_detections.extend(static.all_detections())

    # Personas.
    pg = PersonaGenerator(triple_set)
    personas = pg.all(boundary_limit=2)

    # Context isolation per triple, using the canonical persona state.
    iso = IsolationHarness(
        llm=llm, calibration_only=calibration_only, seed=seed
    )
    canonical = personas[0]
    for triple in triple_set:
        res = iso.run(triple, state=dict(canonical.seed_state))
        all_detections.extend(res.detections)

    # Sequence runs — one per persona.
    for persona in personas:
        trace, detections = SequenceRunner(
            graph, llm=llm, seed=seed
        ).run(
            persona,
            simulator_version=__version__,
            taxonomy_version=TAXONOMY_VERSION,
        )
        all_detections.extend(detections)
        log.info(
            f"Sequence run persona={persona.persona_id} "
            f"steps={trace.metrics.steps_executed} outcome={trace.outcome.value}"
        )

    # Branch boundary probes.
    boundary = BranchBoundaryHarness(graph, llm=llm, seed=seed).probe_all()
    for b in boundary:
        all_detections.extend(b.detections)

    # Classify + emit.
    classifier = FindingClassifier(strict=False)
    findings = []
    for det in all_detections:
        try:
            finding = classifier.classify(det, run_id)
            store.emit_finding(finding, run_id)
            findings.append(finding)
        except Exception as e:  # noqa: BLE001
            log.error(f"Failed to classify detection {det.signal_type}: {e}")

    store.complete_run(
        run_id,
        metrics={
            "total_triples": inv_report.total_triples,
            "total_findings": len(findings),
            "personas": len(personas),
            "boundary_gateways": len(boundary),
        },
    )
    store.close()

    paths = write_reports(inv_report, findings, run_id, run_dir)
    log.info(
        f"Reports written: {paths['markdown_path']} | {paths['json_path']}"
    )

    click.echo(f"\n{'=' * 60}")
    click.echo(f"Run ID:            {run_id}")
    click.echo(f"Driver:            {driver} (seed={seed})")
    click.echo(f"Personas:          {len(personas)}")
    click.echo(f"Findings emitted:  {len(findings)}")
    click.echo(f"Calibration only:  {calibration_only}")
    click.echo(f"Reports:           {run_dir}")
    click.echo(f"{'=' * 60}\n")
    return 0


@cli.command()
@click.option(
    "--db",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to a findings.db SQLite file produced by a prior run.",
)
@click.option(
    "--out",
    type=click.Path(path_type=Path),
    default=Path("./reports/summary"),
    help="Output directory for backlog.md + heatmap.json.",
)
@click.option(
    "--previous-db",
    type=click.Path(path_type=Path),
    default=None,
    help="Optional: previous run's findings.db for regression comparison.",
)
def report(db: Path, out: Path, previous_db: Optional[Path]):
    """Phase 4: render backlog, heatmap, regression delta, dossiers
    from an existing findings.db."""
    store = FindingStore(db)
    findings = store.get_findings()
    previous = None
    if previous_db is not None and Path(previous_db).exists():
        prev_store = FindingStore(Path(previous_db))
        previous = prev_store.get_findings()
        prev_store.close()
    triple_ids = sorted(
        {f.primary_triple_id for f in findings if f.primary_triple_id}
    )
    rb = ReportBuilder(Path(out))
    paths = rb.write_all(
        findings=findings,
        previous_findings=previous,
        triple_ids=triple_ids[:10],  # first 10 dossiers by default
    )
    store.close()
    click.echo(f"Findings: {len(findings)}")
    click.echo(f"Backlog:  {paths['backlog']}")
    click.echo(f"Heatmap:  {paths['heatmap']}")
    if "regression" in paths:
        click.echo(f"Regression: {paths['regression']}")
    click.echo(f"Dossiers: {len(triple_ids[:10])}")
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
