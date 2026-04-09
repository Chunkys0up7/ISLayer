---
corpus_id: "CRP-PRC-PA-002"
title: "Appraisal Report Review Procedure"
slug: "appraisal-report-review"
doc_type: "procedure"
domain: "Mortgage Lending"
subdomain: "Property Appraisal"
tags:
  - "appraisal-review"
  - "uad-xml"
  - "form-1004"
  - "form-1073"
  - "form-2055"
  - "completeness-check"
  - "comparable-selection"
applies_to:
  process_ids:
    - "Process_PropertyAppraisal"
    - "Process_AppraisalReview"
  task_types:
    - "userTask"
    - "businessRuleTask"
  task_name_patterns:
    - "receive.*report"
    - "review.*appraisal"
    - "validate.*completeness"
    - "check.*appraisal.*report"
  goal_types:
    - "validation"
    - "quality_assurance"
  roles:
    - "appraisal_reviewer"
    - "underwriter"
    - "senior_underwriter"
version: "1.3"
status: "current"
effective_date: "2025-06-01"
review_date: "2026-06-01"
supersedes: null
superseded_by: null
author: "Appraisal Operations Committee"
last_modified: "2025-05-10"
last_modified_by: "K. Navarro"
source: "internal"
source_ref: "SOP-PA-2025-002"
related_corpus_ids:
  - "CRP-PRC-PA-001"
  - "CRP-PRC-PA-003"
  - "CRP-PRC-PA-004"
  - "CRP-RUL-PA-001"
  - "CRP-DAT-PA-001"
regulation_refs:
  - "USPAP Standards Rule 2"
  - "Fannie Mae Selling Guide B4-1.2-01"
  - "FHA 4000.1 II.D.3"
policy_refs:
  - "POL-PA-001"
---

# Appraisal Report Review Procedure

## 1. Scope

This procedure defines how to receive, validate, and review an appraisal report delivered by an AMC. It covers format verification, form type validation, completeness checking, photo and sketch review, and comparable sales analysis. The procedure applies to all appraisal reports received for residential mortgage transactions.

## 2. Prerequisites

| # | Prerequisite | Source |
|---|---|---|
| 1 | Appraisal order submitted and tracked per CRP-PRC-PA-001 | Appraisal tracking log |
| 2 | Report received from AMC (PDF + UAD XML) | AMC portal or webhook |
| 3 | Appraisal Completeness Checklist available (CRP-RUL-PA-001) | Reference library |
| 4 | Access to MLS and comparable sales databases | System credentials |

## 3. Procedure Steps

### Step 1: Receive and Register Report

1.1. Retrieve the appraisal report package from the AMC portal. The package must include:
- Appraisal report in PDF format (human-readable)
- UAD XML data file (machine-readable, for automated validation)
- Invoice or fee confirmation

1.2. Verify the file integrity:
- PDF opens without corruption and all pages are legible
- UAD XML parses without schema validation errors
- PDF and XML data are consistent (property address, appraised value, effective date match)

1.3. Register the report in the appraisal tracking system with receipt timestamp. Link the report to the loan file using the loan number and order confirmation number.

1.4. If the report package is incomplete (missing PDF, missing XML, or corrupted files), reject the delivery and notify the AMC within 1 business day for resubmission.

### Step 2: Verify Form Type

2.1. Confirm the correct appraisal form was used based on the property type and loan program:

| Property Type | Standard Form | Exterior-Only Form |
|---|---|---|
| Single-Family Residence (SFR) | Uniform Residential Appraisal Report (Form 1004) | Form 2055 |
| Condominium Unit | Individual Condominium Unit Appraisal Report (Form 1073) | Form 1075 |
| 2-4 Unit Residential | Small Residential Income Property (Form 1025) | Form 2055 |
| Manufactured Housing | Manufactured Home Appraisal Report (Form 1004C) | N/A |

2.2. Verify the form type aligns with the loan program requirements:
- FHA loans require interior inspection (no exterior-only forms except for streamline refinances)
- VA loans require VA-assigned appraiser and VA-specific amendments
- Conventional loans follow Fannie Mae / Freddie Mac form requirements
- Jumbo loans may require enhanced reporting per investor overlay

2.3. If the wrong form type was used, initiate a revision request per CRP-PRC-PA-004.

### Step 3: Check Completeness

