"""Stage 2: Enrichment prompts for corpus disambiguation."""

DISAMBIGUATION_SYSTEM = """You are a knowledge corpus matching specialist for the MDA Intent Layer.
Your job is to judge whether a corpus document is relevant to a specific BPMN task.
Be precise. A document is relevant only if it directly provides procedural knowledge,
business rules, or regulatory context that would populate a knowledge capsule for this task."""


def build_disambiguation_prompt(
    node_context: dict, candidates: list[dict]
) -> str:
    """Build a prompt for disambiguating corpus matches.

    Args:
        node_context: {id, name, element_type, lane_name, process_name, domain}
        candidates: [{corpus_id, title, doc_type, tags, snippet}]

    Returns the prompt string.
    """
    prompt = f"""Evaluate the relevance of these corpus documents to a BPMN task.

## BPMN Task
- ID: {node_context['id']}
- Name: {node_context['name']}
- Type: {node_context['element_type']}
- Lane: {node_context.get('lane_name', 'unassigned')}
- Process: {node_context.get('process_name', 'unknown')}
- Domain: {node_context.get('domain', 'unknown')}

## Candidate Documents
"""
    for i, c in enumerate(candidates, 1):
        prompt += f"""
### Candidate {i}: {c['corpus_id']}
- Title: {c['title']}
- Type: {c['doc_type']}
- Tags: {', '.join(c.get('tags', []))}
- Snippet: {c.get('snippet', 'N/A')}
"""

    prompt += """
For each candidate, assess:
1. Is it relevant to this BPMN task? (true/false)
2. Confidence: high, medium, or low
3. Brief reason (one sentence)

Return your assessment using the structured_output tool."""

    return prompt


DISAMBIGUATION_SCHEMA = {
    "type": "object",
    "properties": {
        "assessments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "corpus_id": {"type": "string"},
                    "relevant": {"type": "boolean"},
                    "confidence": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                    },
                    "reason": {"type": "string"},
                },
                "required": [
                    "corpus_id",
                    "relevant",
                    "confidence",
                    "reason",
                ],
            },
        }
    },
    "required": ["assessments"],
}
