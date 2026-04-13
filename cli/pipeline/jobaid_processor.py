"""Job Aid Processor — import from Excel, validate, and query."""
import sys, os
from pathlib import Path
from typing import Optional
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib.util
def _load_io(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mda_io", f"{name}.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
yaml_io = _load_io("yaml_io")
schema_val = _load_io("schema_validator")

from models.jobaid import JobAid, Dimension, ActionField, Rule, Precedence


def import_from_excel(
    excel_path: Path,
    capsule_id: str,
    title: Optional[str] = None,
    dimension_columns: Optional[list[str]] = None,
    sheet_name: Optional[str] = None,
) -> JobAid:
    """Import a job aid from an Excel file.

    The Excel file should have:
    - Column headers in row 1
    - Each row is a rule
    - dimension_columns specifies which columns are conditions (rest are actions)
    - If dimension_columns is None, tries to auto-detect based on column names
    """
    try:
        import openpyxl
    except ImportError:
        raise ImportError(
            "openpyxl is required for Excel import.\n"
            "Install it: pip install openpyxl"
        )

    wb = openpyxl.load_workbook(str(excel_path), read_only=True, data_only=True)
    ws = wb[sheet_name] if sheet_name else wb.active

    # Read headers
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        raise ValueError("Excel file is empty")

    headers = [str(h).strip() if h else f"column_{i}" for i, h in enumerate(rows[0])]

    # Auto-detect dimension columns if not specified
    if dimension_columns is None:
        # Heuristic: columns with few unique values are likely dimensions
        col_unique_counts = {}
        for col_idx, header in enumerate(headers):
            values = set()
            for row in rows[1:]:
                if col_idx < len(row) and row[col_idx] is not None:
                    values.add(str(row[col_idx]))
            col_unique_counts[header] = len(values)

        # Columns with < 20 unique values are likely dimensions
        dimension_columns = [h for h, count in col_unique_counts.items() if count < 20 and count > 0]
        if not dimension_columns:
            # Fallback: first 3 columns are dimensions
            dimension_columns = headers[:min(3, len(headers))]

    action_columns = [h for h in headers if h not in dimension_columns]

    # Build dimensions
    dim_values = {dc: set() for dc in dimension_columns}
    for row in rows[1:]:
        for col_idx, header in enumerate(headers):
            if header in dimension_columns and col_idx < len(row) and row[col_idx] is not None:
                dim_values[header].add(str(row[col_idx]))

    dimensions = [
        Dimension(name=dc, values=sorted(dim_values[dc]))
        for dc in dimension_columns
    ]

    # Build action fields
    action_fields = [
        ActionField(name=ac, type="string")
        for ac in action_columns
    ]

    # Build rules
    rules = []
    for row_idx, row in enumerate(rows[1:], start=1):
        if all(v is None for v in row):
            continue  # Skip empty rows

        conditions = {}
        for col_idx, header in enumerate(headers):
            if header in dimension_columns:
                val = str(row[col_idx]).strip() if col_idx < len(row) and row[col_idx] is not None else "*"
                conditions[header] = val

        action = {}
        for col_idx, header in enumerate(headers):
            if header in action_columns:
                val = row[col_idx] if col_idx < len(row) else None
                if val is not None:
                    # Handle comma-separated lists
                    val_str = str(val).strip()
                    if "," in val_str and not val_str.startswith("{"):
                        action[header] = [v.strip() for v in val_str.split(",")]
                    else:
                        action[header] = val_str

        rule_id = f"R{row_idx:03d}"
        rules.append(Rule(id=rule_id, conditions=conditions, action=action))

    wb.close()

    # Generate job aid ID from capsule_id
    stem = capsule_id.replace("CAP-", "")
    jobaid_id = f"JA-{stem}"

    return JobAid(
        jobaid_id=jobaid_id,
        capsule_id=capsule_id,
        title=title or f"Job Aid for {capsule_id}",
        version="1.0",
        description=f"Imported from {excel_path.name}",
        source_file=str(excel_path.name),
        author="mda-cli",
        last_modified=datetime.utcnow().strftime("%Y-%m-%d"),
        last_modified_by="mda-cli",
        dimensions=dimensions,
        action_fields=action_fields,
        rules=rules,
        precedence=Precedence.FIRST_MATCH,
    )


def validate_jobaid(jobaid_path: Path, schemas_dir: Optional[Path] = None) -> list[dict]:
    """Validate a .jobaid.yaml file against the schema and check internal consistency."""
    errors = []

    data = yaml_io.read_yaml(jobaid_path)
    if not data:
        return [{"path": str(jobaid_path), "error": "Empty or invalid YAML"}]

    # Schema validation
    if schemas_dir:
        validator = schema_val.SchemaValidator(schemas_dir)
        schema_errors = validator._validate(data, "jobaid")
        for e in schema_errors:
            errors.append({"path": e.path, "error": e.message})

    # Internal consistency checks
    jobaid = JobAid.from_dict(data)

    # Check: all dimension names used in rules are defined
    defined_dims = {d.name for d in jobaid.dimensions}
    for rule in jobaid.rules:
        for dim_name in rule.conditions:
            if dim_name not in defined_dims:
                errors.append({"path": f"rules/{rule.id}/conditions", "error": f"Dimension '{dim_name}' not defined in dimensions list"})

    # Check: no duplicate rule IDs
    rule_ids = [r.id for r in jobaid.rules]
    dupes = [rid for rid in set(rule_ids) if rule_ids.count(rid) > 1]
    if dupes:
        errors.append({"path": "rules", "error": f"Duplicate rule IDs: {dupes}"})

    # Check: condition values are in the dimension's allowed values (if defined)
    dim_allowed = {d.name: set(d.values) for d in jobaid.dimensions if d.values}
    for rule in jobaid.rules:
        for dim_name, value in rule.conditions.items():
            if dim_name in dim_allowed and value != "*" and value is not None:
                if isinstance(value, list):
                    for v in value:
                        if v not in dim_allowed[dim_name]:
                            errors.append({"path": f"rules/{rule.id}/conditions/{dim_name}", "error": f"Value '{v}' not in dimension '{dim_name}' allowed values"})
                elif value not in dim_allowed[dim_name]:
                    errors.append({"path": f"rules/{rule.id}/conditions/{dim_name}", "error": f"Value '{value}' not in dimension '{dim_name}' allowed values"})

    return errors


def query_jobaid(jobaid_path: Path, conditions: dict[str, str]) -> list[dict]:
    """Query a job aid with specific conditions and return matching rules."""
    data = yaml_io.read_yaml(jobaid_path)
    jobaid = JobAid.from_dict(data)
    matches = jobaid.query(conditions)
    return [r.to_dict() for r in matches]


def list_jobaids(triples_dir: Path, decisions_dir: Optional[Path] = None) -> list[dict]:
    """List all job aid files in the process."""
    results = []
    for base_dir in [triples_dir, decisions_dir]:
        if not base_dir or not base_dir.exists():
            continue
        for f in sorted(base_dir.rglob("*.jobaid.yaml")):
            try:
                data = yaml_io.read_yaml(f)
                results.append({
                    "jobaid_id": data.get("jobaid_id", ""),
                    "capsule_id": data.get("capsule_id", ""),
                    "title": data.get("title", ""),
                    "rules": len(data.get("rules", [])),
                    "dimensions": len(data.get("dimensions", [])),
                    "status": data.get("status", ""),
                    "path": str(f),
                })
            except Exception:
                results.append({"path": str(f), "error": "Failed to parse"})
    return results


def write_jobaid(jobaid: JobAid, output_path: Path) -> None:
    """Write a job aid to a .jobaid.yaml file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    yaml_io.write_yaml(output_path, jobaid.to_dict())
