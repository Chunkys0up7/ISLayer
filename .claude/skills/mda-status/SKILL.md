---
name: mda-status
description: Show the status of all triples in the current process repository. Use to see draft/review/approved/current counts and binding status.
allowed-tools: Bash(python *)
---

# MDA Status -- Process Repository Status

This command shows a summary of all triples in the current process repository, including their lifecycle status (draft, review, approved, current) and corpus binding coverage.

## Context

Current working directory: !`pwd`
Config exists: !`test -f mda.config.yaml && echo "YES" || echo "NO"`
Triple files: !`find . -path "*/triples/*" -name "*.yaml" 2>/dev/null | wc -l || echo "0"` files

## Steps

1. Run the status command:

```
python cli/mda.py status
```

2. Present a clear summary showing:
   - Total triple count by type (capsules, intents, contracts)
   - Breakdown by lifecycle status (draft / in-review / approved / current)
   - Corpus binding coverage (how many capsules have bound corpus documents)
   - Any triples with gaps or missing dependencies

3. If the repository looks incomplete, suggest next actions:
   - Ungenerated triples: run `/mda-ingest`
   - Draft triples: run `/mda-review`
   - Gaps found: run `/mda-gaps`
