---
corpus_id: "CRP-PRC-PA-004"
title: "Appraisal Revision Request Procedure"
slug: "appraisal-revision-request"
doc_type: "procedure"
domain: "Mortgage Lending"
subdomain: "Property Appraisal"
tags:
  - "revision-request"
  - "reconsideration-of-value"
  - "appraisal-deficiency"
  - "amc-communication"
  - "sla-tracking"
applies_to:
  process_ids:
    - "Process_PropertyAppraisal"
    - "Process_AppraisalRevision"
  task_types:
    - "userTask"
    - "serviceTask"
  task_name_patterns:
    - "request.*revision"
    - "reconsider.*value"
    - "submit.*correction"
    - "flag.*deficiency"
  goal_types:
    - "remediation"
  roles:
    - "appraisal_reviewer"
    - "underwriter"
    - "appraisal_coordinator"
version: "1.0"
status: "current"
effective_date: "2025-06-01"
review_date: "2026-06-01"
supersedes: null
superseded_by: null
author: "Appraisal Operations Committee"
last_modified: "2025-05-14"
last_modified_by: "K. Navarro"
source: "internal"
source_ref: "SOP-PA-2025-004"
related_corpus_ids:
  - "CRP-PRC-PA-002"
  - "CRP-PRC-PA-003"
  - "CRP-REG-PA-002"
  - "CRP-SYS-PA-001"
regulation_refs:
  - "Dodd-Frank Act Section 1472"
  - "USPAP Standards Rule 1-5"
  - "Fannie Mae Selling Guide B4-1.4-01"
policy_refs:
  - "POL-PA-001"
---

# Appraisal Revision Request Procedure

## 1. Scope

This procedure governs the process of requesting revisions or reconsiderations of value from an appraiser through the AMC. It covers deficiency identification, request preparation, compliance with appraiser independence requirements, submission, tracking, and revised report review. All revision requests must avoid any language that suggests, implies, or directs a specific value outcome.

## 2. Prerequisites

| # | Prerequisite | Source |
|---|---|---|
| 1 | Appraisal report reviewed per CRP-PRC-PA-002 | Appraisal review worksheet |
| 2 | Value assessment completed per CRP-PRC-PA-003 (if value-related) | Underwriting worksheet |
| 3 | Specific deficiencies documented with supporting evidence | Reviewer notes |
| 4 | Reviewer trained on appraiser independence requirements (CRP-REG-PA-002) | Training records |

## 3. Procedure Steps

### Step 1: Identify and Document Deficiencies

1.1. Categorize each identified deficiency by type:

| Deficiency Type | Examples | Priority |
|---|---|---|
| Factual Error | Incorrect GLA, wrong year built, incorrect sale price of comparable | High |
| Missing Information | Blank sections, missing photos, incomplete sketch | High |
| Comparable Selection Issue | Inferior comparables available, non-arm's-length sales used without disclosure | Medium |
| Adjustment Concern | Net adjustments exceed 15%, gross exceed 25%, inconsistent adjustments | Medium |
| Form or Compliance Issue | Wrong form type, missing certification, USPAP non-compliance | High |
| Condition or Quality Concern | Rating inconsistent with photos, undisclosed defects visible | Medium |
| Market Analysis Issue | Market trend unsupported by data, outdated market conditions | Low-Medium |

1.2. For each deficiency, prepare the following documentation:
- Clear description of the issue
- Reference to the specific section of the appraisal report
- Supporting evidence (MLS data, public records, photos, prior appraisal data)
- Specific question or request for the appraiser (what needs to be addressed)

1.3. If the deficiency relates to value (reconsideration of value), compile additional comparable sales data:
- Include MLS sheets for suggested comparable sales
- Provide factual property data only (sale price, date, address, property characteristics)
- Do NOT include any statement about what the value should be

### Step 2: Prepare Revision Request

2.1. Draft the revision request using the standardized Appraisal Revision Request Form (Form ARR-100). The form must include:
- Loan number and order reference number
- Appraiser name and license number
- Type of request (correction, completion, reconsideration of value)
- Itemized list of deficiencies with supporting documentation
- Response deadline (aligned with SLA)

2.2. **Critical Compliance Check**: Before submission, verify that the revision request does NOT contain:

