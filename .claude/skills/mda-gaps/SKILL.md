---
name: mda-gaps
description: List all gaps across triples, filterable by severity and type. Use to see what knowledge is missing from capsules.
argument-hint: [--severity critical|high|medium|low]
allowed-tools: Bash(python *)
---

# MDA Gaps -- List Knowledge Gaps in Triples

This command identifies gaps in the generated triples -- missing corpus bindings, incomplete procedure steps, unresolved references, and other areas where human knowledge input is needed.

## Context

Current working directory: !`pwd`
Triple files: !`find . -path "*/triples/*" -name "*.yaml" 2>/dev/null | wc -l || echo "0"` files

## Steps

1. List all gaps, optionally filtered by severity:

```
python cli/mda.py gaps $ARGUMENTS
```

2. Present gaps organized by:
   - **Severity**: Critical, High, Medium, Low
   - **Type**: Missing corpus binding, incomplete steps, ambiguous gateway logic, missing error handling, etc.
   - **Location**: Which triple and field the gap appears in

3. For each gap, provide a brief summary of what knowledge is needed to fill it.

4. Suggest actions:
   - Add corpus documents to fill knowledge gaps (`/mda-corpus-add`)
   - Search existing corpus for relevant documents (`/mda-corpus-search`)
   - Manually edit triples to fill small gaps
