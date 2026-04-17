"""Implementation of the Context Isolation Harness.

Spec reference: files/07-context-isolation-harness.md §B1..B6.

Compares three runs of the same triple with progressively less context.
Divergence surfaces as ``handoff_carried_by_external_context`` findings.

Calibration mode (Risk R4): the harness can be invoked with
``calibration_only=True`` — it records divergences without emitting findings
so an SME can review whether the Level 1/2/3 deltas reflect genuine
contract gaps or simply legitimate content richness.
"""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from typing import Any, Optional

from triple_flow_sim.components.c05_llm import (
    FakeLLM,
    LLMClient,
    LLMRequest,
    LLMResponse,
)
from triple_flow_sim.components.c05_llm.prompts import (
    TEMPLATE_VERSION,
    RenderedPrompt,
    render,
)
from triple_flow_sim.contracts import (
    DivergenceSignature,
    Evidence,
    Generator,
    IsolationOutcome,
    IsolationResult,
    RawDetection,
    StateFieldRef,
    Triple,
)


# ---------------------------------------------------------------------------
# Level results
# ---------------------------------------------------------------------------
@dataclass
class IsolationLevelResult:
    level: str                        # "level1" | "level2" | "level3"
    outcome: IsolationOutcome = IsolationOutcome.SUCCESS
    raw_response: str = ""
    parsed_response: Optional[dict] = None
    refusals: list[dict] = field(default_factory=list)
    produced_writes: list[str] = field(default_factory=list)
    missing_declared_writes: list[str] = field(default_factory=list)
    extra_writes: list[str] = field(default_factory=list)
    template_id: str = ""
    prompt: str = ""


@dataclass
class IsolationRunResult:
    triple_id: str
    levels: dict[str, IsolationLevelResult] = field(default_factory=dict)
    divergence: bool = False
    divergence_signature: Optional[DivergenceSignature] = None
    detections: list[RawDetection] = field(default_factory=list)

    def as_contract(self) -> IsolationResult:
        """Convert into the contract IsolationResult shape (trace embedding)."""
        l1 = self.levels.get("level1")
        l2 = self.levels.get("level2")
        return IsolationResult(
            full_content_outcome=(
                l1.outcome if l1 else IsolationOutcome.SUCCESS
            ),
            declared_only_outcome=(
                l2.outcome if l2 else IsolationOutcome.SUCCESS
            ),
            divergence=self.divergence,
            divergence_signature=self.divergence_signature,
        )


# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------
class IsolationHarness:
    """Compare Level 1/2/3 outputs for a single triple."""

    def __init__(
        self,
        llm: Optional[LLMClient] = None,
        calibration_only: bool = False,
        seed: int = 0,
    ):
        self.llm = llm or FakeLLM(seed=seed)
        self.calibration_only = calibration_only
        self.seed = seed

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(
        self,
        triple: Triple,
        state: Optional[dict] = None,
    ) -> IsolationRunResult:
        state = state or {}
        l1 = self._run_level(triple, state, level="level1")
        l2 = self._run_level(triple, state, level="level2")
        l3 = self._run_level(triple, state, level="level3")

        result = IsolationRunResult(triple_id=triple.triple_id)
        result.levels = {"level1": l1, "level2": l2, "level3": l3}

        divergence, sig = self._detect_divergence(triple, l1, l2, l3)
        result.divergence = divergence
        result.divergence_signature = sig

        if divergence and not self.calibration_only:
            result.detections.extend(self._emit_detections(triple, sig))

        return result

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _run_level(
        self, triple: Triple, state: dict, level: str
    ) -> IsolationLevelResult:
        if level == "level1":
            prompt = self._level1_prompt(triple, state)
        elif level == "level2":
            prompt = self._level2_prompt(triple, state)
        elif level == "level3":
            prompt = self._level3_prompt(triple)
        else:  # pragma: no cover
            raise ValueError(level)

        req = LLMRequest(
            model=getattr(self.llm, "model", "fake"),
            prompt=prompt.prompt,
            system=prompt.system,
            temperature=0.0,
            seed=self.seed,
        )
        resp = self.llm.complete(req)
        return self._summarise_response(triple, prompt, resp, level)

    # --- level prompts ------------------------------------------------
    def _level1_prompt(self, triple: Triple, state: dict) -> RenderedPrompt:
        chunks = (triple.psm.enriched_content if triple.psm else []) or []
        state_reads = (triple.pim.state_reads if triple.pim else []) or []
        state_writes = (triple.pim.state_writes if triple.pim else []) or []
        return render(
            "level1_full_content",
            triple_id=triple.triple_id,
            bpmn_node_id=triple.bpmn_node_id or "",
            bpmn_node_type=triple.bpmn_node_type,
            intent=(triple.cim.intent if triple.cim else "") or "",
            content_chunks=chunks,
            state_reads=state_reads,
            state_writes=state_writes,
            state_json=_safe_json(state),
        )

    def _level2_prompt(self, triple: Triple, state: dict) -> RenderedPrompt:
        state_reads = (triple.pim.state_reads if triple.pim else []) or []
        state_writes = (triple.pim.state_writes if triple.pim else []) or []
        reduced_state = _project_state(state, state_reads)
        return render(
            "level2_declared_only",
            triple_id=triple.triple_id,
            bpmn_node_id=triple.bpmn_node_id or "",
            bpmn_node_type=triple.bpmn_node_type,
            intent=(triple.cim.intent if triple.cim else "") or "",
            state_reads=state_reads,
            state_writes=state_writes,
            state_json=_safe_json(reduced_state),
        )

    def _level3_prompt(self, triple: Triple) -> RenderedPrompt:
        return render(
            "level3_minimum",
            triple_id=triple.triple_id,
            intent=(triple.cim.intent if triple.cim else "") or "",
            minimal_state_json=_safe_json({}),
        )

    # --- parsing ------------------------------------------------------
    def _summarise_response(
        self,
        triple: Triple,
        prompt: RenderedPrompt,
        resp: LLMResponse,
        level: str,
    ) -> IsolationLevelResult:
        outcome = IsolationOutcome.SUCCESS
        parsed = resp.parsed
        if resp.finish_reason == "refused":
            outcome = IsolationOutcome.FAILURE
        elif resp.finish_reason == "stuck":
            outcome = IsolationOutcome.FAILURE
        elif parsed is None:
            try:
                parsed = json.loads(resp.raw_text)
            except Exception:  # noqa: BLE001
                parsed = None
                outcome = IsolationOutcome.PARTIAL

        produced_paths = _extract_paths(parsed or {})
        declared_writes = {
            r.path for r in ((triple.pim.state_writes if triple.pim else []) or [])
        }
        missing = sorted(declared_writes - set(produced_paths))
        extra = sorted(set(produced_paths) - declared_writes)
        if missing and outcome == IsolationOutcome.SUCCESS:
            outcome = IsolationOutcome.PARTIAL

        return IsolationLevelResult(
            level=level,
            outcome=outcome,
            raw_response=resp.raw_text,
            parsed_response=parsed,
            refusals=list(resp.refusals),
            produced_writes=produced_paths,
            missing_declared_writes=missing,
            extra_writes=extra,
            template_id=prompt.template_id,
            prompt=prompt.prompt,
        )

    # --- divergence ---------------------------------------------------
    def _detect_divergence(
        self,
        triple: Triple,
        l1: IsolationLevelResult,
        l2: IsolationLevelResult,
        l3: IsolationLevelResult,
    ) -> tuple[bool, Optional[DivergenceSignature]]:
        # Divergence signature draws from the spec — paths that were missing
        # only when content was removed are the tell-tale signs.
        missing_without_content = [
            StateFieldRef(path=p)
            for p in set(l2.missing_declared_writes)
            - set(l1.missing_declared_writes)
        ]
        extra_with_content = [
            StateFieldRef(path=p)
            for p in set(l1.extra_writes) - set(l2.extra_writes)
        ]
        behavior_change = ""
        if l1.outcome != l2.outcome or l1.outcome != l3.outcome:
            behavior_change = (
                f"level1={l1.outcome.value} "
                f"level2={l2.outcome.value} "
                f"level3={l3.outcome.value}"
            )
        if (
            not missing_without_content
            and not extra_with_content
            and not behavior_change
        ):
            return False, None
        sig = DivergenceSignature(
            missing_without_content=missing_without_content,
            extra_with_content=extra_with_content,
            behavior_change=behavior_change,
        )
        return True, sig

    # --- findings -----------------------------------------------------
    def _emit_detections(
        self, triple: Triple, sig: DivergenceSignature
    ) -> list[RawDetection]:
        detections: list[RawDetection] = []
        if sig.missing_without_content:
            detections.append(
                RawDetection(
                    signal_type="handoff_carried_by_external_context",
                    generator=Generator.CONTEXT_ISOLATION,
                    primary_triple_id=triple.triple_id,
                    bpmn_node_id=triple.bpmn_node_id or None,
                    detector_context={
                        "level_comparison": "level1_vs_level2",
                        "missing_without_content": [
                            r.path for r in sig.missing_without_content
                        ],
                        "behavior_change": sig.behavior_change,
                        "template_version": TEMPLATE_VERSION,
                    },
                    evidence=Evidence(
                        observed=(
                            f"Declared outputs "
                            f"{[r.path for r in sig.missing_without_content]} "
                            f"produced at Level 1 but absent at Level 2 — "
                            f"the step relied on content the contract does "
                            f"not guarantee."
                        )
                    ),
                )
            )
        if sig.extra_with_content:
            detections.append(
                RawDetection(
                    signal_type="output_over_promise",
                    generator=Generator.CONTEXT_ISOLATION,
                    primary_triple_id=triple.triple_id,
                    bpmn_node_id=triple.bpmn_node_id or None,
                    detector_context={
                        "extra_paths": [r.path for r in sig.extra_with_content],
                        "template_version": TEMPLATE_VERSION,
                    },
                    evidence=Evidence(
                        observed=(
                            f"Level 1 produced undeclared outputs "
                            f"{[r.path for r in sig.extra_with_content]} — "
                            f"the declared contract does not capture these."
                        )
                    ),
                )
            )
        return detections


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _safe_json(obj: Any) -> str:
    try:
        return json.dumps(obj, sort_keys=True, default=str)
    except Exception:  # noqa: BLE001
        return "{}"


def _project_state(state: dict, refs: list[StateFieldRef]) -> dict:
    """Return a subset of ``state`` limited to the declared read paths."""
    out: dict = {}
    for ref in refs:
        parts = ref.path.split(".")
        # walk and copy
        src = state
        dst = out
        for part in parts[:-1]:
            if not isinstance(src, dict) or part not in src:
                src = None
                break
            if part not in dst or not isinstance(dst[part], dict):
                dst[part] = {}
            dst = dst[part]
            src = src[part]
        if isinstance(src, dict) and parts[-1] in src:
            dst[parts[-1]] = copy.deepcopy(src[parts[-1]])
    return out


def _extract_paths(obj: Any, prefix: str = "") -> list[str]:
    """Flatten a dict into dotted paths. Ignore list internals — count the
    key that holds the list, not the list items."""
    if not isinstance(obj, dict):
        return []
    out: list[str] = []
    for k, v in obj.items():
        p = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict) and v:
            out.extend(_extract_paths(v, p))
        else:
            out.append(p)
    return out
