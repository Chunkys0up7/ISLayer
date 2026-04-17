"""Invariant I3 — cim.intent is non-empty and single-sentence.

Spec: files/triple-schema.md §I3
"""
from __future__ import annotations

import re

from triple_flow_sim.contracts import (
    Evidence,
    Generator,
    RawDetection,
    TripleSet,
)


# Heuristic: count sentence-terminating punctuation followed by whitespace AND
# some more non-whitespace content. Trailing punctuation is fine.
_MID_SENTENCE_BREAK = re.compile(r"[.!?]\s+\S")


def _is_single_sentence(text: str) -> bool:
    trimmed = text.strip()
    if not trimmed:
        return False
    # If there's a sentence boundary in the middle of the string, it's multi-sentence.
    return _MID_SENTENCE_BREAK.search(trimmed) is None


def check(triple_set: TripleSet, graph=None) -> list[RawDetection]:
    detections: list[RawDetection] = []
    for triple in triple_set.triples.values():
        if triple.cim is None:
            continue  # I2 handles missing CIM layer
        intent = (triple.cim.intent or "").strip()
        if not intent or not _is_single_sentence(intent):
            detections.append(RawDetection(
                signal_type="empty_or_multi_sentence_intent",
                generator=Generator.INVENTORY,
                primary_triple_id=triple.triple_id or "<unnamed>",
                bpmn_node_id=triple.bpmn_node_id or None,
                detector_context={"observed_intent": intent[:200]},
                evidence=Evidence(
                    observed=intent[:200] or "<empty>",
                    expected="non-empty, single sentence",
                ),
            ))
    return detections
