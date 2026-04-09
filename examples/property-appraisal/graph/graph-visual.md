---
title: "Property Appraisal Process Flow"
process_id: "Process_PropertyAppraisal"
generated_date: "2026-04-09"
---

# Property Appraisal Process Flow

```mermaid
graph TD
    Start_Ordered((Appraisal Ordered))
    Task_OrderAppraisal[/Order Appraisal\]
    Task_ReceiveReport[\Receive Appraisal Report/]
    Task_ValidateCompleteness{{Validate Appraisal Completeness}}
    Gateway_Complete{Complete?}
    Task_RequestRevision[/Request Appraisal Revision\]
    Task_AssessValue[Assess Property Value]
    Gateway_LTV{Value Within LTV?}
    Task_EmitComplete[/Emit Appraisal Complete Event\]
    Task_ManualReview>Flag for Manual Review]
    End_Complete((Appraisal Complete))
    End_ManualReview((Manual Review Required))

    Start_Ordered --> Task_OrderAppraisal
    Task_OrderAppraisal --> Task_ReceiveReport
    Task_ReceiveReport --> Task_ValidateCompleteness
    Task_ValidateCompleteness --> Gateway_Complete
    Gateway_Complete -->|complete| Task_AssessValue
    Gateway_Complete -->|incomplete| Task_RequestRevision
    Task_RequestRevision -->|loop back| Task_ReceiveReport
    Task_AssessValue --> Gateway_LTV
    Gateway_LTV -->|within LTV| Task_EmitComplete
    Gateway_LTV -->|exceeds LTV| Task_ManualReview
    Task_EmitComplete --> End_Complete
    Task_ManualReview --> End_ManualReview

    classDef loanProc fill:#d4e6f1,stroke:#2874a6
    classDef apprMgmt fill:#d5f5e3,stroke:#1e8449
    classDef uwReview fill:#fdebd0,stroke:#ca6f1e
    classDef gateway fill:#f9e79f,stroke:#b7950b
    classDef startEnd fill:#e8daef,stroke:#6c3483

    class Task_OrderAppraisal,Task_EmitComplete loanProc
    class Task_ReceiveReport,Task_ValidateCompleteness,Task_RequestRevision,Task_AssessValue apprMgmt
    class Task_ManualReview uwReview
    class Gateway_Complete,Gateway_LTV gateway
    class Start_Ordered,End_Complete,End_ManualReview startEnd
```

## Lane Legend

| Color | Lane | Responsibility |
|-------|------|----------------|
| Blue | Loan Processing | Loan officer activities for ordering and finalizing |
| Green | Appraisal Management | AMC coordination, validation, and value assessment |
| Orange | Underwriting Review | Manual review for LTV exceptions |

## Triple Cross-Reference

| Node | Triple ID | Type |
|------|-----------|------|
| Order Appraisal | PA-ORD-001 | sendTask |
| Receive Appraisal Report | PA-RCV-001 | receiveTask |
| Validate Appraisal Completeness | PA-VAL-001 | businessRuleTask |
| Request Appraisal Revision | PA-REV-001 | sendTask |
| Assess Property Value | PA-ASV-001 | serviceTask |
| Flag for Manual Review | PA-MRV-001 | userTask |
| Emit Appraisal Complete Event | PA-NTF-001 | sendTask |
| Complete? | PA-DEC-001 | exclusiveGateway |
| Value Within LTV? | PA-DEC-002 | exclusiveGateway |
