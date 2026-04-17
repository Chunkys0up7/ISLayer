"""MDA-format triple adapter.

Reads the MDA project layout — one directory per triple, containing:
  {slug}.cap.md         — capsule (YAML frontmatter + markdown body)
  {slug}.intent.md      — intent (YAML frontmatter + body)
  {slug}.contract.md    — integration contract (YAML frontmatter + body)
  {slug}.jobaid.yaml    — optional decision table
  triple.manifest.json  — optional manifest

Maps these into the target Triple schema (files/triple-schema.md).

Spec reference: files/01-triple-loader.md §B2-B4.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

import yaml

from triple_flow_sim.contracts.triple import (
    AssertionPredicate,
    BpmnNodeType,
    BranchPredicate,
    BusinessRule,
    CIMLayer,
    ContentChunk,
    ContentType,
    ContextAssertion,
    ObligationType,
    PIMLayer,
    PSMLayer,
    RegulatoryRef,
    StateFieldRef,
    ToolRef,
    Triple,
)

BPMN_NS = "http://www.omg.org/spec/BPMN/20100524/MODEL"

_BPMN_TYPE_MAP: dict[str, BpmnNodeType] = {
    "servicetask": BpmnNodeType.TASK,
    "usertask": BpmnNodeType.TASK,
    "businessruletask": BpmnNodeType.TASK,
    "sendtask": BpmnNodeType.TASK,
    "receivetask": BpmnNodeType.TASK,
    "task": BpmnNodeType.TASK,
    "manualtask": BpmnNodeType.TASK,
    "scripttask": BpmnNodeType.TASK,
    "exclusivegateway": BpmnNodeType.EXCLUSIVE_GATEWAY,
    "inclusivegateway": BpmnNodeType.EXCLUSIVE_GATEWAY,
    "eventbasedgateway": BpmnNodeType.EXCLUSIVE_GATEWAY,
    "parallelgateway": BpmnNodeType.PARALLEL_GATEWAY,
    "startevent": BpmnNodeType.START_EVENT,
    "endevent": BpmnNodeType.END_EVENT,
    "boundaryevent": BpmnNodeType.INTERMEDIATE_EVENT,
    "intermediatethrowevent": BpmnNodeType.INTERMEDIATE_EVENT,
    "intermediatecatchevent": BpmnNodeType.INTERMEDIATE_EVENT,
}


def normalize_bpmn_type(mda_type: str) -> BpmnNodeType:
    """Map an MDA bpmn_task_type string to the BpmnNodeType enum.

    Unknown values fall back to TASK (the schema default).
    """
    if not mda_type:
        return BpmnNodeType.TASK
    key = str(mda_type).strip().lower()
    return _BPMN_TYPE_MAP.get(key, BpmnNodeType.TASK)


# -----------------------------------------------------------------------------
# Frontmatter parsing
# -----------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(
    r"\A---\s*\n(.*?)\n---\s*\n?(.*)",
    re.DOTALL,
)


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body_text).

    If no frontmatter block is present, returns ({}, text).
    """
    if not text:
        return {}, ""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm_raw, body = m.group(1), m.group(2)
    try:
        fm = yaml.safe_load(fm_raw) or {}
    except yaml.YAMLError:
        fm = {}
    if not isinstance(fm, dict):
        fm = {}
    return fm, body or ""


def _split_markdown_sections(body: str) -> list[tuple[str, str]]:
    """Split markdown body by H2 headings.

    Returns a list of (section_title, section_body) tuples. Content before
    the first H2 is discarded (headings below H2 stay inside their section).
    """
    sections: list[tuple[str, str]] = []
    current_title: Optional[str] = None
    current_lines: list[str] = []

    for line in body.splitlines():
        if line.startswith("## "):
            if current_title is not None:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = line[3:].strip()
            current_lines = []
        else:
            if current_title is not None:
                current_lines.append(line)

    if current_title is not None:
        sections.append((current_title, "\n".join(current_lines).strip()))

    return sections


def _slugify(text: str) -> str:
    """Lowercase, replace non-alnum with '-'."""
    s = re.sub(r"[^A-Za-z0-9]+", "-", text.strip().lower())
    return s.strip("-")


def _extract_business_rules(body: str, triple_id: str) -> list[BusinessRule]:
    """Pull bullet lines from a '## Business Rules' section."""
    rules: list[BusinessRule] = []
    for title, content in _split_markdown_sections(body):
        if title.strip().lower() != "business rules":
            continue
        idx = 0
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("- ") or stripped.startswith("* "):
                idx += 1
                rule_text = stripped[2:].strip()
                rules.append(
                    BusinessRule(
                        rule_id=f"{triple_id}:BR:{idx:02d}",
                        rule_text=rule_text,
                    )
                )
    return rules


# -----------------------------------------------------------------------------
# Discovery
# -----------------------------------------------------------------------------

