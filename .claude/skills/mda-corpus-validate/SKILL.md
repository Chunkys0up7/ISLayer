---
name: mda-corpus-validate
description: Validate all corpus documents against the JSON schema. Use to check corpus document quality.
allowed-tools: Bash(python *)
---

# MDA Corpus Validate -- Validate Corpus Documents

This command validates all corpus documents (`.corpus.md` files) against the expected JSON schema, checking frontmatter completeness, required sections, and structural correctness.

## Context

Current working directory: !`pwd`
Corpus documents: !`find . -name "*.corpus.md" 2>/dev/null | wc -l || echo "0"` files found

## Steps

1. Run corpus validation:

```
python cli/mda.py corpus validate
```

2. Report results:
   - Number of documents validated
   - Number passing / failing
   - For each failure: file path, specific validation errors (missing fields, invalid types, structural issues)

3. If there are failures, suggest fixes for each. Common issues include:
   - Missing required frontmatter fields
   - Invalid document type values
   - Missing required content sections
   - Malformed YAML in frontmatter
