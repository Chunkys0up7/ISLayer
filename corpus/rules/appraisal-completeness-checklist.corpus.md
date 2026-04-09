---
corpus_id: "CRP-RUL-PA-001"
title: "Appraisal Completeness Checklist"
slug: "appraisal-completeness-checklist"
doc_type: "rule"
domain: "Mortgage Lending"
subdomain: "Property Appraisal"
tags:
  - "completeness-checklist"
  - "appraisal-validation"
  - "uspap-compliance"
  - "photo-requirements"
  - "comparable-sales"
  - "appraiser-certification"
applies_to:
  process_ids:
    - "Process_PropertyAppraisal"
    - "Process_AppraisalReview"
  task_types:
    - "businessRuleTask"
    - "userTask"
  task_name_patterns:
    - "completeness"
    - "check.*appraisal"
    - "validate.*report"
    - "verify.*sections"
  goal_types:
    - "validation"
  roles:
    - "appraisal_reviewer"
    - "underwriter"
version: "2.0"
status: "current"
effective_date: "2025-06-01"
review_date: "2026-06-01"
supersedes: null
superseded_by: null
author: "Appraisal Operations Committee"
last_modified: "2025-05-08"
last_modified_by: "K. Navarro"
source: "internal"
source_ref: "RUL-PA-2025-001"
related_corpus_ids:
  - "CRP-PRC-PA-002"
  - "CRP-DAT-PA-001"
  - "CRP-REG-PA-001"
regulation_refs:
  - "USPAP Standards Rule 2"
  - "Fannie Mae Selling Guide B4-1.2-01"
  - "FHA 4000.1 II.D.3"
policy_refs:
  - "POL-PA-001"
---

# Appraisal Completeness Checklist

## 1. Purpose

This checklist defines the minimum completeness requirements for an appraisal report to be accepted for underwriting review. It is used during the appraisal report review process (CRP-PRC-PA-002) to systematically verify that all required sections, data elements, photographs, and certifications are present and substantive. Items marked "Critical" must be present for the report to be accepted; items marked "Important" should be present but may be addressed through a revision request if missing.

## 2. Checklist

### Section A: Property Description

| # | Item | Priority | Pass Criteria |
|---|---|---|---|
| A.1 | Property address (street, city, state, ZIP) | Critical | Complete USPS-standardized address; matches loan file |
| A.2 | Legal description | Critical | Present; matches public records |
| A.3 | Census tract number | Important | Present; 11-digit format |
| A.4 | Map reference (tax map, plat) | Important | Present; identifiable reference |
| A.5 | Property rights appraised | Critical | Specified (fee simple, leasehold, other) |
| A.6 | Property type classification | Critical | Matches loan file (SFR, condo, 2-4 unit, manufactured) |
| A.7 | Year built | Critical | Present; consistent with public records |
| A.8 | Gross Living Area (GLA) | Critical | Present; consistent with sketch calculations |
| A.9 | Number of rooms, bedrooms, bathrooms | Critical | Present; consistent with interior photos and sketch |
| A.10 | Basement description | Important | Described (finished/unfinished area, egress, ceiling height) |
| A.11 | Heating and cooling systems | Important | Type and condition noted |
| A.12 | Garage/parking | Important | Type, capacity, and condition noted |

### Section B: Neighborhood Analysis

| # | Item | Priority | Pass Criteria |
|---|---|---|---|
| B.1 | Location classification | Critical | Urban, suburban, or rural selected |
| B.2 | Built-up percentage | Important | Over 75%, 25-75%, or under 25% selected |
| B.3 | Growth rate | Important | Rapid, stable, or slow selected |
| B.4 | Property values trend | Critical | Increasing, stable, or declining selected with narrative support |
| B.5 | Demand/supply balance | Critical | Shortage, in balance, or over supply selected |
| B.6 | Marketing time | Critical | Under 3 months, 3-6 months, or over 6 months selected |
| B.7 | Predominant occupancy | Important | Owner, tenant, or vacant percentages noted |
| B.8 | Single-unit housing price range | Important | Low, high, and predominant values provided |
| B.9 | Neighborhood boundaries | Important | Defined (streets, natural features, or other boundaries) |
| B.10 | Neighborhood description narrative | Critical | Substantive narrative (not just boilerplate); addresses factors affecting value and marketability |

### Section C: Site Description

| # | Item | Priority | Pass Criteria |
|---|---|---|---|
| C.1 | Lot dimensions or area | Critical | Dimensions or acreage provided |
| C.2 | Zoning classification | Critical | Code and description provided; compliant or legally non-conforming noted |
| C.3 | Highest and best use | Critical | As improved and as vacant analysis provided |
| C.4 | Utilities (electric, gas, water, sewer) | Important | Public or private noted for each |
| C.5 | Flood zone designation | Critical | FEMA zone identified; map number and date provided |
| C.6 | Site improvements | Important | Driveway, patio, fence, landscaping noted |
| C.7 | Adverse site conditions | Critical | Any easements, encroachments, environmental hazards disclosed |
| C.8 | View description | Important | Described (residential, commercial, water, mountain, etc.) |

### Section D: Improvement Description

