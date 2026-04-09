# Stage 5: Contract Generator

**Input:** Enriched model from Stage 2 + Intent specs from Stage 4
**Output:** `.contract.md` files (one per eligible BPMN element)

---

## Overview

Generate an Integration Contract for each BPMN element that has a paired intent spec. Each contract is a markdown file with YAML frontmatter conforming to `schemas/contract.schema.json`. Contracts define the platform-specific bindings -- which systems, APIs, protocols, and schemas are needed to fulfill the intent.

In MDA terms, the intent spec is the Platform-Independent Model (PIM) and the contract is the Platform-Specific Model (PSM).

## Prerequisites

- Enriched BPMN model (output of Stage 2)
- Generated intent specs (output of Stage 4)
- Enterprise API catalog or service registry (if available)
- `schemas/contract.schema.json` -- frontmatter validation schema

## Instructions

### Step 1: Identify Contract-Eligible Nodes

Every node that produced an intent spec in Stage 4 also produces a contract. Use the same set of nodes.

### Step 2: Generate Contract ID

Use the same ID stem as the paired capsule and intent:

```
ICT-{domain_code}-{subdomain_code}-{sequence_number}
```

If the intent is `INT-MO-INC-001`, the contract is `ICT-MO-INC-001`.

### Step 3: Resolve Sources

For each `input` in the paired intent spec, attempt to bind it to a concrete data source:

1. **Look up the source system** in the enterprise API catalog or service registry
2. **If found**, populate a source entry:

```yaml
sources:
  - name: "Tax Return Data"
    protocol: rest          # rest | grpc | graphql | soap | jdbc | file | message_queue
    endpoint: "https://api.internal/v2/tax-returns/{ssn}"
    auth: "oauth2"
    schema_ref: "schemas/tax-return-response.json"
    sla_ms: 2000
```

3. **If not found**, add the input name to `unbound_sources`:

```yaml
unbound_sources:
  - "Tax Return Data"
```

**Protocol selection guidance:**

| Indicator | Protocol |
|-----------|----------|
| RESTful API, HTTP endpoints | `rest` |
| gRPC service definitions | `grpc` |
| GraphQL schema available | `graphql` |
| Legacy WSDL/SOAP services | `soap` |
| Direct database access | `jdbc` |
| File-based integration (SFTP, S3) | `file` |
| Event-driven, Kafka, MQ | `message_queue` |

### Step 4: Resolve Sinks

For each `output` in the paired intent spec, attempt to bind it to a concrete data sink:

1. **Look up the sink system** in the enterprise catalog
2. **If found**, populate a sink entry:

```yaml
sinks:
  - name: "Verified Income Record"
    protocol: rest
    endpoint: "https://api.internal/v2/income-verification"
    auth: "oauth2"
    schema_ref: "schemas/income-record.json"
    sla_ms: 1000
    idempotency_key: "application_id + verification_date"
```

3. **If not found**, add to `unbound_sinks`:

```yaml
unbound_sinks:
  - "Verified Income Record"
```

### Step 5: Define Events

For each notification, state change, or inter-process signal:

```yaml
events:
  - topic: "loan.income.verified"
    schema_ref: "schemas/events/income-verified.json"
    delivery: at_least_once   # at_least_once | at_most_once | exactly_once
    key_field: "application_id"
```

Sources of events:
- Boundary events on the BPMN task
- Message flows in the collaboration
- SendTask / ReceiveTask semantics
- State transition outputs that other processes might observe

### Step 6: Define Rule Engines

If the paired intent spec involves decision logic and a rule engine is available:

```yaml
rule_engines:
  - name: "DTI Threshold Engine"
    version: "2.1"
    endpoint: "https://rules.internal/v1/dti-check"
```

### Step 7: Define Audit Requirements

Based on the process domain, regulatory context from enrichment, and organizational policy:

```yaml
audit:
  record_type: "income_verification_audit"
  retention_years: 7
  fields_required:
    - "application_id"
    - "agent_id"
    - "timestamp"
    - "input_hash"
    - "output_hash"
    - "decision_rationale"
  sink: "https://audit.internal/v1/records"
```

**Default retention periods by domain:**

| Domain | Default retention |
|--------|------------------|
| Financial / lending | 7 years |
| Healthcare | 10 years |
| General business | 3 years |
| Compliance-critical | 10 years |

### Step 8: Set Binding Status

Evaluate the completeness of bindings:

| Status | Condition |
|--------|-----------|
| `bound` | All sources and sinks are resolved to concrete endpoints |
| `partial` | Some sources or sinks are resolved, others are in `unbound_*` arrays |
| `unbound` | No sources or sinks are resolved to concrete endpoints |

```yaml
binding_status: partial
```

### Step 9: Write the Markdown Body

After the frontmatter `---` delimiter, write these sections:

#### Binding Rationale

Explain the integration decisions:

```markdown
## Binding Rationale

This contract binds the [intent description] to the following systems:

- **[Source/Sink name]**: Selected because [reason]. Protocol [X] was chosen
  because [reason]. SLA of [N]ms is based on [source].

### Unbound Integrations

The following integrations could not be resolved:

- **[Unbound name]**: [Why it is unbound and what is needed to resolve it]
```

#### Change Protocol

Define how changes to this contract should be managed:

```markdown
## Change Protocol

1. **Source/Sink endpoint changes**: Update the endpoint in this contract,
   bump the MINOR version, submit for review.
2. **Schema changes**: Coordinate with the upstream/downstream team.
   Breaking changes require a MAJOR version bump.
3. **Protocol changes**: Require a new contract version and review of
   the intent spec's execution boundaries.
4. **SLA changes**: Update `sla_ms`, notify dependent teams,
   bump MINOR version.
```

#### Decommissioning

Define what happens when this contract is no longer needed:

```markdown
## Decommissioning

Before decommissioning this contract:

1. Verify no active intent specs reference `ICT-XX-YYY-NNN`
2. Ensure audit records have been retained per retention policy
3. Notify downstream consumers of the deprecation timeline
4. Set status to `deprecated`, wait for the retention period, then `archived`
```

## Demo / Greenfield Mode

When no enterprise API catalog exists (e.g., first-time setup or demo scenarios):

1. Generate **plausible REST endpoints** based on the task domain and data objects:
   ```yaml
   sources:
     - name: "Loan Application"
       protocol: rest
       endpoint: "https://api.example.com/v1/applications/{id}"
       auth: "oauth2"
       schema_ref: "schemas/loan-application.json"
       sla_ms: 500
   ```

2. Set `binding_status: "unbound"` regardless of how plausible the endpoints look

3. Add a note in the Binding Rationale:
   ```markdown
   > **Note:** All endpoints in this contract are illustrative placeholders
   > generated during initial pipeline execution. They must be replaced with
   > actual enterprise endpoints before this contract can advance past `draft` status.
   ```

## Output File Naming

Each contract is written to:

```
triples/{process_id}/{contract_id}.contract.md
```

## Validation Before Output

Before writing each contract file, verify:

1. `contract_id` matches the pattern `^ICT-[A-Z]{2,3}-[A-Z]{3}-\d{3}$`
2. All required frontmatter fields are present per `schemas/contract.schema.json`
3. `intent_id` references an existing intent spec from Stage 4
4. ID stem matches across the triple (CAP/INT/ICT)
5. Every source and sink has at minimum `name`, `protocol`, and `endpoint`
6. `binding_status` accurately reflects the state of `unbound_sources` and `unbound_sinks`
7. `mda_layer` is set to `"PSM"`
8. YAML frontmatter parses without error
