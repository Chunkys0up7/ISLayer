"""Stage 3: Capsule generation prompts — extraction-based, zero-hallucination.

The LLM acts as an EDITOR organizing extracted corpus content,
NOT as an author creating new content. Every claim must cite a corpus ID.
"""

CAPSULE_SYSTEM = """You are a knowledge capsule EDITOR for the MDA Intent Layer.
You ORGANIZE and FORMAT pre-extracted corpus content into structured Markdown sections.

ABSOLUTE RULES — violations will cause rejection:
1. Every factual sentence MUST end with a (CORPUS-ID) citation in parentheses.
2. You may ONLY use information from the SOURCE CONTENT provided below.
3. If a section has NO source content, write EXACTLY: "NO SOURCE CONTENT — GAP FLAGGED"
4. Do NOT paraphrase loosely. Preserve the original wording and structure from sources.
5. Do NOT add information, examples, explanations, or inferences not in the sources.
6. Do NOT invent procedures, rules, thresholds, or regulatory references.
7. You are an EDITOR — you organize, you do not create.

When merging content from multiple sources into one section:
- Keep citations inline with each statement
- If sources conflict, include both with their citations and note the conflict
- Order by match confidence (highest first)"""


def build_capsule_body_prompt(
    node_context: dict,
    grounded_content: dict,
    enrichment_summary: dict,
    jobaid_content: str = "",
) -> str:
    """Build prompt for generating capsule markdown body from extracted sections.

    Args:
        node_context: BPMN node details (name, type, lane, predecessors, successors)
        grounded_content: Dict keyed by section name, each a list of
            {corpus_id, doc_title, heading, content, match_confidence} dicts
        enrichment_summary: Summary of enrichment (gaps, match counts)
        jobaid_content: Pre-formatted job aid markdown (deterministic, not LLM-generated)
    """
    prompt = f"""Organize the following pre-extracted corpus content into a knowledge capsule.

## BPMN Task Context
- Name: {node_context['name']}
- Type: {node_context['element_type']}
- Lane/Role: {node_context.get('lane_name', 'unassigned')}
- Predecessors: {', '.join(node_context.get('predecessor_names', ['(start)']))}
- Successors: {', '.join(node_context.get('successor_names', ['(end)']))}

## SOURCE CONTENT (extracted from corpus — this is ALL you may use)
"""

    # Inject procedure content
    prompt += "\n### Procedure Sources\n"
    proc_items = grounded_content.get("procedure", [])
    if proc_items:
        for item in proc_items:
            prompt += f"\n**[{item['corpus_id']}] {item['doc_title']}** — Section: {item['heading']} (confidence: {item['match_confidence']})\n"
            prompt += f"{item['content']}\n"
    else:
        prompt += "NONE — no procedure content matched.\n"

    # Inject business rules content
    prompt += "\n### Business Rules Sources\n"
    rules_items = grounded_content.get("business_rules", [])
    if rules_items:
        for item in rules_items:
            prompt += f"\n**[{item['corpus_id']}] {item['doc_title']}** — Section: {item['heading']} (confidence: {item['match_confidence']})\n"
            prompt += f"{item['content']}\n"
    else:
        prompt += "NONE — no business rules content matched.\n"

    # Inject input/output content
    prompt += "\n### Data / Input / Output Sources\n"
    io_items = grounded_content.get("inputs_outputs", [])
    if io_items:
        for item in io_items:
            prompt += f"\n**[{item['corpus_id']}] {item['doc_title']}** — Section: {item['heading']} (confidence: {item['match_confidence']})\n"
            prompt += f"{item['content']}\n"
    else:
        prompt += "NONE — no data definition content matched.\n"

    # Inject exception handling content
    prompt += "\n### Exception Handling Sources\n"
    exc_items = grounded_content.get("exception_handling", [])
    if exc_items:
        for item in exc_items:
            prompt += f"\n**[{item['corpus_id']}] {item['doc_title']}** — Section: {item['heading']} (confidence: {item['match_confidence']})\n"
            prompt += f"{item['content']}\n"
    else:
        prompt += "NONE — no exception handling content matched.\n"

    # Inject regulatory content
    prompt += "\n### Regulatory / Compliance Sources\n"
    reg_items = grounded_content.get("regulatory_context", [])
    if reg_items:
        for item in reg_items:
            prompt += f"\n**[{item['corpus_id']}] {item['doc_title']}** — Section: {item['heading']} (confidence: {item['match_confidence']})\n"
            prompt += f"{item['content']}\n"
    else:
        prompt += "NONE — no regulatory content matched.\n"

    # Add the required sections
    prompt += """
## ORGANIZE INTO THESE SECTIONS

Use ONLY the source content above. Cite (CORPUS-ID) after every factual statement.

1. **Purpose** — One paragraph: what this task accomplishes in the process. Cite the source.
2. **Procedure** — Numbered steps from the procedure sources. Preserve original step numbering and detail. Cite each step.
3. **Business Rules** — Bullet list of rules/thresholds/constraints. Cite each rule.
4. **Inputs Required** — Markdown table: Input | Source | Description | Citation. Use data sources.
5. **Outputs Produced** — Markdown table: Output | Destination | Description | Citation. Use data sources.
6. **Exception Handling** — Bullet list with bold exception names. Cite sources.
7. **Regulatory Context** — From regulatory sources. Cite specific sections.
8. **Notes** — Corpus IDs used, confidence levels, and any conflicts between sources.

For ANY section with no source content, write EXACTLY:
"NO SOURCE CONTENT — GAP FLAGGED"
"""

    # Append job aid content if present (deterministic, not LLM-generated)
    if jobaid_content:
        prompt += f"\n## JOB AID DATA (include verbatim — do not modify)\n\n{jobaid_content}\n"
        prompt += "\nInclude the job aid data as a '## Decision Parameters' section AFTER the Procedure section. Copy it exactly as provided.\n"

    return prompt
