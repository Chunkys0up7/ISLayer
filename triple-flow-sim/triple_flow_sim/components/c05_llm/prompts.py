"""Prompt templates for grounded execution and context isolation.

Spec references:
- files/05-grounded-handoff-runner.md §Prompt scaffolding
- files/07-context-isolation-harness.md §Level 1/2/3 prompts

Templates are rendered via Jinja2. Each template is addressed by a stable
``template_id`` so Phase 3 findings can record ``prompt_template_version``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jinja2 import Environment, StrictUndefined

TEMPLATE_VERSION = "1.0.0"


@dataclass
class RenderedPrompt:
    template_id: str
    system: str
    prompt: str
    inputs: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
_SYSTEM_COMMON = (
    "You are simulating the execution of a business process step. "
    "Respond with valid JSON matching the expected output schema. "
    "Be concise. Do NOT invent facts not present in the provided content."
)

_LEVEL1_FULL_CONTENT = """\
Triple: {{ triple_id }}
BPMN node: {{ bpmn_node_id }} ({{ bpmn_node_type }})

Goal: {{ intent }}

Available content:
{% for chunk in content_chunks %}
[{{ chunk.chunk_id }}] {{ chunk.text }}
{% endfor %}

Declared inputs (state reads):
{% for ref in state_reads %}- {{ ref.path }} ({{ ref.type }})
{% endfor %}

Declared outputs (state writes):
{% for ref in state_writes %}- {{ ref.path }} ({{ ref.type }})
{% endfor %}

Current state:
{{ state_json }}

Produce the output state JSON.
"""

_LEVEL2_DECLARED_ONLY = """\
Triple: {{ triple_id }}
BPMN node: {{ bpmn_node_id }} ({{ bpmn_node_type }})

Goal: {{ intent }}

Declared inputs (state reads):
{% for ref in state_reads %}- {{ ref.path }} ({{ ref.type }})
{% endfor %}

Declared outputs (state writes):
{% for ref in state_writes %}- {{ ref.path }} ({{ ref.type }})
{% endfor %}

Current state (declared fields only):
{{ state_json }}

Produce the output state JSON using ONLY the declared inputs above.
"""

_LEVEL3_MINIMUM = """\
Triple: {{ triple_id }}

Goal: {{ intent }}

Produce a valid output for this step. You have no content and no external
state beyond what is listed here:
{{ minimal_state_json }}
"""

_GROUNDED_TASK = _LEVEL1_FULL_CONTENT  # alias for the grounded runner

_GROUNDED_GATEWAY = """\
Triple: {{ triple_id }} (exclusive gateway)

Goal: {{ intent }}

Predicates:
{% for p in predicates %}  - edge {{ p.edge_id }}: {{ p.expression }}
{% endfor %}

Available content:
{% for chunk in content_chunks %}
[{{ chunk.chunk_id }}] {{ chunk.text }}
{% endfor %}

Current state:
{{ state_json }}

Choose exactly one edge. Respond with JSON: {"edge_id": "<id>", "evidence": ["<chunk_id>", ...]}.
"""


_REGISTRY: dict[str, str] = {
    "level1_full_content": _LEVEL1_FULL_CONTENT,
    "level2_declared_only": _LEVEL2_DECLARED_ONLY,
    "level3_minimum": _LEVEL3_MINIMUM,
    "grounded_task": _GROUNDED_TASK,
    "grounded_gateway": _GROUNDED_GATEWAY,
}


_env = Environment(undefined=StrictUndefined, autoescape=False)


def render(template_id: str, **kwargs: Any) -> RenderedPrompt:
    """Render one of the registered templates."""
    if template_id not in _REGISTRY:
        raise KeyError(f"Unknown prompt template {template_id!r}")
    body = _env.from_string(_REGISTRY[template_id]).render(**kwargs)
    return RenderedPrompt(
        template_id=template_id,
        system=_SYSTEM_COMMON,
        prompt=body,
        inputs=dict(kwargs),
    )


def list_templates() -> list[str]:
    return sorted(_REGISTRY.keys())
