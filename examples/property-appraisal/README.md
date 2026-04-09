# Property Appraisal Process - MDA Demo Data

This directory contains the complete MDA Intent Layer triple decomposition of the **Property Appraisal** subprocess within mortgage loan origination.

## Process Overview

The Property Appraisal process covers the end-to-end workflow from ordering an appraisal through an Appraisal Management Company (AMC) to finalizing the property valuation for underwriting. The process enforces USPAP compliance, appraiser independence requirements (AIR/Dodd-Frank), and GSE/FHA appraisal standards.

## Directory Structure

```
property-appraisal/
  bpmn/                          BPMN 2.0 process model
    property-appraisal.bpmn      Process definition (XML)
    bpmn-metadata.yaml           Process metadata and element index
  triples/                       Task triples (CAP + INT + ICT)
    _manifest.json               Process-level triple registry
    order-appraisal/             PA-ORD-001: Order Appraisal
    receive-report/              PA-RCV-001: Receive Appraisal Report
    validate-completeness/       PA-VAL-001: Validate Appraisal Completeness
    request-revision/            PA-REV-001: Request Appraisal Revision
    assess-value/                PA-ASV-001: Assess Property Value
    manual-review/               PA-MRV-001: Flag for Manual Review
    emit-complete/               PA-NTF-001: Emit Appraisal Complete Event
  decisions/                     Decision gateway triples
    completeness-check/          PA-DEC-001: Complete?
    ltv-check/                   PA-DEC-002: Value Within LTV?
  graph/                         Process graph representations
    process-graph.yaml           Structured graph (nodes + edges)
    graph-visual.md              Mermaid diagram with lane coloring
  gaps/                          Identified process gaps
    GAP-001.md                   Missing MLS comparable sales validation
  audit/                         Audit and provenance records
    ingestion-log.yaml           Pipeline ingestion record
    change-log.yaml              Version history
  mda.config.yaml                Process configuration
  README.md                      This file
```

## Triple Summary

| Triple ID | Task | Type | Lane |
|-----------|------|------|------|
| PA-ORD-001 | Order Appraisal | sendTask | Loan Processing |
| PA-RCV-001 | Receive Appraisal Report | receiveTask | Appraisal Management |
| PA-VAL-001 | Validate Appraisal Completeness | businessRuleTask | Appraisal Management |
| PA-REV-001 | Request Appraisal Revision | sendTask | Appraisal Management |
| PA-ASV-001 | Assess Property Value | serviceTask | Appraisal Management |
| PA-MRV-001 | Flag for Manual Review | userTask | Underwriting Review |
| PA-NTF-001 | Emit Appraisal Complete Event | sendTask | Loan Processing |
| PA-DEC-001 | Complete? | exclusiveGateway | Appraisal Management |
| PA-DEC-002 | Value Within LTV? | exclusiveGateway | Appraisal Management |

## Key Regulatory References

- **USPAP** - Uniform Standards of Professional Appraisal Practice (Standards Rules 1-3)
- **AIR** - Appraiser Independence Requirements (Dodd-Frank Section 1472)
- **ECOA** - Equal Credit Opportunity Act (appraisal delivery requirements)
- **TRID** - TILA-RESPA Integrated Disclosure (timing requirements)
- **FNMA** - Fannie Mae Selling Guide B4-1 (appraisal requirements)
- **FHA** - FHA Handbook 4000.1 Sections D4-D5 (FHA appraisal requirements)

## Status

All triples are in **draft** status with **unbound** contracts, pending system integration mapping.
