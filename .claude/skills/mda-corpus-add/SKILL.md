---
name: mda-corpus-add
description: Create a new knowledge corpus document. Use when adding procedures, policies, regulations, rules, data dictionaries, system docs, training, or glossary entries.
argument-hint: [type] (procedure|policy|regulation|rule|data-dictionary|system|training|glossary)
allowed-tools: Bash(python *) Edit
---

# MDA Corpus Add -- Create a New Corpus Document

This command creates a new knowledge corpus document of a specific type. Corpus documents feed the enrichment pipeline, providing the domain knowledge that gets bound to BPMN tasks.

## Context

Current working directory: !`pwd`
Existing corpus types: !`find . -name "*.corpus.md" 2>/dev/null | sed 's/.*\///' | sed 's/\.corpus\.md//' | sort -u | head -10 || echo "None found"`

## Steps

1. The document type is `$0`. Valid types: procedure, policy, regulation, rule, data-dictionary, system, training, glossary.

2. If domain or title are not provided, ask the user for:
   - **Domain**: The business domain this document belongs to (e.g., "lending", "compliance", "onboarding")
   - **Title**: A descriptive title for the document

3. Create the corpus document:

```
python cli/mda.py corpus add $0 --domain "$1" --title "$2"
```

4. After creation, open the generated file for editing so the user can fill in the actual content. The template will have the required frontmatter and section structure.

5. Remind the user to run `/mda-corpus-index` after finishing edits to update the search index.
