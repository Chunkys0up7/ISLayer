---
name: mda-corpus-search
description: Search the knowledge corpus by keyword, type, or domain. Use when looking for existing procedures, policies, or regulations.
argument-hint: [search-query]
allowed-tools: Bash(python *)
---

# MDA Corpus Search -- Search the Knowledge Corpus

This command searches the indexed corpus documents by keyword, type, or domain. Useful for finding existing knowledge before adding new documents or understanding what corpus coverage exists for a given topic.

## Context

Current working directory: !`pwd`
Corpus indexed: !`test -f corpus/corpus.config.yaml && echo "YES" || echo "NO -- run /mda-corpus-index first"`

## Steps

1. Search the corpus for `$ARGUMENTS`:

```
python cli/mda.py corpus search "$ARGUMENTS"
```

2. Present results showing:
   - Document title and type
   - Domain
   - Relevance score or match context
   - File path for each match

3. If no results found, suggest:
   - Trying broader search terms
   - Checking if the corpus index is up to date (`/mda-corpus-index`)
   - Adding new corpus documents (`/mda-corpus-add`)
