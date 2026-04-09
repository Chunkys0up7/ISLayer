---
corpus_id: "CRP-DAT-PA-001"
title: "Appraisal Report Data Object"
slug: "appraisal-report-data"
doc_type: "data-dictionary"
domain: "Mortgage Lending"
subdomain: "Property Appraisal"
tags:
  - "appraisal-report"
  - "data-object"
  - "uad"
  - "condition-rating"
  - "quality-rating"
  - "comparable-sales"
  - "appraiser-info"
  - "mismo"
applies_to:
  process_ids:
    - "Process_PropertyAppraisal"
  task_types:
    - "serviceTask"
    - "businessRuleTask"
    - "userTask"
  task_name_patterns:
    - ".*appraisal.*"
  goal_types:
    - "data_production"
    - "validation"
  roles:
    - "appraisal_reviewer"
    - "underwriter"
    - "loan_processor"
    - "data_analyst"
version: "2.0"
status: "current"
effective_date: "2025-06-01"
review_date: "2026-06-01"
supersedes: null
superseded_by: null
author: "Data Architecture Team"
last_modified: "2025-05-10"
last_modified_by: "A. Patel"
source: "internal"
source_ref: "DAT-PA-2025-001"
related_corpus_ids:
  - "CRP-PRC-PA-002"
  - "CRP-PRC-PA-003"
  - "CRP-RUL-PA-001"
  - "CRP-SYS-PA-001"
regulation_refs:
  - "MISMO Reference Model v3.4"
  - "UAD Specification (Fannie Mae / Freddie Mac)"
policy_refs:
  - "POL-DA-001"
---

# Appraisal Report Data Object

## 1. Overview

This document defines the canonical data object representing an appraisal report within the mortgage lending system. The data object is populated from UAD XML received from AMCs, supplemented by manual entry for fields not captured in the UAD format. It serves as the primary data structure for appraisal review, value assessment, underwriting, and compliance reporting.

## 2. Object: AppraisalReport

### 2.1 Core Identification Fields

| Field Name | Data Type | Length/Format | Required | Description |
|---|---|---|---|---|
| report_id | String | UUID v4 | Yes | System-generated unique identifier for the appraisal report |
| order_id | String | UUID v4 | Yes | Reference to the originating appraisal order |
| loan_number | String | 10-20 chars | Yes | Associated loan file number |
| amc_reference_number | String | Up to 30 chars | Yes | AMC's internal order/report reference number |
| report_status | Enum | See enum table | Yes | Current status of the report in the review workflow |

**report_status Enum Values:**

| Value | Description |
|---|---|
| RECEIVED | Report received from AMC, pending initial review |
| IN_REVIEW | Report assigned to reviewer, review in progress |
| REVISION_REQUESTED | Deficiencies identified; revision request sent to AMC |
| REVISED_RECEIVED | Revised report received from AMC |
| ACCEPTED | Report reviewed and accepted for underwriting |
| REJECTED | Report rejected (unresolvable deficiencies or independence concern) |
| SUPERSEDED | Report replaced by a new appraisal |

### 2.2 Property Information Fields