| # | Item | Priority | Pass Criteria |
|---|---|---|---|
| D.1 | Foundation type | Critical | Described (slab, crawl space, basement, pier) |
| D.2 | Exterior walls | Important | Material described (brick, vinyl, wood, stucco) |
| D.3 | Roof type and condition | Important | Material and estimated remaining life |
| D.4 | Interior finish (floors, walls, trim) | Important | Materials and condition described |
| D.5 | Appliances included | Important | Listed (range, refrigerator, dishwasher, etc.) |
| D.6 | Condition rating (C1-C6) | Critical | UAD-compliant rating assigned with narrative support |
| D.7 | Quality rating (Q1-Q6) | Critical | UAD-compliant rating assigned with narrative support |
| D.8 | Effective age | Important | Stated; reasonable relative to actual age and condition |
| D.9 | Remaining economic life | Important | Stated; supports the condition rating |
| D.10 | Functional adequacy | Critical | Any functional obsolescence identified and described |
| D.11 | Physical deficiencies | Critical | Any deferred maintenance or needed repairs itemized |
| D.12 | Energy-efficient items | Important | Noted if present (solar, insulation upgrades, Energy Star) |

### Section E: Comparable Sales

| # | Item | Priority | Pass Criteria |
|---|---|---|---|
| E.1 | Minimum 3 closed comparable sales | Critical | 3+ closed sales with verified sale prices and dates |
| E.2 | Comparable proximity | Critical | Preferably within 1 mile (urban) or 5 miles (rural); explanation if farther |
| E.3 | Comparable recency | Critical | Closed within 6 months preferred; 12 months maximum with explanation |
| E.4 | Comparable data verification | Important | Data source identified (MLS, deed records, appraiser verification) |
| E.5 | Adjustment grid complete | Critical | All adjustment categories populated for each comparable |
| E.6 | Net adjustment within 15% | Important | If exceeded, narrative explanation required |
| E.7 | Gross adjustment within 25% | Important | If exceeded, narrative explanation required |
| E.8 | Active listings or pending sales | Important | At least 1 current listing or pending sale for market support |
| E.9 | Prior sales history of subject | Critical | 3-year sale/transfer history of subject property disclosed |
| E.10 | Prior sales history of comparables | Important | 1-year sale/transfer history of each comparable disclosed |

### Section F: Photographs

| # | Item | Priority | Pass Criteria |
|---|---|---|---|
| F.1 | Subject front exterior photo | Critical | Clear; full structure visible; identifies the property |
| F.2 | Subject rear exterior photo | Critical | Clear; full rear of structure visible |
| F.3 | Subject street scene photo | Critical | Shows street context and neighboring properties |
| F.4 | Subject interior photos | Critical | Kitchen, main living area, bathrooms; minimum 4-6 interior photos |
| F.5 | Photos of any deficiencies or repairs needed | Critical | Each noted deficiency must have a corresponding photo |
| F.6 | Comparable sale exterior photos | Critical | Front exterior photo of each comparable (minimum 3) |
| F.7 | Photo quality | Important | Clear, well-lit, properly oriented; not blurry or dark |
| F.8 | Photo dates | Important | Photos dated and taken within reasonable timeframe of inspection |

### Section G: Sketch and Floor Plan

| # | Item | Priority | Pass Criteria |
|---|---|---|---|
| G.1 | Floor plan sketch present | Critical | Sketch included for all levels |
| G.2 | Room dimensions labeled | Critical | Length and width for each room/area |
| G.3 | GLA calculation shown | Critical | Arithmetic correct; matches reported GLA |
| G.4 | Non-living areas identified | Important | Garage, porch, basement, unfinished areas separately labeled |
| G.5 | Scale and orientation | Important | North arrow and approximate scale indicated |

### Section H: Appraiser Certification and Compliance

| # | Item | Priority | Pass Criteria |
|---|---|---|---|
| H.1 | Appraiser certification signed | Critical | Original signature (or digital equivalent) with date |
| H.2 | Appraiser license/certification number | Critical | Present; valid for subject property state |
| H.3 | License expiration date | Critical | License not expired as of effective date of appraisal |
| H.4 | USPAP compliance statement | Critical | Standard USPAP compliance statement included and signed |
| H.5 | Supervisory appraiser info (if trainee) | Conditional | If trainee appraiser, supervisory appraiser co-signed with credentials |
| H.6 | Prior inspection disclosure | Important | Appraiser discloses whether they previously inspected or appraised the subject |
| H.7 | Appraiser independence certification | Critical | No undisclosed interest in subject; no outcome-based compensation |
| H.8 | Effective date of appraisal | Critical | Present; aligns with inspection date |

## 3. Scoring and Decision

| Result | Criteria | Action |
|---|---|---|
| **Pass** | All Critical items pass; no more than 3 Important items missing | Proceed to value assessment (CRP-PRC-PA-003) |
| **Conditional Pass** | All Critical items pass; 4+ Important items missing | Proceed to value assessment; initiate revision request for missing items (CRP-PRC-PA-004) |
| **Fail** | 1+ Critical items fail | Reject report; initiate revision request for all deficiencies (CRP-PRC-PA-004) |

## 4. References

- CRP-PRC-PA-002: Appraisal Report Review Procedure
- CRP-DAT-PA-001: Appraisal Report Data Object
- CRP-REG-PA-001: USPAP Standards Summary
- USPAP Standards Rule 2
- Fannie Mae Selling Guide B4-1.2-01
