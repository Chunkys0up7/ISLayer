---
name: mda-ingest
description: Run the full BPMN-to-triples pipeline. Parses BPMN, enriches from corpus, generates capsules/intents/contracts. Use when converting a BPMN process into agent-executable triples.
argument-hint: [bpmn-file-path]
disable-model-invocation: true
allowed-tools: Bash(python *)
---

# MDA Ingest -- Full BPMN-to-Triples Pipeline

This command runs the complete ingestion pipeline: parse BPMN, enrich with corpus knowledge, and generate all triple artifacts (capsules, intents, contracts). This is the primary workflow for converting a business process into agent-executable form.

## Context

Current working directory: !`pwd`
Config exists: !`test -f mda.config.yaml && echo "YES" || echo "NO"`
Corpus index: !`test -f corpus/corpus.config.yaml && echo "YES -- corpus indexed" || echo "NO -- corpus not indexed, consider running corpus index first"`

## Steps

1. Ask the user whether they want to run in `--skip-llm` mode (uses heuristic generation instead of LLM calls -- faster, no API key needed, but lower quality output).

2. Run the full ingestion pipeline on `$ARGUMENTS`:

```
python cli/mda.py ingest $ARGUMENTS
```

Or with skip-llm:

```
python cli/mda.py ingest $ARGUMENTS --skip-llm
```

3. The pipeline will:
   - Parse the BPMN file
   - Match corpus documents to tasks via multi-factor scoring
   - Generate capsule, intent, and contract triples for each task
   - Write output to the configured triples directory

4. After completion, report:
   - Number of triples generated (capsules, intents, contracts)
   - Any gaps or warnings flagged during generation
   - Suggested next steps (validate, review, fill gaps)
