# Process Owner Guide

This guide is for the person responsible for a BPMN business process and its triple artifacts. As a process owner, you are the authority on how the process works, what rules govern it, and what changes are needed. The MDA Intent Layer translates your knowledge into structured artifacts that agents can execute.

## Your Role

You own the truth of how the business process works. Specifically:

- You decide what procedures, policies, and business rules apply to each task
- You review generated capsules for accuracy
- You approve changes to triples that affect your process
- You maintain the knowledge corpus documents that feed your process
- You triage and resolve gaps identified during ingestion
- You coordinate with tech leads and integration leads on intent specs and contracts

You do not need to write code, configure APIs, or understand the LLM pipeline. Your job is to make sure the content is right.

## Setting Up Your Process Repository

Each business process gets its own repository (or directory within a larger repo). Initialize it with:

```bash
mda init income-verification --domain "Mortgage Lending" --prefix IV
```

This creates a directory structure:

```
income-verification/
  bpmn/                  # Your BPMN diagram goes here
  triples/               # Generated capsule/intent/contract triples
  decisions/             # Triples for gateway/decision nodes
  graph/                 # Process flow graph visualization
  gaps/                  # Identified gaps and issues
  audit/                 # Ingestion and change logs
  mda.config.yaml        # Process configuration
  README.md
```

The `mda.config.yaml` file contains your process configuration. The key settings are:

```yaml
process:
  id: Process_IncomeVerification
  name: Income Verification
  domain: mortgage-underwriting

paths:
  bpmn: bpmn/
  triples: triples/
  decisions: decisions/
  corpus: ../../corpus        # Path to the shared knowledge corpus

naming:
  id_prefix: IV               # Used in capsule/intent/contract IDs
```

## Providing the BPMN File

Your BPMN file is the starting point for everything. Place it in the `bpmn/` directory.

**Where to get it**: Export from your process modeling tool (Camunda Modeler, Signavio, Bizagi, etc.) as a standard BPMN 2.0 XML file.

**Format**: Standard `.bpmn` XML. The file must contain:
- At least one process with a process ID
- Tasks with IDs and names (the names become triple names)
- Sequence flows connecting the tasks
- Gateways for decision points

**Placement**: Save the file as `bpmn/<process-name>.bpmn`:

```
bpmn/income-verification.bpmn
```

You can also add a metadata file alongside it at `bpmn/bpmn-metadata.yaml` with additional context:

```yaml
source_tool: "Camunda Modeler 5.x"
source_version: "2026-03-15"
exported_by: "Process Architecture Team"
```

## Running the Initial Ingestion

Once your BPMN file is in place, run the full ingestion pipeline:

```bash
mda ingest bpmn/income-verification.bpmn
```

The pipeline runs six stages:

```
Stage 1 (Parse):     Reads the BPMN XML and extracts nodes, edges, and structure
Stage 2 (Enrich):    Matches corpus documents to each task and identifies gaps
Stage 3 (Capsules):  Generates capsule documents for each task
Stage 4 (Intents):   Generates intent specs from each capsule
Stage 5 (Contracts): Generates integration contracts from each intent
Stage 6 (Validate):  Validates all generated artifacts against schemas
```

Example output:

```
Ingest: income-verification.bpmn

  Stage 1 (Parse): 12 nodes, 14 edges
  Stage 2 (Enrich): 3 gaps found
  Stage 3 (Capsules): 8 created
  Stage 4 (Intents): 8 created
  Stage 5 (Contracts): 8 created
  Stage 6 (Validate): 8/8 passed, 0 failed [pass]

  Total files created: 24

  3 gaps detected -- run 'mda gaps' for details

  Mode: LLM-assisted generation

Ingest complete
```

If you do not have an LLM API key configured, you can still run ingestion with template stubs:

```bash
mda ingest bpmn/income-verification.bpmn --skip-llm
```

This generates structurally correct but content-sparse triples that you can fill in manually.

## Understanding the Generated Output

