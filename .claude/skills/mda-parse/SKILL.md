---
name: mda-parse
description: Parse a BPMN 2.0 XML file into a typed object model. Use when ingesting or analyzing a BPMN file.
argument-hint: [bpmn-file-path]
allowed-tools: Bash(python *)
---

# MDA Parse -- Parse a BPMN 2.0 XML File

This command parses a BPMN 2.0 XML file into MDA's typed object model, extracting all process elements (tasks, gateways, events, sequence flows, lanes, pools) into a structured representation.

## Context

Current working directory: !`pwd`
BPMN files in project: !`find . -name "*.bpmn" -o -name "*.bpmn20.xml" 2>/dev/null | head -5 || echo "None found"`

## Steps

1. Parse the BPMN file at `$ARGUMENTS`:

```
python cli/mda.py parse $ARGUMENTS
```

2. Display a summary of the parsed model:
   - Total number of process elements (tasks, gateways, events)
   - Number of sequence flows (edges)
   - Lanes and pools found
   - Any warnings or unsupported elements

3. If the file path is not provided or invalid, check for `.bpmn` files in the current project and suggest one to the user.

4. If parsing produces warnings about unsupported BPMN constructs, explain what they mean and whether they will affect downstream processing.
