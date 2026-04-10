---
name: mda-test
description: Run verification checks on the current process repository. Checks BPMN parsing, triple integrity, corpus consistency. Use to validate your work before committing.
argument-hint: [--quick] [--bpmn] [--triples] [--corpus]
allowed-tools: Bash(python *)
---

# MDA Test -- Run Verification Checks

This command runs a suite of verification checks against the current process repository, covering BPMN parsing, triple schema integrity, corpus consistency, and cross-reference validation.

## Context

Current working directory: !`pwd`
Config exists: !`test -f mda.config.yaml && echo "YES" || echo "NO"`
BPMN files: !`find . -name "*.bpmn" -o -name "*.bpmn20.xml" 2>/dev/null | wc -l || echo "0"` found
Triple files: !`find . -path "*/triples/*" -name "*.yaml" 2>/dev/null | wc -l || echo "0"` found
Corpus files: !`find . -name "*.corpus.md" 2>/dev/null | wc -l || echo "0"` found

## Steps

1. Run the test suite. If no specific flags are given via `$ARGUMENTS`, run all checks:

```
python cli/mda.py test $ARGUMENTS
```

2. Available flags:
   - `--quick` -- Fast subset of checks, skips expensive validations
   - `--bpmn` -- Only check BPMN parsing
   - `--triples` -- Only check triple integrity
   - `--corpus` -- Only check corpus consistency

3. Report results:
   - Total checks run, passed, failed
   - Details for each failure with file path and description
   - Overall pass/fail status

4. If failures are found, suggest targeted fixes. If all pass, confirm the repository is ready for commit.
