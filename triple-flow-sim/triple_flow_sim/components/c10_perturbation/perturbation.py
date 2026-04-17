"""State perturbation generator.

Spec reference: files/10-perturbation-generator.md §B1..B4.

A perturbation takes a baseline state and applies a deterministic mutation
(drop, null, truncate, corrupt-type) to one path, then re-runs the triple.
If the triple still claims to succeed, the contract may be too permissive;
if it now fails where the baseline didn't, the handoff depends on fragile
input — surface via ``input_under_declaration`` or ``cumulative_drift``.
"""
from __future__ import annotations

import copy
import random
from dataclasses import dataclass, field
from typing import Any, Optional

from triple_flow_sim.contracts import (
    Evidence,
    Generator,
    RawDetection,
    Triple,
)


@dataclass
class PerturbationSpec:
    kind: str                        # "drop" | "null" | "truncate" | "corrupt"
    path: str
    seed: int = 0


@dataclass
class PerturbationOutcome:
    spec: PerturbationSpec
    baseline_state: dict
    perturbed_state: dict
    baseline_response: dict
    perturbed_response: dict
    diverged: bool = False
    detections: list[RawDetection] = field(default_factory=list)


def _get_path(obj: dict, path: str) -> Any:
    cur = obj
    for p in path.split("."):
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur


def _set_path(obj: dict, path: str, value: Any) -> None:
    parts = path.split(".")
    cur = obj
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def _drop_path(obj: dict, path: str) -> None:
    parts = path.split(".")
    cur = obj
    for p in parts[:-1]:
        if not isinstance(cur, dict) or p not in cur:
            return
        cur = cur[p]
    if isinstance(cur, dict):
        cur.pop(parts[-1], None)


def apply_perturbation(state: dict, spec: PerturbationSpec) -> dict:
    """Return a mutated copy of ``state`` per ``spec``."""
    out = copy.deepcopy(state)
    rng = random.Random(spec.seed)
    if spec.kind == "drop":
        _drop_path(out, spec.path)
    elif spec.kind == "null":
        _set_path(out, spec.path, None)
    elif spec.kind == "truncate":
        v = _get_path(out, spec.path)
        if isinstance(v, str) and v:
            _set_path(out, spec.path, v[: max(1, len(v) // 2)])
        elif isinstance(v, list):
            _set_path(out, spec.path, v[: max(0, len(v) // 2)])
    elif spec.kind == "corrupt":
        v = _get_path(out, spec.path)
        if isinstance(v, (int, float)):
            _set_path(out, spec.path, f"CORRUPT-{rng.randint(1, 999)}")
        elif isinstance(v, str):
            _set_path(out, spec.path, rng.randint(1, 999))
        else:
            _set_path(out, spec.path, "CORRUPT")
    else:
        raise ValueError(f"Unknown perturbation kind: {spec.kind!r}")
    return out


class PerturbationGenerator:
    """Produce perturbation specs for a triple."""

    def __init__(self, seed: int = 0):
        self.seed = seed

    def plan(self, triple: Triple, kinds: Optional[list[str]] = None) -> list[PerturbationSpec]:
        kinds = kinds or ["drop", "null", "truncate", "corrupt"]
        reads = (triple.pim.state_reads if triple.pim else None) or []
        specs: list[PerturbationSpec] = []
        for i, ref in enumerate(reads):
            for j, kind in enumerate(kinds):
                specs.append(
                    PerturbationSpec(
                        kind=kind,
                        path=ref.path,
                        seed=self.seed + i * 100 + j,
                    )
                )
        return specs

    def diff_to_detection(
        self,
        triple: Triple,
        outcome: PerturbationOutcome,
    ) -> list[RawDetection]:
        if not outcome.diverged:
            return []
        return [
            RawDetection(
                signal_type="cumulative_drift",
                generator=Generator.PERTURBATION,
                primary_triple_id=triple.triple_id,
                bpmn_node_id=triple.bpmn_node_id or None,
                detector_context={
                    "kind": outcome.spec.kind,
                    "path": outcome.spec.path,
                    "seed": outcome.spec.seed,
                },
                evidence=Evidence(
                    observed=(
                        f"Perturbation {outcome.spec.kind} on "
                        f"{outcome.spec.path} changed the response."
                    )
                ),
            )
        ]
