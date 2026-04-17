"""Naming drift suspect detector (B3).

For each pair of writer/reader paths that are syntactically similar but not
identical, emit a naming_drift_suspect detection. Uses difflib.SequenceMatcher
ratio and caps at 20 findings/corpus to avoid noise.

Spec: files/02-triple-inventory.md §B3
"""
from __future__ import annotations

from difflib import SequenceMatcher

from triple_flow_sim.contracts import (
    Evidence,
    Generator,
    RawDetection,
    TripleSet,
)


SIMILARITY_THRESHOLD = 0.8
MAX_FINDINGS_PER_CORPUS = 20


def _writer_paths(triple_set: TripleSet) -> dict[str, str]:
    """path -> writer_triple_id (first occurrence)."""
    writers: dict[str, str] = {}
    for triple in triple_set.triples.values():
        if triple.pim is None:
            continue
        sources = []
        if triple.pim.state_writes:
            sources.extend(triple.pim.state_writes)
        if triple.pim.postconditions:
            sources.extend(triple.pim.postconditions)
        for ref in sources:
            path = getattr(ref, "path", None)
            if path and path not in writers:
                writers[path] = triple.triple_id
    return writers


def _reader_paths(triple_set: TripleSet) -> dict[str, str]:
    readers: dict[str, str] = {}
    for triple in triple_set.triples.values():
        if triple.pim is None:
            continue
        sources = []
        if triple.pim.state_reads:
            sources.extend(triple.pim.state_reads)
        if triple.pim.preconditions:
            sources.extend(triple.pim.preconditions)
        for ref in sources:
            path = getattr(ref, "path", None)
            if path and path not in readers:
                readers[path] = triple.triple_id
    return readers


def detect_naming_drift(triple_set: TripleSet) -> list[RawDetection]:
    writers = _writer_paths(triple_set)
    readers = _reader_paths(triple_set)
    detections: list[RawDetection] = []

    seen: set[tuple[str, str]] = set()
    for rp, reader_tid in readers.items():
        for wp, writer_tid in writers.items():
            if rp == wp:
                continue
            key = tuple(sorted((rp, wp)))
            if key in seen:
                continue
            seen.add(key)
            score = SequenceMatcher(None, rp, wp).ratio()
            if score <= SIMILARITY_THRESHOLD:
                continue
            detections.append(RawDetection(
                signal_type="naming_drift_suspect",
                generator=Generator.INVENTORY,
                primary_triple_id=reader_tid,
                related_triple_ids=[writer_tid] if writer_tid != reader_tid else [],
                detector_context={
                    "path_a": wp,
                    "path_b": rp,
                    "writer_a": writer_tid,
                    "reader_b": reader_tid,
                    "similarity_score": round(score, 3),
                },
                evidence=Evidence(
                    observed=f"{wp} vs {rp} score={score:.3f}",
                    expected="identical path or clearly-distinct paths",
                ),
            ))
            if len(detections) >= MAX_FINDINGS_PER_CORPUS:
                return detections
    return detections
