"""Tests for GroundedRunner and SequenceRunner."""
from __future__ import annotations

from triple_flow_sim.components.c05_llm import FakeLLM, LLMRequest, LLMResponse
from triple_flow_sim.components.c08_grounded import GroundedRunner
from triple_flow_sim.contracts import (
    CIMLayer,
    JourneyContext,
    PIMLayer,
    PSMLayer,
    StateFieldRef,
    Triple,
)


class _ScriptedLLM:
    model = "scripted"
    model_version = "1.0"

    def __init__(self, payload: dict):
        self.payload = payload

    def complete(self, req: LLMRequest) -> LLMResponse:
        import json
        raw = json.dumps(self.payload, sort_keys=True)
        return LLMResponse(
            raw_text=raw, parsed=self.payload, model=self.model
        )


def _triple(writes: list[str]) -> Triple:
    return Triple(
        triple_id="T1",
        cim=CIMLayer(intent="go"),
        pim=PIMLayer(
            state_writes=[StateFieldRef(path=p, type="string") for p in writes],
            state_reads=[],
        ),
        psm=PSMLayer(),
    )


def test_grounded_runner_writes_declared_paths():
    t = _triple(["decision.outcome"])
    llm = _ScriptedLLM({"decision": {"outcome": "approved"}})
    ctx = JourneyContext(journey_id="j1")
    runner = GroundedRunner(llm=llm)
    step, detections = runner.execute(t, ctx, step_index=0)
    assert ctx.state["decision"]["outcome"] == "approved"
    # No missing / extra path detections in the happy path.
    kinds = [d.signal_type for d in detections]
    assert "output_under_declaration" not in kinds
    assert "output_over_promise" not in kinds


def test_grounded_runner_flags_missing_declared_writes():
    t = _triple(["decision.outcome"])
    llm = _ScriptedLLM({"other": "field"})
    ctx = JourneyContext(journey_id="j1")
    runner = GroundedRunner(llm=llm)
    _, detections = runner.execute(t, ctx, step_index=0)
    assert any(
        d.signal_type == "output_under_declaration" for d in detections
    )


def test_grounded_runner_flags_extra_outputs():
    t = _triple(["decision.outcome"])
    llm = _ScriptedLLM(
        {"decision": {"outcome": "approved"}, "surprise": "value"}
    )
    ctx = JourneyContext(journey_id="j1")
    runner = GroundedRunner(llm=llm)
    _, detections = runner.execute(t, ctx, step_index=0)
    assert any(d.signal_type == "output_over_promise" for d in detections)


def test_grounded_runner_records_llm_interaction():
    t = _triple(["x"])
    llm = _ScriptedLLM({"x": 1})
    ctx = JourneyContext(journey_id="j1")
    step, _ = GroundedRunner(llm=llm).execute(t, ctx, step_index=0)
    assert step.llm_interaction is not None
    assert step.llm_interaction.prompt_template_version
