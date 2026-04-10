---
name: mda-reingest
description: Re-ingest an updated BPMN file, diff against existing triples, and propose changes. Use when the upstream BPMN has been modified.
argument-hint: [bpmn-file-path]
disable-model-invocation: true
allowed-tools: Bash(python *)
---

# MDA Reingest -- Re-ingest Updated BPMN with Diff

This command re-ingests a BPMN file that has been modified since the last ingestion. It diffs the new parse against existing triples and proposes additions, deletions, and modifications rather than regenerating everything from scratch.

## Context

Current working directory: !`pwd`
Existing triples: !`find . -path "*/triples/*" -name "*.yaml" 2>/dev/null | wc -l || echo "0"` files found

## Steps

1. Always start with a dry run to preview changes:

```
python cli/mda.py reingest $ARGUMENTS --dry-run
```

2. Present the diff summary to the user:
   - New tasks added in BPMN (will generate new triples)
   - Tasks removed from BPMN (triples to be archived)
   - Tasks modified (triples to be updated)
   - Unchanged tasks (no action needed)

3. Ask the user if they want to proceed with the actual re-ingestion.

4. If confirmed, run without dry-run:

```
python cli/mda.py reingest $ARGUMENTS
```

5. Report what changed and suggest reviewing the modified triples.
