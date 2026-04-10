---
name: mda-init
description: Scaffold a new MDA process repository. Use when creating a new BPMN process project from scratch.
argument-hint: [process-name]
allowed-tools: Bash(python *) Bash(mkdir *) Bash(ls *)
---

# MDA Init -- Scaffold a New Process Repository

This command creates a new MDA process repository with the standard directory structure, default configuration, and template files needed to begin modeling a BPMN process.

## Context

Current working directory: !`pwd`
Existing MDA config: !`test -f mda.config.yaml && echo "mda.config.yaml found" || echo "No mda.config.yaml in current directory"`

## Steps

1. Run the scaffolding command for the process named `$ARGUMENTS`:

```
python cli/mda.py init $ARGUMENTS
```

2. If the command asks for additional information (domain prefix, namespace, etc.), prompt the user for those values before re-running.

3. After successful scaffolding, list the created directory structure to confirm everything was set up:

```
ls -R $ARGUMENTS/
```

4. Show the user:
   - The created directory tree
   - The generated `mda.config.yaml` contents
   - Suggested next steps (add BPMN file, add corpus documents, run ingest)
