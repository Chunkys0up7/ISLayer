---
name: mda-docs
description: Generate and serve the MkDocs documentation site for the current process. Use to browse triples, corpus, and process flow visually.
argument-hint: [generate|build|serve]
allowed-tools: Bash(python *)
---

# MDA Docs -- Generate and Serve Documentation

This command generates and optionally serves an MkDocs documentation site for the current process repository, providing a browsable view of triples, corpus documents, and process flow diagrams.

## Context

Current working directory: !`pwd`
Config exists: !`test -f mda.config.yaml && echo "YES" || echo "NO"`
Docs directory: !`test -d docs && echo "EXISTS" || echo "NOT FOUND"`

## Steps

1. Run the docs command. Default to `serve` if no subcommand is specified via `$ARGUMENTS`:

```
python cli/mda.py docs $ARGUMENTS
```

2. Available subcommands:
   - `generate` -- Generate Markdown documentation files from triples and corpus
   - `build` -- Build the static MkDocs site
   - `serve` -- Start the MkDocs dev server for local browsing

3. If serving, report the local URL (typically `http://localhost:8000`) so the user can open the docs in a browser.

4. If generating, report how many documentation pages were created and for which triples/corpus documents.
