"""Stage 3: Capsule generation prompts."""

CAPSULE_SYSTEM = """You are a knowledge capsule author for the MDA Intent Layer.
You produce knowledge capsules — structured Markdown documents that capture procedural
knowledge, business rules, and domain context for a specific BPMN task.

Capsules are consumed by AI agents as domain knowledge. Be precise, factual, and thorough.
Draw from the provided corpus documents. Cite corpus IDs where appropriate.
Do not fabricate procedures or rules — if information is missing, leave the section empty
and note the gap."""


def build_capsule_body_prompt(
    node_context: dict, corpus_content: list[dict], enrichment: dict
) -> str:
    """Build prompt for generating capsule markdown body.

    Args:
        node_context: BPMN node details (id, name, type, lane, predecessors, successors)
        corpus_content: List of {corpus_id, title, doc_type, body_text} for matched docs
        enrichment: Enrichment data for this node
    """
    prompt = f"""Generate the markdown body for a knowledge capsule.

## BPMN Task Context
- Name: {node_context['name']}
- Type: {node_context['element_type']}
- Lane/Role: {node_context.get('lane_name', 'unassigned')}
- Predecessors: {', '.join(node_context.get('predecessor_names', ['(start)']))}
- Successors: {', '.join(node_context.get('successor_names', ['(end)']))}

## Source Knowledge (from corpus)
"""
    for doc in corpus_content:
        prompt += (
            f"\n### [{doc['corpus_id']}] {doc['title']} ({doc['doc_type']})\n"
            f"{doc['body_text']}\n"
        )

    prompt += """
## Required Sections

Generate these sections. Use the corpus content as source material.
Cite corpus IDs in parentheses where you draw from specific documents.

1. **Purpose** — One paragraph: what this task accomplishes in the process
2. **Procedure** — Numbered steps drawn from the corpus procedure documents
3. **Business Rules** — Bullet list of rules/thresholds/constraints from corpus rule documents
4. **Inputs Required** — Markdown table: Input | Source | Description
5. **Outputs Produced** — Markdown table: Output | Destination | Description
6. **Exception Handling** — Bullet list with bold exception names
7. **Regulatory Context** — From corpus regulation documents, cite specific sections
8. **Notes** — Any additional context, warnings, or tips

If no corpus content exists for a section, write "No source knowledge available — gap flagged."
"""
    return prompt
