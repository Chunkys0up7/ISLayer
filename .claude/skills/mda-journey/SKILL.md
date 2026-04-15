---
name: mda-journey
description: Show the complete process journey from start to finish. Trace data lineage, see what each step needs and produces, navigate the critical path. Use to understand the full process flow and data dependencies.
argument-hint: [--step <capsule-id>] [--data <data-name>] [--critical-path] [--format yaml|json|mermaid]
allowed-tools: Bash(python *)
---

# MDA Journey -- Process Journey Map & Data Lineage

Shows the complete process journey from start to finish, including what data enters and exits each step, what systems are called, and where decision branches occur.

## Context

Current working directory: !`pwd`
Triples found: !`find . -name "*.cap.md" 2>/dev/null | wc -l || echo "0"`

## Steps

1. Run the journey command:

```
python cli/mda.py journey $ARGUMENTS
```

2. Common usage:
   - **Full journey table**: `python cli/mda.py journey`
   - **Single step detail**: `python cli/mda.py journey --step CAP-IV-W2V-001`
   - **Trace a data object**: `python cli/mda.py journey --data borrower_profile`
   - **Show critical path**: `python cli/mda.py journey --critical-path`
   - **Export as YAML**: `python cli/mda.py journey --format yaml`
   - **Mermaid diagram**: `python cli/mda.py journey --format mermaid`

3. For the journey table, explain:
   - Step numbers show the execution order
   - Bold steps are on the critical path (main happy path)
   - Inputs/Outputs columns show data dependency counts
   - Systems column shows external API calls
   - Gaps indicate missing knowledge

4. For data lineage, explain where the data originates and what steps consume it.
