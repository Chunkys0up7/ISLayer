"""Perturbation generator (component 10) + Ablation generator.

Spec reference: files/10-perturbation-generator.md.

Phase 4 scope: two compact generators that stress-test triples by mutating
either the input state (perturbation) or the declared content (ablation)
and re-running execution. Divergence from the baseline becomes a finding.
"""
from triple_flow_sim.components.c10_perturbation.perturbation import (
    PerturbationGenerator,
    PerturbationSpec,
)
from triple_flow_sim.components.c10_perturbation.ablation import (
    AblationGenerator,
    AblationSpec,
)

__all__ = [
    "PerturbationGenerator",
    "PerturbationSpec",
    "AblationGenerator",
    "AblationSpec",
]
