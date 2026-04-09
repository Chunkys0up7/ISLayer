"""Parse and write YAML frontmatter from Markdown files.

Used for .cap.md, .intent.md, .contract.md, and .corpus.md files.
"""

import yaml
from pathlib import Path
from typing import Optional


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from a markdown string.

    Frontmatter is delimited by --- lines.
    Returns (frontmatter_dict, body_text).
    If no frontmatter found, returns ({}, full_content).
    """
    if not content.startswith("---"):
        return {}, content

    # Find the closing ---
    # Skip the first line (opening ---) and search for the closing delimiter
    lines = content.split("\n")
    end_index = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_index = i
            break

    if end_index is None:
        # No closing delimiter found -- treat entire content as body
        return {}, content

    # Extract the YAML block between the delimiters
    yaml_block = "\n".join(lines[1:end_index])

    # Parse YAML; handle empty frontmatter
    if yaml_block.strip():
        try:
            frontmatter = yaml.safe_load(yaml_block)
        except yaml.YAMLError:
            # If YAML is malformed, return empty dict and full content
            return {}, content
        if frontmatter is None:
            frontmatter = {}
    else:
        frontmatter = {}

    # Body is everything after the closing ---
    # Skip the blank line immediately after --- if present
    body_lines = lines[end_index + 1 :]
    body = "\n".join(body_lines)

    # Strip at most one leading newline from body (conventional blank line after ---)
    if body.startswith("\n"):
        body = body[1:]

    return frontmatter, body


def read_frontmatter_file(path: Path) -> tuple[dict, str]:
    """Read a file and parse its frontmatter."""
    content = path.read_text(encoding="utf-8")
    return parse_frontmatter(content)


def write_frontmatter_file(path: Path, frontmatter: dict, body: str) -> None:
    """Write a file with YAML frontmatter + markdown body.

    Uses yaml.dump with default_flow_style=False for readable output.
    Handles proper --- delimiters.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    parts = ["---\n"]

    if frontmatter:
        yaml_str = yaml.dump(
            frontmatter,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        )
        parts.append(yaml_str)
    else:
        parts.append("")

    # Ensure YAML block ends with a newline before closing ---
    if parts[-1] and not parts[-1].endswith("\n"):
        parts.append("\n")

    parts.append("---\n")

    # Add body with a separating blank line
    if body:
        if not body.startswith("\n"):
            parts.append("\n")
        parts.append(body)
        # Ensure file ends with a newline
        if not body.endswith("\n"):
            parts.append("\n")

    path.write_text("".join(parts), encoding="utf-8")


def update_frontmatter(path: Path, updates: dict) -> None:
    """Read a file, update specific frontmatter fields, write back.

    Preserves existing fields and body content.
    """
    frontmatter, body = read_frontmatter_file(path)
    frontmatter.update(updates)
    write_frontmatter_file(path, frontmatter, body)
