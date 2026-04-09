---
corpus_id: "CRP-POL-PA-002"
title: "AMC Selection and Rotation Policy"
slug: "amc-selection-policy"
doc_type: "policy"
domain: "Mortgage Lending"
subdomain: "Property Appraisal"
tags:
  - "amc-selection"
  - "amc-rotation"
  - "performance-scoring"
  - "blacklist"
  - "geographic-coverage"
  - "vendor-management"
applies_to:
  process_ids:
    - "Process_PropertyAppraisal"
    - "Process_AppraisalOrdering"
    - "Process_VendorManagement"
  task_types:
    - "userTask"
    - "serviceTask"
  task_name_patterns:
    - "order.*appraisal"
    - "select.*amc"
    - "rotate.*amc"
    - "evaluate.*vendor"
  goal_types:
    - "governance"
  roles:
    - "appraisal_coordinator"
    - "vp_appraisal_operations"
    - "vendor_manager"
version: "2.0"
status: "current"
effective_date: "2025-06-01"
review_date: "2026-06-01"
supersedes: null
superseded_by: null
author: "Vendor Management & Appraisal Operations"
last_modified: "2025-05-25"
last_modified_by: "D. Park"
source: "internal"
source_ref: "POL-PA-002"
related_corpus_ids:
  - "CRP-POL-PA-001"
  - "CRP-PRC-PA-001"
  - "CRP-REG-PA-002"
regulation_refs:
  - "Dodd-Frank Act Section 1473 (AMC Rule)"
  - "Dodd-Frank Act Section 1472"
  - "Interagency Appraisal and Evaluation Guidelines (2010)"
policy_refs:
  - "POL-PA-001"
  - "POL-VM-001"
---

# AMC Selection and Rotation Policy

## 1. Policy Statement

This policy governs the selection, evaluation, rotation, and removal of Appraisal Management Companies (AMCs) from the approved vendor panel. The policy ensures fair, compliant, and quality-driven AMC management while maintaining appraiser independence and geographic coverage for all lending markets.

## 2. Approved AMC List

### 2.1 Eligibility Criteria

To be considered for the approved AMC panel, an AMC must meet all of the following criteria:

| Criterion | Minimum Requirement |
|---|---|
| State registration | Registered in all states where the lender originates loans (or a defined subset) |
| E&O insurance | Minimum $1 million per occurrence, $3 million aggregate |
| Years in operation | Minimum 3 years continuous operation |
| Appraiser panel size | Minimum 5,000 active appraisers nationwide (or 500 for regional AMCs) |
| Quality control program | Documented QC program with USPAP-trained review appraisers |
| Technology platform | API integration capability (MISMO XML), online portal, status tracking |
| Financial stability | Audited financial statements; no bankruptcy or material litigation |
| Compliance history | No regulatory enforcement actions in the prior 3 years |
| Appraiser compensation | Demonstrated customary and reasonable fee practices |
| Background checks | Criminal background checks on all staff with access to appraisal data |

### 2.2 Current Panel Categories

| Category | Description | Count |
|---|---|---|
| Tier 1 (Primary) | National coverage, highest performance scores, full service | 2-3 AMCs |
| Tier 2 (Standard) | National or large regional coverage, solid performance | 2-3 AMCs |
| Tier 3 (Specialty) | Regional or specialty coverage (rural, manufactured, complex) | 1-2 AMCs |

### 2.3 Panel Maintenance

The approved AMC list is reviewed and updated:
- **Quarterly**: Performance score review and tier assignment
- **Annually**: Full recertification (state registrations, insurance, financials)
- **Ad-hoc**: Triggered by compliance events, performance failures, or market changes

## 3. Rotation Algorithm

### 3.1 Algorithm Design

The rotation algorithm distributes appraisal orders among approved AMCs to ensure fairness, prevent concentration risk, and reward quality performance. The algorithm operates at the state level to account for geographic coverage differences.

**Order Assignment Logic:**

```
FOR each new appraisal order:
  1. Filter AMC panel to those with active registration in subject property state
  2. Filter to those with performance score >= 70
  3. Filter to those below maximum concurrent order capacity
  4. Filter to those with appraiser coverage in subject county
  5. Calculate assignment priority score for each remaining AMC:
     Priority = (Target_Share - Actual_Share) x Performance_Weight
     Where:
       Target_Share = Tier-based target (Tier 1: 40%, Tier 2: 35%, Tier 3: 25%)
       Actual_Share = AMC's actual share of orders in current quarter
       Performance_Weight = Performance_Score / 80
  6. Assign to AMC with highest priority score
  7. Log assignment with rationale
```

### 3.2 Target Share Distribution

| Tier | Target Share of Orders | Rationale |
|---|---|---|
| Tier 1 | 35-45% | Proven performance, broad coverage |
| Tier 2 | 30-40% | Solid performance, diversification |
| Tier 3 | 15-25% | Specialty coverage, competition |

### 3.3 Rebalancing

The rotation algorithm rebalances order distribution quarterly. If any AMC's actual share deviates more than 10 percentage points from its target, the algorithm adjusts priority weights to correct the imbalance over the following quarter.

## 4. Performance Scoring

### 4.1 Scoring Methodology

Each AMC is scored on a 100-point scale using the following weighted categories:

| Category | Weight | Metrics |
|---|---|---|
| Timeliness | 25% | Average turnaround time, on-time delivery rate, SLA compliance |
| Quality | 35% | Completeness rate (pass on first review), revision request rate, USPAP compliance |
| Appraiser Credentials | 15% | Credential appropriateness, license verification accuracy, competency |
| Responsiveness | 10% | Revision request turnaround, communication quality, issue resolution time |
| Compliance | 15% | Independence violations, regulatory findings, complaint volume |