After ingestion, your `triples/` and `decisions/` directories contain one subdirectory per BPMN task:

```
triples/
  receive-request/
    receive-request.cap.md           # Capsule
    receive-request.intent.md        # Intent spec
    receive-request.contract.md      # Contract
    triple.manifest.json             # Manifest linking the three files
  classify-employment/
    classify-employment.cap.md
    classify-employment.intent.md
    classify-employment.contract.md
    triple.manifest.json
  verify-w2/
    verify-w2.cap.md
    verify-w2.intent.md
    verify-w2.contract.md
    triple.manifest.json
  ...

decisions/
  employment-type/                   # Gateway/decision node triples
    employment-type.cap.md
    employment-type.intent.md
    employment-type.contract.md
    triple.manifest.json
```

### Reading a Capsule

The capsule (`.cap.md`) is the artifact you will work with most. It has YAML frontmatter with metadata and a Markdown body with the procedure.

**Frontmatter** -- Key fields to understand:

```yaml
capsule_id: "CAP-IV-W2V-001"          # Unique ID for this capsule
bpmn_task_id: "Task_VerifyW2"          # Links back to the BPMN task
bpmn_task_name: "Verify W-2 Income"    # Human-readable task name
status: "draft"                         # Lifecycle status
predecessor_ids:                        # What comes before this task
  - "CAP-IV-DEC-001"
successor_ids:                          # What comes after this task
  - "CAP-IV-QAL-001"
gaps:                                   # Issues identified during generation
  - type: "missing_detail"
    description: "OCR threshold not defined"
    severity: "low"
```

**Body** -- The procedure in Markdown. This is what you review for accuracy:

```markdown
# Verify W-2 Income

## Purpose
Validates the borrower's W-2 wage income by cross-referencing
employer-issued W-2 forms against IRS tax return transcripts.

## Procedure
1. Retrieve W-2 Documents...
2. Retrieve Tax Return Transcripts...
3. Cross-Reference W-2 to 1040...

## Business Rules
- Fannie Mae Selling Guide B3-3.1-01: ...

## Inputs
| Field | Source | Required |
|---|---|---|
| borrower_profile | Process Context | Yes |

## Outputs
| Field | Destination | Description |
|---|---|---|
| verifiedMonthlyIncome | Process Context | ... |
```

### Reading an Intent Spec

The intent spec (`.intent.md`) is the machine-readable contract with the executing agent. Key sections:

- **goal**: What the agent must accomplish
- **preconditions**: What must be true before the agent starts
- **invariants**: Rules that must never be violated during execution
- **success_criteria**: How to know the task succeeded
- **failure_modes**: What can go wrong and what to do about it
- **forbidden_actions**: What the agent must never do (always includes browser_automation, screen_scraping, ui_click)

You do not need to write intent specs, but you should review the goal and invariants to make sure they match your understanding of the business rules.

### Reading a Contract

The contract (`.contract.md`) defines how the task connects to real systems. Key sections:

- **sources**: APIs the task reads from (e.g., DocVault, LOS)
- **sinks**: APIs the task writes to
- **events**: Domain events the task publishes or consumes
- **audit**: What gets logged and for how long
- **binding_status**: Whether the endpoints are real (`bound`), placeholder (`unbound`), or partially connected (`partial`)

You do not need to configure APIs, but you should verify that the right systems are listed. If the contract says the task reads from DocVault but your team actually uses a different document system, flag it.

## Using the MkDocs Site

The MDA pipeline can generate a documentation website for your process. Generate and serve it with:

```bash
mda docs serve
```

This starts a local web server (default port 8000) where you can browse:

- Process overview and flow diagram
- All triples with their capsules, intents, and contracts
- Gap reports
- Corpus document index

This is the easiest way to navigate a large process with many triples.

To generate the docs without serving them:

```bash
mda docs generate
```

To build a static site you can host:

```bash
mda docs build
```

## Day-to-Day Workflows

### Updating a capsule when a procedure changes

