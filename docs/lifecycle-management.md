# Lifecycle Management

## Status Lifecycle

Every triple follows a managed lifecycle with six states. Transitions are enforced by Git workflow and CI validation. No artifact is ever deleted --- decommissioned artifacts are archived, preserving full audit history.

```
                    ┌──────────────┐
                    │    draft     │
                    └──────┬───────┘
                           │ PR opened
                           v
                    ┌──────────────┐
              ┌─────│    review    │─────┐
              │     └──────┬───────┘     │
    changes   │            │ all         │
    requested │            │ approvals   │
              │            v             │
              │     ┌──────────────┐     │
              └────>│   approved   │     │
                    └──────┬───────┘     │
                           │ PR merged   │
                           v             │
                    ┌──────────────┐     │
              ┌─────│   current    │     │
              │     └──────┬───────┘     │
    direct    │            │ superseded  │
    edit      │            │ or removed  │
    (resets)  │            v             │
              │     ┌──────────────┐     │
              └────>│  deprecated  │     │
                    └──────┬───────┘     │
                           │ retention   │
                           │ elapsed     │
                           v             │
                    ┌──────────────┐     │
                    │   archived   │<────┘
                    └──────────────┘
```

## Status Transition Rules

| From | To | Trigger | Required Conditions |
|------|----|---------|---------------------|
| --- | `draft` | Pipeline generates new triple | BPMN task ID assigned, generated metadata populated |
| `draft` | `review` | PR opened against `main` | Pipeline validation passes, all required fields populated |
| `review` | `approved` | All required reviewers approve | Minimum 2 approvals, no critical gaps remaining, CI passes |
| `review` | `draft` | Changes requested | Reviewer requests modifications |
| `approved` | `current` | PR merged to `main` | All CI checks pass, no merge conflicts |
| `approved` | `draft` | PR reopened for changes | Author or reviewer reopens |
| `current` | `deprecated` | New version merged, or BPMN task removed | Superseding triple at `current`, or re-ingestion removes task |
| `current` | `draft` | Direct edit triggers re-review | Any content modification to a `current` triple |
| `deprecated` | `archived` | Retention period elapsed | Compliance sign-off received |

Invalid transitions (e.g., `draft` directly to `current`, `archived` to any state) are rejected by CI validation.

## Re-Ingestion Workflow

When the upstream BPMN diagram changes, the re-ingestion pipeline runs a structured diff:

### Step 1: BPMN Diff

The pipeline compares the new BPMN XML against the previously ingested version, producing a change report:

- **Added tasks** --- New BPMN elements that have no corresponding triple.
- **Removed tasks** --- BPMN elements that existed previously but are absent in the new version.
- **Modified tasks** --- BPMN elements whose attributes (name, type, lane assignment, connections) have changed.
- **Unchanged tasks** --- BPMN elements with no detectable change.

### Step 2: Triple Impact Assessment

| BPMN Change | Triple Action |
|-------------|---------------|
| Task added | Generate new draft triple |
| Task removed | Deprecate existing triple |
| Task renamed | Update capsule and intent spec names, reset to draft |
| Task type changed | Regenerate triple with new goal type, reset to draft |
| Lane reassigned | Update owner_role in capsule, reset to draft |
| Connections changed | Update predecessor/successor IDs in capsule, reset to draft |
| No change | No action --- triple remains at current status |

### Step 3: Human Review

The re-ingestion PR includes the full change report. Reviewers must verify:

- New triples have appropriate gap flags.
- Deprecated triples are correctly identified.
- Modified triples preserve human-authored content (business rules, API details) where applicable.
- The triple manifest reflects the updated state.

## Breaking vs Non-Breaking Changes

