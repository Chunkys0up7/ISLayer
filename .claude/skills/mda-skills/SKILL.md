---
name: mda-skills
description: Generate step-level skills from process triples. Creates a SKILL.md for each BPMN step containing the complete briefing packet (procedure, inputs, outputs, business rules, job aid conditions, systems, failure modes). Use to create actionable task skills from your process.
argument-hint: [generate] [--step <name>] [--output <path>]
allowed-tools: Bash(python *)
disable-model-invocation: true
---

# MDA Skills — Generate Task Skills from Triples

Auto-generate a skill per BPMN step. Each skill gives the user/agent everything needed to execute that task.

## Context

Current working directory: !`pwd`
Triples: !`find . -name "*.cap.md" 2>/dev/null | wc -l || echo "0"` steps found
Existing step skills: !`ls .claude/skills/*/SKILL.md 2>/dev/null | wc -l || echo "0"` skills

## Steps

1. Generate skills for all steps:

```
python cli/mda.py skills generate $ARGUMENTS
```

2. Options:
   - `--step "verify-w2"` — generate for one step only
   - `--output /custom/path/` — write to a custom directory

3. After generation, the user can invoke any step skill by name:
   - `/verify-w2-income` — W-2 income verification briefing
   - `/classify-employment-type` — employment classification briefing

4. Each generated skill includes:
   - Process position (step N of M, predecessor/successor)
   - Preconditions, required inputs, procedure steps
   - Business rules, job aid conditions (if any)
   - Expected outputs with invariants
   - Systems to call (from contract)
   - Failure modes with detection and action
   - Regulatory context and known gaps
