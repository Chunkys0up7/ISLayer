---
name: mda-report
description: Generate a GAP analysis report with health scoring for the current process. Scores each triple on 5 dimensions (completeness, consistency, schema compliance, knowledge coverage, anti-UI compliance) and produces XML/JSON/YAML output. Use to assess process health before review.
argument-hint: [--format xml|json|yaml] [--output path]
allowed-tools: Bash(python *)
---

# MDA Report -- GAP Analysis & Health Scoring

Generate a comprehensive health report for the current process repository, scoring each triple on 5 dimensions and producing a machine-readable GAP analysis.

## Context

Current working directory: !`pwd`
Config exists: !`test -f mda.config.yaml && echo "YES" || echo "NO"`
Triple count: !`find . -name "*.cap.md" 2>/dev/null | wc -l || echo "0"`
Gap count: !`grep -r "severity:" triples/ decisions/ 2>/dev/null | wc -l || echo "0"`

## Steps

1. Generate the report. Default format is XML:

```
python cli/mda.py report $ARGUMENTS
```

2. Available options:
   - `--format xml|json|yaml` -- Output format (default: xml)
   - `--output <path>` -- Write to file instead of stdout
   - `--include-details` -- Show per-dimension breakdowns

3. The report scores each triple on 5 dimensions:
   - **Completeness** (30%) -- All files exist, required fields populated, no critical gaps
   - **Consistency** (25%) -- IDs match, cross-references valid, status/version aligned
   - **Schema Compliance** (20%) -- Frontmatter validates against JSON schemas
   - **Knowledge Coverage** (15%) -- Corpus refs populated, procedure sections filled
   - **Anti-UI Compliance** (10%) -- forbidden_actions present with all 4 required values

4. Health grades: A (90+) Excellent, B (80-89) Good, C (70-79) Acceptable, D (60-69) Needs Work, F (<60) Critical

5. After viewing the report, suggest improvements for any triples with grade D or F.