def discover_triple_dirs(root: Path, ignore_paths: list[str]) -> list[Path]:
    """Walk root. Return list of directories containing at least one .cap.md file.

    For the MDA examples structure, looks under:
      {root}/triples/{slug}/
      {root}/decisions/{slug}/
    and also falls back to a recursive scan if those aren't at the root.
    """
    ignore_paths = ignore_paths or []
    results: set[Path] = set()

    def _is_ignored(p: Path) -> bool:
        as_str = str(p)
        return any(ig in as_str for ig in ignore_paths)

    # Conventional MDA layout
    for subdir_name in ("triples", "decisions"):
        sub = root / subdir_name
        if sub.is_dir():
            for child in sub.iterdir():
                if child.is_dir() and not _is_ignored(child):
                    if any(child.glob("*.cap.md")):
                        results.add(child.resolve())

    # Fallback: any directory anywhere containing a *.cap.md
    if not results:
        for cap in root.rglob("*.cap.md"):
            parent = cap.parent
            if not _is_ignored(parent):
                results.add(parent.resolve())

    return sorted(results)


# -----------------------------------------------------------------------------
# BPMN gateway predicate extraction
# -----------------------------------------------------------------------------

_BPMN_EXPR_WRAPPER_RE = re.compile(r"^\s*\$\{(.+)\}\s*$", re.DOTALL)


def _extract_gateway_predicates(
    bpmn_xml: str,
    gateway_node_id: str,
) -> list[BranchPredicate]:
    """Parse BPMN XML and return BranchPredicate entries for one gateway.

    Scans <bpmn:sequenceFlow> elements with sourceRef == gateway_node_id and
    extracts the text inside <bpmn:conditionExpression>. Strips the ${...}
    wrapper if present.
    """
    predicates: list[BranchPredicate] = []
    if not bpmn_xml or not gateway_node_id:
        return predicates

    try:
        root = ET.fromstring(bpmn_xml)
    except ET.ParseError:
        return predicates

    ns = {"bpmn": BPMN_NS}
    default_flow_id: Optional[str] = None

    # Find the gateway element (to check its default attribute).
    for gw_tag in ("exclusiveGateway", "inclusiveGateway", "eventBasedGateway"):
        for gw_elem in root.iter(f"{{{BPMN_NS}}}{gw_tag}"):
            if gw_elem.attrib.get("id") == gateway_node_id:
                default_flow_id = gw_elem.attrib.get("default")
                break
        if default_flow_id is not None:
            break

    for flow in root.iter(f"{{{BPMN_NS}}}sequenceFlow"):
        if flow.attrib.get("sourceRef") != gateway_node_id:
            continue
        flow_id = flow.attrib.get("id", "")
        cond_elem = flow.find("bpmn:conditionExpression", ns)
        if cond_elem is None or cond_elem.text is None:
            if flow_id == default_flow_id:
                predicates.append(
                    BranchPredicate(
                        edge_id=flow_id,
                        predicate_expression="default",
                        is_default=True,
                    )
                )
            continue
        raw = cond_elem.text.strip()
        m = _BPMN_EXPR_WRAPPER_RE.match(raw)
        if m:
            expr = m.group(1).strip()
        else:
            expr = raw
        predicates.append(
            BranchPredicate(
                edge_id=flow_id,
                predicate_expression=expr,
                is_default=(flow_id == default_flow_id),
            )
        )
    return predicates


# -----------------------------------------------------------------------------
# Main loader
# -----------------------------------------------------------------------------

def _find_triple_file(triple_dir: Path, suffix: str) -> Optional[Path]:
    """Find {triple_dir}/*.{suffix}. Returns None if not found."""
    candidates = sorted(triple_dir.glob(f"*{suffix}"))
    return candidates[0] if candidates else None


