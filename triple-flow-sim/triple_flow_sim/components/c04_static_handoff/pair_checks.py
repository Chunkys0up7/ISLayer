"""Pair-level static handoff checks C1-C6.

Each check is a pure function taking a producer Triple, consumer Triple, the
edge_id, and the shared evaluator/symbolic instances. Each returns a list of
RawDetection (possibly empty).

Spec reference: files/04-static-handoff-checker.md §B2
"""
from __future__ import annotations

from typing import Any, Optional

from triple_flow_sim.contracts import (
    ContextAssertion,
    Evidence,
    Generator,
    RawDetection,
    StateFieldRef,
    Triple,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _post_fields(producer: Triple) -> dict[str, StateFieldRef]:
    """path -> StateFieldRef for producer's state_writes."""
    out: dict[str, StateFieldRef] = {}
    if producer.pim is None:
        return out
    for sw in producer.pim.state_writes or []:
        out[sw.path] = sw
    return out


def _post_assertions(producer: Triple) -> dict[str, ContextAssertion]:
    """path -> ContextAssertion for producer's postconditions."""
    out: dict[str, ContextAssertion] = {}
    if producer.pim is None:
        return out
    for a in producer.pim.postconditions or []:
        out[a.path] = a
    return out


def _read_fields(consumer: Triple) -> dict[str, StateFieldRef]:
    out: dict[str, StateFieldRef] = {}
    if consumer.pim is None:
        return out
    for sr in consumer.pim.state_reads or []:
        out[sr.path] = sr
    return out


def _pre_assertions(consumer: Triple) -> list[ContextAssertion]:
    if consumer.pim is None:
        return []
    return list(consumer.pim.preconditions or [])


def _base_detection(
    signal_type: str,
    consumer: Triple,
    producer: Triple,
    edge_id: Optional[str],
    context: dict,
    observed: Any,
    expected: Any,
) -> RawDetection:
    return RawDetection(
        signal_type=signal_type,
        generator=Generator.STATIC_HANDOFF,
        primary_triple_id=consumer.triple_id,
        related_triple_ids=[producer.triple_id],
        bpmn_node_id=consumer.bpmn_node_id,
        bpmn_edge_id=edge_id,
        detector_context=context,
        evidence=Evidence(observed=observed, expected=expected),
    )


# ---------------------------------------------------------------------------
# C1 — State flow coverage
# ---------------------------------------------------------------------------
def c1_state_flow(
    producer: Triple,
    consumer: Triple,
    edge_id: Optional[str],
    evaluator=None,
    symbolic=None,
    upstream_writes: Optional[dict[str, StateFieldRef]] = None,
) -> list[RawDetection]:
    """For every consumer precondition/read, ensure some upstream producer writes it.

    If the producer (or any upstream producer in upstream_writes) writes the
    path, check passes. Missing path → state_flow_gap. Type mismatch on path
    → type_mismatch.
    """
    detections: list[RawDetection] = []
    post_fields = _post_fields(producer)
    all_writes: dict[str, StateFieldRef] = dict(upstream_writes or {})
    all_writes.update(post_fields)

    # Build the set of paths consumer expects from preconditions + state_reads.
    expected_paths: dict[str, str] = {}
    for pre in _pre_assertions(consumer):
        expected_paths[pre.path] = getattr(pre, "type", "any") or "any"
    for read in _read_fields(consumer).values():
        expected_paths.setdefault(read.path, read.type or "any")

    for path, expected_type in expected_paths.items():
        if path in all_writes:
            writer = all_writes[path]
            w_type = (writer.type or "any").lower()
            e_type = (expected_type or "any").lower()
            if w_type == "any" or e_type == "any" or w_type == e_type:
                continue
            detections.append(
                _base_detection(
                    "type_mismatch",
                    consumer, producer, edge_id,
                    context={
                        "path": path,
                        "expected_type": expected_type,
                        "observed_type": writer.type,
                    },
                    observed=writer.type,
                    expected=expected_type,
                )
            )
        else:
            detections.append(
                _base_detection(
                    "state_flow_gap",
                    consumer, producer, edge_id,
                    context={
                        "path": path,
                        "expected_type": expected_type,
                    },
                    observed=f"No upstream triple writes '{path}'",
                    expected=f"Some upstream triple to write '{path}'",
                )
            )
    return detections


# ---------------------------------------------------------------------------
# C2 — Type compatibility (focused on postcondition<->precondition type)
# ---------------------------------------------------------------------------
def c2_type_mismatch(
    producer: Triple,
    consumer: Triple,
    edge_id: Optional[str],
    evaluator=None,
    symbolic=None,
) -> list[RawDetection]:
    """Compare types between producer postconditions and consumer preconditions
    on the same path. Mismatches → type_mismatch.
    """
    detections: list[RawDetection] = []
    post_a = _post_assertions(producer)
    post_f = _post_fields(producer)

    for pre in _pre_assertions(consumer):
        pre_type = (getattr(pre, "type", "any") or "any").lower()
        producer_type: Optional[str] = None
        if pre.path in post_a:
            producer_type = (post_a[pre.path].type or "any").lower()
        elif pre.path in post_f:
            producer_type = (post_f[pre.path].type or "any").lower()
        else:
            continue
        if producer_type == "any" or pre_type == "any":
            continue
        if producer_type != pre_type:
            detections.append(
                _base_detection(
                    "type_mismatch",
                    consumer, producer, edge_id,
                    context={
                        "path": pre.path,
                        "expected_type": pre.type,
                        "observed_type": producer_type,
                    },
                    observed=producer_type,
                    expected=pre.type,
                )
            )
    return detections


# ---------------------------------------------------------------------------
# C3 — Semantic satisfaction via symbolic evaluator
# ---------------------------------------------------------------------------
def c3_semantic(
    producer: Triple,
    consumer: Triple,
    edge_id: Optional[str],
    evaluator=None,
    symbolic=None,
) -> list[RawDetection]:
    """Use the symbolic evaluator to pair postcondition vs precondition
    assertions on the same path.

    Verdict mapping (per-path):
        NEVER_SATISFIED     → handoff_format_mismatch (high confidence)
        SOMETIMES_SATISFIED → handoff_implicit_setup (medium confidence)
        UNDETERMINED        → handoff_implicit_setup (low confidence, only
                               when both sides carry concrete values)
        ALWAYS_SATISFIED    → no detection
    """
    if symbolic is None:
        return []

    from triple_flow_sim.evaluator.symbolic import SymbolicVerdict

    detections: list[RawDetection] = []
    post_a = _post_assertions(producer)

    for pre in _pre_assertions(consumer):
        if pre.path not in post_a:
            continue
        prod_assertion = post_a[pre.path]
        # Real evaluator takes lists; pass a single-item list per side so the
        # verdict reflects only this path pair.
        result = symbolic.compare_assertions([prod_assertion], [pre])
        verdict = getattr(result, "verdict", result)

        if verdict == SymbolicVerdict.NEVER_SATISFIED:
            detections.append(
                _base_detection(
                    "handoff_format_mismatch",
                    consumer, producer, edge_id,
                    context={
                        "path": pre.path,
                        "producer_assertion": _a_repr(prod_assertion),
                        "consumer_assertion": _a_repr(pre),
                        "verdict": verdict.value,
                    },
                    observed=_a_repr(prod_assertion),
                    expected=_a_repr(pre),
                )
            )
        elif verdict == SymbolicVerdict.SOMETIMES_SATISFIED:
            detections.append(
                _base_detection(
                    "handoff_implicit_setup",
                    consumer, producer, edge_id,
                    context={
                        "path": pre.path,
                        "confidence_hint": "medium",
                        "verdict": verdict.value,
                    },
                    observed=_a_repr(prod_assertion),
                    expected=_a_repr(pre),
                )
            )
        elif verdict == SymbolicVerdict.UNDETERMINED:
            # Conservative: stay quiet on UNDETERMINED unless both sides
            # carry concrete values (noisy LOW otherwise).
            if (
                getattr(prod_assertion, "value", None) is not None
                and getattr(pre, "value", None) is not None
            ):
                detections.append(
                    _base_detection(
                        "handoff_implicit_setup",
                        consumer, producer, edge_id,
                        context={
                            "path": pre.path,
                            "confidence_hint": "low",
                            "verdict": verdict.value,
                        },
                        observed=_a_repr(prod_assertion),
                        expected=_a_repr(pre),
                    )
                )
    return detections


def _a_repr(a: ContextAssertion) -> str:
    pred = getattr(a, "predicate", None)
    pred_name = getattr(pred, "value", pred)
    return f"{a.path} {pred_name}={a.value!r}"


# ---------------------------------------------------------------------------
# C4 — Obligation propagation (Phase 2 simplification)
# ---------------------------------------------------------------------------
def c4_obligations(
    producer: Triple,
    consumer: Triple,
    edge_id: Optional[str],
    evaluator=None,
    symbolic=None,
    downstream_closes: Optional[set[str]] = None,
) -> list[RawDetection]:
    """Phase 2 simplification per spec: flag only when direct successor does
    not close an obligation that producer opens AND there is no reachable
    triple closing it. ``downstream_closes`` is the set of obligation_ids
    closed by any downstream triple (passed by the facade).
    """
    detections: list[RawDetection] = []
    if producer.pim is None:
        return detections
    opened = producer.pim.obligations_opened or []
    if not opened:
        return detections

    consumer_closes: set[str] = set()
    if consumer.pim is not None:
        consumer_closes = set(consumer.pim.obligations_closed or [])
    all_closes = set(downstream_closes or set()) | consumer_closes

    for ob in opened:
        if ob.exits_journey:
            continue
        if ob.obligation_id in all_closes:
            continue
        det = RawDetection(
            signal_type="orphan_obligation",
            generator=Generator.STATIC_HANDOFF,
            primary_triple_id=producer.triple_id,
            related_triple_ids=[consumer.triple_id],
            bpmn_node_id=producer.bpmn_node_id,
            bpmn_edge_id=edge_id,
            detector_context={
                "obligation_id": ob.obligation_id,
                "obligation_description": ob.description,
                "direct_successor": consumer.triple_id,
            },
            evidence=Evidence(
                observed=(
                    f"Obligation '{ob.obligation_id}' opened by "
                    f"{producer.triple_id} not closed by direct successor "
                    f"{consumer.triple_id}"
                ),
                expected="A downstream triple must close this obligation",
            ),
        )
        detections.append(det)
    return detections


# ---------------------------------------------------------------------------
# C5 — Naming drift
# ---------------------------------------------------------------------------
def _normalize_path(p: str) -> str:
    """Remove '.' and '_' and lowercase for near-match comparison."""
    return p.replace(".", "").replace("_", "").lower()


def c5_naming_drift(
    producer: Triple,
    consumer: Triple,
    edge_id: Optional[str],
    evaluator=None,
    symbolic=None,
) -> list[RawDetection]:
    """Consumer reads a path that no producer writes, but there exists a
    producer-written path whose normalized form equals the consumer-read
    path's normalized form. → handoff_naming_drift (low confidence).
    """
    detections: list[RawDetection] = []
    writes = _post_fields(producer)
    writes_norm = {_normalize_path(p): p for p in writes}

    consumer_paths: set[str] = set()
    if consumer.pim is not None:
        for pre in consumer.pim.preconditions or []:
            consumer_paths.add(pre.path)
        for rd in consumer.pim.state_reads or []:
            consumer_paths.add(rd.path)

    for read_path in consumer_paths:
        if read_path in writes:
            continue
        norm = _normalize_path(read_path)
        if norm and norm in writes_norm and writes_norm[norm] != read_path:
            writer_path = writes_norm[norm]
            detections.append(
                RawDetection(
                    signal_type="handoff_naming_drift",
                    generator=Generator.STATIC_HANDOFF,
                    primary_triple_id=consumer.triple_id,
                    related_triple_ids=[producer.triple_id],
                    bpmn_node_id=consumer.bpmn_node_id,
                    bpmn_edge_id=edge_id,
                    detector_context={
                        "path_a": writer_path,
                        "path_b": read_path,
                        "writer_a": producer.triple_id,
                        "reader_b": consumer.triple_id,
                        "similarity_score": 1.0,
                    },
                    evidence=Evidence(
                        observed=f"Consumer reads '{read_path}'",
                        expected=(
                            f"Producer writes '{writer_path}' "
                            "(same normalized form)"
                        ),
                    ),
                )
            )
    return detections


# ---------------------------------------------------------------------------
# C6 — Implicit setup
# ---------------------------------------------------------------------------
def c6_implicit_setup(
    producer: Triple,
    consumer: Triple,
    edge_id: Optional[str],
    evaluator=None,
    symbolic=None,
    upstream_writes: Optional[dict[str, StateFieldRef]] = None,
) -> list[RawDetection]:
    """Consumer precondition path not written by any producer in the set,
    but consumer's PSM prompt_scaffold or content chunks reference the path
    (substring match) → handoff_implicit_setup (medium confidence).
    """
    detections: list[RawDetection] = []
    all_writes: dict[str, StateFieldRef] = dict(upstream_writes or {})
    all_writes.update(_post_fields(producer))

    psm_text = _collect_psm_text(consumer)
    if not psm_text:
        return detections

    psm_text_lower = psm_text.lower()

    expected_paths: set[str] = set()
    if consumer.pim is not None:
        for pre in consumer.pim.preconditions or []:
            expected_paths.add(pre.path)
        for rd in consumer.pim.state_reads or []:
            expected_paths.add(rd.path)

    for path in expected_paths:
        if path in all_writes:
            continue
        # Match on the last segment or the whole path.
        last = path.split(".")[-1]
        if (
            path.lower() in psm_text_lower
            or last.lower() in psm_text_lower
        ):
            detections.append(
                RawDetection(
                    signal_type="handoff_implicit_setup",
                    generator=Generator.STATIC_HANDOFF,
                    primary_triple_id=consumer.triple_id,
                    related_triple_ids=[producer.triple_id],
                    bpmn_node_id=consumer.bpmn_node_id,
                    bpmn_edge_id=edge_id,
                    detector_context={
                        "path": path,
                        "confidence_hint": "medium",
                        "evidence_source": "psm_text_reference",
                    },
                    evidence=Evidence(
                        observed=(
                            f"PSM references '{path}' but no producer "
                            f"declares it as output"
                        ),
                        expected=(
                            f"Some triple should declare '{path}' as "
                            "postcondition or state_write"
                        ),
                    ),
                )
            )
    return detections


def _collect_psm_text(t: Triple) -> str:
    if t.psm is None:
        return ""
    parts: list[str] = []
    if t.psm.prompt_scaffold:
        parts.append(t.psm.prompt_scaffold)
    for chunk in t.psm.enriched_content or []:
        if chunk.text:
            parts.append(chunk.text)
    return "\n".join(parts)
