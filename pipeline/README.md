# MDA Intent Layer Pipeline

The pipeline transforms a BPMN 2.0 XML process definition into a set of **triples** -- one capsule, one intent specification, and one integration contract per actionable BPMN element.

## Input / Output

| | |
|---|---|
| **Input** | A single BPMN 2.0 XML file describing one or more business processes |
| **Output** | A set of triples: `.cap.md` + `.intent.md` + `.contract.md` per task |

Each stage takes the output of the previous stage. Stages can be executed manually (by a human following the instructions) or automated (by an AI agent or script).

## Pipeline Flow

```
                        BPMN 2.0 XML
                             |
                             v
                +--------------------------+
                |  Stage 1: BPMN Parser    |
                |  (stage-1-parser.md)     |
                +--------------------------+
                             |
                     Parsed object model
                       (YAML / JSON)
                             |
                             v
                +--------------------------+
                |  Stage 2: Corpus         |
                |  Enricher                |
                |  (stage-2-enricher.md)   |
                +--------------------------+
                             |
                  Enriched model + gap list
                             |
              +--------------+--------------+
              |              |              |
              v              v              v
  +----------------+ +----------------+ +----------------+
  | Stage 3:       | | Stage 4:       | | Stage 5:       |
  | Capsule Gen    | | Intent Gen     | | Contract Gen   |
  | (stage-3-...)  | | (stage-4-...)  | | (stage-5-...)  |
  +----------------+ +----------------+ +----------------+
              |              |              |
         .cap.md        .intent.md     .contract.md
              |              |              |
              +--------------+--------------+
                             |
                        Triple set
                             |
                             v
                +--------------------------+
                |  Stage 6: Triple         |
                |  Validator               |
                |  (stage-6-validator.md)  |
                +--------------------------+
                             |
                     Validation report
                      (PASS / FAIL)
```

> **Note:** Stages 3, 4, and 5 all read from the enriched model produced by Stage 2. Stage 4 also reads capsules from Stage 3 for cross-referencing. Stage 5 also reads intent specs from Stage 4. In practice they run sequentially: 3 then 4 then 5.

## Stage Summary

| Stage | Name | Input | Output |
|-------|------|-------|--------|
| 1 | BPMN Parser | BPMN 2.0 XML | Typed object model (YAML/JSON) |
| 2 | Corpus Enricher | Parsed model | Enriched model + gap list |
| 3 | Capsule Generator | Enriched model | `.cap.md` files |
| 4 | Intent Generator | Enriched model + capsules | `.intent.md` files |
| 5 | Contract Generator | Enriched model + intents | `.contract.md` files |
| 6 | Triple Validator | All triples | Validation report |

## Key References

- **Element mapping**: `ontology/bpmn-element-mapping.yaml` -- defines which BPMN elements produce which triple components and their default goal types
- **ID conventions**: `ontology/id-conventions.yaml` -- naming rules for capsule, intent, and contract IDs
- **Status lifecycle**: `ontology/status-lifecycle.yaml` -- allowed statuses, transitions, and required fields per status
- **Goal types**: `ontology/goal-types.yaml` -- allowed values for `goal_type` in intent specifications
- **Schemas**: `schemas/capsule.schema.json`, `schemas/intent.schema.json`, `schemas/contract.schema.json` -- JSON Schema for frontmatter validation

## Execution Modes

**Manual execution.** A human reads each stage document and performs the described steps, using the BPMN XML and any available knowledge base as inputs.

**Agent execution.** An AI agent receives the stage document as its prompt, along with the required inputs, and produces the required outputs. Each stage is a self-contained instruction set.

**Automated pipeline.** A script or orchestrator chains the stages together, passing outputs forward. The validator at the end determines whether the pipeline run succeeded.
