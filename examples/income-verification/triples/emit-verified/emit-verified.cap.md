---
capsule_id: "CAP-IV-NTF-001"
bpmn_task_id: "Task_EmitVerified"
bpmn_task_name: "Emit Income Verified Event"
bpmn_task_type: "sendTask"
process_id: "Process_IncomeVerification"
process_name: "Income Verification"
version: "1.0"
status: "draft"
generated_from: "income-verification.bpmn"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
last_modified: "2026-04-09T00:00:00Z"
last_modified_by: "MDA Demo"
owner_role: "Underwriter"
owner_team: "Income Verification"
reviewers: []
domain: "Mortgage Lending"
subdomain: "Income Verification"
regulation_refs:
  - "Fannie Mae Selling Guide A2-1-01 (Record Retention)"
  - "GLBA Safeguards Rule (PII Encryption)"
policy_refs:
  - "POL-IV-007 Income Verification Event Publication Policy"
intent_id: "INT-IV-NTF-001"
contract_id: "ICT-IV-NTF-001"
parent_capsule_id: null
predecessor_ids:
  - "CAP-IV-DEC-002"
successor_ids: []
exception_ids: []
gaps:
  - type: "missing_detail"
    description: "Dead-letter queue topic for failed publishes not yet provisioned"
    severity: "low"
---

# Emit Income Verified Event

## Purpose

Publishes the income verification result as a domain event to the underwriting event bus. This event signals to downstream consumers (automated underwriting engine, loan officer dashboard, compliance audit trail) that income verification has completed successfully and the qualifying income figure is available.

## Procedure

1. **Assemble Event Payload**: Construct the `IncomeVerified` domain event from the `income_result` data object:
   - Include the loan application ID, borrower ID, and correlation ID for traceability.
   - Include the total qualifying monthly income and annual equivalent.
   - Include the income breakdown by source type.
   - Include the variance analysis result (stated vs. verified).
   - Include the verification method and document references used.

2. **Stamp Audit Metadata**: Add audit fields to the event:
   - `verifiedAt`: Current UTC timestamp
   - `verifiedBy`: System principal or agent ID that performed the verification
   - `processInstanceId`: The BPMN process instance identifier
   - `ruleVersions`: Versions of the rule sets applied during verification

3. **Validate Event Completeness**: Before publishing, confirm all required fields are populated. The event schema is enforced at the message broker level, but pre-validation prevents serialization errors.

4. **Publish to Event Bus**: Send the `IncomeVerified` event to the `underwriting.events` topic. Use the `loanApplicationId` as the partition key to ensure ordering within a loan application.

5. **Confirm Delivery**: Wait for broker acknowledgement. If delivery fails, retry up to 3 times with exponential backoff. If all retries fail, log a critical error and alert the operations team.

6. **Update LOS Status**: Call the LOS API to update the loan application's verification status to `INCOME_VERIFIED`.

## Business Rules

- All income verification events must be retained for a minimum of 5 years per Fannie Mae Selling Guide A2-1-01 (Record Retention).
- Event payloads containing PII must be encrypted in transit and at rest per GLBA Safeguards Rule.
- The event bus (Kafka or similar) is configured with appropriate retention and replication.
- Downstream consumers are subscribed to the `underwriting.events` topic.
- The LOS status update API is idempotent.

## Inputs

| Field | Source | Required |
|---|---|---|
| income_result | Process Context | Yes |
| loanApplicationId | Process Context | Yes |
| borrowerId | Process Context | Yes |
| correlationId | Process Context | Yes |
| processInstanceId | Process Engine | Yes |

## Outputs

| Field | Destination | Description |
|---|---|---|
| IncomeVerified event | Event Bus | Domain event published to underwriting.events topic |
| losStatusUpdate | LOS | Loan application status updated to INCOME_VERIFIED |
| deliveryConfirmation | Process Context | Broker acknowledgement receipt |

## Exception Handling

- **Publish Failure**: If event bus rejected the message or is unavailable, retry 3 times with exponential backoff; if still failing, persist to dead-letter queue and alert ops.
- **LOS Update Failure**: If LOS status update API returned error, log warning; event was published so downstream can proceed; retry LOS update asynchronously.
- **Schema Invalid**: If event payload fails schema validation, log error with payload; do not publish invalid events; escalate to engineering.