| Field Name | Data Type | Length/Format | Required | Description |
|---|---|---|---|---|
| property_address | Object | See sub-fields | Yes | Standardized property address |
| property_address.street | String | Up to 100 chars | Yes | Street number and name (USPS standardized) |
| property_address.unit | String | Up to 20 chars | No | Unit, suite, or apartment number |
| property_address.city | String | Up to 50 chars | Yes | City name |
| property_address.state | String | 2 chars (ISO 3166-2:US) | Yes | State abbreviation |
| property_address.zip_code | String | 5 or 10 chars (ZIP+4) | Yes | ZIP code |
| property_address.county | String | Up to 50 chars | Yes | County name |
| property_type | Enum | SFR, CONDO, 2UNIT, 3UNIT, 4UNIT, MFH, COOP, PUD, MIXED | Yes | Property type classification |
| legal_description | String | Up to 500 chars | Yes | Legal description from public records |
| census_tract | String | 11 digits | Yes | Census tract number |
| map_reference | String | Up to 50 chars | No | Tax map or plat reference |
| property_rights_appraised | Enum | FEE_SIMPLE, LEASEHOLD, OTHER | Yes | Property rights being appraised |
| year_built | Integer | 4 digits (YYYY) | Yes | Original year of construction |
| effective_age | Integer | Years | Yes | Effective age as determined by appraiser |
| gla_sqft | Decimal | Up to 99999.99 | Yes | Gross Living Area in square feet |
| lot_size | Decimal | Acres or sq ft | Yes | Lot size (specify unit in lot_size_unit) |
| lot_size_unit | Enum | ACRES, SQFT | Yes | Unit of measurement for lot_size |
| room_count | Integer | 1-99 | Yes | Total number of rooms |
| bedroom_count | Integer | 0-99 | Yes | Number of bedrooms |
| bathroom_count | Decimal | 0.0-99.5 | Yes | Number of bathrooms (half-baths = 0.5) |
| basement_type | Enum | FULL, PARTIAL, CRAWL, SLAB, NONE | Yes | Basement configuration |
| basement_finished_sqft | Decimal | Up to 99999.99 | Conditional | Finished basement area (required if basement_type is FULL or PARTIAL) |
| garage_type | Enum | ATTACHED, DETACHED, BUILT_IN, CARPORT, NONE | Yes | Garage configuration |
| garage_capacity | Integer | 0-9 | Yes | Number of car spaces |
| flood_zone | String | Up to 10 chars | Yes | FEMA flood zone designation (e.g., X, A, AE, V) |

### 2.3 Valuation Fields

| Field Name | Data Type | Length/Format | Required | Description |
|---|---|---|---|---|
| appraised_value | Decimal | Currency (USD) | Yes | Final reconciled appraised value |
| effective_date | Date | YYYY-MM-DD | Yes | Effective date of the appraisal (typically inspection date) |
| report_date | Date | YYYY-MM-DD | Yes | Date the report was signed |
| form_type | Enum | 1004, 1073, 1025, 1004C, 2055, 1075, DESKTOP | Yes | Appraisal form type used |
| cost_approach_value | Decimal | Currency (USD) | No | Value indication from cost approach |
| income_approach_value | Decimal | Currency (USD) | No | Value indication from income approach |
| sales_comparison_value | Decimal | Currency (USD) | Yes | Value indication from sales comparison approach |
| condition_rating | Enum | C1, C2, C3, C4, C5, C6 | Yes | UAD condition rating |
| quality_rating | Enum | Q1, Q2, Q3, Q4, Q5, Q6 | Yes | UAD quality rating |
| market_conditions | Enum | INCREASING, STABLE, DECLINING | Yes | Neighborhood property values trend |
| highest_best_use | Enum | PRESENT_USE, OTHER | Yes | Highest and best use determination |

**Condition Rating Definitions:**

| Rating | Description |
|---|---|
| C1 | New construction; all components are new and no physical depreciation |
| C2 | Recently built or completely renovated; no deferred maintenance |
| C3 | Well-maintained; limited physical depreciation due to normal wear |
| C4 | Adequately maintained; some minor deferred maintenance |
| C5 | Obvious deferred maintenance; some items approaching end of useful life |
| C6 | Substantial damage or deferred maintenance; major systems need replacement |

**Quality Rating Definitions:**

| Rating | Description |
|---|---|
| Q1 | Unique, custom design and construction; highest quality materials and workmanship |
| Q2 | Custom design for individual owners; high quality materials and workmanship |
| Q3 | Well-designed and built; above-standard quality materials and workmanship |
| Q4 | Standard quality construction; common design and materials for the market area |
| Q5 | Economy quality construction; minimal design and basic materials |
| Q6 | Below minimum quality; may not meet building codes; substandard materials |

### 2.4 Comparable Sales Array

