---
name: mda-validate
description: Validate triples for schema compliance, cross-reference integrity, and consistency. Use to check triple quality before review.
argument-hint: [path]
allowed-tools: Bash(python *)
---

# MDA Validate -- Validate Triple Artifacts

This command validates generated triples (capsules, intents, contracts) for schema compliance, cross-reference integrity between related triples, and internal consistency.

## Context

Current working directory: !`pwd`
Triple files: !`find . -path "*/triples/*" -name "*.yaml" 2>/dev/null | wc -l || echo "0"` files found
Config exists: !`test -f mda.config.yaml && echo "YES" || echo "NO"`

## Steps

1. Run validation on the specified path (or all triples if no path given):

```
python cli/mda.py validate $ARGUMENTS
```

2. Report results organized by severity:
   - **Errors**: Schema violations, broken cross-references, missing required fields
   - **Warnings**: Incomplete sections, weak descriptions, missing optional enrichments
   - **Info**: Suggestions for improvement

3. For each issue found, include the file path and specific field so the user can locate and fix it.

4. If all triples pass validation, confirm they are ready for review (`/mda-review`).
