# Loan Origination - MDA Demo Process

This directory contains a complete MDA Intent Layer demo for a residential mortgage Loan Origination process. It demonstrates the full pipeline from BPMN process model to Intent Layer triples.

## Process Overview

The Loan Origination process covers the intake, verification, and preparation of a residential mortgage loan application for underwriting review. It includes:

- Application receipt and validation
- Borrower identity verification (CIP/OFAC)
- Credit report retrieval and scoring
- Debt-to-income ratio assessment
- Documentation collection loop
- Loan file packaging and underwriting submission

## Directory Structure

```
loan-origination/
  bpmn/                    BPMN 2.0 source model
    loan-origination.bpmn  Process definition XML
    bpmn-metadata.yaml     Source metadata
  triples/                 Intent Layer triples (per task)
    _manifest.json         Index of all triples
    receive-application/   CAP/INT/ICT-LO-APP-001
    verify-identity/       CAP/INT/ICT-LO-IDV-001
    pull-credit/           CAP/INT/ICT-LO-CRC-001
    assess-dti/            CAP/INT/ICT-LO-DTI-001
    request-docs/          CAP/INT/ICT-LO-DOC-001
    package-loan/          CAP/INT/ICT-LO-PKG-001
    submit-underwriting/   CAP/INT/ICT-LO-SUB-001
    timeout-no-response/   CAP/INT/ICT-LO-TMO-001
  decisions/               Decision gateway triples
    loan-eligibility/      CAP/INT/ICT-LO-DEC-001
    docs-received/         CAP/INT/ICT-LO-DEC-002
  graph/                   Process graph representations
    process-graph.yaml     Nodes and edges
    graph-visual.md        Mermaid diagram
  gaps/                    Identified knowledge gaps
    GAP-001.md             Self-employment income calculation
  audit/                   Pipeline audit trail
    ingestion-log.yaml     Ingestion run details
    change-log.yaml        Change history
  mda.config.yaml          Process configuration
```

## Triple Summary

| Triple ID | Task | Type | Goal Type |
|---|---|---|---|
| LO-APP-001 | Receive Loan Application | receiveTask | state_transition |
| LO-IDV-001 | Verify Borrower Identity | serviceTask | data_production |
| LO-CRC-001 | Pull Credit Report | serviceTask | data_production |
| LO-DTI-001 | Assess Debt-to-Income Ratio | businessRuleTask | decision |
| LO-DOC-001 | Request Additional Documentation | sendTask | notification |
| LO-PKG-001 | Package Loan File | task | data_production |
| LO-SUB-001 | Submit to Underwriting | sendTask | notification |
| LO-DEC-001 | Eligible? (gateway) | exclusiveGateway | decision |
| LO-DEC-002 | Docs Received? (gateway) | exclusiveGateway | decision |
| LO-TMO-001 | Timeout - No Response | boundaryEvent | state_transition |

## Regulatory Context

This process operates under the following regulatory framework:

- **TILA / Regulation Z**: Truth in Lending disclosure requirements
- **RESPA / Regulation X**: Real Estate Settlement Procedures
- **ECOA / Regulation B**: Equal Credit Opportunity
- **FCRA / Regulation V**: Fair Credit Reporting
- **HMDA / Regulation C**: Home Mortgage Disclosure Act
- **USA PATRIOT Act Section 326**: Customer Identification Program
- **BSA/AML**: Bank Secrecy Act / Anti-Money Laundering
- **QM Rule**: Qualified Mortgage / Ability-to-Repay

## Status

All triples are in **draft** status with **unbound** integration contracts. This is demo data intended to illustrate the MDA Intent Layer triple structure and is not connected to live systems.
