# Spec Template — Author's Guide

## What This Template Is

`spec.template.md` is the optimal input format for the MDA Intent Layer
spec-to-JIRA pipeline. Filling in this template gives you the highest-quality
output: clean story extraction, accurate JIRA hierarchy, attached architectural
standards, and a verifiable provenance trail from each JIRA story back to the
specific paragraphs of the spec it came from.

You do not have to use this template. The parser will work on any reasonably
structured PRD. But this template removes ambiguity — it tells the parser
exactly where to find each piece of information, so you get fewer
"gap flagged" warnings and fewer ambiguous stories.

## How to Use It

1. Copy `spec.template.md` to your spec repository, e.g.
   `specs/payments-refunds.spec.md`.
2. Fill in the frontmatter (top of file) with the initiative's metadata.
3. Walk through each numbered section in order. Skip sections that don't
   apply by deleting them entirely — do not leave empty headings.
4. Run `mda parse-spec specs/payments-refunds.spec.md` to validate it.
5. Address any gaps the parser flags.
6. Run `mda jira sync` to push the resulting Epic + Stories to JIRA.

## The Twelve Sections at a Glance

| # | Section | What It Drives | Skippable? |
| - | ------- | -------------- | ---------- |
| 1 | Background and Context | Epic description; story-level context | No |
| 2 | Goals and Success Metrics | Epic Definition of Done | No |
| 3 | Stakeholders and Teams (Lanes) | Story owner_team assignments | No |
| 4 | Data Objects and APIs | Data dictionary entries; API catalog matches | If no APIs |
| 5 | Cross-Cutting Concerns | Auto-applied to every story | If genuinely none |
| 6 | Stories | The JIRA stories themselves | No — this is the point |
| 7 | Decision Points | Decision stories + job aid YAMLs | If no runtime branches |
| 8 | Risks and Mitigations | Epic-level risk register | Optional |
| 9 | Open Questions | Flagged gaps on Epic | If genuinely none |
| 10 | Out of Scope | Scope-drift detection | Recommended |
| 11 | Glossary | Local term definitions | Optional |
| 12 | Source References | Citation candidates for stories | If no external refs |

## Anti-Patterns to Avoid

### Don't bury stories in long prose

The parser looks for `### [STORY-XXX]` headings inside section 6. If your
stories are described in flowing paragraphs without explicit headings, the
parser cannot identify discrete work units.

**Bad**:
> The payments team will need to define the refund schema, then build the
> API endpoint, then add audit logging, then configure the gateway...

**Good**: Each item gets its own H3 heading with a stable ID and a structured
frontmatter block.

### Don't infer dependencies from order

Even if STORY-002 appears after STORY-001 in the document, the parser will
not assume STORY-002 depends on STORY-001. Use the `depends_on` field
explicitly.

**Bad**:
> First we'll define the schema, then we'll implement the endpoint.

**Good**:
```
depends_on: ["STORY-001"]
```

### Don't write unmeasurable acceptance criteria

The grounding verifier flags acceptance criteria that cannot be tested.

**Bad**:
> The system shall be performant.

**Good**:
> Given 100 concurrent requests, when the endpoint is called, then p99
> latency is under 500ms.

### Don't reference standards that aren't in section 12

If you cite ADR-042 in a story but ADR-042 is not listed in the
"Source References" section, the parser flags it as an unverifiable
citation.

### Don't change story IDs across revisions

Story IDs are the anchor for JIRA sync. If you renumber STORY-003 to
STORY-005 in a later revision, the system will treat it as a deleted
story and a new story — leading to duplication or data loss in JIRA.

**Append new stories at the end. Mark removed ones with status `removed`,
don't delete the heading.**

## What Happens at Parse Time

When you run `mda parse-spec`, the parser:

1. **Reads the frontmatter** → creates the Epic skeleton
2. **Extracts background** → populates Epic description with paragraph provenance
3. **Extracts goals** → populates Epic success criteria
4. **Reads lanes** → builds the team assignment lookup
5. **Reads data objects** → matches against the API catalog corpus
6. **Reads cross-cutting concerns** → propagates to every story
7. **For each story**:
   - Parses frontmatter into structured fields
   - Extracts acceptance criteria
   - Resolves dependencies against other story IDs
   - Records source paragraph numbers
8. **For each decision point**:
   - Parses the decision matrix
   - Generates a job aid YAML stub
9. **Validates** — every story has owner, every dep resolves, every reference is in section 12
10. **Verifies grounding** — every claim traces to a paragraph or a section-12 reference

## What Happens at JIRA Sync Time

When you run `mda jira sync`:

1. The Epic is created (or updated, if `jira_epic_key` is set).
2. Each story creates or updates a JIRA Story under the Epic.
3. Each contract source/sink/event creates a Sub-task under the Story.
4. Dependencies become `blocks` / `blocked by` links.
5. Cross-cutting concerns appear in every story description.
6. Open questions become custom-field flags.
7. The sync is idempotent — re-running on unchanged content is a no-op.

## Tuning the Template for Your Organisation

This template is a starting point. Common adaptations:

- **Add organisation-specific frontmatter fields** (cost centre, programme,
  business unit) — extend the frontmatter block; update the JIRA field
  mapping in `mda.config.yaml > jira > custom_field_mapping`.
- **Add additional lane attributes** (cost code, on-call rota) — extend
  the lanes table; extend the parser's lane schema.
- **Add organisation-specific cross-cutting concerns** — add them to
  section 5 once and they propagate to every story automatically.
- **Reference your own corpus IDs** — replace ADR-018 etc. with your
  actual architecture decision identifiers.

## Related Documents

- `SPEC-TO-JIRA-DESIGN.md` — full technical specification for the parser
  and sync pipeline
- `SPEC-TO-JIRA-EXECUTIVE.md` — executive overview for sponsors
- `GROUNDING-AGENT-SPEC.md` — how the grounding verification works
- `EXECUTION-SPEC.md` — overall MDA Intent Layer architecture