| Change Type | Breaking | Non-Breaking |
|-------------|----------|--------------|
| Goal type changed | Yes | --- |
| Precondition added | Yes | --- |
| Precondition removed | --- | Yes |
| Postcondition added | Yes | --- |
| Postcondition removed | --- | Yes |
| Input added (required) | Yes | --- |
| Input added (optional) | --- | Yes |
| Output removed | Yes | --- |
| Output added | --- | Yes |
| Forbidden action added | Yes | --- |
| Forbidden action removed | --- | Yes |
| API endpoint URL changed | Yes | --- |
| API request schema changed | Yes | --- |
| API response field added | --- | Yes |
| API response field removed | Yes | --- |
| Error mapping added | --- | Yes |
| Error mapping removed | Yes | --- |
| Business rule added to capsule | --- | Yes |
| Business rule removed from capsule | Yes | --- |

Breaking changes require all downstream agent runtimes to be notified and tested before the triple reaches `current` status.

## Version Numbering

Triples follow a simplified version scheme tied to their lifecycle:

- **Major version** increments when a breaking change is merged to `main`. The previous version is deprecated.
- **Minor version** increments when a non-breaking change is merged.
- **Patch version** is not used. All changes go through the full PR workflow.

Version format: `{major}.{minor}` (e.g., `1.0`, `1.1`, `2.0`).

Version is tracked in the triple manifest, not in the artifact filenames. Filenames remain stable across versions; Git history provides the version trail.

### Version History Example

```
v1.0  — Initial ingestion (draft → current)
v1.1  — Gap filled: added missing error mapping (non-breaking)
v1.2  — Enrichment: added edge cases to capsule (non-breaking)
v2.0  — API endpoint changed (breaking, v1.2 deprecated)
```

## Gap Management

Gaps are unresolved fields in draft triples --- places where the pipeline could not determine the correct value and a human has not yet provided one.

### Gap Classification

| Severity | Definition | Example |
|----------|------------|---------|
| **Critical** | Triple cannot reach `current` without resolution | Missing API endpoint in contract, missing precondition in intent |
| **Major** | Triple functions but with reduced reliability | Missing error mapping, incomplete edge cases in capsule |
| **Minor** | Triple functions normally, gap is cosmetic or supplementary | Missing example in capsule, incomplete description |

### Gap Aging

Gaps are tracked from the date they are first created:

| Age | Action |
|-----|--------|
| 0--14 days | Normal. Gap is expected for newly ingested triples. |
| 15--29 days | Warning. Gap appears in weekly status reports. Owner is notified. |
| 30+ days | Escalation. Gap is escalated to the Process Owner and Tech Lead. Blocking flag is added to the triple manifest. |
| 60+ days | Critical escalation. Gap is escalated to the Platform Team lead. Triple cannot be promoted past `review` until resolved. |

### Gap Resolution

When a gap is filled:

1. Author creates an `update/{task-id}/gap-fill` branch.
2. Author fills the gap with verified content.
3. PR is opened with change reason code `GAP_FILL`.
4. Artifact owner reviews and approves.
5. Gap count in triple manifest is decremented on merge.

## Decommissioning Workflow

When a BPMN task is permanently removed from the business process:

1. Re-ingestion pipeline detects the removal and marks the triple as `deprecated`.
2. Platform Team verifies no active agent runtimes reference the deprecated triple.
3. If active references exist, a 30-day migration period begins. Consuming teams are notified.
4. After migration period (or immediately if no references), the triple remains at `deprecated`.
5. After the retention period elapses and Compliance provides sign-off, the triple transitions to `archived`.

Deprecated triples remain readable in the repository. They are not deleted, moved, or hidden. Their status in the triple manifest is sufficient to distinguish them from active triples.

## Archival Policy

| Domain | Retention Period (deprecated to archived) | Rationale |
|--------|-------------------------------------------|-----------|
| Regulated (financial, healthcare) | 7 years | Regulatory audit requirements |
| Standard business | 3 years | Business continuity and audit trail |
| Internal/experimental | 1 year | Minimal regulatory exposure |

Archived triples are:

- Retained in the Git repository indefinitely (Git history is never rewritten).
- Excluded from the active triple manifest (a separate `archived-manifest.json` may be maintained).
- Not served to agent runtimes.
- Available for audit, compliance review, and historical analysis.
