---
name: mda-graph
description: Generate a process flow graph from capsule predecessor/successor relationships. Use to visualize the process flow.
argument-hint: [--format yaml|mermaid|dot]
allowed-tools: Bash(python *)
---

# MDA Graph -- Generate Process Flow Graph

This command generates a visual process flow graph from the capsule predecessor/successor relationships, showing how tasks connect through the modeled process.

## Context

Current working directory: !`pwd`
Triple files: !`find . -path "*/triples/*" -name "*.yaml" 2>/dev/null | wc -l || echo "0"` files

## Steps

1. Generate the graph in the requested format (default: mermaid):

```
python cli/mda.py graph --format mermaid
```

If the user specified a different format via `$ARGUMENTS`, use that instead:

```
python cli/mda.py graph $ARGUMENTS
```

2. Supported formats:
   - **mermaid**: Mermaid.js flowchart syntax (can be rendered in Markdown)
   - **yaml**: Structured YAML adjacency list
   - **dot**: Graphviz DOT format

3. If the output is Mermaid format, present it in a fenced code block so it renders visually in supported viewers.

4. Highlight any disconnected nodes or unreachable paths in the graph.
