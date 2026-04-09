---
contract_id: "ICT-PA-ORD-001"
contract_name: "Order Appraisal Binding"
bpmn_task_id: "Task_OrderAppraisal"
bpmn_task_name: "Order Appraisal"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"

version: "1.0.0"
status: "draft"
mda_layer: "PSM"

generated_from: "CAP-PA-ORD-001 + INT-PA-ORD-001"
generated_date: "2026-04-09"
generated_by: "mda-pipeline"
last_modified: "2026-04-09"
last_modified_by: "mda-pipeline"

owner_role: "Integration Architect"
owner_team: "Mortgage Technology"
reviewers:
  - "Appraisal Desk Supervisor"
  - "API Platform Lead"

domain: "Mortgage"
subdomain: "Property Appraisal"

capsule_id: "CAP-PA-ORD-001"
intent_id: "INT-PA-ORD-001"

binding_status: "unbound"

input_schema:
  - name: "loan_number"
    type: "string"
    required: true
    description: "Unique loan identifier from the LOS."
    source: "LOS"
    constraints: "pattern: '^LN-[0-9]{10}$'"
  - name: "property_address"
    type: "object"
    required: true
    description: "Structured property address with street, city, state, zip, county."
    source: "LOS"
    constraints: "All address fields required; state must be 2-letter code"
  - name: "property_type"
    type: "string"
    required: true
    description: "Property type classification."
    source: "LOS"
    constraints: "enum: [SFR, Condo, Townhouse, 2-4_Unit, Manufactured, Co-op]"
  - name: "legal_description"
    type: "string"
    required: true
    description: "Legal description of the property from title records."
    source: "LOS"
    constraints: "maxLength: 2000"
  - name: "loan_amount"
    type: "float"
    required: true
    description: "Requested loan amount in USD."
    source: "LOS"
    constraints: "min: 1000, max: 5000000"
  - name: "loan_program"
    type: "string"
    required: true
    description: "Loan program type determining appraisal form requirements."
    source: "Product Engine"
    constraints: "enum: [Conventional, FHA, VA, USDA, Jumbo, Non-QM]"
  - name: "appraisal_form_type"
    type: "string"
    required: true
    description: "URAR form number for the appraisal."
    source: "Product Engine"
    constraints: "enum: [1004, 1004D, 1073, 1025, 2055, 1004C]"
  - name: "fee_authorization_id"
    type: "string"
    required: true
    description: "Reference ID for borrower's appraisal fee payment authorization."
    source: "Payment Gateway"
    constraints: "pattern: '^FEE-[A-Z0-9]{8}$'"
  - name: "special_instructions"
    type: "string"
    required: false
    description: "Access instructions, tenant contact info, or other notes for the appraiser."
    source: "LOS"
    constraints: "maxLength: 1000"

output_schema:
  - name: "order_confirmation_id"
    type: "string"
    required: true
    description: "AMC-assigned order confirmation number."
    destination: "LOS"
    constraints: "pattern: '^ORD-[A-Z0-9]{12}$'"
  - name: "amc_name"
    type: "string"
    required: true
    description: "Name of the AMC that accepted the order."
    destination: "LOS"
    constraints: "maxLength: 200"
  - name: "estimated_completion_date"
    type: "date"
    required: true
    description: "Expected appraisal report delivery date."
    destination: "LOS"
    constraints: "Must be a future date within 30 calendar days"
  - name: "fee_charge_reference"
    type: "string"
    required: true
    description: "Payment transaction reference for the appraisal fee charge."
    destination: "Payment Gateway"
    constraints: "pattern: '^CHG-[A-Z0-9]{10}$'"
  - name: "order_status"
    type: "string"
    required: true
    description: "Current status of the appraisal order."
    destination: "LOS"
    constraints: "enum: [Ordered, Accepted, Assigned, Scheduled]"

error_codes:
  - code: "ERR-PA-ORD-001"
    name: "AMC Unavailable"
    severity: "error"
    description: "No AMC in the approved panel has coverage for the property location."
    resolution: "Escalate to Appraisal Desk Supervisor to manually assign or onboard a new AMC."
  - code: "ERR-PA-ORD-002"
    name: "Fee Authorization Invalid"
    severity: "error"
    description: "Borrower fee authorization is expired, declined, or insufficient."
    resolution: "Notify loan officer to obtain updated payment authorization from borrower."
  - code: "ERR-PA-ORD-003"
    name: "Duplicate Order Detected"
    severity: "warning"
    description: "An active appraisal order already exists for this property and loan."
    resolution: "Block the duplicate order and alert the appraisal desk for review."
  - code: "ERR-PA-ORD-004"
    name: "MISMO Payload Validation Failure"
    severity: "error"
    description: "The order payload does not conform to MISMO 3.4 XML schema requirements."
    resolution: "Log the validation errors, correct the payload, and retry."

max_latency_ms: 30000
throughput: "200 orders/hour"
availability: "99.5%"

min_capsule_version: "1.0.0"
min_intent_version: "1.0.0"
breaking_changes: []

api_endpoints:
  - method: "POST"
    path: "/api/v1/appraisal/orders"
    description: "Submit a new appraisal order to the AMC portal."
    request_content_type: "application/json"
    response_content_type: "application/json"
  - method: "GET"
    path: "/api/v1/appraisal/orders/{order_id}/status"
    description: "Check the status of a submitted appraisal order."
    response_content_type: "application/json"

gaps:
  - "MISMO 3.4 schema mapping not yet complete -- Integration Architect to finalize"
---

# Order Appraisal Binding

## Binding Rationale

This contract binds **Order Appraisal** (`CAP-PA-ORD-001`) to
**Submit Appraisal Order to AMC** (`INT-PA-ORD-001`).

The binding ensures that the RPA agent assembling and transmitting the appraisal order has a well-defined data contract with both the LOS (input) and the AMC Appraisal Portal (output). Without this contract, field mismatches between the LOS export and the MISMO order payload would cause silent failures or incomplete orders, delaying the loan timeline.

**Key guarantees:**

- The agent receives a complete, validated property address and loan program before constructing the order.
- The output always includes an AMC confirmation number that can be traced back to the original loan.
- All error conditions are enumerated; the agent never produces an undocumented error state.

## Change Protocol

All changes to this contract MUST follow this protocol:

1. **Non-breaking changes** (MINOR/PATCH version bump):
   - Adding optional fields to input or output schemas.
   - Adding new error codes.
   - Updating descriptions, constraints, or documentation.

2. **Breaking changes** (MAJOR version bump):
   - Removing or renaming fields in input or output schemas.
   - Changing a field from optional to required.
   - Altering the semantics of an existing error code.
   - These MUST trigger a coordinated update to the paired capsule and intent.

3. **Review and approval**:
   - All changes require at least one reviewer from `reviewers`.
   - Breaking changes require approval from `owner_role` of all three triple members.

4. **Version alignment**:
   - After a breaking change, update `min_capsule_version` and `min_intent_version`.

## Decommissioning

This contract may be decommissioned when:

- The appraisal ordering process is replaced by a direct-to-appraiser model.
- The parent BPMN task is removed from the process model.
- The business process is retired entirely.

**Data retention:** Retired contracts must be preserved for 7 years per mortgage regulatory retention requirements.
