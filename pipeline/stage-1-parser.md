# Stage 1: BPMN Parser

**Input:** BPMN 2.0 XML file
**Output:** Typed object model (YAML or JSON)

---

## Overview

Parse a BPMN 2.0 XML file into a structured, typed object model that downstream stages can consume without needing to understand XML. The output captures the full process graph -- nodes, edges, lanes, data objects, and message flows.

## Prerequisites

- The element mapping table at `ontology/bpmn-element-mapping.yaml`
- A BPMN 2.0 compliant XML file

## Instructions

### Step 1: Parse the XML

Load the BPMN XML and validate it against the BPMN 2.0 namespace (`http://www.omg.org/spec/BPMN/20100524/MODEL`). If the namespace is missing or the XML is malformed, halt with error `PARSE_ERR_MALFORMED_XML` and include the parser error message.

### Step 2: Extract Process Metadata

For each `<bpmn:process>` or `<bpmn:participant>` element, extract:

| Field | Source |
|-------|--------|
| `process_id` | `<process id="...">` attribute |
| `process_name` | `<process name="...">` attribute |
| `is_executable` | `<process isExecutable="...">` attribute |
| `participant_id` | `<participant id="...">` in the collaboration |
| `participant_name` | `<participant name="...">` in the collaboration |

If a collaboration element exists, map participants to their processes via `processRef`.

### Step 3: Extract Nodes

For every element listed in `ontology/bpmn-element-mapping.yaml`, extract:

| Field | Description |
|-------|-------------|
| `id` | The element's `id` attribute |
| `name` | The element's `name` attribute (may be null) |
| `type` | The BPMN element type (e.g., `userTask`, `exclusiveGateway`, `startEvent`) |
| `lane` | The lane ID containing this element (resolved from `<laneSet>`) |
| `incoming` | Array of incoming sequence flow IDs |
| `outgoing` | Array of outgoing sequence flow IDs |
| `boundary_events` | Array of boundary event IDs attached to this element (`attachedToRef`) |
| `documentation` | Contents of any `<bpmn:documentation>` child element |
| `attributes` | Map of additional element-specific attributes (e.g., `implementation`, `scriptFormat`, `calledElement`) |

For gateways, also extract:
- `gateway_direction` (converging, diverging, mixed, unspecified)
- `default` flow ID if present

For events, also extract:
- `event_definitions` -- array of event definition types (e.g., `timerEventDefinition`, `errorEventDefinition`, `messageEventDefinition`) with their attributes

### Step 4: Extract Edges

For each `<bpmn:sequenceFlow>`:

| Field | Description |
|-------|-------------|
| `id` | The flow's `id` attribute |
| `name` | The flow's `name` attribute (may be null) |
| `source` | `sourceRef` attribute -- the originating node ID |
| `target` | `targetRef` attribute -- the destination node ID |
| `condition_expression` | Contents of `<bpmn:conditionExpression>` child, if present |

### Step 5: Extract Lanes and Participants

From each `<bpmn:laneSet>`:

| Field | Description |
|-------|-------------|
| `lane_id` | The lane's `id` attribute |
| `lane_name` | The lane's `name` attribute |
| `flow_node_refs` | Array of node IDs belonging to this lane |

### Step 6: Extract Data Objects and Data Stores

For each `<bpmn:dataObjectReference>` and `<bpmn:dataStoreReference>`:

| Field | Description |
|-------|-------------|
| `id` | Reference ID |
| `name` | Reference name |
| `type` | `dataObject` or `dataStore` |
| `item_subject_ref` | The `itemSubjectRef` if defined |

Also extract `<bpmn:dataInputAssociation>` and `<bpmn:dataOutputAssociation>` elements to build the data flow connections between tasks and data objects.

### Step 7: Extract Message Flows

For each `<bpmn:messageFlow>` (from the collaboration):

| Field | Description |
|-------|-------------|
| `id` | Flow ID |
| `name` | Flow name |
| `source` | `sourceRef` -- may be a task or participant |
| `target` | `targetRef` -- may be a task or participant |
| `message_ref` | Reference to a `<bpmn:message>` element if present |

### Step 8: Assemble Output

Produce a single structured document (YAML or JSON) with this shape:

```yaml
mda_parsed_model:
  source_file: "<filename>"
  parse_date: "<ISO 8601 timestamp>"
  bpmn_version: "2.0"

  processes:
    - process_id: "..."
      process_name: "..."
      is_executable: true
      participant_id: "..."
      participant_name: "..."

  nodes:
    - id: "..."
      name: "..."
      type: "userTask"
      lane: "..."
      incoming: ["flow_1"]
      outgoing: ["flow_2"]
      boundary_events: []
      documentation: "..."
      attributes: {}

  edges:
    - id: "..."
      name: null
      source: "..."
      target: "..."
      condition_expression: null

  lanes:
    - lane_id: "..."
      lane_name: "..."
      flow_node_refs: ["node_1", "node_2"]

  data_objects:
    - id: "..."
      name: "..."
      type: "dataObject"
      item_subject_ref: null

  data_stores:
    - id: "..."
      name: "..."
      type: "dataStore"

  data_associations:
    - task_id: "..."
      data_ref: "..."
      direction: "input"  # or "output"

  message_flows:
    - id: "..."
      name: "..."
      source: "..."
      target: "..."
      message_ref: null
```

## Error Handling

| Condition | Action |
|-----------|--------|
| XML is not well-formed | Halt. Report `PARSE_ERR_MALFORMED_XML` with line/column. |
| XML is well-formed but not valid BPMN 2.0 | Halt. Report `PARSE_ERR_INVALID_BPMN` with details. |
| Element has no `id` attribute | Generate a synthetic ID (`_synthetic_{type}_{n}`), add a warning to the output. |
| Element has no `name` attribute | Set `name` to `null`. This is not an error -- names are optional in BPMN. |
| Unknown element type not in the mapping table | Include it in the output with `type: "unknown"` and add a warning. Do not halt. |
| Sequence flow references a non-existent node | Include the edge but add a warning with the dangling reference. |
| Multiple processes in one file | Parse all processes. Downstream stages handle them individually. |

## Output Validation

Before completing, verify:

1. Every node ID referenced by an edge exists in the nodes array (warn if not)
2. Every node has at least one incoming or outgoing flow (except start/end events)
3. Lane references resolve to actual node IDs
4. No duplicate IDs exist in any array