3.1. Apply the Appraisal Completeness Checklist (CRP-RUL-PA-001) to verify all required sections are populated. The automated UAD XML validator performs an initial pass; manual review addresses items the validator cannot assess.

3.2. Verify the following critical sections are complete and substantive (not just boilerplate):

| Section | Key Verification Points |
|---|---|
| Subject Property Description | Legal description, census tract, map reference, property rights appraised |
| Neighborhood Analysis | Location rating, built-up percentage, growth rate, property values trend, demand/supply, marketing time |
| Site Description | Lot dimensions, zoning classification, highest and best use determination, utilities, flood zone |
| Improvement Description | Year built, effective age, condition (C1-C6), quality (Q1-Q6), GLA, room count, basement, heating/cooling |
| Sales Comparison Approach | Minimum 3 comparable sales with adjustments, reconciliation narrative |
| Cost Approach | If applicable: reproduction/replacement cost, depreciation, site value |
| Income Approach | If applicable: gross rent multiplier, market rent analysis |
| Reconciliation | Final value conclusion with narrative explanation |
| Appraiser Certification | Signed, dated, license/certification number, USPAP compliance statement |

3.3. For any section that is incomplete, blank, or contains only generic language, flag the deficiency for revision request.

### Step 4: Validate Photos and Sketches

4.1. Confirm the required photographs are included and of acceptable quality:

| Photo Requirement | Count | Quality Standard |
|---|---|---|
| Subject front exterior | 1 | Clear, full structure visible, street number legible if possible |
| Subject rear exterior | 1 | Clear, full rear of structure visible |
| Subject street scene | 1 | Shows street, neighboring properties, overall neighborhood character |
| Subject interior (kitchen) | 1 | Clear, representative of condition |
| Subject interior (living areas) | 2-3 | Main living area, bathrooms, any significant features or deficiencies |
| Each comparable sale exterior | 1 per comp | Clear, front view of comparable property |

4.2. Verify the floor plan sketch:
- Includes all levels (main, upper, basement)
- Shows room labels and dimensions
- Gross Living Area (GLA) calculation is arithmetically correct
- GLA is consistent between sketch, improvement description, and UAD XML
- Non-living areas (garage, porch, basement) are separately identified

4.3. Flag any missing, blurry, or misrepresentative photos. If critical photos are missing (front, rear, or street scene), initiate a revision request.

### Step 5: Review Comparable Selection

5.1. Evaluate the comparable sales selected by the appraiser against these criteria:

| Criterion | Standard |
|---|---|
| Proximity | Preferably within 1 mile (urban/suburban) or 5 miles (rural) |
| Recency | Closed within 6 months (12 months if market data is limited) |
| Similarity | Similar property type, style, age, size, condition, and quality |
| Data source | Verified through MLS, public records, or appraiser inspection |
| Minimum count | 3 closed sales required; 1-2 active listings or pending sales encouraged |

5.2. Independently verify at least one comparable sale using MLS data or public records to confirm accuracy of the reported sale price, sale date, and property characteristics.

5.3. Check for better comparable sales that the appraiser may have omitted. If superior comparables exist within the defined proximity and recency parameters, note this for the value assessment step (CRP-PRC-PA-003) or revision request (CRP-PRC-PA-004).

5.4. Verify that no comparable sale involves a related-party transaction, foreclosure, or short sale without appropriate disclosure and adjustment.

## 4. Exception Handling

| Exception | Action |
|---|---|
| UAD XML fails schema validation | Return to AMC for corrected XML; do not proceed with manual-only review |
| Report received after SLA deadline | Accept report but flag in tracking system; update AMC performance score |
| Appraiser license expired at effective date | Reject report; notify AMC compliance team; order new appraisal |
| Desktop appraisal submitted when interior required | Reject and re-order with correct scope |

## 5. Quality Controls

- UAD XML automated validation catches approximately 80% of completeness issues
- Manual review covers subjective quality areas (narrative adequacy, photo quality, comparable appropriateness)
- Reviewer must document all findings in the appraisal review worksheet
- Review completion target: 2 business days from report receipt

## 6. References

- CRP-RUL-PA-001: Appraisal Completeness Checklist
- CRP-PRC-PA-003: Property Value Assessment Procedure
- CRP-PRC-PA-004: Appraisal Revision Request Procedure
- CRP-DAT-PA-001: Appraisal Report Data Object
- USPAP Standards Rule 2
- Fannie Mae Selling Guide B4-1.2-01
