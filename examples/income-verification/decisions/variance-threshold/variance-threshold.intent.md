---
intent_id: "INT-IV-DEC-002"
capsule_id: "CAP-IV-DEC-002"
bpmn_task_id: "Gateway_Variance"
version: "1.0"
status: "draft"
goal: "Determine whether the stated-vs-verified income variance is acceptable for automated processing or requires exception handling and manual underwriter review."
goal_type: "decision"
preconditions:
  - "Task_CalcQualifying has completed and set both variancePercent and varianceThreshold process variables."
  - "Both variables are numeric (decimal) values."
  - "varianceThreshold has been set according to the loan program rules."
inputs:
  - name: "variancePercent"
    source: "Process Variable"
    schema_ref: "schemas/variance.json"
    required: true
  - name: "varianceThreshold"
    source: "Process Variable"
    schema_ref: "schemas/variance.json"
    required: true
outputs:
  - name: "selectedPath"
    type: "string"
    sink: "Process Flow"
    invariants:
      - "Exactly one outbound flow is taken"
      - "Flow_VarianceToEmit (within threshold) or Flow_VarianceToException (exceeds threshold)"
invariants:
  - "Exactly one outbound flow MUST be taken."
  - "The comparison MUST use the absolute value of the variance; both over-stated and under-stated income must be checked."
  - "The threshold MUST NOT be modified at the gateway; it must be the value set by Task_CalcQualifying based on the loan program."
  - "A variance exactly equal to the threshold MUST be treated as within threshold (less-than-or-equal)."
success_criteria:
  - "The process is routed to Task_EmitVerified if variance is within threshold."
  - "The process is routed to End_VarianceException if variance exceeds threshold."
failure_modes:
  - mode: "Variable missing"
    detection: "variancePercent or varianceThreshold is null"
    action: "Process engine raises exception; indicates upstream calculation failure"
  - mode: "Invalid variable type"
    detection: "Variables are not numeric"
    action: "Process engine raises type error; escalate to engineering"
contract_ref: "ICT-IV-DEC-002"
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
generated_from: "CAP-IV-DEC-002"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
mda_layer: "PIM"
gaps: []
---

# Intent: Variance Threshold Decision

## Goal

Determine whether the stated-vs-verified income variance is acceptable for automated processing or requires exception handling and manual underwriter review.

## Preconditions

- Task_CalcQualifying has completed and set both `variancePercent` and `varianceThreshold` process variables.
- Both variables are numeric (decimal) values.
- varianceThreshold has been set according to the loan program rules.

## Execution Notes

This intent is evaluated natively by the BPMN process engine. The gateway must not override the threshold at the gateway level, must not treat the exceeds-threshold path as a soft warning (it must terminate with an error event), and must not allow the process to continue to Task_EmitVerified if variance exceeds threshold.
