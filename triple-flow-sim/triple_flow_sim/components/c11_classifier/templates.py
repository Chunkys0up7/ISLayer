"""Jinja2 templating for summary/detail rendering in findings.

Supports both Jinja2 double-brace syntax `{{ field }}` and the shorter
`{field}` syntax used in rules.yaml. When no `{{` is present in the template,
single-brace `{name}` tokens are normalized to `{{ name }}` before rendering.
"""
from __future__ import annotations

import re

from jinja2 import Template


_SINGLE_BRACE_PATTERN = re.compile(r"\{(\w+)\}")


def render(template_str: str, context: dict) -> str:
    """Render a summary/detail template with Jinja2.

    Uses double-brace {{ }} syntax; rules.yaml uses {field}. Support both:
    treat {x} as {{ x }} if no {{ already present in the template.
    """
    if template_str is None:
        return ""
    if "{{" not in template_str and "{" in template_str:
        normalized = _SINGLE_BRACE_PATTERN.sub(r"{{ \1 }}", template_str)
    else:
        normalized = template_str
    return Template(normalized).render(**context)
