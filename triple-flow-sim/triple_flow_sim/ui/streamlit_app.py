"""Streamlit demo for the Triple Flow Simulator.

Launch from the triple-flow-sim directory:

    pip install -e ".[ui]"
    streamlit run triple_flow_sim/ui/streamlit_app.py

Three panels:
1. Live Simulation — pick a corpus + BPMN + driver, click Run, watch findings stream.
2. Journey Graph — interactive BPMN with triple bindings and finding overlays.
3. Isolation Walkthrough — pick a triple, see Level 1/2/3 prompts and responses
   side-by-side.
"""
from __future__ import annotations

import io
import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

# Streamlit is an optional dependency — add a clear message if missing.
try:
    import pandas as pd  # noqa: F401
    import streamlit as st
except ImportError as exc:  # pragma: no cover - UI only
    sys.stderr.write(
        "Streamlit UI dependencies missing. "
        "Install with `pip install -e \".[ui]\"`.\n"
    )
    raise

# Ensure the package is importable when Streamlit is launched from anywhere.
_HERE = Path(__file__).resolve().parent
_PKG_ROOT = _HERE.parents[1]
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

import pandas as pd  # noqa: E402  (after sys.path tweak)

from triple_flow_sim import TAXONOMY_VERSION, __version__
from triple_flow_sim.components.c01_loader import TripleLoader
from triple_flow_sim.components.c02_inventory import TripleInventory
from triple_flow_sim.components.c03_graph import JourneyGraph
from triple_flow_sim.components.c04_static_handoff.checker import (
    StaticHandoffChecker,
)
from triple_flow_sim.components.c05_llm import build_default_client, FakeLLM
from triple_flow_sim.components.c05_llm.prompts import render as render_prompt
from triple_flow_sim.components.c06_persona import PersonaGenerator
from triple_flow_sim.components.c07_isolation import IsolationHarness
from triple_flow_sim.components.c08_grounded import SequenceRunner
from triple_flow_sim.components.c09_boundary import BranchBoundaryHarness
from triple_flow_sim.components.c11_classifier import FindingClassifier
from triple_flow_sim.config import load_config
from triple_flow_sim.ui.graph_view import render_graph


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Triple Flow Simulator",
    page_icon="🔀",
    layout="wide",
)

