"""LLM-assisted quality review prompts."""

REVIEW_SYSTEM = """You are a quality reviewer for MDA Intent Layer triples.
Review the capsule, intent spec, and integration contract for completeness,
accuracy, consistency, and anti-UI compliance.

Be specific in your findings. Reference exact fields and sections.
Assign severity: critical (must fix), high (should fix), medium (consider fixing), low (minor)."""


def build_review_prompt(
    capsule_content: str,
    intent_content: str,
    contract_content: str,
    aspect: str = "all",
) -> str:
    prompt = f"""Review this triple for quality issues.

## Knowledge Capsule
{capsule_content[:3000]}

## Intent Specification
{intent_content[:3000]}

## Integration Contract
{contract_content[:3000]}

## Review Aspects: {aspect}
"""
    if aspect in ("all", "completeness"):
        prompt += """
### Completeness
- Are all required sections populated?
- Are gaps properly documented?
- Are inputs/outputs fully defined?
"""
    if aspect in ("all", "accuracy"):
        prompt += """
### Accuracy
- Do business rules match standard domain practices?
- Are regulatory references correct?
- Are data types and constraints reasonable?
"""
    if aspect in ("all", "consistency"):
        prompt += """
### Consistency
- Do IDs match across all three files?
- Do inputs/outputs in the intent match the contract sources/sinks?
- Is the capsule procedure aligned with the intent goal?
"""

    prompt += """
Return findings using the structured_output tool."""
    return prompt


REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "overall_rating": {
            "type": "string",
            "enum": [
                "pass",
                "pass_with_warnings",
                "needs_revision",
                "fail",
            ],
        },
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "severity": {
                        "type": "string",
                        "enum": ["critical", "high", "medium", "low"],
                    },
                    "aspect": {
                        "type": "string",
                        "enum": [
                            "completeness",
                            "accuracy",
                            "consistency",
                            "anti_ui",
                        ],
                    },
                    "file": {
                        "type": "string",
                        "enum": ["capsule", "intent", "contract"],
                    },
                    "field_or_section": {"type": "string"},
                    "finding": {"type": "string"},
                    "recommendation": {"type": "string"},
                },
                "required": [
                    "severity",
                    "aspect",
                    "file",
                    "finding",
                    "recommendation",
                ],
            },
        },
        "summary": {"type": "string"},
    },
    "required": ["overall_rating", "findings", "summary"],
}
