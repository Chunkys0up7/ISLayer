---
capsule_id: "CAP-PA-ORD-001"
bpmn_task_id: "Task_OrderAppraisal"
bpmn_task_name: "Order Appraisal"
bpmn_task_type: "sendTask"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"

version: "1.0.0"
status: "draft"

generated_from: "bpmn/property-appraisal.bpmn"
generated_date: "2026-04-09"
generated_by: "mda-pipeline"
last_modified: "2026-04-09"
last_modified_by: "mda-pipeline"

owner_role: "Loan Processing Manager"
owner_team: "Mortgage Origination"
reviewers:
  - "Appraisal Desk Supervisor"
  - "Compliance Officer"

domain: "Mortgage"
subdomain: "Property Appraisal"
regulation_refs:
  - "USPAP-SR1: Standards Rule 1 - Real Property Appraisal Development"
  - "ECOA: Equal Credit Opportunity Act - Appraiser Independence"
  - "AIR: Appraiser Independence Requirements (Dodd-Frank Section 1472)"
policy_refs:
  - "POL-MTG-APR-001: Appraisal Ordering Policy"
  - "POL-MTG-APR-002: AMC Selection and Rotation Policy"

intent_id: "INT-PA-ORD-001"
contract_id: "ICT-PA-ORD-001"
parent_capsule_id: ""
predecessor_ids: []
successor_ids:
  - "CAP-PA-RCV-001"
exception_ids: []

gaps:
  - "AMC rotation algorithm not yet formalized -- Appraisal Desk Supervisor to define"
---

# Order Appraisal

## Purpose

The Order Appraisal task initiates the property valuation process by transmitting an appraisal order to a licensed Appraisal Management Company (AMC) or panel appraiser. This step is critical because the appraisal determines whether the property value supports the requested loan amount. Without a timely and compliant appraisal order, the loan cannot proceed to underwriting, causing delays and potential lock expiration.

## Procedure

1. Retrieve the loan file from the Loan Origination System (LOS), confirming the property address, property type, and loan program parameters.
2. Verify that the borrower has provided payment authorization for the appraisal fee per TRID disclosure requirements.
3. Select the appropriate AMC or appraiser panel based on the property location, property type (SFR, condo, multi-family, manufactured home), and the lender's rotation policy.
4. Populate the appraisal order form with property details including legal description, county, census tract, and any known access instructions.
5. Specify the required appraisal form type (URAR 1004, 1073 for condos, 1025 for small residential income, 2055 for exterior-only) based on the loan program.
6. Transmit the order to the selected AMC via the Appraisal Portal integration (MISMO XML or vendor API).
7. Record the order confirmation number, estimated turnaround date, and assigned appraiser (if known) in the LOS.
8. Set the appraisal status to "Ordered" and initiate the turnaround tracking timer.

## Business Rules

- The loan officer who originated the loan must not select or communicate directly with the appraiser (AIR / Dodd-Frank Section 1472).
- Appraisal orders must be placed within 3 business days of the initial loan application per internal SLA.
- The appraisal fee must be disclosed on the Loan Estimate and cannot exceed the amount disclosed without a revised LE.
- FHA loans require FHA Roster appraisers; VA loans require VA-assigned appraisers through the VA portal.
- Condo appraisals must include the condo project questionnaire (Form 1073) when required by the investor.
- Rush orders (turnaround under 5 business days) require supervisor approval and incur a surcharge disclosed to the borrower.

## Inputs Required

| Input | Source | Description |
|-------|--------|-------------|
| Loan Application Data | LOS (Encompass/ICE) | Borrower info, property address, loan amount, program type |
| Property Details | LOS | Property type, legal description, county, census tract, access instructions |
| Appraisal Fee Authorization | Borrower | Signed fee disclosure or credit card authorization |
| AMC Panel List | Vendor Management System | Approved AMC roster with rotation status and geographic coverage |
| Loan Program Requirements | Product Engine | Required appraisal form type and any investor-specific overlays |

## Outputs Produced

| Output | Destination | Description |
|--------|-------------|-------------|
| Appraisal Order Confirmation | LOS | Order ID, AMC name, estimated completion date, assigned appraiser |
| Order Transmission Record | Appraisal Portal | MISMO XML order payload sent to the AMC |
| Appraisal Fee Charge | Payment Gateway | Fee charge record against borrower authorization |
| Status Update | LOS | Loan status updated to "Appraisal Ordered" with timestamp |

## Exception Handling

- **AMC Rejection** -- If the AMC rejects the order (coverage area, capacity, or appraiser availability), re-route to the next AMC in the rotation queue. Log the rejection reason.
- **Fee Authorization Failure** -- If payment cannot be processed, place a hold on the order and notify the loan officer to obtain updated payment authorization within 24 hours.
- **Property Access Issues** -- If the property is tenant-occupied or has gate access restrictions, flag the order with special instructions and extend the expected turnaround by 2 business days.
- **Duplicate Order Detection** -- If an active appraisal order already exists for this property and loan, block the duplicate and alert the appraisal desk.

## Regulatory Context

Appraiser Independence Requirements (AIR) under Dodd-Frank Section 1472 prohibit loan production staff from selecting, retaining, or influencing appraisers. The appraisal ordering function must be performed by an independent appraisal desk or AMC. All communications between the lender and appraiser must be logged for examiner review. USPAP Standards Rule 1 governs the scope of work that must be specified in the engagement.

## Notes

- Transfer appraisals from prior lenders may be accepted under certain investor guidelines, bypassing a new order.
- Desktop appraisals (Form 1004 Desktop) may be permitted for certain GSE-eligible loans based on collateral risk scoring.
- The appraisal order must reference the correct UCDP (Uniform Collateral Data Portal) submission requirements for GSE loans.
