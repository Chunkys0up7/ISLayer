# From Specification to Delivery — How It Works

## An Executive Overview

| Field        | Value                                                |
| ------------ | ---------------------------------------------------- |
| **Audience** | Executive leadership, product sponsors, programme owners |
| **Status**   | Draft                                                |
| **Created**  | 2026-04-27                                           |
| **Companion**| `SPEC-TO-JIRA-DESIGN.md` (technical detail)          |

---

## The Idea in One Sentence

We turn a product specification — a PRD, a plan, a strategy doc — into a fully scoped, traceable, ready-to-build set of JIRA stories, with every requirement linked back to the document it came from and to the engineering standards that govern it.

---

## The Problem We're Solving

Most organisations lose time and accuracy in three places between strategy and code:

| Where the slip happens | What it costs |
| --- | --- |
| **Spec → Backlog** — A product manager writes a 30-page PRD. Engineering reads it, interprets it, and creates JIRA stories. Different people interpret it differently. Acceptance criteria drift from the original intent. | Weeks of clarification meetings; rework when "that's not what I meant" surfaces in QA or UAT |
| **Backlog → Standards** — Each new story needs to comply with architectural standards, security policies, API conventions, and regulatory requirements. Engineers either look these up themselves or skip them. | Late-stage rework, security review failures, inconsistent APIs, compliance findings |
| **Backlog → Audit Trail** — When a regulator or auditor asks "why did you build it this way?", the trail from the original spec to the code is lost in JIRA comments and email threads. | Weeks of forensic effort; sometimes findings that lead to rebuild |

This system addresses all three by making the path from spec to delivery **deterministic, traceable, and grounded**.

---

## How It Works — The Plain-English Walkthrough

### Step 1 — A Specification Comes In

A product manager produces a PRD — markdown, Word, Confluence, doesn't matter. They describe the product, the user stories, the goals, the constraints.

### Step 2 — The System Decomposes It

The system reads the spec and identifies:

- The overall **Initiative** (becomes a JIRA Epic)
- Each individual **Story** that needs to be built
- The **Dependencies** between stories (what must happen before what)
- The **Owning Team** for each story (from team mentions in the doc)
- The **Data and APIs** referenced (linked to the API catalog)

Crucially, every identified story carries a pointer back to **the exact paragraphs of the PRD** it came from. Nothing is invented.

### Step 3 — The System Adds Engineering Context

For each story, the system searches your **engineering knowledge base** — architecture decisions, API specs, runbooks, coding standards, security policies — and attaches the relevant ones.

A story like "Add a refunds API endpoint" automatically gets linked to:

- The architecture decision record on idempotency
- The API versioning standard
- The PCI-DSS compliance requirements for payment APIs
- The deployment runbook for the payments service
- The refund object schema in the API catalog

The engineer doesn't have to hunt for these. They appear in the story.

### Step 4 — The System Writes the Stories

For each work unit identified, the system produces three linked artifacts:

1. **A Knowledge Capsule** — what to do and why, with every claim citing a source document
2. **An Intent Specification** — the Definition of Done and acceptance criteria
3. **An Integration Contract** — the technical sub-tasks (APIs to call, events to emit, audit logs to write)

These map cleanly to JIRA: Capsule + Intent become a Story; the Contract becomes its Sub-tasks.

### Step 5 — The System Verifies Itself

Before anything reaches JIRA, the system checks its own work:

- Every factual statement must trace to a source — either the original PRD or an engineering standard
- Anything that cannot be traced is flagged as a **Gap** and made visible
- Stories that cannot be grounded are labelled as needing clarification — not silently fabricated

### Step 6 — The System Synchronises with JIRA

The Epic, Stories, and Sub-tasks are created in JIRA with:

- Acceptance criteria pre-populated
- Dependencies linked (`blocks` / `blocked by`)
- Compliance and architectural references attached
- Open questions surfaced as visible flags
- A bi-directional link between the JIRA story and its source paragraphs in the PRD

### Step 7 — The Spec Changes? Re-Run It

When the PM updates the PRD, the system re-reads it and:

- Updates the description of stories where the source has changed
- Creates new stories for newly added scope
- Marks stories as "removed from spec" if the corresponding section was deleted
- Leaves untouched anything the team has manually marked as protected (sprint assignment, story points, current status)

The team still owns the work; the system owns the **traceability**.

---

## What Makes This Different

### It Doesn't Hallucinate

Every requirement, every acceptance criterion, every architectural reference traces to a specific source. If the system can't find a source for something, it flags it as a gap rather than inventing one. This is a property the system **enforces with automated verification**, not a hope.

### It Bridges Product and Engineering Knowledge

The same engine that reads your PRD also reads your architecture decisions, runbooks, and API specs. When it generates a story, it brings the relevant engineering context with it — no separate lookup required.

### It Produces an Audit Trail by Default

When asked "why was this built this way?", the trail is already there: the JIRA story links to the spec paragraphs and to the engineering standards that governed the work. No reconstruction needed.

### It Re-runs Cleanly

Specs evolve. The system is built so that re-running it after a spec change produces a clean diff in JIRA — only the affected stories change. There is no risk of overwriting the team's own working state (sprint, points, status); those are protected by configuration.

### It Makes Gaps Visible

