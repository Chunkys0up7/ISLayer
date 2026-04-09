# Governance Model

## Roles and Responsibilities

| Role | Responsibilities | Artifact Ownership |
|------|------------------|--------------------|
| **Process Owner** | Owns the BPMN diagram and the business process it represents. Approves capsule content. Final authority on business rules and edge cases. | Knowledge Capsules |
| **Tech Lead** | Owns the intent specification correctness. Reviews goal types, preconditions, postconditions, and outcome verification criteria. Ensures specs are platform-independent. | Intent Specifications |
| **Integration Lead** | Owns the integration contract. Reviews API endpoints, authentication, error mappings, retry policies, and circuit breaker configuration. Ensures contracts are accurate and current. | Integration Contracts |
| **Compliance** | Reviews triples for regulatory adherence. Validates forbidden actions. Approves triples in regulated domains before they reach `current` status. | Cross-cutting review |
| **Platform Team** | Maintains the pipeline tooling, schemas, templates, and validation infrastructure. Owns the process repository scaffold and CI/CD configuration. | Pipeline and infrastructure |

## PR Workflow: Initial Ingestion

When a new BPMN diagram is ingested for the first time:

1. Platform Team runs the ingestion pipeline against the BPMN XML.
2. Pipeline generates draft triples and opens a PR to the `main` branch.
3. PR title follows the convention: `ingest: {process-name} — initial triple generation`.
4. PR description includes gap summary (count of unresolved gaps per triple).
5. Reviewers are auto-assigned based on artifact type (see Reviewer Assignment Rules below).
6. Reviewers fill gaps, correct inaccuracies, and approve their respective artifacts.
7. All required reviewers must approve before merge.
8. PR is squash-merged to `main`. All triples transition from `draft` to `current`.

## PR Workflow: Triple Updates

When an existing triple is modified (gap resolution, business rule update, API change):

1. Author creates a feature branch: `update/{task-id}/{change-type}`.
2. Author modifies the relevant artifact(s) and updates the change reason in the triple manifest.
3. Modified triples auto-reset to `draft` status.
4. PR is opened with title: `update: {task-id} — {brief description}`.
5. Reviewers are assigned based on which artifacts were modified.
6. Review follows the same approval requirements as initial ingestion.
7. PR is squash-merged. Triples transition to `current`.

## PR Workflow: BPMN Re-Ingestion

When the upstream BPMN diagram changes:

1. Platform Team runs the re-ingestion pipeline, which diffs the new BPMN against the existing triples.
2. Pipeline generates a change report: new tasks (triples to create), removed tasks (triples to deprecate), modified tasks (triples to update).
3. PR is opened with title: `reingest: {process-name} — BPMN update {date}`.
4. PR description includes the full change report.
5. New triples are generated as drafts. Modified triples are reset to draft. Removed triples are marked `deprecated`.
6. All reviewers must review the change report and approve the net effect.
7. PR is squash-merged.

## Reviewer Assignment Rules

| Artifact Modified | Required Reviewers | Optional Reviewers |
|-------------------|--------------------|--------------------|
| Knowledge Capsule | Process Owner | Compliance |
| Intent Specification | Tech Lead | Process Owner |
| Integration Contract | Integration Lead | Tech Lead |
| Triple Manifest | Platform Team | Tech Lead |
| Multiple artifact types | All owners of modified types | Compliance |
| Regulated domain (any artifact) | All artifact owners + Compliance | --- |

Minimum required approvals: **2** (the artifact owner plus one additional reviewer).

## CI/CD Validation Requirements

Every PR must pass the following automated checks before merge is permitted:

1. **Schema validation** --- All modified artifacts validate against their JSON schemas.
2. **Cross-reference integrity** --- All `capsule_id`, `intent_id`, and `contract_id` references resolve to existing artifacts.
3. **Triple manifest consistency** --- The manifest reflects the current state of all triples in the repository.
4. **Gap count accuracy** --- Reported gap counts match actual gaps in artifact content.
5. **ID convention compliance** --- All IDs follow the naming conventions defined in the ontology.
6. **Status lifecycle compliance** --- No triple has an invalid status transition (e.g., jumping from `draft` to `current` without passing through `review` and `approved`).
7. **Anti-UI check** --- No integration contract references UI-based fulfillment paths.

CI failures block merge. There are no overrides for validation failures.

## Branch Strategy

| Branch | Purpose | Protection |
|--------|---------|------------|
| `main` | Production-ready triples. All artifacts at `current` or `deprecated` status. | Protected. No direct pushes. Requires PR with passing CI and required approvals. |
| `ingest/{process-name}` | Initial BPMN ingestion work. | Unprotected. Deleted after merge. |
| `update/{task-id}/{change-type}` | Triple modifications. | Unprotected. Deleted after merge. |
| `reingest/{process-name}/{date}` | BPMN re-ingestion work. | Unprotected. Deleted after merge. |

## Merge Strategy

All PRs are **squash-merged** to maintain clean, linear history on `main`. Each squash commit represents one logical change: an ingestion, an update, or a re-ingestion. This makes `git log` on `main` a readable audit trail of every change to the process triples.

Commit message format for squash merges:

```
{type}: {scope} — {description}

Change-Reason: {reason-code}
Reviewed-By: {reviewer-list}
Gap-Delta: {+N/-N gaps}
```

## Permissions Model

| Permission | Process Owner | Tech Lead | Integration Lead | Compliance | Platform Team |
|------------|:---:|:---:|:---:|:---:|:---:|
| Read all artifacts | Yes | Yes | Yes | Yes | Yes |
| Create feature branch | Yes | Yes | Yes | No | Yes |
| Modify capsules | Yes | No | No | No | Yes (pipeline only) |
| Modify intent specs | No | Yes | No | No | Yes (pipeline only) |
| Modify contracts | No | No | Yes | No | Yes (pipeline only) |
| Modify triple manifest | No | No | No | No | Yes |
| Approve PRs | Own artifacts | Own artifacts | Own artifacts | Any artifact | Any artifact |
| Merge PRs | No | No | No | No | Yes |
| Run pipeline | No | No | No | No | Yes |

## Change Reason Codes

Every PR must include a change reason code in the commit message:

| Code | Meaning | Example |
|------|---------|---------|
| `INGEST` | Initial BPMN ingestion | First-time triple generation |
| `REINGEST` | BPMN model changed upstream | Task added/removed/modified in BPMN |
| `GAP_FILL` | Filling a previously flagged gap | Adding missing API endpoint to contract |
| `BIZ_RULE` | Business rule change | Updated income threshold |
| `API_CHANGE` | Integration endpoint change | API version upgrade |
| `COMPLIANCE` | Regulatory requirement change | New forbidden action added |
| `CORRECTION` | Fixing an error in existing content | Correcting a wrong postcondition |
| `DEPRECATION` | Marking triple as no longer active | Process step removed |
| `ENRICHMENT` | Adding detail without changing semantics | Adding edge cases to capsule |

## Audit Trail Requirements

The following information must be recoverable from Git history for any triple at any point in time:

- Who created the triple (pipeline run or human author).
- When each lifecycle transition occurred (draft to review, review to approved, etc.).
- Who approved each transition (PR reviewer list).
- What changed in each modification (diff).
- Why each change was made (change reason code).
- What gaps existed at each point in time (gap count in commit message).

No triple is ever deleted. Decommissioned triples transition through `deprecated` to `archived`, preserving the complete history. See [Lifecycle Management](lifecycle-management.md) for archival policy details.