| Field Name | Data Type | Length/Format | Required | Description |
|---|---|---|---|---|
| comparable_sales[] | Array | Min 3 elements | Yes | Array of comparable sale records |
| comparable_sales[].comp_number | Integer | 1-6 | Yes | Comparable sale number (1-based) |
| comparable_sales[].address | String | Up to 150 chars | Yes | Comparable property address |
| comparable_sales[].sale_price | Decimal | Currency (USD) | Yes | Recorded sale price |
| comparable_sales[].sale_date | Date | YYYY-MM-DD | Yes | Date of sale (closing date) |
| comparable_sales[].data_source | String | Up to 50 chars | Yes | MLS number, deed book reference, or other verification |
| comparable_sales[].proximity_miles | Decimal | Up to 99.99 | Yes | Distance from subject property in miles |
| comparable_sales[].gla_sqft | Decimal | Up to 99999.99 | Yes | Comparable GLA in square feet |
| comparable_sales[].lot_size | Decimal | Acres or sq ft | Yes | Comparable lot size |
| comparable_sales[].year_built | Integer | YYYY | Yes | Comparable year built |
| comparable_sales[].condition_rating | Enum | C1-C6 | Yes | Comparable condition rating |
| comparable_sales[].quality_rating | Enum | Q1-Q6 | Yes | Comparable quality rating |
| comparable_sales[].adjusted_price | Decimal | Currency (USD) | Yes | Sale price after all adjustments |
| comparable_sales[].is_arms_length | Boolean | true/false | Yes | Whether the sale was an arm's-length transaction |

### 2.5 Adjustments Array

| Field Name | Data Type | Length/Format | Required | Description |
|---|---|---|---|---|
| adjustments[] | Array | Nested within comparable_sales[] | Yes | Array of adjustment records per comparable |
| adjustments[].category | Enum | See enum table | Yes | Adjustment category |
| adjustments[].amount | Decimal | Currency (USD), signed | Yes | Adjustment amount (positive = subject superior, negative = comp superior) |
| adjustments[].description | String | Up to 200 chars | No | Narrative description of adjustment basis |

**Adjustment Category Enum Values:**

| Value | Description |
|---|---|
| LOCATION | Location or neighborhood adjustment |
| SITE_VIEW | Site size or view adjustment |
| DESIGN_APPEAL | Design, style, or appeal adjustment |
| QUALITY | Quality of construction adjustment |
| AGE | Actual or effective age adjustment |
| CONDITION | Condition adjustment |
| GLA | Gross Living Area size adjustment |
| BASEMENT | Basement finish or size adjustment |
| FUNCTIONAL | Functional utility adjustment |
| HEATING_COOLING | Heating and cooling system adjustment |
| GARAGE_CARPORT | Garage or carport adjustment |
| PORCH_DECK | Porch, patio, or deck adjustment |
| CONCESSIONS | Sales or financing concession adjustment |
| OTHER | Other adjustment (must include description) |

### 2.6 Photos Array

| Field Name | Data Type | Length/Format | Required | Description |
|---|---|---|---|---|
| photos[] | Array | Min 7 elements | Yes | Array of appraisal photographs |
| photos[].photo_id | String | UUID v4 | Yes | Unique identifier for the photo |
| photos[].photo_type | Enum | FRONT, REAR, STREET, INTERIOR, DEFICIENCY, COMP_FRONT | Yes | Type/purpose of photo |
| photos[].file_path | String | URL or file path | Yes | Location of the photo file |
| photos[].caption | String | Up to 200 chars | No | Photo caption or description |
| photos[].date_taken | Date | YYYY-MM-DD | Yes | Date the photo was taken |
| photos[].comparable_ref | Integer | 1-6 | Conditional | If photo_type is COMP_FRONT, reference to comparable number |

### 2.7 Appraiser Information

| Field Name | Data Type | Length/Format | Required | Description |
|---|---|---|---|---|
| appraiser_info | Object | See sub-fields | Yes | Appraiser identification and credentials |
| appraiser_info.name | String | Up to 100 chars | Yes | Appraiser full name |
| appraiser_info.license_number | String | Up to 30 chars | Yes | State license or certification number |
| appraiser_info.license_state | String | 2 chars | Yes | State of licensure |
| appraiser_info.license_type | Enum | LICENSED, CERTIFIED_RESIDENTIAL, CERTIFIED_GENERAL | Yes | Level of appraiser credential |
| appraiser_info.license_expiration | Date | YYYY-MM-DD | Yes | License expiration date |
| appraiser_info.company_name | String | Up to 100 chars | No | Appraiser's company or firm name |
| appraiser_info.phone | String | Phone format | No | Appraiser contact phone |
| appraiser_info.email | String | Email format | No | Appraiser contact email |
| appraiser_info.is_trainee | Boolean | true/false | Yes | Whether the appraiser is a trainee |
| appraiser_info.supervisor_name | String | Up to 100 chars | Conditional | Supervisory appraiser name (required if is_trainee = true) |
| appraiser_info.supervisor_license | String | Up to 30 chars | Conditional | Supervisor license number (required if is_trainee = true) |