When a business procedure changes (new regulatory guidance, updated SOP, process improvement), update the capsule directly:

1. Open the capsule file (e.g., `triples/verify-w2/verify-w2.cap.md`)
2. Update the procedure steps in the Markdown body
3. Update the business rules section if rules changed
4. Update `regulation_refs` or `policy_refs` in the frontmatter if citations changed
5. Increment the `version` field
6. Update `last_modified` and `last_modified_by`
7. Validate your changes:

```bash
mda validate triples/verify-w2/
```

8. Commit and open a PR for review

### Adding a new corpus document when you get a new SOP

When you receive a new standard operating procedure or policy:

1. Create the corpus document:

```bash
mda corpus add procedure --title "FHA Streamline Refinance" --domain "Mortgage Lending"
```

2. Fill in the frontmatter fields, especially `applies_to` with the process IDs and task name patterns that this document should match
3. Write the procedure content following the body section templates
4. Set the status to `draft` initially
5. Validate the document:

```bash
mda corpus validate
```

6. Rebuild the corpus index:

```bash
mda corpus index
```

7. When ready for production, change status to `current`

### Handling gaps

Gaps are identified during ingestion when the pipeline cannot find enough information to generate complete artifacts. Review gaps with:

```bash
mda gaps
```

Filter to see only the urgent ones:

```bash
mda gaps --severity critical
```

For each gap, you have three options:

**Resolve it**: Write a corpus document that fills the gap, update the capsule, and remove the gap entry. For example, if the gap says "No procedure found for gig economy income verification," write a new procedure corpus document for gig economy workers.

**Accept it**: If the gap is low severity and does not block execution, you can leave it in place. Add a note explaining why it is acceptable. For example, an OCR confidence threshold is a configuration detail that can be set during implementation.

**Escalate it**: If the gap reveals a fundamental process issue (e.g., your BPMN has a task for something nobody does), escalate to the process architecture team for resolution.

### When the BPMN changes upstream

If your process modeling team updates the BPMN diagram, you need to re-ingest it. First, see what changed:

```bash
mda reingest bpmn/income-verification.bpmn
```

This compares the new BPMN with your existing triples and shows a diff:

```
Reingest: income-verification.bpmn
  New model: 14 nodes, 16 edges

  Diff
  Task ID                    Name                    Status
  Task_VerifyW2              Verify W-2 Income       unchanged
  Task_VerifySelfEmployment  Verify Self-Employment  unchanged
  Task_VerifyRental          Verify Rental Income    ADDED
  Task_OldManualCheck        Manual Check            REMOVED

  Added: 1, Removed: 1, Unchanged: 6
  Run 'mda ingest' with --stages=1,2,3,4,5 to generate triples for new tasks
  Removed tasks still have triples on disk -- review and delete manually
```

For added tasks, run ingestion for the new tasks. For removed tasks, manually review and delete the orphaned triple directories after confirming the task is truly gone.

To force a full regeneration of all triples:

```bash
mda reingest bpmn/income-verification.bpmn --force
```

### Reviewing status

Get a summary of all your triples and their current state:

```bash
mda status
```

This shows each triple with the status of its capsule, intent, and contract, plus the number of open gaps.

## Working with the Knowledge Corpus

### Which corpus docs feed your capsules

Each capsule's frontmatter includes `corpus_refs` or `regulation_refs` and `policy_refs` that trace back to corpus documents. During enrichment, the pipeline matches corpus documents to tasks based on the `applies_to` metadata.

To see which corpus documents match a specific task, search the corpus:

```bash
mda corpus search "w-2 verification"
```

```
Search: 'w-2 verification' (4 results)

  Results
  ID              Type       Title                                Status
  CRP-PRC-IV-001  procedure  W-2 Income Verification Procedure    current
  CRP-RUL-IV-001  rule       Employment Type Classification Rules current
  CRP-POL-IV-001  policy     W-2 Verification Policy              current
  CRP-DAT-IV-001  data-dict  Income Verification Data Objects     current
```

