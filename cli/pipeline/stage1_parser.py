"""Stage 1: BPMN Parser — Parse BPMN 2.0 XML into a typed ParsedModel."""

from pathlib import Path
from typing import Optional
import sys
import os
import importlib.util

_CLI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _CLI_DIR)


def _load_local(module_name: str, file_path: str):
    """Load a module from the cli/ tree, bypassing stdlib 'io' shadowing."""
    spec = importlib.util.spec_from_file_location(module_name, os.path.join(_CLI_DIR, file_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_bpmn_xml = _load_local("mda_io.bpmn_xml", "mda_io/bpmn_xml.py")
_yaml_io = _load_local("mda_io.yaml_io", "mda_io/yaml_io.py")

parse_bpmn = _bpmn_xml.parse_bpmn
read_yaml = _yaml_io.read_yaml

from models.bpmn import ParsedModel


def run_parser(bpmn_path: Path, ontology_dir: Optional[Path] = None) -> ParsedModel:
    """Execute Stage 1: Parse BPMN XML into a ParsedModel.

    Args:
        bpmn_path: Path to BPMN 2.0 XML file
        ontology_dir: Path to ontology/ directory (for bpmn-element-mapping.yaml)

    Returns:
        ParsedModel with all extracted elements

    Raises:
        FileNotFoundError: If bpmn_path doesn't exist
        ValueError: If the file is not valid BPMN 2.0
    """
    if not bpmn_path.exists():
        raise FileNotFoundError(f"BPMN file not found: {bpmn_path}")

    # Parse the BPMN XML
    model = parse_bpmn(bpmn_path)

    # Load element mapping ontology if available
    if ontology_dir:
        mapping_path = ontology_dir / "bpmn-element-mapping.yaml"
        if mapping_path.exists():
            mapping = read_yaml(mapping_path)
            _annotate_with_mapping(model, mapping)

    # Run validation checks
    warnings = _validate_parsed_model(model)

    return model


def _annotate_with_mapping(model: ParsedModel, mapping: dict) -> None:
    """Cross-reference nodes against the BPMN element mapping ontology.

    Sets attributes on each node:
    - triple_type: standard, decision, coordination, process_boundary, reference, container, exception, none
    - default_goal_type: from the mapping
    - generates_capsule, generates_intent, generates_contract: booleans
    """
    if not mapping or "mappings" not in mapping:
        return

    # Build a lookup from element_type to mapping entry
    mapping_lookup = {}
    for entry in mapping["mappings"]:
        bpmn_elem = entry.get("bpmn_element", "")
        mapping_lookup[bpmn_elem] = entry

    for node in model.nodes:
        entry = mapping_lookup.get(node.element_type, {})
        node.attributes["triple_type"] = entry.get("triple_type", "standard")
        node.attributes["default_goal_type"] = entry.get("default_goal_type")
        node.attributes["generates_capsule"] = entry.get("generates_capsule", True)
        node.attributes["generates_intent"] = entry.get("generates_intent", True)
        node.attributes["generates_contract"] = entry.get("generates_contract", True)


def _validate_parsed_model(model: ParsedModel) -> list[str]:
    """Run validation checks on the parsed model. Returns warnings."""
    warnings = []

    node_ids = {n.id for n in model.nodes}

    # Check for dangling edge references
    for edge in model.edges:
        if edge.source_id not in node_ids:
            warnings.append(f"Edge {edge.id} references unknown source node: {edge.source_id}")
        if edge.target_id not in node_ids:
            warnings.append(f"Edge {edge.id} references unknown target node: {edge.target_id}")

    # Check for nodes without names
    for node in model.nodes:
        if not node.name:
            warnings.append(f"Node {node.id} ({node.element_type}) has no name")

    # Check for duplicate IDs
    seen = set()
    for node in model.nodes:
        if node.id in seen:
            warnings.append(f"Duplicate node ID: {node.id}")
        seen.add(node.id)

    return warnings


def get_parse_summary(model: ParsedModel) -> dict:
    """Generate a summary of the parsed model for display."""
    from collections import Counter

    type_counts = Counter(n.element_type for n in model.nodes)

    return {
        "source_file": model.source_file,
        "processes": len(model.processes),
        "total_nodes": len(model.nodes),
        "node_types": dict(type_counts),
        "edges": len(model.edges),
        "lanes": len(model.lanes),
        "data_objects": len(model.data_objects),
        "message_flows": len(model.message_flows),
    }
