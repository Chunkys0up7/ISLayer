---
title: "Loan Origination Process - Visual Graph"
process_id: "Process_LoanOrigination"
generated_date: "2026-04-09"
---

# Loan Origination Process Flow

```mermaid
graph TD
    Start_AppReceived((Application Received))
    Task_ReceiveApplication[Receive Loan Application]
    Task_VerifyIdentity[Verify Borrower Identity]
    Task_PullCredit[Pull Credit Report]
    Task_AssessDTI[Assess Debt-to-Income Ratio]
    Gateway_Eligible{Eligible?}
    Task_RequestDocs[Request Additional Documentation]
    Boundary_Timeout>Timeout - No Response]
    Gateway_DocsReceived{Docs Received?}
    Task_PackageLoan[Package Loan File]
    Task_SubmitUW[Submit to Underwriting]
    End_LoanSubmitted((Loan Submitted))
    End_Rejected((Application Rejected))

    Start_AppReceived --> Task_ReceiveApplication
    Task_ReceiveApplication --> Task_VerifyIdentity
    Task_VerifyIdentity --> Task_PullCredit
    Task_PullCredit --> Task_AssessDTI
    Task_AssessDTI --> Gateway_Eligible
    Gateway_Eligible -->|Eligible| Task_PackageLoan
    Gateway_Eligible -->|Needs Docs| Task_RequestDocs
    Task_RequestDocs --> Gateway_DocsReceived
    Task_RequestDocs -.- Boundary_Timeout
    Gateway_DocsReceived -->|Yes| Task_AssessDTI
    Gateway_DocsReceived -->|No| End_Rejected
    Boundary_Timeout --> End_Rejected
    Task_PackageLoan --> Task_SubmitUW
    Task_SubmitUW --> End_LoanSubmitted

    classDef startEnd fill:#e1f5fe,stroke:#0288d1
    classDef task fill:#fff3e0,stroke:#f57c00
    classDef gateway fill:#fce4ec,stroke:#c62828
    classDef event fill:#f3e5f5,stroke:#7b1fa2

    class Start_AppReceived,End_LoanSubmitted,End_Rejected startEnd
    class Task_ReceiveApplication,Task_VerifyIdentity,Task_PullCredit,Task_AssessDTI,Task_RequestDocs,Task_PackageLoan,Task_SubmitUW task
    class Gateway_Eligible,Gateway_DocsReceived gateway
    class Boundary_Timeout event
```

## Lane Assignment

| Lane | Elements |
|---|---|
| Loan Officer | Start_AppReceived, Task_ReceiveApplication, Task_RequestDocs, Boundary_Timeout, Gateway_DocsReceived |
| Processing Team | Task_PackageLoan, Task_SubmitUW, End_LoanSubmitted |
| Automated Systems | Task_VerifyIdentity, Task_PullCredit, Task_AssessDTI, Gateway_Eligible, End_Rejected |
