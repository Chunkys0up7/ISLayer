# Component 01 — Triple Loader

## Purpose

Ingest triples from bitbucket into the simulator's in-memory/on-disk representation conforming to `contracts/triple-schema.md`. Produces a normalized triple set ready for inventory and simulation.

## Inputs

- **Source:** bitbucket repository URL, branch, and path to triple corpus. Supports both clone-on-ingest and pre-cloned local path.
- **Configuration:** `loader.config.yaml` specifying:
  - `source_format` — enum: `yaml_per_triple`, `json_per_triple`, `markdown_frontmatter`, `custom_jsonl`
  - `field_mapping` — optional dict mapping source field names to triple schema field names (for adapting pre-existing formats to the schema)
  - `content_chunk_extraction` — rules for how `psm.enriched_content` is parsed from source (e.g., each corpus citation = one chunk, or structured block extraction)
  - `strict_mode` — boolean; if true, unmappable fields throw; if false, they are preserved under `_raw` for later inspection

## Outputs

- A `TripleSet` object: `dict[triple_id, Triple]` where each Triple conforms to the schema.
- A `LoadReport` listing:
  - Total files attempted
  - Successfully loaded count
  - Failed loads with reasons (malformed YAML/JSON, missing identity fields, etc.)
  - Source-to-schema field mapping applied
  - Any `_raw` preservation that occurred
- On-disk cache at `./cache/triples/<corpus_version_hash>/` containing normalized triples as JSON, enabling downstream components to avoid re-parsing.

## Behavior

**B1.** Resolves source: either `git clone` into a tempdir or reads from specified local path. Records the git commit SHA as `corpus_version_hash`.

**B2.** Walks the triple directory. Each file → one triple. Subdirectories are traversed unless `ignore_paths` is configured.

**B3.** Parses each file according to `source_format`. Malformed files do NOT abort the run — they are recorded in LoadReport with the parse error and skipped.

**B4.** Applies `field_mapping` if present. This adapter layer lets existing triple formats work without requiring corpus-wide migration.

**B5.** Validates required identity fields per invariant I1 (`triple_id`, `version`, `bpmn_node_id`, `bpmn_node_type`). Triples failing I1 are excluded from TripleSet and listed in LoadReport.

**B6.** Normalizes into schema shape. Missing optional fields are set to their schema defaults (empty lists, null objects). **Does not fabricate contracts** — if `pim.preconditions` is missing entirely, the field stays missing (not empty list). This distinction is critical for downstream inventory: missing-field vs. explicitly-empty are different findings.

**B7.** Computes `corpus_version_hash` as the SHA256 of the concatenated sorted (triple_id, version) pairs. This hash appears in every trace for reproducibility.

**B8.** Writes normalized triples to cache directory as `<triple_id>.json`.

## Public API

```python
class TripleLoader:
    def __init__(self, config: LoaderConfig): ...
    def load(self) -> tuple[TripleSet, LoadReport]: ...
    def load_from_cache(self, corpus_version_hash: str) -> TripleSet: ...
```

## What this component does NOT do

- Does not validate invariants I2-I10. That is component 02.
- Does not construct the BPMN graph. That is component 03.
- Does not emit findings. It emits a LoadReport; findings are created downstream.
- Does not repair or infer missing contracts.

## Dependencies

- `contracts/triple-schema.md` — the target shape.
- `git` (shelled out or via `gitpython`) for repo access.
- YAML/JSON/Markdown parsers per `source_format`.

## Verification

**V1.** Given a corpus of 10 hand-authored triples, all properly formatted, loader produces TripleSet with 10 entries, LoadReport with 0 failures.

**V2.** Given a corpus with 2 malformed YAML files, loader produces TripleSet with 8 entries and LoadReport listing both failures with specific parse errors.

**V3.** Given a corpus with 1 triple missing `bpmn_node_id`, that triple is excluded from TripleSet and appears in LoadReport under `identity_failures`.

**V4.** Given identical corpus on disk, two successive `load()` calls produce identical `corpus_version_hash`.

**V5.** `load_from_cache(hash)` returns a TripleSet equal to the one that produced the hash.

## Implementation notes

- Keep parsing logic isolated in one module per `source_format` so new formats can be added without touching normalization.
- Log loading progress; on a large corpus (hundreds of triples), silent parsing feels broken.
- `field_mapping` should support nested paths (e.g., `"source.business_intent" -> "cim.intent"`).
- Preserve source file paths in each triple under `_source_path` for error reporting downstream.
