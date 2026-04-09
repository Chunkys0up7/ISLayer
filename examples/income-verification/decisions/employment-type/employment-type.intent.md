---
intent_id: "INT-IV-DEC-001"
capsule_id: "CAP-IV-DEC-001"
bpmn_task_id: "Gateway_EmploymentType"
version: "1.0"
status: "draft"
goal: "Route the process to the correct income verification path based on the borrower's employment classification, ensuring the appropriate documentation and calculation rules are applied."
goal_type: "decision"
preconditions:
  - "Task_ClassifyEmployment has completed and set the employmentType process variable."
  - "The employmentType value is one of the supported enum values: W2, SELF_EMPLOYED."
inputs:
  - name: "employmentType"
    source: "Process Variable"
    schema_ref: "schemas/employment-type.json"
    required: true
outputs:
  - name: "selectedPath"
    type: "string"
    sink: "Process Flow"
    invariants:
      - "Exactly one outbound flow is taken (exclusive gateway semantics)"
invariants:
  - "Exactly one outbound flow MUST be taken; the gateway MUST NOT activate both paths simultaneously (exclusive gateway semantics)."
  - "The employmentType variable MUST be evaluated as a string literal comparison, not a pattern match."
  - "If employmentType is null or unrecognized, the process engine MUST raise an exception rather than silently dropping the token."
success_criteria:
  - "The process is routed to Task_VerifyW2 or Task_VerifySelfEmployment based on the employmentType variable."
failure_modes:
  - mode: "Unmatched gateway"
    detection: "employmentType does not match any condition expression"
    action: "Process engine raises exception; alert underwriter for manual classification"
  - mode: "Variable missing"
    detection: "employmentType process variable is not set"
    action: "Process engine raises exception; indicates upstream task failure"
contract_ref: "ICT-IV-DEC-001"
idempotency: "safe"
retry_policy: "none"
timeout_seconds: 5
side_effects: []
execution_hints:
  preferred_agent: "process_engine"
  tool_access:
    - "process_engine_native"
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"
generated_from: "CAP-IV-DEC-001"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PIM"
gaps: []
---

# Intent: Employment Type Decision

## Goal

Route the process to the correct income verification path based on the borrower's employment classification, ensuring the appropriate documentation and calculation rules are applied.

## Preconditions

- Task_ClassifyEmployment has completed and set the `employmentType` process variable.
- The employmentType value is one of the supported enum values: W2, SELF_EMPLOYED.

## Execution Notes

This intent is evaluated natively by the BPMN process engine. The gateway must not route to both paths simultaneously (that would require a parallel gateway) and must not default to W2 if the variable is missing or unrecognized.