### 4.2 Scoring Scale

| Score Range | Rating | Action |
|---|---|---|
| 90-100 | Excellent | Eligible for Tier 1; may receive increased order share |
| 80-89 | Good | Eligible for Tier 1 or Tier 2 |
| 70-79 | Satisfactory | Eligible for Tier 2 or Tier 3 |
| 60-69 | Below Standard | Performance improvement plan required; reduced order share |
| Below 60 | Unsatisfactory | Suspension from panel; 90-day improvement window |

### 4.3 Scoring Data Sources

| Data Source | Metrics Captured |
|---|---|
| Appraisal tracking system | Turnaround time, SLA compliance, order volume |
| Appraisal review worksheets | Completeness pass rate, revision request rate |
| Compliance audit results | Independence violations, USPAP issues |
| Customer complaints | Loan officer or borrower complaints about AMC or appraiser |
| AMC self-reporting | Appraiser panel changes, state registration updates |

### 4.4 Scoring Calendar

| Activity | Frequency |
|---|---|
| Data collection and metric calculation | Monthly |
| Score tabulation and tier assignment | Quarterly |
| Performance review meeting with each AMC | Quarterly |
| Formal scorecard distribution to AMCs | Quarterly |
| Comprehensive annual review | Annual |

## 5. Blacklist Criteria

### 5.1 AMC Blacklist (Permanent Removal)

An AMC is permanently removed from the panel and blacklisted for:

| Violation | Evidence Required |
|---|---|
| Appraiser independence violation (systemic) | Regulatory finding, internal audit, or multiple documented incidents |
| Fraud (appraisal fabrication, alteration, or submission of fraudulent reports) | Documented evidence; regulatory or law enforcement referral |
| Felony conviction of AMC principal or officer | Background check, court records |
| Loss of state registration in majority of operating states | State regulatory records |
| Material misrepresentation during onboarding or recertification | Due diligence findings |

### 5.2 AMC Suspension (Temporary Removal)

An AMC may be temporarily suspended for:

| Issue | Suspension Duration | Reinstatement Criteria |
|---|---|---|
| Performance score below 60 (two quarters) | 90 days minimum | Improvement plan approved and implemented; score >= 70 |
| Single appraiser independence incident | 30-90 days | Root cause analysis; corrective action verified |
| E&O insurance lapse | Until reinstated | Proof of renewed coverage |
| State registration lapse (limited states) | Until reinstated | Proof of renewed registration |
| Repeated SLA failures | 60 days | Process improvements demonstrated; SLA compliance for 30 days |

### 5.3 Individual Appraiser Exclusion

Individual appraisers (not the AMC) may be excluded from future assignments for:

| Reason | Action |
|---|---|
| USPAP violation | Notify AMC; exclude appraiser from all future assignments |
| Repeated quality failures (3+ revision requests in 12 months) | Exclude appraiser; notify AMC |
| License suspension or revocation | Automatic exclusion; notify AMC |
| Conflict of interest discovered | Exclude from transactions in affected area |
| Competency concerns | Exclude pending AMC review of appraiser qualifications |

## 6. Geographic Coverage Requirements

### 6.1 Coverage Standards

The AMC panel collectively must provide coverage for all geographic markets where the lender originates loans. Coverage is measured at the county level.

| Coverage Tier | Definition | Requirement |
|---|---|---|
| Primary markets | Top 100 MSAs by loan volume | Minimum 3 AMCs with active coverage |
| Secondary markets | MSAs ranked 101-300 by loan volume | Minimum 2 AMCs with active coverage |
| Rural/underserved markets | Non-MSA counties | Minimum 1 AMC with active coverage |

### 6.2 Coverage Gap Management

When a coverage gap is identified (no AMC can fulfill an order in a specific county):

1. Contact Tier 3 (specialty) AMCs for one-time coverage arrangement
2. If no AMC coverage available, engage a directly-sourced appraiser through the compliance-approved direct engagement process (requires appraiser independence controls equivalent to AMC)
3. Document the coverage gap and report to VP Appraisal Operations for panel expansion consideration
4. Allow extended turnaround (up to 15 business days) for underserved areas

### 6.3 Coverage Reporting

AMC coverage maps are maintained and updated quarterly. Coverage reports are distributed to:
- VP Appraisal Operations
- Loan Production management (for origination planning)
- Compliance Department (for risk assessment)

## 7. Governance and Oversight

| Activity | Responsible Party | Frequency |
|---|---|---|
| AMC panel approval/removal decisions | VP Appraisal Operations | As needed |
| Performance score calculation | Appraisal Operations Analyst | Monthly |
| Tier assignment | VP Appraisal Operations | Quarterly |
| AMC relationship management | Appraisal Coordinator | Ongoing |
| Rotation algorithm audit | Internal Audit | Annual |
| Blacklist/suspension decisions | VP Appraisal Operations + Compliance | As needed |
| Policy review and update | Appraisal Operations Committee | Annual |

## 8. References

- CRP-POL-PA-001: Appraisal Ordering Policy
- CRP-PRC-PA-001: Appraisal Ordering Procedure
- CRP-REG-PA-002: Appraiser Independence Requirements
- Dodd-Frank Act Section 1473 (AMC Rule)
- Interagency Appraisal and Evaluation Guidelines (2010)