### 2.8 Certification Status

| Field Name | Data Type | Length/Format | Required | Description |
|---|---|---|---|---|
| certification_status | Object | See sub-fields | Yes | Appraiser certification and compliance |
| certification_status.signed | Boolean | true/false | Yes | Whether the certification is signed |
| certification_status.signature_date | Date | YYYY-MM-DD | Yes | Date of appraiser signature |
| certification_status.uspap_compliant | Boolean | true/false | Yes | USPAP compliance statement included |
| certification_status.inspection_type | Enum | INTERIOR, EXTERIOR_ONLY, DESKTOP | Yes | Type of inspection performed |
| certification_status.inspection_date | Date | YYYY-MM-DD | Yes | Date of property inspection |
| certification_status.extraordinary_assumptions | String | Up to 1000 chars | No | Any extraordinary assumptions stated |
| certification_status.hypothetical_conditions | String | Up to 1000 chars | No | Any hypothetical conditions stated |
| certification_status.prior_services_disclosure | Boolean | true/false | Yes | Whether appraiser disclosed prior services for the subject |

### 2.9 Calculated and Derived Fields

| Field Name | Data Type | Calculation | Description |
|---|---|---|---|
| net_adjustment_pct[] | Decimal[] | Per comparable: \|sum of adjustments\| / sale_price x 100 | Net adjustment percentage for each comparable |
| gross_adjustment_pct[] | Decimal[] | Per comparable: sum of \|each adjustment\| / sale_price x 100 | Gross adjustment percentage for each comparable |
| ltv_ratio | Decimal | loan_amount / base_value x 100 | Calculated LTV ratio |
| avm_variance_pct | Decimal | (appraised_value - avm_value) / avm_value x 100 | Variance between appraised value and AVM |
| days_since_inspection | Integer | current_date - inspection_date | Days elapsed since property inspection |

## 3. Data Validation Rules

| Rule ID | Field(s) | Validation | Severity |
|---|---|---|---|
| V-001 | appraised_value | Must be > 0 | Error |
| V-002 | effective_date | Must not be in the future | Error |
| V-003 | comparable_sales[] | Array length >= 3 | Error |
| V-004 | form_type | Must match property_type (e.g., 1004 for SFR, 1073 for CONDO) | Error |
| V-005 | gla_sqft | Must be > 0 and < 50,000 | Error |
| V-006 | condition_rating | Must be valid UAD code (C1-C6) | Error |
| V-007 | quality_rating | Must be valid UAD code (Q1-Q6) | Error |
| V-008 | appraiser_info.license_expiration | Must be >= effective_date | Error |
| V-009 | certification_status.signed | Must be true | Error |
| V-010 | net_adjustment_pct[] | Warning if any > 15% | Warning |
| V-011 | gross_adjustment_pct[] | Warning if any > 25% | Warning |
| V-012 | photos[] | Must include FRONT, REAR, STREET types | Error |
| V-013 | comparable_sales[].proximity_miles | Warning if > 1.0 (urban) or > 5.0 (rural) | Warning |
| V-014 | comparable_sales[].sale_date | Warning if > 180 days before effective_date | Warning |

## 4. Data Sources and Mapping

| Source System | Fields Populated | Format |
|---|---|---|
| AMC Portal (UAD XML) | All valuation, property, comparable, and appraiser fields | MISMO XML v3.4 |
| AMC Portal (PDF) | Photos, sketches (as image files) | PDF extraction |
| Loan Origination System | loan_number, property_address (for cross-reference) | Internal API |
| AVM Service | avm_value (for variance calculation) | API response |
| Appraisal Tracking System | report_status, order_id, reviewer assignments | Internal database |

## 5. References

- CRP-PRC-PA-002: Appraisal Report Review Procedure
- CRP-PRC-PA-003: Property Value Assessment Procedure
- CRP-RUL-PA-001: Appraisal Completeness Checklist
- CRP-SYS-PA-001: Appraisal Portal Integration Guide
- MISMO Reference Model v3.4
- UAD Specification (Fannie Mae / Freddie Mac)