| Prohibited Content | Example of Violation |
|---|---|
| Target value or value range | "The value needs to come in at $350,000" |
| Implication of desired outcome | "We need the value to support the purchase price" |
| Pressure language | "The deal will fall through if the value is not adjusted" |
| Directive to change value | "Please reconsider and increase the value" |
| Comparison to purchase price as justification | "The purchase price is $350,000 so the value should be at least that" |

2.3. Acceptable language examples:

| Acceptable Request Language |
|---|
| "Please address why Comparable Sale X at 123 Oak St was not considered, given its proximity and recency" |
| "The GLA reported as 1,800 sq ft appears inconsistent with the sketch dimensions. Please verify." |
| "Please provide additional support for the location adjustment applied to Comparable 2" |
| "The following comparable sales are provided for your consideration: [MLS data attached]" |

2.4. Have a second reviewer (peer or supervisor) review the revision request for independence compliance before submission.

### Step 3: Submit via AMC Portal

3.1. Submit the revision request through the AMC ordering portal using the revision request workflow. Attach all supporting documentation.

3.2. Record the submission timestamp, request type, and assigned tracking number in the appraisal tracking log.

3.3. The AMC is required to forward the request to the original appraiser. If the original appraiser is unavailable (license expired, declined, conflict of interest), the AMC must assign a replacement appraiser of equal or higher credential level.

3.4. Confirm receipt acknowledgment from the AMC within 1 business day.

### Step 4: Track Response Time (5 Business Day SLA)

4.1. The standard SLA for revision request responses is 5 business days from the date the AMC acknowledges receipt.

4.2. Monitoring timeline:

| Day | Action |
|---|---|
| Day 0 | Request submitted and acknowledged |
| Day 3 | If no response, send automated reminder via portal |
| Day 5 | SLA deadline; if no response, escalate to AMC account manager |
| Day 7 | If still unresolved, escalate to VP of Appraisal Operations |
| Day 10 | Consider ordering a new appraisal from a different AMC |

4.3. Track the following metrics for each revision request:
- Request type (correction, completion, reconsideration)
- Turnaround time (business days from submission to response)
- Outcome (revised, no change with explanation, new appraisal ordered)
- Value change (if reconsideration: original value, revised value, delta)

### Step 5: Review Revised Report

5.1. Upon receipt of the appraiser's response, evaluate the revision:

| Response Type | Required Action |
|---|---|
| Full revision (corrected report) | Re-run completeness check per CRP-PRC-PA-002 and value assessment per CRP-PRC-PA-003 |
| Partial revision with explanation | Evaluate whether the explanation adequately addresses the deficiency |
| No change with explanation | Review the appraiser's rationale; determine if it is persuasive and well-supported |
| Appraiser declines to revise | Document rationale; escalate to senior underwriter for determination |

5.2. If the revised report resolves all identified deficiencies, update the appraisal status to "Accepted" and proceed with underwriting.

5.3. If deficiencies remain after revision:
- Determine if a second revision request is warranted (maximum of 2 revision requests per appraisal)
- Consider ordering a second appraisal from a different AMC
- Escalate to manual review per CRP-PRC-PA-005

5.4. Document all revision request activity, responses, and outcomes in the appraisal review worksheet and compliance log.

## 4. Exception Handling

| Exception | Action |
|---|---|
| Appraiser raises independence concern about the request | Compliance review of the request; adjust language if needed |
| Borrower or loan officer provides comparable data for ROV | Acceptable to forward factual MLS data; do not include value commentary |
| Appraiser's license expired between original report and revision | AMC must assign new appraiser; may require new inspection |
| Multiple revision requests on same appraisal | Maximum 2 requests; after 2nd, escalate to manual review or new appraisal |

## 5. Quality Controls

- All revision requests reviewed for independence compliance before submission
- Monthly audit of 15% of revision requests for compliance and appropriateness
- Revision request outcomes tracked as KPIs (acceptance rate, turnaround time, value change frequency)
- AMC responsiveness to revision requests factored into quarterly performance reviews

## 6. References

- CRP-PRC-PA-002: Appraisal Report Review Procedure
- CRP-PRC-PA-003: Property Value Assessment Procedure
- CRP-REG-PA-002: Appraiser Independence Requirements
- CRP-SYS-PA-001: Appraisal Portal Integration Guide
- Dodd-Frank Act Section 1472
- Fannie Mae Selling Guide B4-1.4-01
