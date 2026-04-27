---
# =============================================================================
# SPEC FRONTMATTER — required metadata for ingestion
# =============================================================================
# Stable identifier for this initiative. Once set, do not change — it is the
# anchor used by the JIRA sync layer to map this spec to its Epic.
spec_id: "SPEC-XXX-001"

# Human-readable title — becomes the JIRA Epic name.
title: "Initiative Title Goes Here"

# Spec version. Use semver. Increment when scope changes.
version: "1.0"

# Lifecycle: draft | review | approved | current | superseded | archived
# Only specs in 'approved' or 'current' will be synced to JIRA by default.
status: "draft"

# Domain and subdomain — used by the corpus matcher to find relevant
# engineering standards (ADRs, runbooks, API specs, security policies).
# Keep these consistent across specs in the same product area.
domain: "Payments"
subdomain: "Refunds"

# Authoring information.
author: "Jane PM"
last_modified: "2026-04-27"
last_modified_by: "Jane PM"

# Source provenance — where this spec originated. Could be a Confluence URL,
# Google Doc URL, or a git path. Used for cross-referencing in audit trails.
source_ref: "https://confluence.example.com/display/PAY/Refunds+Initiative"

# JIRA project key for the synced Epic. Required for sync.
jira_project_key: "PAY"

# Optional: existing JIRA Epic key. If set, the sync uses this instead of
# creating a new Epic. Useful for retrofitting an existing Epic.
jira_epic_key: null

# Tags — used for searchability and corpus matching.
tags:
  - payments
  - refunds
  - api
  - pci-dss

# Related specs — other initiative specs this depends on or extends.
related_specs:
  - spec_id: "SPEC-PAY-001"
    relationship: "depends_on"
    description: "Core payments service must exist before refunds"

# Compliance / regulatory context — listed here so corpus matching can
# attach the right regulations to every story by default.
compliance_context:
  - "PCI-DSS v4.0"
  - "GDPR Article 17 (Right to Erasure)"
  - "SOX Section 404"
---

<!--
=============================================================================
INGESTION GUIDANCE — read before authoring
=============================================================================

This template is the optimal input format for the MDA Intent Layer
spec-to-JIRA pipeline. Following its structure produces:
  - Clean story extraction with paragraph-level provenance
  - Accurate dependency graphs from explicit links (no inference required)
  - Correct team assignment from lane declarations
  - Compliance and architectural standards auto-attached
  - Verifiable grounding (every story traces back to specific paragraphs)

