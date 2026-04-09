---
intent_id: "INT-IV-NTF-001"
capsule_id: "CAP-IV-NTF-001"
bpmn_task_id: "Task_EmitVerified"
version: "1.0"
status: "draft"
goal: "Publish a verified income event to the underwriting event bus and update the loan application status, enabling downstream underwriting decisions to proceed."
goal_type: "state_transition"
preconditions:
  - "The income variance is within the acceptable threshold (varianceStatus = WITHIN_THRESHOLD)."
  - "The income_result data object is fully populated with qualifying income and variance analysis."
  - "The event bus topic underwriting.events is accessible and writable."
  - "The LOS status update endpoint is available."
inputs:
  - name: "income_result"
    source: "Process Context"
    schema_ref: "schemas/income-result.json"
    required: true
  - name: "loanApplicationId"
    source: "Process Context"
    schema_ref: "schemas/verification-request.json"
    required: true
  - name: "borrowerId"
    source: "Process Context"
    schema_ref: "schemas/verification-request.json"
    required: true
  - name: "correlationId"
    source: "Process Context"
    schema_ref: "schemas/verification-request.json"
    required: true
  - name: "processInstanceId"
    source: "Process Engine"
    schema_ref: null
    required: true
outputs:
  - name: "IncomeVerified_event"
    type: "object"
    sink: "Event Bus"
    invariants:
      - "Event includes complete income result; partial results MUST NOT be published"
      - "Event is published with loanApplicationId as the partition key"
      - "verifiedAt timestamp reflects actual time of event publication"
      - "PII fields are encrypted or tokenized before publishing"
  - name: "losStatusUpdate"
    type: "object"
    sink: "LOS"
  - name: "deliveryConfirmation"
    type: "object"
    sink: "Process Context"
invariants:
  - "The event MUST include the complete income result; partial results MUST NOT be published."
  - "The event MUST be published with the loanApplicationId as the partition key."
  - "The verifiedAt timestamp MUST reflect the actual time of event publication, not the time of income calculation."
  - "PII fields in the event payload MUST be encrypted or tokenized before publishing."
success_criteria:
  - "The IncomeVerified event is published to the underwriting.events topic."
  - "The LOS application status is updated to INCOME_VERIFIED."
  - "Broker acknowledgement is received confirming delivery."
failure_modes:
  - mode: "Event bus publish failure"
    detection: "Event bus rejected the message or is unavailable"
    action: "Retry 3 times with exponential backoff; if still failing, persist to dead-letter queue and alert ops"
  - mode: "LOS status update failure"
    detection: "LOS status update API returned error"
    action: "Log warning; event was published so downstream can proceed; retry LOS update asynchronously"
  - mode: "Event schema invalid"
    detection: "Event payload fails schema validation"
    action: "Log error with payload; do not publish invalid events; escalate to engineering"
contract_ref: "ICT-IV-NTF-001"
idempotency: "safe"
retry_policy: "exponential_backoff, max_retries=3, base_delay=5s"
timeout_seconds: 60
side_effects:
  - "Publishes IncomeVerified event to underwriting.events topic"
  - "Updates loan application status in LOS to INCOME_VERIFIED"
execution_hints:
  preferred_agent: "income-verification-service"
  tool_access:
    - "event_bus"
    - "los_api"
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"
generated_from: "CAP-IV-NTF-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PIM"
gaps: []
---

# Intent: Emit Income Verified Event

## Goal

Publish a verified income event to the underwriting event bus and update the loan application status, enabling downstream underwriting decisions to proceed.

## Preconditions

- The income variance is within the acceptable threshold (varianceStatus = WITHIN_THRESHOLD).
- The `income_result` data object is fully populated with qualifying income and variance analysis.
- The event bus topic `underwriting.events` is accessible and writable.
- The LOS status update endpoint is available.

## Execution Notes

This intent publishes the final verification result. The executing agent must not publish the event if the variance exceeds the threshold (that path goes to End_VarianceException), must not include unmasked SSN in the event payload, must not publish duplicate events for the same verification without idempotency controls, and must not update LOS status before the event is confirmed published to the event bus.