def load_mda_triple(
    triple_dir: Path,
    bpmn_content: Optional[str] = None,
) -> tuple[Optional[Triple], Optional[dict]]:
    """Read an MDA triple directory and map into the target Triple schema."""
    triple_dir = Path(triple_dir)
    try:
        cap_file = _find_triple_file(triple_dir, ".cap.md")
        intent_file = _find_triple_file(triple_dir, ".intent.md")
        contract_file = _find_triple_file(triple_dir, ".contract.md")
        jobaid_file = _find_triple_file(triple_dir, ".jobaid.yaml")

        if cap_file is None:
            return None, {
                "path": str(triple_dir),
                "error_message": "no *.cap.md file found",
            }

        cap_text = cap_file.read_text(encoding="utf-8")
        cap_fm, cap_body = _parse_frontmatter(cap_text)

        intent_fm: dict = {}
        if intent_file is not None:
            intent_text = intent_file.read_text(encoding="utf-8")
            intent_fm, _ = _parse_frontmatter(intent_text)

        contract_fm: dict = {}
        if contract_file is not None:
            contract_text = contract_file.read_text(encoding="utf-8")
            contract_fm, _ = _parse_frontmatter(contract_text)

        jobaid: Optional[dict] = None
        if jobaid_file is not None:
            try:
                loaded = yaml.safe_load(jobaid_file.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    jobaid = loaded
            except yaml.YAMLError:
                jobaid = None

        # ---- Identity ----
        triple_id = str(cap_fm.get("capsule_id", "") or "").strip()
        version = str(cap_fm.get("version", "0") or "0")
        bpmn_node_id = str(cap_fm.get("bpmn_task_id", "") or "")
        bpmn_node_type = normalize_bpmn_type(cap_fm.get("bpmn_task_type", "task"))

        # ---- CIM ----
        reg_refs_raw = cap_fm.get("regulation_refs") or []
        regulatory_refs = [
            RegulatoryRef(
                citation=str(r),
                rule_text="",
                obligation_type=ObligationType.REFERENCES,
            )
            for r in reg_refs_raw
            if isinstance(r, str)
        ]
        business_rules = _extract_business_rules(cap_body, triple_id or "UNKNOWN")
        intent_goal = str(intent_fm.get("goal", "") or "").strip()
        cim = CIMLayer(
            intent=intent_goal,
            regulatory_refs=regulatory_refs,
            business_rules=business_rules,
        )

        # ---- PIM ----
        preconditions: Optional[list[ContextAssertion]]
        if "preconditions" in intent_fm:
            pre_raw = intent_fm.get("preconditions") or []
            preconditions = [
                ContextAssertion(
                    path=_slugify(str(s)) or "precondition",
                    predicate=AssertionPredicate.EXISTS,
                )
                for s in pre_raw
                if isinstance(s, str)
            ]
        else:
            preconditions = None

        state_reads: Optional[list[StateFieldRef]]
        if "inputs" in intent_fm:
            ins_raw = intent_fm.get("inputs") or []
            state_reads = []
            for item in ins_raw:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("name", "") or "")
                if not name:
                    continue
                state_reads.append(
                    StateFieldRef(
                        path=name,
                        type=str(item.get("type", "any") or "any"),
                        namespace=item.get("source"),
                    )
                )
        else:
            state_reads = None

        state_writes: Optional[list[StateFieldRef]]
        if "outputs" in intent_fm:
            outs_raw = intent_fm.get("outputs") or []
            state_writes = []
            for item in outs_raw:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("name", "") or "")
                if not name:
                    continue
                state_writes.append(
                    StateFieldRef(
                        path=name,
                        type=str(item.get("type", "any") or "any"),
                        namespace=item.get("sink"),
                    )
                )
        else:
            state_writes = None

        # Decision predicates (gateways only, from BPMN XML).
        decision_predicates: Optional[list[BranchPredicate]] = None
        if bpmn_node_type in (
            BpmnNodeType.EXCLUSIVE_GATEWAY,
            BpmnNodeType.PARALLEL_GATEWAY,
        ):
            if bpmn_content and bpmn_node_id:
                preds = _extract_gateway_predicates(bpmn_content, bpmn_node_id)
                if preds:
                    decision_predicates = preds

        pim = PIMLayer(
            preconditions=preconditions,
            postconditions=None,  # MDA format has no explicit postconditions.
            obligations_opened=None,
            obligations_closed=None,
            decision_predicates=decision_predicates,
            state_reads=state_reads,
            state_writes=state_writes,
        )

        # ---- PSM ----
        # Split capsule body into ContentChunks by H2 section.
        enriched_content: list[ContentChunk] = []
        try:
            rel_src = str(cap_file.resolve())
        except OSError:
            rel_src = str(cap_file)

        for title, content in _split_markdown_sections(cap_body):
            if not content:
                continue
            section_slug = _slugify(title) or "section"
            chunk_id = f"{triple_id or 'UNKNOWN'}:{section_slug}"
            content_type = (
                ContentType.REGULATORY
                if title.strip().lower() == "regulatory context"
                else ContentType.KNOWLEDGE
            )
            enriched_content.append(
                ContentChunk(
                    chunk_id=chunk_id,
                    source_document=rel_src,
                    content_type=content_type,
                    text=content,
                )
            )

        hints = intent_fm.get("execution_hints") or {}
        preferred_agent: Optional[str] = None
        if isinstance(hints, dict):
            pa = hints.get("preferred_agent")
            preferred_agent = str(pa) if pa else None

        tool_bindings: list[ToolRef] = []
        sources_raw = contract_fm.get("sources") or []
        if isinstance(sources_raw, list):
            for item in sources_raw:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("name", "") or "")
                if not name:
                    continue
                tool_bindings.append(
                    ToolRef(
                        tool_id=name,
                        purpose=str(item.get("protocol", "") or ""),
                        mock_response_template=item.get("endpoint"),
                    )
                )

        psm = PSMLayer(
            enriched_content=enriched_content,
            prompt_scaffold=preferred_agent,
            tool_bindings=tool_bindings,
        )

        triple = Triple(
            triple_id=triple_id or triple_dir.name,
            version=version,
            bpmn_node_id=bpmn_node_id,
            bpmn_node_type=bpmn_node_type,
            cim=cim,
            pim=pim,
            psm=psm,
            source_path=str(triple_dir.resolve()),
            raw={
                "capsule_fm": cap_fm,
                "intent_fm": intent_fm,
                "contract_fm": contract_fm,
                "jobaid": jobaid,
            },
        )
        return triple, None

    except Exception as exc:  # noqa: BLE001 — catchall returns as error dict
        return None, {
            "path": str(triple_dir),
            "error_message": f"{type(exc).__name__}: {exc}",
        }
