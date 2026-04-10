---
name: mda-review
description: LLM-assisted quality review of a triple. Checks completeness, accuracy, consistency, and anti-UI compliance. Use before approving a triple.
argument-hint: [triple-path]
allowed-tools: Bash(python *)
---

# MDA Review -- LLM-Assisted Triple Quality Review

This command performs an LLM-assisted quality review of a triple artifact, checking completeness, accuracy, internal consistency, and anti-UI compliance (ensuring the triple describes agent behavior, not UI interactions).

## Context

Current working directory: !`pwd`
Triple files: !`find . -path "*/triples/*" -name "*.yaml" 2>/dev/null | head -10 || echo "None found"`

## Steps

1. Run the review on the specified triple at `$ARGUMENTS`:

```
python cli/mda.py review $ARGUMENTS
```

2. Present the review results organized by dimension:
   - **Completeness**: Are all required fields populated? Are procedures fully specified?
   - **Accuracy**: Do the steps match the bound corpus knowledge?
   - **Consistency**: Are cross-references valid? Do input/output schemas align?
   - **Anti-UI Compliance**: Does the triple describe agent actions, not user interface interactions?

3. For each finding, show severity (critical/high/medium/low) and a specific recommendation.

4. If the triple passes review, suggest approving it. If not, suggest specific edits to address each finding.
