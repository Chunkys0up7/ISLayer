# Changelog

All notable changes to the MDA Intent Engine will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-04-09

### Fixed
- Schema ID patterns now allow digits in category codes (e.g., W2V) — changed `[A-Z]` to `[A-Z0-9]`
- Template field names aligned with schemas — removed `intent_name`, `contract_name`
- Template contract ID prefix corrected from `CON-` to `ICT-`
- Added missing `mda_layer: "PSM"` to 9 property-appraisal contract files
- Added missing `goal`, `goal_type`, `contract_ref`, `forbidden_actions` to property-appraisal and loan-origination intent files

### Added
- MIT License
- EXECUTION-SPEC.md — complete build-from-scratch specification (5,342 lines)
- TEST-SPEC.md — test suite recreation specification (1,251 lines)
- Process repo scaffold templates (README, mda.config.yaml, .gitignore)
- Specification links in README

## [0.2.0] - 2026-04-09

### Added
- Python CLI with 18 commands (parse, ingest, validate, status, gaps, graph, corpus, docs, test, etc.)
- Provider-agnostic LLM integration (Anthropic, OpenAI, Ollama)
- Knowledge corpus with 46 source documents and searchable index
- MkDocs process navigator with auto-generated per-process sites
- Comprehensive test suite (518 pytest tests + 25 CLI checks)
- User guides: getting started, CLI reference, process owner, corpus authoring, triple review

## [0.1.0] - 2026-04-09

### Added
- Initial project structure
- JSON Schemas for capsule, intent, contract, and triple manifest validation
- Canonical templates for all three artifact types
- METHODOLOGY.md --- MDA alignment rationale
- Ontology definitions (goal types, status lifecycle, BPMN element mapping, ID conventions)
- Pipeline stage definitions (6 stages: parser through validator)
- Documentation (architecture, governance model, lifecycle management)
- Three demo BPMN processes (loan origination, income verification, property appraisal)
