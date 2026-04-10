---
name: mda-enrich
description: Enrich a parsed BPMN model with corpus matches. Runs the multi-factor scoring algorithm to find relevant knowledge documents for each task.
argument-hint: [parsed-model-path]
allowed-tools: Bash(python *)
---

# MDA Enrich -- Enrich Parsed Model with Corpus Knowledge

This command runs the multi-factor scoring algorithm to match corpus documents to parsed BPMN tasks. It produces enrichment scores showing which knowledge documents are most relevant to each task, forming the basis for triple generation.

## Context

Current working directory: !`pwd`
Corpus indexed: !`test -f corpus/corpus.config.yaml && echo "YES" || echo "NO -- run /mda-corpus-index first"`
Corpus documents: !`find . -name "*.corpus.md" 2>/dev/null | wc -l || echo "0"` files

## Steps

1. Run enrichment on the parsed model at `$ARGUMENTS`:

```
python cli/mda.py enrich $ARGUMENTS
```

2. Report enrichment results:
   - For each BPMN task, show the top-matched corpus documents and their scores
   - Highlight tasks with no corpus matches (these will produce gaps in generation)
   - Show the scoring factors used (keyword overlap, domain match, type relevance)

3. If tasks have low or no matches, suggest:
   - Adding more corpus documents (`/mda-corpus-add`)
   - Checking corpus index is current (`/mda-corpus-index`)
   - Reviewing task naming for better keyword alignment
