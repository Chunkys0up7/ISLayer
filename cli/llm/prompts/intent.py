"""Stage 4: Intent specification generation prompts — grounded extraction.

The LLM extracts preconditions, invariants, and failure modes from corpus
content rather than inventing them. Every field must trace to a source.
"""

INTENT_SYSTEM = """You are an intent specification architect for the MDA Intent Layer.
You produce intent specifications — machine-readable outcome contracts that define
what an AI agent must achieve for a specific business task.

CRITICAL RULES:
1. Intent specs describe OUTCOMES, not procedures. They say WHAT must be achieved, not HOW.
2. The capsule handles the HOW; the intent spec handles the WHAT.
3. Every precondition, invariant, and failure mode MUST be traceable to the capsule content
   or BPMN structure provided. Cite (CORPUS-ID) where applicable.
4. Do NOT invent preconditions, invariants, or rules not present in the source material.
5. If information is missing, write "DERIVED FROM BPMN STRUCTURE" for BPMN-sourced items.

ANTI-UI PRINCIPLE: Intent specs must NEVER be satisfied through browser automation,
screen scraping, or UI clicks. forbidden_actions MUST always include:
- browser_automation
- screen_scraping
- ui_click
- rpa_style_macros"""


def build_intent_frontmatter_prompt(
    node_context: dict, capsule_content: str, enrichment: dict
) -> str:
    """Build prompt for generating intent spec frontmatter fields."""
    prompt = f"""Generate the frontmatter fields for an intent specification.

## BPMN Task
- Name: {node_context['name']}
- Type: {node_context['element_type']}
- Goal Type: {node_context.get('default_goal_type', 'data_production')}

## Capsule Content (source material — extract from this)
{capsule_content[:4000]}

## Generate These Fields

Extract from the capsule content above. Cite (CORPUS-ID) in string values where the
information originates from a corpus document cited in the capsule.

1. **goal**: A single sentence describing the required outcome (not the procedure)
2. **preconditions**: Array of observable state conditions that must be true before execution.
   Extract these from the capsule's Prerequisites/Inputs sections.
3. **inputs**: Array of {{name, source, schema_ref, required}} objects.
   Extract from capsule Inputs Required table.
4. **outputs**: Array of {{name, type, sink, invariants[]}} objects.
   Extract from capsule Outputs Produced table.
5. **invariants**: Array of conditions that must hold at completion.
   Extract from capsule Business Rules section.
6. **success_criteria**: Array of conditions confirming successful execution.
   Derive from capsule Procedure completion + outputs.
7. **failure_modes**: Array of {{mode, detection, action}} objects.
   Extract from capsule Exception Handling section.
8. **execution_hints**: Object with preferred_agent, tool_access[], forbidden_actions[]

IMPORTANT: forbidden_actions MUST include: browser_automation, screen_scraping, ui_click, rpa_style_macros

Return using the structured_output tool."""
    return prompt


def build_intent_body_prompt(node_context: dict, frontmatter: dict,
                              capsule_content: str = "") -> str:
    """Build prompt for generating intent spec markdown body."""
    import json

    prompt = f"""Generate the markdown body for an intent specification.

## Task: {node_context['name']}
## Goal: {frontmatter.get('goal', 'unspecified')}
## Goal Type: {frontmatter.get('goal_type', 'unspecified')}

## Capsule Content (for reference — extract, don't invent)
{capsule_content[:3000]}

## Frontmatter (already generated)
{json.dumps(frontmatter, indent=2, default=str)[:2000]}

## Required Sections

For each section, cite (CORPUS-ID) where the information originates from the capsule's
cited sources. If derived from BPMN structure, note "DERIVED FROM BPMN STRUCTURE".

1. **Outcome Statement** — What must be achieved (2-3 sentences). Cite source.
2. **Outcome Contract** — When is this intent satisfied? Reference the invariants.
3. **Reasoning Guidance** — Numbered steps for an agent executing this intent.
   Extract from capsule procedure, reframed as WHAT-to-achieve steps, not HOW-to-do steps.
4. **Anti-Patterns** — What the agent must NEVER do. Always include:
   - Never use browser automation
   - Never scrape screens
   - Never click UI elements
   - Never use RPA-style macros
5. **Paired Capsule** — Reference to the capsule ID
6. **Paired Integration Contract** — Reference to the contract ID
"""
    return prompt


INTENT_FRONTMATTER_SCHEMA = {
    "type": "object",
    "properties": {
        "goal": {"type": "string"},
        "preconditions": {"type": "array", "items": {"type": "string"}},
        "inputs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "source": {"type": "string"},
                    "schema_ref": {"type": "string"},
                    "required": {"type": "boolean"},
                },
                "required": ["name", "source"],
            },
        },
        "outputs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "sink": {"type": "string"},
                    "invariants": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["name", "type", "sink"],
            },
        },
        "invariants": {"type": "array", "items": {"type": "string"}},
        "success_criteria": {"type": "array", "items": {"type": "string"}},
        "failure_modes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string"},
                    "detection": {"type": "string"},
                    "action": {"type": "string"},
                },
                "required": ["mode", "detection", "action"],
            },
        },
        "execution_hints": {
            "type": "object",
            "properties": {
                "preferred_agent": {"type": "string"},
                "tool_access": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "forbidden_actions": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
        },
    },
    "required": [
        "goal",
        "inputs",
        "outputs",
        "invariants",
        "success_criteria",
        "failure_modes",
        "execution_hints",
    ],
}