WHAT THE PARSER LOOKS FOR
  - H2 headings (##) define top-level sections
  - H3 headings (###) inside the "Stories" section define individual stories
  - Story IDs in the form `[STORY-XYZ]` make stories addressable for dependencies
  - Frontmatter inside each story (between `+++` markers) gives structured fields
  - Acceptance criteria use Gherkin form (Given / When / Then) or a checklist
  - Dependencies use explicit story IDs, not prose ("after STORY-002" not "later")

ANTI-PATTERNS TO AVOID
  - Don't bury stories in long prose paragraphs — give each its own H3 heading
  - Don't write "the system shall be performant" without measurable criteria
  - Don't use ambiguous owner references ("the team should...") — name a lane
  - Don't infer dependencies from order — state them explicitly with story IDs
  - Don't mix scope and out-of-scope in the same section — separate them

GROUNDING NOTE
  Anything in this spec must be a sourceable claim. If you cannot point to a
  reason a requirement exists (a regulation, a customer commitment, an ADR,
  a research finding), flag it as an open question rather than asserting it.

LINE NUMBERS MATTER
  The parser tracks every story back to the line range of the source spec
  it came from. Keep this template in source control so re-runs produce
  consistent provenance.
-->

# {{ TITLE }}

## 1. Background and Context

<!--
Plain-English narrative of why this initiative exists. The parser uses this
to populate the Epic description and to add context to every story. Keep it
to 3-5 paragraphs. Cite sources where possible:
  - Customer research (CRP-RES-XXX)
  - Strategic objectives (OKR or strategy doc reference)
  - Regulatory drivers (specific regulation + section)
  - Technical drivers (ADR-XXX or incident reference)

Every assertion in this section will become part of the Epic description
and inherits citations from corpus matches. Unsourced assertions become
gaps flagged on the Epic.
-->

[Background paragraph 1 — what is the problem]

[Background paragraph 2 — why now, what's changed]

[Background paragraph 3 — what this initiative achieves at a strategic level]

## 2. Goals and Success Metrics

<!--
The parser reads this section to populate the Epic-level Definition of Done.
Each goal should be:
  - Measurable (numeric or boolean)
  - Time-bound where applicable
  - Attributable to a stakeholder

Use this exact bullet structure so the parser can extract each goal as a
distinct success criterion. Each becomes an item in the Epic's
"Success Criteria" custom field.
-->

- **Goal 1**: [Specific outcome]. Metric: [How measured]. Target: [Number/threshold]. Owner: [Stakeholder/team].
- **Goal 2**: [...]
- **Goal 3**: [...]

### Non-Goals

<!--
Explicit list of things this initiative does NOT include. The parser uses
this to mark the Epic boundary and to prevent stories from drifting into
out-of-scope work. Each non-goal becomes a labelled exclusion on the Epic.
-->

- This initiative does not include [explicit out-of-scope item].
- This initiative does not include [explicit out-of-scope item].

## 3. Stakeholders and Teams (Lanes)

<!--
Lanes map directly to JIRA components / team labels. Every story must
reference at least one lane in its `owner_team` field. The parser will
warn if a story has no lane assignment.

Lanes are also used by the corpus matcher to attach team-specific runbooks,
coding standards, and on-call procedures to each story.
-->

| Lane (Team / Role) | Responsibility in This Initiative | JIRA Component |
| ------------------ | --------------------------------- | -------------- |
| `payments-platform` | Core service implementation        | payments-platform |
| `data-platform`     | Event publishing and analytics     | data-platform     |
| `compliance`        | Audit logging review and signoff   | compliance        |
| `qa-platform`       | Test strategy and automation       | qa-platform       |
| `product`           | Acceptance and stakeholder review  | product           |

## 4. Data Objects and APIs

<!--
List every data object, API endpoint, schema, or shared artifact that
stories in this spec will reference. Each entry becomes a `data_object`
in the parsed model and is matched against the API catalog corpus.

If the artifact already exists, give its catalog ID (e.g., API-PAY-007).
If it is new, mark it with `status: proposed` and the system will create
a placeholder data dictionary entry.
-->

| Name | Type | Status | Catalog ID / Reference | Description |
| ---- | ---- | ------ | --------------------- | ----------- |
| `RefundRequest` | object schema | existing | DAT-PAY-014 | Inbound refund request payload |
| `RefundOutcome` | object schema | proposed | (new) | Result of refund processing — to be defined in this initiative |
| `POST /v2/refunds` | REST endpoint | proposed | (new) | New refund creation endpoint |
| `payments.refund.completed` | event topic | proposed | (new) | Emitted when a refund is finalised |
| `audit.refund_log` | audit sink | existing | SYS-AUD-002 | Immutable audit trail destination |

## 5. Cross-Cutting Concerns

<!--
Concerns that apply to EVERY story in this initiative. The parser
applies these to all stories automatically — you do not need to repeat
them in each story.

This is also where you anchor the architectural standards that govern
the work. List ADRs explicitly so the corpus matcher can attach them.
-->

- **Idempotency**: All state-mutating endpoints must support idempotency keys per ADR-042.
- **Audit logging**: All financial state changes must be written to `audit.refund_log` per SOX compliance requirement.
- **PII handling**: Refund metadata must not contain customer PAN or full card numbers per PCI-DSS v4.0.
- **Observability**: All endpoints must emit metrics per the platform observability standard (ADR-018).
- **Backwards compatibility**: No breaking changes to v1 payment APIs. All work is additive.

## 6. Stories

<!--
This is the section the parser cares about most. Each story below becomes
a JIRA Story under the Epic. Follow the exact structure for every story:

  ### [STORY-XXX] Name of the story
  +++
  owner_team: lane-id
  estimated_complexity: xs | s | m | l | xl
  depends_on: ["STORY-YYY", "STORY-ZZZ"]
  blocks: ["STORY-AAA"]
  data_refs: ["RefundRequest", "POST /v2/refunds"]
  compliance_refs: ["PCI-DSS v4.0 Req 3.4"]
  risk_level: low | medium | high
  +++

  **Description**: One-paragraph description of what this story delivers.

  **Acceptance Criteria**:
  - Given [precondition], when [action], then [observable outcome].
  - Given [precondition], when [action], then [observable outcome].

  **Definition of Done**:
  - [ ] Code reviewed and merged
  - [ ] Tests at coverage threshold
  - [ ] Runbook updated
  - [ ] [Story-specific items]

  **Failure Modes / Edge Cases**:
  - **[Failure name]**: [How detected] → [Action to take]

  **Configuration Parameters** (job aid candidates):
  - `param_name` (range): description — used by [story logic]

  **Notes**: Optional. Any additional context, prior-art references,
  or architectural rationale.

KEEP STORIES SMALL
  A story should fit in a single sprint for one engineer. If a story
  needs more than 4 acceptance criteria or 3 sub-tasks, split it.

USE STABLE IDS
  STORY-XXX numbers should be stable across spec revisions. Do not
  renumber stories — append new ones at the end. The JIRA sync uses
  these IDs to find the corresponding JIRA story on re-runs.
-->

### [STORY-001] Define RefundOutcome data schema

+++
owner_team: payments-platform
estimated_complexity: s
depends_on: []
blocks: ["STORY-002", "STORY-003"]
data_refs: ["RefundOutcome"]
compliance_refs: []
risk_level: low
+++

**Description**: Define the canonical schema for refund outcomes — the response payload returned by the new `/v2/refunds` endpoint and the data contract carried by the `payments.refund.completed` event. Schema must include refund ID, original payment ID, amount, currency, status, reason code, and audit timestamps.

**Acceptance Criteria**:
- Given the schema is published, when consumers fetch it from the API catalog, then it is retrievable at `/api/catalog/RefundOutcome`.
- Given a refund outcome instance, when validated against the schema, then all required fields are enforced and unknown fields are rejected.
- Given the schema is updated, when the change is non-breaking, then versioning conventions per ADR-031 are followed.

**Definition of Done**:
- [ ] Schema authored in the API catalog repository
- [ ] Schema validated against the catalog linter
- [ ] Schema linked from the corpus data dictionary
- [ ] PR reviewed and merged

**Failure Modes / Edge Cases**:
- **Backwards-incompatible field rename**: Detected by catalog CI → block PR; require version bump per ADR-031.

**Configuration Parameters**: None.

**Notes**: This story unblocks both the API endpoint and the event emission stories.

---

### [STORY-002] Implement POST /v2/refunds endpoint

+++
owner_team: payments-platform
estimated_complexity: l
depends_on: ["STORY-001"]
blocks: ["STORY-004", "STORY-005"]
data_refs: ["RefundRequest", "RefundOutcome", "POST /v2/refunds"]
compliance_refs: ["PCI-DSS v4.0 Req 3.4", "PCI-DSS v4.0 Req 10.2"]
risk_level: high
+++

**Description**: Implement the REST endpoint that accepts a `RefundRequest`, validates it, processes the refund through the payment provider, and returns a `RefundOutcome`. Endpoint must be idempotent on the `Idempotency-Key` header per ADR-042.

**Acceptance Criteria**:
- Given a valid `RefundRequest` and a unique `Idempotency-Key`, when POST is called, then a `RefundOutcome` is returned with status `accepted` and a refund ID is generated.
- Given the same `Idempotency-Key` is replayed within 24 hours, when POST is called again, then the original `RefundOutcome` is returned without re-processing.
- Given a refund request whose original payment is not found, when POST is called, then a 404 with structured error is returned.
- Given a refund request whose amount exceeds the original payment, when POST is called, then a 422 with `excess_amount` error code is returned.

**Definition of Done**:
- [ ] Endpoint implementation merged
- [ ] Unit and integration tests at >=85% coverage
- [ ] Idempotency tested under concurrent replay
- [ ] OpenAPI spec updated and published
- [ ] Runbook updated with new endpoint
- [ ] Performance test: p99 < 500ms at 100 RPS

**Failure Modes / Edge Cases**:
- **Provider timeout**: Detected by 30s timeout → return 504; rely on idempotency for client retry.
- **Partial refund double-spend**: Detected by amount tracking → reject with `excess_amount`.
- **Idempotency key collision across customers**: Detected by per-customer key scoping → not possible by design.

**Configuration Parameters** (job aid candidates):
- `provider_timeout_ms` (1000–60000, default 30000): Timeout per call to the payment provider.
- `idempotency_ttl_hours` (1–168, default 24): How long to retain idempotency records.
- `max_partial_refunds_per_payment` (1–10, default 5): Cap on partial refund attempts.

**Notes**: This is the highest-risk story in the initiative. Recommend pairing with a senior engineer and adding a feature flag (`refunds.v2.enabled`) for staged rollout.

---

### [STORY-003] Emit payments.refund.completed event

+++
owner_team: payments-platform
estimated_complexity: m
depends_on: ["STORY-001", "STORY-002"]
blocks: []
data_refs: ["RefundOutcome", "payments.refund.completed"]
compliance_refs: []
risk_level: medium
+++

**Description**: When a refund reaches a terminal state (`completed`, `failed`, `cancelled`), publish a `payments.refund.completed` event carrying the `RefundOutcome` payload to the platform event bus. Delivery semantics: at-least-once, ordered by refund ID.

**Acceptance Criteria**:
- Given a refund reaches `completed` state, when the state transition commits, then an event is published within 500ms.
- Given the event bus is unavailable, when an event cannot be published, then the event is queued for retry per the platform event-publishing standard (ADR-024).
- Given two events for the same refund ID, when consumed, then they are received in the correct order.

**Definition of Done**:
- [ ] Event publishing integrated with platform event bus
- [ ] Event schema published in the schema registry
- [ ] Retry behaviour tested
- [ ] Consumer documentation updated

**Failure Modes / Edge Cases**:
- **Event bus down**: Detected by health check → queue locally; alert on-call.
- **Schema validation failure**: Detected by registry → reject publish; log and alert.

**Configuration Parameters** (job aid candidates): None.

**Notes**: Coordinate with `data-platform` team for analytics consumer wiring.

---

### [STORY-004] Add audit logging for refund operations

+++
owner_team: payments-platform
estimated_complexity: s
depends_on: ["STORY-002"]
blocks: []
data_refs: ["RefundOutcome", "audit.refund_log"]
compliance_refs: ["SOX Section 404", "PCI-DSS v4.0 Req 10.2"]
risk_level: medium
+++

**Description**: Every refund operation (request received, processing started, terminal state reached) must produce an immutable audit log record in `audit.refund_log` with required fields per the audit logging standard.

**Acceptance Criteria**:
- Given any refund state transition, when it occurs, then an audit record is written within 1 second.
- Given an audit record, when inspected, then it contains: timestamp, actor (service principal), action, refund_id, prior_state, new_state, request_id.
- Given a refund operation fails to write an audit record, when this is detected, then the refund operation is rolled back.

**Definition of Done**:
- [ ] Audit hooks added to all state transitions
- [ ] Audit retention configured to 7 years per SOX
- [ ] Compliance team review and signoff (`compliance` lane)
- [ ] Alert on audit write failures

**Failure Modes / Edge Cases**:
- **Audit sink unavailable**: Detected by write timeout → fail the originating refund operation; do NOT proceed without audit.
- **Audit record tampering**: Prevented by sink immutability per SYS-AUD-002.

**Configuration Parameters** (job aid candidates):
- `audit_write_timeout_ms` (100–10000, default 1000): How long to wait for audit write.
- `audit_retention_years` (3–10, default 7): Retention period.

**Notes**: Compliance signoff is required before merge. Allow time for review.

---

### [STORY-005] Add /v2/refunds endpoint to API gateway and rate limits

+++
owner_team: payments-platform
estimated_complexity: s
depends_on: ["STORY-002"]
blocks: []
data_refs: ["POST /v2/refunds"]
compliance_refs: []
risk_level: low
+++

**Description**: Configure the API gateway to route `/v2/refunds` traffic to the payments service, apply per-customer rate limits, and configure the WAF policy.

**Acceptance Criteria**:
- Given the gateway configuration is deployed, when a request hits `/v2/refunds`, then it is routed to the payments service.
- Given a customer exceeds 10 requests per second, when they make further requests, then they receive 429 with retry-after header.
- Given a malformed request, when it hits the WAF, then it is blocked before reaching the service.

**Definition of Done**:
- [ ] Gateway route added in IaC
- [ ] Rate limit configured
- [ ] WAF policy applied
- [ ] Load test confirms rate limits enforce correctly
- [ ] Runbook updated

**Failure Modes / Edge Cases**:
- **Misconfigured rate limit**: Detected by load test → adjust before production rollout.

**Configuration Parameters** (job aid candidates):
- `rate_limit_rps_per_customer` (1–100, default 10): Per-customer request rate ceiling.

**Notes**: Coordinate with platform team for IaC review.

## 7. Decision Points

<!--
Decision points represent gateway-style logic in the BPMN-equivalent
sense — branches in execution that depend on conditions. Each becomes
a Decision Story (a special triple type) and may have an associated
job aid for the decision matrix.

Use this section when the implementation has runtime branches that
need explicit specification. Skip this section if there are none.
-->

### [DECISION-001] Refund eligibility determination

+++
owner_team: payments-platform
depends_on: ["STORY-002"]
data_refs: ["RefundRequest"]
+++

**Decision Question**: Given a refund request, is the original payment eligible for refund?

**Decision Inputs**:
- `payment_age_days` (number)
- `payment_state` (enum: settled, pending, refunded, disputed)
- `payment_method` (enum: card, bank_transfer, wallet)
- `merchant_refund_policy` (enum: standard, restricted, no_refund)

**Decision Matrix** (job aid candidate — will become `JA-PAY-RFD-001`):

| payment_state | payment_age_days | merchant_refund_policy | -> eligible | -> reason_code |
| ------------- | ---------------- | --------------------- | ----------- | -------------- |
| settled       | <=180            | standard              | true        | OK |
| settled       | <=180            | restricted            | true        | OK_RESTRICTED |
| settled       | <=180            | no_refund             | false       | MERCHANT_POLICY |
| settled       | >180             | *                     | false       | TIME_LIMIT_EXCEEDED |
| pending       | *                | *                     | false       | PAYMENT_NOT_SETTLED |
| refunded      | *                | *                     | false       | ALREADY_REFUNDED |
| disputed      | *                | *                     | false       | PAYMENT_DISPUTED |

**Default Action**: `eligible: false, reason_code: UNKNOWN_STATE` (fail closed).

**Precedence**: `most_specific`.

**Notes**: This decision matrix will be extracted into a job aid YAML on first parse and attached to STORY-002's capsule. Updates to this matrix in the spec will diff into the job aid on re-parse.

## 8. Risks and Mitigations

<!--
Initiative-level risks. Each becomes a risk register entry linked to
the Epic. Story-level risks live inside the story under "Failure Modes".
-->

| Risk | Likelihood | Impact | Mitigation | Owner |
| ---- | ---------- | ------ | ---------- | ----- |
| Provider API changes during implementation | Low | High | Lock provider SDK version; subscribe to provider changelog | payments-platform |
| Compliance signoff delays release | Medium | Medium | Engage compliance team at story authoring, not at PR | product |
| Customer support volume spikes on launch | Medium | Medium | Stage rollout via feature flag; pre-brief support team | product |

## 9. Open Questions

<!--
Things you don't know yet. Each becomes a flagged gap on the Epic
and on any stories that reference unresolved questions.

The parser will not invent answers — open questions stay open until
this document is updated.
-->

- [ ] Should refunds be allowed on payments older than 180 days with merchant override?
- [ ] What is the SLA expectation for refund completion notifications to customers?
- [ ] Are partial refunds always allowed, or only for specific merchant tiers?

## 10. Out of Scope

<!--
Explicit non-stories. The parser uses this to ensure no stories are
generated for items in this list, and to flag any apparent scope drift
between this section and the stories in section 6.
-->

- Refund initiation via the customer-facing dashboard (separate initiative SPEC-PAY-RFD-UI-001).
- Refund analytics reporting (handled by data-platform initiative SPEC-DAT-RFD-001).
- Refund chargeback dispute handling (existing capability, no changes required).
- Multi-currency refunds (deferred to Phase 2).

## 11. Glossary

<!--
Local glossary for terms specific to this initiative. The parser
attaches these to the corpus glossary so all generated stories can
reference them. Terms that already exist in the platform glossary
should not be redefined here — link to them instead.
-->

| Term | Definition |
| ---- | ---------- |
| Refund | A return of funds to a customer for a previously settled payment, partial or full. |
| Idempotency Key | A client-supplied unique identifier that ensures a request, if retried, produces the same result without duplicate side effects. |
| Terminal state | A refund state from which no further transitions occur: `completed`, `failed`, or `cancelled`. |
| Reason code | A structured enum value classifying why a refund was accepted or rejected, used for analytics and customer communication. |

## 12. Source References

<!--
Anchor every external reference here. Each becomes a citation
candidate that stories can use. The parser will warn if a story
cites a reference not listed here.
-->

| Reference ID | Type | Title / URL |
| ------------ | ---- | ----------- |
| ADR-018 | Architecture Decision | Platform Observability Standard |
| ADR-024 | Architecture Decision | Event Publishing Reliability |
| ADR-031 | Architecture Decision | API Versioning Conventions |
| ADR-042 | Architecture Decision | Idempotency Keys for State-Mutating Endpoints |
| DAT-PAY-014 | Data Dictionary | RefundRequest Schema |
| SYS-AUD-002 | System Catalog | Audit Log Sink |
| API-PAY-007 | API Catalog | Payments Service v2 |
| CRP-RES-RFD-001 | Customer Research | Refund UX Pain Points (2026 Q1 study) |
| REG-PCI-DSS-V4 | Regulation | PCI-DSS v4.0 Requirements |
| REG-SOX-404 | Regulation | SOX Section 404 |
