---
name: mda-config
description: Show or edit the MDA process configuration (mda.config.yaml). Use when checking or changing project settings.
allowed-tools: Bash(python *) Read Edit
---

# MDA Config -- View or Edit Process Configuration

This command displays or modifies the MDA process configuration stored in `mda.config.yaml`. Configuration controls process metadata, pipeline settings, LLM parameters, and output paths.

## Context

Current working directory: !`pwd`
Config file exists: !`test -f mda.config.yaml && echo "YES -- $(wc -l < mda.config.yaml) lines" || echo "NO -- not found"`

## Steps

### Viewing Configuration

1. Run:

```
python cli/mda.py config
```

2. Present the configuration values to the user in a readable format, highlighting any non-default settings.

### Editing Configuration

If the user wants to change a setting:

1. Use the CLI setter:

```
python cli/mda.py config --set KEY VALUE
```

2. After setting, re-read the config to confirm the change took effect.

3. If the user wants to edit the file directly, read `mda.config.yaml` and use the Edit tool to make precise changes.

### Common Configuration Keys

- `process.name` -- The process display name
- `process.domain` -- Domain prefix for triple IDs
- `pipeline.skip_llm` -- Whether to skip LLM calls during ingestion
- `pipeline.model` -- LLM model to use for generation
- `output.triples_dir` -- Output directory for generated triples