The most valuable output is often what the system **cannot** do. If a PRD says "the system shall be performant" with no specifics, the resulting story is flagged as ungrounded and surfaces as an open question. This is a feature, not a failure: it forces clarity earlier in the cycle.

---

## What Stays Human

The system is deliberately **not** trying to replace product managers, engineers, architects, or delivery managers. It does not:

- Decide what to build
- Estimate effort or assign sprints
- Approve releases
- Resolve trade-offs between competing goals
- Replace conversation between PM and engineering

It does:

- Free those people from spending half their time on translation work
- Make sure the translation, when it happens, is consistent and traceable
- Surface ambiguity early, when it's cheap to resolve

---

## The Operating Model

### Roles

| Role | What They Do | What Changes With This System |
| --- | --- | --- |
| **Product Manager** | Writes PRDs, defines scope | Same — but their PRD becomes the canonical, audit-ready source |
| **Architect / Tech Lead** | Authors engineering standards (ADRs, API specs, runbooks) | Same — but their work is now **automatically applied** to every story |
| **Engineering Manager** | Plans sprints, assigns work, tracks progress | Same — but they receive pre-scoped stories with pre-attached context |
| **Engineer** | Builds the feature | Same — but they spend less time hunting for context and more time building |
| **Compliance / Risk** | Reviews releases for adherence | Same — but they have an audit trail by default |

### Cadence

- **Continuous**: As PRDs are updated, the pipeline re-runs and JIRA updates within minutes
- **Per-release gate**: Compliance review uses the auto-generated audit trail
- **Per-quarter**: Engineering standards (the corpus) are reviewed and refreshed; coverage gaps surfaced by the system drive corpus authoring

---

## What Has to Be in Place

| Prerequisite | What's Needed | Effort |
| --- | --- | --- |
| **Engineering knowledge corpus** | Architecture decisions, API specs, runbooks, standards documented in markdown | High up-front, then incremental |
| **Spec authoring discipline** | PRDs structured with consistent sections (goals, stories, acceptance criteria) | Low — most teams already do this |
| **JIRA project structure** | Epic / Story / Sub-task hierarchy, custom fields for traceability | Low |
| **Inside-firewall LLM access** | A vetted LLM provider (cloud or self-hosted) | Depends on existing posture |

The corpus is the most significant prerequisite — and also the most reusable asset. Every PRD that flows through the system benefits from a richer corpus, and every gap the system surfaces drives corpus growth.

---

## Why It Works

The technical foundation already exists in the MDA Intent Layer:

- A **grounding verification system** that ensures every output is traceable to a source
- A **multi-signal corpus matching engine** that finds relevant standards for each work unit
- A **schema-enforced output pipeline** that produces consistent, structured artifacts
- A **gap-detection mechanism** that makes missing information visible rather than fabricated

These were built originally for regulated business processes (think mortgage underwriting, healthcare workflows). They translate naturally to product engineering because the underlying problem is the same: take a structured input, ground every output in source material, produce an auditable trail, never hallucinate.

The extension to specs and JIRA is, in architectural terms, replacing one input parser (BPMN) with another (PRD prose) and adding one output target (JIRA) alongside the existing ones (markdown, docs site, git). The trustworthy core stays the same.

---

## What Success Looks Like

After 3 months of running on real specs, we expect to see:

| Metric | Today (typical) | With the system |
| --- | --- | --- |
| Time from PRD signoff to JIRA backlog ready | 1-2 weeks | 1-2 hours |
| Acceptance-criteria rewrite cycles | 2-4 per story | 0-1 per story |
| Compliance/audit findings per release | Variable, often surprising | Predictable; gaps known up front |
| Engineering time on standards lookup | ~10% per story | <2% per story |
| Audit trail reconstruction time when asked | Days to weeks | Immediate |

These are not promises — they are the targets the system is built to make achievable. The actual numbers depend on corpus maturity and PRD quality.

---

## What to Decide

The technical work to extend the system from BPMN to PRD/JIRA is scoped at roughly 14-16 engineer-weeks (see `SPEC-TO-JIRA-DESIGN.md` for the milestone breakdown). The decisions for executive sponsorship are:

1. **Pilot scope** — Which product area runs the first end-to-end pilot? A team with mature engineering standards and an upcoming feature spec is the ideal candidate
2. **Corpus investment** — Who owns the initial engineering corpus? Architecture, principal engineers, and platform teams typically lead this
3. **JIRA configuration** — Custom fields for traceability (Triple ID, Evidence Links, Spec Grounded?) need to be configured once per project
4. **LLM choice** — Inside-firewall LLM access: cloud provider, self-hosted, or both
5. **Governance** — How are protected JIRA fields agreed (Sprint, Points, Status), and how are PRD-format conventions enforced

A pilot of 4-6 weeks on a single product area, against an existing PRD, will demonstrate the operating model end-to-end and reveal the genuine integration costs versus the projected savings.

---

## In Summary

The system exists to remove the most expensive and error-prone step in software delivery: the human translation of a specification into a structured, traceable, standards-aware engineering backlog. It does this by treating that translation as a deterministic, auditable, re-runnable pipeline — and by refusing to invent anything it cannot trace to a source.

The result is faster cycle times, fewer rewrite cycles, predictable compliance posture, and an audit trail that exists by default rather than by reconstruction.

It does not replace people. It removes the part of their work that wastes their time.
