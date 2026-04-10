---
name: mda-corpus-index
description: Regenerate the corpus index (corpus.config.yaml) from all .corpus.md files. Use after adding or modifying corpus documents.
allowed-tools: Bash(python *)
---

# MDA Corpus Index -- Rebuild the Corpus Index

This command scans all `.corpus.md` files in the corpus directory and regenerates `corpus.config.yaml`, which serves as the searchable index for the enrichment pipeline.

## Context

Current working directory: !`pwd`
Corpus documents: !`find . -name "*.corpus.md" 2>/dev/null | wc -l || echo "0"` files found
Current index: !`test -f corpus/corpus.config.yaml && echo "EXISTS -- last modified $(stat -c %y corpus/corpus.config.yaml 2>/dev/null || stat -f %Sm corpus/corpus.config.yaml 2>/dev/null)" || echo "NOT FOUND"`

## Steps

1. Run the corpus indexing command:

```
python cli/mda.py corpus index
```

2. Report:
   - Number of corpus documents indexed
   - Types of documents found (procedures, policies, regulations, etc.)
   - Any documents that failed validation during indexing
   - Any orphaned entries in the old index that no longer have matching files

3. If no corpus documents are found, suggest creating some with `/mda-corpus-add`.
