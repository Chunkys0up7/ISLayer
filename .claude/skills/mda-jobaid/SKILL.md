---
name: mda-jobaid
description: Import, validate, query, and manage job aids. Job aids are structured condition/action lookup tables that parameterize how a task executes based on conditions like loan program, income type, and state. Use when working with decision tables, lookup matrices, or conditional business rules.
argument-hint: [import|validate|query|list]
allowed-tools: Bash(python *) Read Edit
---

# MDA Job Aid -- Manage Condition/Action Tables

Job aids are structured YAML files that define how a task's parameters change based on conditions. A single BPMN task has ONE triple, but the values the agent uses depend on conditions looked up from the job aid.

## Context

Current working directory: !`pwd`
Job aids found: !`find . -name "*.jobaid.yaml" 2>/dev/null | wc -l || echo "0"`

## Commands

### Import from Excel
Convert a decision table Excel file into a .jobaid.yaml:
```
python cli/mda.py jobaid import <excel-file> --capsule-id CAP-XX-YYY-NNN [--title "My Job Aid"] [--dimensions "col1,col2,col3"]
```

### Validate
Check job aid files for schema compliance and internal consistency:
```
python cli/mda.py jobaid validate [path-to-jobaid.yaml]
```

### Query
Look up rules matching specific conditions:
```
python cli/mda.py jobaid query <jobaid.yaml> --conditions "loan_program=FHA,income_type=overtime"
```

### List
Show all job aids in the current process:
```
python cli/mda.py jobaid list
```

## Steps

1. Determine which subcommand the user needs based on `$ARGUMENTS`
2. Run the appropriate command
3. If importing, suggest running validate afterward
4. If querying, explain the matching results
