---
capsule_id: "CAP-LO-PKG-001"
bpmn_task_id: "Task_PackageLoan"
bpmn_task_name: "Package Loan File"
bpmn_task_type: "task"
process_id: "Process_LoanOrigination"
process_name: "Loan Origination"
version: "1.0"
status: "draft"
generated_from: "loan-origination.bpmn"
generated_date: "2026-04-09T00:00:00Z"
generated_by: "MDA Demo"
last_modified: "2026-04-09T00:00:00Z"
last_modified_by: "MDA Demo"
owner_role: "Processing Team"
owner_team: "Retail Lending"
domain: "Mortgage Lending"
subdomain: "Loan Processing"
regulation_refs:
  - "TRID (TILA-RESPA Integrated Disclosure)"
policy_refs:
  - "POL-LO-050 Loan File Completeness Standards"
  - "POL-LO-051 Underwriting Submission Requirements"
intent_id: "INT-LO-PKG-001"
contract_id: "ICT-LO-PKG-001"
predecessor_ids:
  - "CAP-LO-DEC-001"
successor_ids:
  - "CAP-LO-SUB-001"
---

# Package Loan File

## Purpose

Assemble all loan application materials, verification documents, credit reports, and assessment results into a complete, organized loan file package ready for underwriting review.

## Procedure

1. **Document Inventory**: Verify that all items on the document checklist have been received and are current (not expired):
   - Signed loan application (1003/URLA)
   - Government-issued ID (verified)
   - Credit report (within validity period)
   - Income documentation (paystubs, W-2s, tax returns)
   - Asset statements (bank statements, investment accounts)
   - Property information (purchase contract, appraisal if ordered)
   - DTI assessment results
   - Identity verification results
2. **Data Reconciliation**: Cross-check key data points between documents for consistency:
   - Borrower name matches across all documents
   - Income figures on application match supporting documentation
   - Property address is consistent throughout
   - Loan terms match between application and disclosures
3. **Disclosure Preparation**: Prepare or verify required disclosures:
   - Loan Estimate (if not already issued within 3 business days of application)
   - Notice of Right to Receive Appraisal
   - Equal Credit Opportunity Act Notice
4. **File Organization**: Arrange documents in the standard underwriting file order per institutional standards, with section tabs and an index.
5. **Quality Control Check**: Run the automated QC checklist to verify file completeness and flag any remaining deficiencies.
6. **Processor Notes**: Add a cover memo summarizing the loan file, noting any conditions, compensating factors, or items requiring underwriter attention.

## Business Rules

- The loan file must contain all required documents per the product-specific checklist before submission to underwriting.
- The Loan Estimate must have been issued within 3 business days of application receipt (TRID requirement).
- Documents older than 120 days must be refreshed (90 days for FHA/VA).
- The processor must not make underwriting decisions; the role is limited to file assembly and completeness verification.

## Inputs

| Field | Source | Required |
|---|---|---|
| loan_application | LOS Database | Yes |
| credit_report | DocVault | Yes |
| dti_result | LOS Database | Yes |
| borrower_profile | LOS Database | Yes |
| all supporting documents | DocVault | Yes |

## Outputs

| Field | Destination | Description |
|---|---|---|
| packaged_loan_file | LOS Database / DocVault | Complete, indexed loan file package |
| qc_checklist_result | LOS Database | Automated QC pass/fail with details |
| processor_cover_memo | LOS Database | Summary memo for underwriter |

## Exception Handling

- **Missing Documents**: If any required document is still missing after DTI assessment passed, send the file back to the loan officer for resolution before proceeding.
- **Data Discrepancy**: If reconciliation reveals conflicting data, flag the specific discrepancy and route to the loan officer for clarification.
- **Expired Documents**: Notify the loan officer to obtain refreshed documentation. Do not submit with expired documents.
