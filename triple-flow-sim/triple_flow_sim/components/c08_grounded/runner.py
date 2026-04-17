"""GroundedRunner + SequenceRunner.

Spec references: files/05-grounded-handoff-runner.md, files/06-sequence-runner.md.

Phase 3 scaffold: the runners walk the BPMN graph, render prompts, call the
LLM, merge the returned JSON into ``JourneyContext``, and emit RawDetection
events when obvious anomalies show up (refusals, missing declared writes,
unparseable output).

Mutation discipline (M1-M5) is lightly enforced: only declared writes are
merged; undeclared keys in the response are recorded as ``extra_writes`` on
the trace step but not mutated into the context state.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Optional
from uuid import uuid4

from triple_flow_sim.components.c05_llm import (
    FakeLLM,
    LLMClient,
    LLMRequest,
)
from triple_flow_sim.components.c05_llm.prompts import TEMPLATE_VERSION, render
from triple_flow_sim.contracts import (
    BpmnNodeType,
    ClosedObligation,
    Evidence,
    ExecutionMode,
    Generator,
    JourneyContext,
    LLMInteractionRecord,
    NodeExecution,
    OpenObligation,
    Persona,
    RawDetection,
    StateDiff,
    StateFieldRef,
    Trace,
    TraceMetrics,
    TraceMode,
    TraceOutcome,
    TraceStep,
    Triple,
)


# ---------------------------------------------------------------------------
# GroundedRunner — one triple at a time
# ---------------------------------------------------------------------------
class GroundedRunner:
    """Execute a single triple against an LLM and produce a TraceStep."""

    def __init__(
        self,
        llm: Optional[LLMClient] = None,
        seed: int = 0,
    ):
        self.llm = llm or FakeLLM(seed=seed)
        self.seed = seed

    def execute(
        self,
        triple: Triple,
        context: JourneyContext,
        step_index: int,
    ) -> tuple[TraceStep, list[RawDetection]]:
        prompt = render(
            "grounded_task" if triple.bpmn_node_type == BpmnNodeType.TASK
            else "grounded_gateway",
            triple_id=triple.triple_id,
            bpmn_node_id=triple.bpmn_node_id or "",
            bpmn_node_type=triple.bpmn_node_type,
            intent=(triple.cim.intent if triple.cim else "") or "",
            content_chunks=(triple.psm.enriched_content if triple.psm else []) or [],
            state_reads=(triple.pim.state_reads if triple.pim else []) or [],
            state_writes=(triple.pim.state_writes if triple.pim else []) or [],
            state_json=json.dumps(context.state, sort_keys=True, default=str),
            predicates=_predicate_dicts(triple),
        )
        req = LLMRequest(
            model=getattr(self.llm, "model", "fake"),
            system=prompt.system,
            prompt=prompt.prompt,
            temperature=0.0,
            seed=self.seed,
        )
        entered = datetime.utcnow()
        resp = self.llm.complete(req)
        exited = datetime.utcnow()
        parsed = resp.parsed
        if parsed is None:
            try:
                parsed = json.loads(resp.raw_text)
            except Exception:  # noqa: BLE001
                parsed = {}

        declared_writes = [
            r for r in ((triple.pim.state_writes if triple.pim else []) or [])
        ]
        declared_write_paths = {r.path for r in declared_writes}

        # Merge only declared writes into context.state (M1-M5 lite).
        observed_write_paths: list[StateFieldRef] = []
        for ref in declared_writes:
            if ref.path in _flatten_paths(parsed):
                observed_write_paths.append(ref)
                _merge_path(context.state, ref.path, _pluck_path(parsed, ref.path))

        extra_paths = sorted(_flatten_paths(parsed) - declared_write_paths)
        detections: list[RawDetection] = []
        if resp.finish_reason == "refused":
            detections.append(
                RawDetection(
                    signal_type="llm_refusal",
                    generator=Generator.GROUNDED_PAIR,
                    primary_triple_id=triple.triple_id,
                    bpmn_node_id=triple.bpmn_node_id or None,
                    detector_context={"refusals": resp.refusals},
                    evidence=Evidence(
                        observed=f"LLM refused: {resp.refusals}"
                    ),
                )
            )
        if extra_paths:
            detections.append(
                RawDetection(
                    signal_type="output_over_promise",
                    generator=Generator.GROUNDED_PAIR,
                    primary_triple_id=triple.triple_id,
                    bpmn_node_id=triple.bpmn_node_id or None,
                    detector_context={"extra_paths": extra_paths},
                )
            )
        missing_paths = sorted(
            declared_write_paths - _flatten_paths(parsed)
        )
        if missing_paths:
            detections.append(
                RawDetection(
                    signal_type="output_under_declaration",
                    generator=Generator.GROUNDED_PAIR,
                    primary_triple_id=triple.triple_id,
                    bpmn_node_id=triple.bpmn_node_id or None,
                    detector_context={"missing_paths": missing_paths},
                )
            )

        llm_record = LLMInteractionRecord(
            model=resp.model,
            model_version=resp.model_version,
            temperature=0.0,
            seed=self.seed,
            prompt_template_version=TEMPLATE_VERSION,
            prompt_sent=prompt.prompt,
            raw_response=resp.raw_text,
            parsed_response=parsed if isinstance(parsed, dict) else {},
            token_counts=resp.token_counts,
            refusals=resp.refusals,
        )

        step = TraceStep(
            step_index=step_index,
            triple_id=triple.triple_id,
            triple_version=triple.version,
            bpmn_node_id=triple.bpmn_node_id or "",
            bpmn_node_type=triple.bpmn_node_type.value
            if hasattr(triple.bpmn_node_type, "value")
            else str(triple.bpmn_node_type),
            entered_at=entered,
            exited_at=exited,
            declared_reads=(triple.pim.state_reads if triple.pim else []) or [],
            declared_writes=declared_writes,
            observed_writes=observed_write_paths,
            state_diff=StateDiff(),
            llm_interaction=llm_record,
            findings=[f"detection:{d.signal_type}" for d in detections],
        )

        # Append to context history for traceability.
        context.history.append(
            NodeExecution(
                step_index=step_index,
                triple_id=triple.triple_id,
                bpmn_node_id=triple.bpmn_node_id or "",
                mode=ExecutionMode.GROUNDED,
                state_writes_observed=observed_write_paths,
                llm_interaction=llm_record,
            )
        )
        # Open / close obligations per declared PIM metadata.
        if triple.pim and triple.pim.obligations_opened:
            for spec in triple.pim.obligations_opened:
                context.open_obligations.append(
                    OpenObligation(
                        obligation_id=spec.obligation_id,
                        opened_at_step=step_index,
                        opened_by_triple=triple.triple_id,
                    )
                )
        if triple.pim and triple.pim.obligations_closed:
            for oid in triple.pim.obligations_closed:
                context.closed_obligations.append(
                    ClosedObligation(
                        obligation_id=oid,
                        closed_at_step=step_index,
                        closed_by_triple=triple.triple_id,
                    )
                )

        return step, detections


# ---------------------------------------------------------------------------
# SequenceRunner — walks the journey graph
# ---------------------------------------------------------------------------
class SequenceRunner:
    """Execute a linear (or gateway-branching) sequence of triples."""

    def __init__(
        self,
        journey_graph,  # JourneyGraph
        llm: Optional[LLMClient] = None,
        seed: int = 0,
        max_steps: int = 100,
    ):
        self.graph = journey_graph
        self.seed = seed
        self.max_steps = max_steps
        self.runner = GroundedRunner(llm=llm, seed=seed)

    def run(
        self,
        persona: Persona,
        simulator_version: str,
        taxonomy_version: str,
    ) -> tuple[Trace, list[RawDetection]]:
        starts = self.graph.start_events()
        if not starts:
            raise RuntimeError("journey graph has no start events")

        context = JourneyContext(
            journey_id=f"journey-{uuid4().hex[:8]}",
            persona_id=persona.persona_id,
            current_node=starts[0],
            state=dict(persona.seed_state or {}),
        )
        trace = Trace(
            trace_id=f"trace-{uuid4().hex[:8]}",
            run_id=f"run-{uuid4().hex[:8]}",
            simulator_version=simulator_version,
            taxonomy_version=taxonomy_version,
            persona=persona,
        )
        trace.generator_config.mode = TraceMode.GROUNDED
        trace.generator_config.persona_seed = self.seed

        detections: list[RawDetection] = []
        node = starts[0]
        steps_taken = 0
        while node and steps_taken < self.max_steps:
            triple = self.graph.get_triple(node)
            if triple is not None:
                step, det = self.runner.execute(
                    triple, context, step_index=len(trace.steps)
                )
                trace.steps.append(step)
                detections.extend(det)
            node_data = self.graph.get_node(node) or {}
            node_type = node_data.get("node_type")
            if node_type == BpmnNodeType.END_EVENT:
                trace.outcome = TraceOutcome.COMPLETED
                trace.outcome_node = node
                break
            # Pick next node. Gateways: if a triple/LLM response nominated
            # an edge_id, use it; else take first successor (deterministic).
            successors = self.graph.successors(node)
            if not successors:
                trace.outcome = TraceOutcome.STUCK
                trace.outcome_node = node
                break
            next_node = None
            if node_type == BpmnNodeType.EXCLUSIVE_GATEWAY and trace.steps:
                last = trace.steps[-1]
                parsed = (
                    last.llm_interaction.parsed_response
                    if last.llm_interaction else {}
                )
                edge_id = (parsed or {}).get("edge_id")
                if edge_id:
                    for s in successors:
                        edge_data = self.graph.networkx.get_edge_data(node, s) or {}
                        if edge_data.get("edge_id") == edge_id:
                            next_node = s
                            break
            if next_node is None:
                next_node = successors[0]
            node = next_node
            steps_taken += 1

        trace.final_context = context
        trace.metrics = TraceMetrics(steps_executed=len(trace.steps))
        return trace, detections


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _flatten_paths(obj, prefix: str = "") -> set[str]:
    out: set[str] = set()
    if not isinstance(obj, dict):
        return out
    for k, v in obj.items():
        p = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict) and v:
            out.update(_flatten_paths(v, p))
        else:
            out.add(p)
    return out


def _pluck_path(obj, path: str):
    cur = obj
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _merge_path(state: dict, path: str, value) -> None:
    parts = path.split(".")
    cur = state
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def _predicate_dicts(triple: Triple) -> list[dict]:
    if triple.pim is None or not triple.pim.decision_predicates:
        return []
    return [
        {
            "edge_id": bp.edge_id,
            "expression": bp.predicate_expression,
            "is_default": bp.is_default,
        }
        for bp in triple.pim.decision_predicates
    ]
