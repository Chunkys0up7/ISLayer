# Income Verification Process Graph

```mermaid
flowchart TD
    Start_Requested(("Verification\nRequested"))
    Task_ReceiveRequest["Receive Verification\nRequest\n<i>receiveTask</i>"]
    Task_ClassifyEmployment["Classify Employment\nType\n<i>businessRuleTask</i>"]
    Gateway_EmploymentType{"W-2 or\nSelf-Employed?"}
    Task_VerifyW2["Verify W-2\nIncome\n<i>serviceTask</i>"]
    Task_VerifySelfEmployment["Verify Self-Employment\nIncome\n<i>serviceTask</i>"]
    Task_CalcQualifying["Calculate Qualifying\nIncome\n<i>businessRuleTask</i>"]
    Gateway_Variance{"Variance Exceeds\nThreshold?"}
    Task_EmitVerified["Emit Income\nVerified Event\n<i>sendTask</i>"]
    End_Verified(("Income\nVerified"))
    End_VarianceException(("Variance\nException"))

    borrower_profile[(borrower_profile)]
    tax_returns[(tax_returns)]
    w2_documents[(w2_documents)]
    income_result[(income_result)]

    Start_Requested --> Task_ReceiveRequest
    Task_ReceiveRequest --> Task_ClassifyEmployment
    Task_ReceiveRequest -.-> borrower_profile
    Task_ClassifyEmployment --> Gateway_EmploymentType
    borrower_profile -.-> Task_ClassifyEmployment
    Gateway_EmploymentType -->|"W-2 Employee"| Task_VerifyW2
    Gateway_EmploymentType -->|"Self-Employed"| Task_VerifySelfEmployment
    w2_documents -.-> Task_VerifyW2
    tax_returns -.-> Task_VerifyW2
    tax_returns -.-> Task_VerifySelfEmployment
    Task_VerifyW2 --> Task_CalcQualifying
    Task_VerifySelfEmployment --> Task_CalcQualifying
    Task_CalcQualifying --> Gateway_Variance
    Task_CalcQualifying -.-> income_result
    Gateway_Variance -->|"Within Threshold"| Task_EmitVerified
    Gateway_Variance -->|"Exceeds Threshold"| End_VarianceException
    income_result -.-> Task_EmitVerified
    Task_EmitVerified --> End_Verified

    classDef startEnd fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
    classDef task fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef gateway fill:#fce4ec,stroke:#c62828,stroke-width:2px
    classDef data fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px,stroke-dasharray: 5

    class Start_Requested,End_Verified,End_VarianceException startEnd
    class Task_ReceiveRequest,Task_ClassifyEmployment,Task_VerifyW2,Task_VerifySelfEmployment,Task_CalcQualifying,Task_EmitVerified task
    class Gateway_EmploymentType,Gateway_Variance gateway
    class borrower_profile,tax_returns,w2_documents,income_result data
```

## Lane Assignments

| Lane | Tasks |
|---|---|
| **Underwriting System** | Receive Verification Request, Emit Income Verified Event |
| **Verification Agent** | Classify Employment Type, Verify W-2 Income, Verify Self-Employment Income, Calculate Qualifying Income |

## Data Flow Summary

| Data Object | Produced By | Consumed By |
|---|---|---|
| borrower_profile | Task_ReceiveRequest | Task_ClassifyEmployment |
| tax_returns | External (DocVault) | Task_VerifyW2, Task_VerifySelfEmployment |
| w2_documents | External (DocVault) | Task_VerifyW2 |
| income_result | Task_CalcQualifying | Task_EmitVerified |