st.title("🔀 Triple Flow Simulator")
st.caption(
    f"Version {__version__} · Taxonomy {TAXONOMY_VERSION} · "
    "Diagnostic harness for inter-triple handoffs"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[2]
_FIXTURES = _REPO_ROOT / "tests" / "fixtures"


@st.cache_data(show_spinner=False)
def _list_demo_corpora() -> list[dict]:
    """Return the pre-bundled demo corpora that ship with the test fixtures."""
    items = []
    if (_FIXTURES / "corpus_clean").exists():
        items.append(
            {
                "label": "Clean corpus (3 triples, expected-clean)",
                "corpus_dir": _FIXTURES / "corpus_clean",
                "bpmn": _FIXTURES / "bpmn" / "simple.bpmn",
            }
        )
    if (_FIXTURES / "corpus_seeded").exists():
        items.append(
            {
                "label": "Seeded corpus (8 defects, each taxonomy class)",
                "corpus_dir": _FIXTURES / "corpus_seeded",
                "bpmn": _FIXTURES / "bpmn" / "simple_seeded.bpmn",
            }
        )
    return items


def _write_loader_yaml(tmp_dir: Path, corpus_dir: Path) -> Path:
    cfg = tmp_dir / "loader.yaml"
    cfg.write_text(
        "source_format: native_yaml\n"
        "source:\n"
        "  type: local\n"
        f"  path: {corpus_dir.name}\n"
        "ignore_paths: [\"README.md\"]\n"
        "strict_mode: false\n",
        encoding="utf-8",
    )
    return cfg


def _stage_corpus(
    corpus_dir: Path, bpmn: Path
) -> tuple[Path, Path]:
    """Copy a fixture into a tmp workspace so the loader's relative paths work."""
    import shutil

    work = Path(tempfile.mkdtemp(prefix="tfs-ui-"))
    shutil.copytree(corpus_dir, work / corpus_dir.name)
    bpmn_dst = work / "bpmn" / bpmn.name
    bpmn_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(bpmn, bpmn_dst)
    cfg = _write_loader_yaml(work, corpus_dir)
    return cfg, bpmn_dst


# ---------------------------------------------------------------------------
# Sidebar — corpus selection + run controls
# ---------------------------------------------------------------------------
st.sidebar.header("Configuration")

demo_options = _list_demo_corpora()
demo_labels = [d["label"] for d in demo_options]
demo_labels.append("Upload my own…")
pick = st.sidebar.selectbox("Corpus", demo_labels, index=0)

corpus_cfg_path: Optional[Path] = None
bpmn_path: Optional[Path] = None

if pick == "Upload my own…":
    up_cfg = st.sidebar.file_uploader(
        "loader.yaml", type=["yaml", "yml"]
    )
    up_bpmn = st.sidebar.file_uploader(
        "BPMN file", type=["bpmn", "xml"]
    )
    if up_cfg and up_bpmn:
        work = Path(tempfile.mkdtemp(prefix="tfs-up-"))
        corpus_cfg_path = work / "loader.yaml"
        corpus_cfg_path.write_bytes(up_cfg.read())
        bpmn_path = work / up_bpmn.name
        bpmn_path.write_bytes(up_bpmn.read())
else:
    demo = demo_options[demo_labels.index(pick)]
    corpus_cfg_path, bpmn_path = _stage_corpus(
        demo["corpus_dir"], demo["bpmn"]
    )

driver = st.sidebar.selectbox(
    "LLM driver", ["fake", "auto", "anthropic"], index=0,
    help=(
        "'fake' runs offline and is deterministic. 'auto' uses Anthropic "
        "if ANTHROPIC_API_KEY is set, else falls back to fake."
    ),
)
seed = st.sidebar.number_input("Seed", value=0, step=1)
calibration_only = st.sidebar.checkbox(
    "Calibration mode (suppress isolation findings, just record divergences)",
    value=False,
)

phases = st.sidebar.multiselect(
    "Phases to run",
    ["inventory", "static", "grounded", "isolation", "boundary"],
    default=["inventory", "static", "grounded", "isolation", "boundary"],
)

run_clicked = st.sidebar.button("▶ Run simulation", use_container_width=True)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
def _run_pipeline(
    corpus_cfg_path: Path,
    bpmn_path: Path,
    driver: str,
    seed: int,
    calibration_only: bool,
    phases: list[str],
    progress_cb,
):
    config = load_config(corpus_cfg_path)
    loader = TripleLoader(config)
    progress_cb("Loading triples…", 0.05)
    triple_set, load_report = loader.load()

    progress_cb("Building journey graph…", 0.15)
    graph = JourneyGraph.from_bpmn_file(bpmn_path, triple_set)

    llm = build_default_client(driver=driver, seed=seed)

    all_detections: list = []

    if "inventory" in phases:
        progress_cb("Running inventory invariants I1–I10…", 0.25)
        inv = TripleInventory(triple_set, graph=graph)
        inv_report = inv.run()
        all_detections.extend(inv_report.raw_detections)
    else:
        inv_report = None

    if "static" in phases:
        progress_cb("Static handoff checker (C1–C6, G1–G3)…", 0.40)
        all_detections.extend(graph.derive_topology_detections())
        all_detections.extend(graph.cross_validate_against_derived())
        all_detections.extend(graph.find_unbounded_loops())
        static_rep = StaticHandoffChecker(graph).check_all()
        all_detections.extend(static_rep.all_detections())

    isolation_runs: dict = {}
    if "isolation" in phases:
        progress_cb("Context Isolation Harness (Level 1/2/3)…", 0.60)
        pg = PersonaGenerator(triple_set)
        canonical = pg.canonical()
        iso = IsolationHarness(
            llm=llm, calibration_only=calibration_only, seed=seed
        )
        for triple in triple_set:
            res = iso.run(triple, state=dict(canonical.seed_state))
            isolation_runs[triple.triple_id] = res
            all_detections.extend(res.detections)

    traces: list = []
    if "grounded" in phases:
        progress_cb("Grounded sequence runs (per persona)…", 0.80)
        pg = PersonaGenerator(triple_set)
        for persona in pg.all(boundary_limit=1):
            trace, dets = SequenceRunner(
                graph, llm=llm, seed=seed
            ).run(
                persona,
                simulator_version=__version__,
                taxonomy_version=TAXONOMY_VERSION,
            )
            traces.append(trace)
            all_detections.extend(dets)

    if "boundary" in phases:
        progress_cb("Branch boundary probes…", 0.92)
        for b in BranchBoundaryHarness(graph, llm=llm, seed=seed).probe_all():
            all_detections.extend(b.detections)

    progress_cb("Classifying findings…", 0.98)
    classifier = FindingClassifier(strict=False)
    findings = []
    run_id = (
        datetime.utcnow().strftime("%Y%m%dT%H%M%S") + f"-ui-{seed}"
    )
    for det in all_detections:
        try:
            findings.append(classifier.classify(det, run_id))
        except Exception as exc:  # noqa: BLE001
            st.warning(f"classifier failed for {det.signal_type}: {exc}")

    progress_cb("Done", 1.0)
    return {
        "triple_set": triple_set,
        "graph": graph,
        "findings": findings,
        "isolation_runs": isolation_runs,
        "traces": traces,
        "run_id": run_id,
    }


# ---------------------------------------------------------------------------
# Execute
# ---------------------------------------------------------------------------
if run_clicked and corpus_cfg_path and bpmn_path:
    progress_bar = st.progress(0.0)
    status = st.empty()

    def cb(msg, pct):
        status.write(msg)
        progress_bar.progress(pct)

    try:
        result = _run_pipeline(
            corpus_cfg_path, bpmn_path,
            driver, int(seed), calibration_only, phases, cb,
        )
        st.session_state["result"] = result
        st.success(
            f"Run complete — {len(result['findings'])} findings on "
            f"{len(list(result['triple_set']))} triples"
        )
    except Exception as exc:  # noqa: BLE001
        st.error(f"Run failed: {exc}")
        raise


result = st.session_state.get("result")


# ---------------------------------------------------------------------------
# Tabs — only shown after a run
# ---------------------------------------------------------------------------
if result is None:
    st.info(
        "Pick a corpus in the sidebar and click **Run simulation** "
        "to populate the demo. The 'Clean corpus' demo runs offline in "
        "under a second with the fake LLM driver."
    )
    st.stop()


tab_graph, tab_findings, tab_iso, tab_trace = st.tabs(
    ["🗺 Journey graph", "📋 Findings", "🔬 Isolation walkthrough", "📝 Grounded trace"]
)

# -- Journey graph ---------------------------------------------------------
with tab_graph:
    st.subheader("BPMN + triple bindings + finding overlay")
    st.caption(
        "Green = bound node with no findings · Orange/red = findings "
        "(severity tints the fill) · Grey = unbound BPMN node · "
        "Thick border = critical path · Dashed edge = default branch"
    )
    out_dir = Path(tempfile.gettempdir()) / "tfs-ui-graph"
    out_file = out_dir / f"graph-{result['run_id']}.html"
    try:
        render_graph(result["graph"], result["findings"], out_file)
        st.components.v1.html(
            out_file.read_text(encoding="utf-8"), height=760, scrolling=True
        )
    except Exception as exc:  # noqa: BLE001
        st.warning(f"Graph render failed: {exc}")

# -- Findings --------------------------------------------------------------
with tab_findings:
    findings = result["findings"]
    if not findings:
        st.success("No findings detected.")
    else:
        rows = []
        for f in findings:
            rows.append(
                {
                    "severity": f.severity.value,
                    "layer": f.layer.value,
                    "defect_class": f.defect_class.value,
                    "triple": f.primary_triple_id or "",
                    "bpmn_node": f.bpmn_node_id or "",
                    "confidence": f.confidence.value,
                    "summary": f.summary,
                }
            )
        df = pd.DataFrame(rows)
        sev_filter = st.multiselect(
            "Filter severity",
            sorted({r["severity"] for r in rows}),
            default=sorted({r["severity"] for r in rows}),
        )
        class_filter = st.multiselect(
            "Filter defect class",
            sorted({r["defect_class"] for r in rows}),
            default=[],
        )
        mask = df["severity"].isin(sev_filter)
        if class_filter:
            mask &= df["defect_class"].isin(class_filter)
        st.dataframe(df[mask], use_container_width=True, hide_index=True)
        st.caption(
            f"{int(mask.sum())} of {len(rows)} findings shown · "
            f"{len({r['defect_class'] for r in rows})} distinct defect classes"
        )

# -- Isolation walkthrough -------------------------------------------------
with tab_iso:
    runs = result["isolation_runs"]
    if not runs:
        st.info("Isolation phase was not selected — enable it in the sidebar.")
    else:
        triple_ids = sorted(runs.keys())
        selected = st.selectbox("Pick a triple", triple_ids)
        run = runs[selected]
        st.write(
            f"**Divergence detected:** "
            f"{'✅ yes' if run.divergence else '❌ no'}"
        )
        if run.divergence_signature:
            sig = run.divergence_signature
            if sig.missing_without_content:
                st.warning(
                    "**Paths missing when content was removed:** "
                    + ", ".join(r.path for r in sig.missing_without_content)
                )
            if sig.extra_with_content:
                st.info(
                    "**Undeclared paths produced at Level 1:** "
                    + ", ".join(r.path for r in sig.extra_with_content)
                )
            if sig.behavior_change:
                st.caption(f"Behavior change: {sig.behavior_change}")

        cols = st.columns(3)
        for col, level in zip(cols, ("level1", "level2", "level3")):
            lv = run.levels.get(level)
            if lv is None:
                continue
            with col:
                st.markdown(f"### {level.upper()}  \n_{lv.template_id}_")
                st.markdown(f"**Outcome:** `{lv.outcome.value}`")
                if lv.missing_declared_writes:
                    st.markdown(
                        "**Missing declared writes:** "
                        + ", ".join(lv.missing_declared_writes)
                    )
                if lv.extra_writes:
                    st.markdown(
                        "**Extra writes:** " + ", ".join(lv.extra_writes)
                    )
                with st.expander("Prompt"):
                    st.code(lv.prompt, language="markdown")
                with st.expander("Response"):
                    st.code(
                        json.dumps(
                            lv.parsed_response or {}, indent=2, sort_keys=True
                        ),
                        language="json",
                    )

# -- Grounded trace --------------------------------------------------------
with tab_trace:
    traces = result["traces"]
    if not traces:
        st.info("No grounded traces — enable grounded phase in the sidebar.")
    else:
        trace = st.selectbox(
            "Trace",
            traces,
            format_func=lambda t: (
                f"{t.persona.persona_id} · "
                f"{t.metrics.steps_executed} steps · "
                f"{t.outcome.value}"
            ),
        )
        rows = []
        for step in trace.steps:
            obs_writes = [r.path for r in step.observed_writes]
            rows.append(
                {
                    "step": step.step_index,
                    "triple": step.triple_id,
                    "node": step.bpmn_node_id,
                    "declared_writes": [
                        r.path for r in step.declared_writes
                    ],
                    "observed_writes": obs_writes,
                    "llm_model": (
                        step.llm_interaction.model
                        if step.llm_interaction else ""
                    ),
                }
            )
        st.dataframe(
            pd.DataFrame(rows), use_container_width=True, hide_index=True
        )
        if trace.final_context:
            with st.expander("Final JourneyContext state"):
                st.code(
                    json.dumps(trace.final_context.state, indent=2, default=str),
                    language="json",
                )