### Adding process-specific procedures

If your process has a unique procedure that does not exist in the shared corpus, create it:

```bash
mda corpus add procedure --title "Verbal VOE Follow-Up Procedure" --domain "Mortgage Lending"
```

Make sure to set `applies_to.task_name_patterns` to match the specific BPMN tasks where this procedure applies:

```yaml
applies_to:
  process_ids:
    - "Process_IncomeVerification"
  task_name_patterns:
    - "verbal.*voe"
    - "verify.*employment"
```

### Requesting regulation summaries

If you need a regulation summary that does not exist yet (for example, a new agency guideline), create a regulation corpus document:

```bash
mda corpus add regulation --title "FHA Mortgagee Letter 2026-01 Summary" --domain "Mortgage Lending"
```

Fill in the expected sections (Regulation Summary, Applicability, Key Requirements, Compliance Obligations, Penalties and Enforcement, Source References) and reference it from any procedures or rules that depend on it.

## Git Workflow

### Clone, branch, edit, PR, merge

The standard workflow for making changes:

```bash
# Get the latest code
git pull origin main

# Create a branch for your changes
git checkout -b update/w2-trending-thresholds

# Make your edits to corpus docs and/or capsules
# ...

# Validate your changes
mda validate
mda corpus validate

# Stage and commit
git add corpus/procedures/w2-income-verification.corpus.md
git add triples/verify-w2/verify-w2.cap.md
git commit -m "Update W-2 trending thresholds per 2026 Fannie Mae guidance

Updated declining income thresholds from 15% to 10% per
Fannie Mae Selling Guide update effective 2026-03-01.
Updated both the corpus procedure and the verify-w2 capsule."

# Push and create PR
git push -u origin update/w2-trending-thresholds
```

### What to put in your commit messages

Be specific about what changed and why:

- What document(s) were modified
- What content changed (new step, updated threshold, added regulation)
- Why it changed (new regulatory guidance, process improvement, gap resolution)

**Good**:
```
Update verbal VOE timing requirement from 10 to 5 business days

POL-IV-004 updated to require verbal VOE within 5 business days
of closing (was 10). Updated corpus procedure and verify-w2 capsule
Step 5.4 to reflect new timing.
```

**Bad**:
```
Updated files
```

### Who reviews your changes

- **Corpus documents** (procedures, policies, rules): Reviewed by another SME or the compliance team
- **Capsules**: Reviewed by the process owner (you may be reviewing your own, which is fine for minor updates) plus a tech lead
- **Intent specs**: Reviewed by a tech lead
- **Contracts**: Reviewed by the integration lead
- **Any change touching regulation_refs**: Must include compliance review

## Getting Help

### Check your work

```bash
# Validate all triples against schemas
mda validate

# Validate corpus documents
mda corpus validate

# Get LLM-assisted quality review of a specific triple
mda review triples/verify-w2/
```

### See what needs attention

```bash
# Overall status of all triples
mda status

# All gaps across the project
mda gaps

# Only critical gaps that need immediate attention
mda gaps --severity critical

# Search the corpus for relevant documents
mda corpus search "appraisal"
```

### Common situations and what to do

| Situation | What to Do |
|-----------|-----------|
| New SOP received from operations | Create a corpus procedure document, rebuild the index, re-ingest if it affects existing tasks |
| Regulatory guidance changed | Update the regulation corpus document, update affected procedures, update affected capsules |
| BPMN diagram updated | Run `mda reingest` to see the diff, generate triples for new tasks, clean up removed tasks |
| Gap report shows critical gaps | Write corpus documents to fill the gaps, or update existing documents with missing detail |
| Capsule procedure is wrong | Edit the capsule `.cap.md` file directly, validate, and open a PR |
| Need to add a new income type | Add a classification rule to the rules corpus doc, add a verification procedure, re-ingest |
| Not sure what corpus docs exist | Run `mda corpus search` with relevant keywords |
| Validation fails | Read the error messages carefully, fix the indicated fields, run validation again |
