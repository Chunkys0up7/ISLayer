---
corpus_id: "CRP-REG-MTG-001"
title: "Fair Credit Reporting Act (FCRA) / Regulation V Summary"
slug: "fcra-summary"
doc_type: "regulation"
domain: "Mortgage Lending"
subdomain: "Compliance"
tags:
  - regulation
  - FCRA
  - RegV
  - credit-reporting
  - consumer-rights
  - compliance
  - permissible-purpose
applies_to:
  process_ids:
    - "PRC-MTG-ORIG-001"
  task_types:
    - origination
    - underwriting
    - credit_check
    - compliance
  task_name_patterns:
    - "*_credit_*"
    - "*_underwriting_*"
    - "*_application_*"
  goal_types:
    - compliance
    - consumer_protection
    - credit_reporting
  roles:
    - loan_officer
    - underwriter
    - compliance_officer
    - loan_processor
version: "1.0"
status: "current"
effective_date: "2026-01-01"
review_date: "2026-07-01"
supersedes: null
superseded_by: null
author: "MDA Demo"
last_modified: "2026-04-09"
last_modified_by: "MDA Demo"
source: "regulatory"
source_ref: "15 USC 1681; 12 CFR Part 1022"
related_corpus_ids:
  - "CRP-REG-MTG-002"
  - "CRP-REG-MTG-003"
  - "CRP-GLO-MTG-001"
regulation_refs:
  - "CRP-REG-MTG-003"
policy_refs:
  - "CRP-POL-MTG-010"
---

# Fair Credit Reporting Act (FCRA) / Regulation V Summary

## Overview

The Fair Credit Reporting Act (FCRA), enacted in 1970 and amended multiple times (most significantly by the Fair and Accurate Credit Transactions Act of 2003), regulates the collection, dissemination, and use of consumer credit information. Regulation V (12 CFR Part 1022) implements the FCRA. For mortgage lenders, the FCRA governs how consumer credit reports are obtained, used, and the disclosures that must be provided to borrowers regarding credit decisions.

The FCRA is enforced by the CFPB, the FTC, and state attorneys general. Violations can result in statutory damages ($100 to $1,000 per consumer for willful violations), actual damages, punitive damages, and attorney's fees.

## Permissible Purpose

A consumer reporting agency may furnish a consumer report only to a person who has a permissible purpose under Section 604 of the FCRA. For mortgage lending, the relevant permissible purposes are:

### Credit Transaction

A creditor may obtain a consumer report in connection with a credit transaction involving the consumer. This is the primary basis for pulling credit reports in mortgage lending. The credit transaction must be initiated by a bona fide application from the consumer.

**Key Requirements**:
- A signed authorization from the borrower must be obtained before pulling credit. The URLA (1003) contains a standard credit authorization.
- The authorization must specifically identify the types of reports that may be obtained (credit report, employment verification, etc.)
- Credit reports pulled for mortgage purposes result in "hard inquiries" that may affect the consumer's credit score

### Legitimate Business Need

A creditor may obtain a consumer report when it has a legitimate business need in connection with a business transaction initiated by the consumer. This may apply to pre-qualification activities but requires careful documentation.

### Written Instruction of the Consumer

A consumer may authorize the release of their credit report through written instruction. This must be specific and voluntary.

## Tri-Merge Credit Reports

Mortgage lending standard practice requires a tri-merge (three-bureau) credit report pulling data from Equifax, Experian, and TransUnion. The representative credit score used for underwriting is determined as follows:

| Borrowers | Score Selection Method |
|-----------|----------------------|
| Single borrower, 3 scores | Use the middle score |
| Single borrower, 2 scores | Use the lower score |
| Single borrower, 1 score | Use the single available score |
| Multiple borrowers | Use the lowest representative score among all borrowers for qualification |

### Credit Report Validity

| Report Type | Validity Period | Extension |
|------------|----------------|-----------|
| Standard tri-merge | 120 days from date of issue | May be updated/refreshed rather than re-pulled |
| FHA loans | 120 days | Must be refreshed if closing beyond 120 days |
| VA loans | 120 days | Same as standard |
| Credit refresh/supplement | Extends validity for 30 additional days | One refresh permitted |

## Consumer Rights and Disclosures

### Pre-Screening Disclosure

When credit reports are used for pre-screened or pre-approved offers (firm offers of credit), the lender must provide:
- Clear identification as a pre-screened offer
- Statement that the consumer's credit was accessed
- Opt-out notice (consumer can opt out of future pre-screened offers)

### Adverse Action Disclosures (Credit-Based)

When a credit report is used in making an adverse action decision, the lender must provide under FCRA Section 615(a):

1. **Notice of Adverse Action**: Statement that adverse action was taken
2. **CRA Identification**: Name, address, and phone number of the consumer reporting agency that furnished the report
3. **CRA Did Not Make Decision**: Statement that the CRA did not make the adverse decision and cannot explain the specific reasons
4. **Right to Free Report**: Notice that the consumer is entitled to a free copy of the report within 60 days
5. **Right to Dispute**: Notice of the consumer's right to dispute inaccurate information in the report

**Credit Score Disclosure Requirements** (under FACTA amendments):
- The credit score(s) used in the decision
- The range of possible scores under the scoring model
- Up to four key factors that adversely affected the score (in order of importance)
- The date the score was created
- The name of the entity that provided the score

### Risk-Based Pricing Notices

When a consumer receives less favorable credit terms (higher interest rate) than the lender's best terms based in whole or in part on the consumer's credit report, a risk-based pricing notice must be provided. Alternatively, lenders may use the Credit Score Disclosure Exception by providing all applicants with a credit score disclosure notice.

**Credit Score Disclosure Exception** (most common method in mortgage lending):
- Provide to all applicants, not just those receiving adverse terms
- Include the credit score, score range, key factors, and date
- Eliminates the need to determine which applicants received "materially less favorable" terms

## Accuracy and Dispute Requirements

### Furnisher Obligations

Lenders who report consumer credit information to CRAs (as furnishers) must:

1. **Accuracy**: Report information accurately and completely. Establish and maintain reasonable policies and procedures regarding the accuracy and integrity of information furnished to CRAs.
2. **Investigation of Disputes**: When a consumer disputes information directly with the furnisher or through a CRA, the furnisher must:
   - Conduct a reasonable investigation within 30 days (45 days if additional information is provided)
   - Review all relevant information provided by the consumer or CRA
   - Report results to the CRA that forwarded the dispute
   - Correct, delete, or modify information found to be inaccurate, incomplete, or unverifiable
3. **Notice of Dispute**: When a consumer disputes information, the furnisher must note the dispute status on the trade line
4. **Duty After Notice of Inaccuracy**: If a furnisher determines reported information is inaccurate, it must promptly notify each CRA to which it reported

### Consumer Dispute Process in Mortgage Context

When a borrower disputes credit information during the mortgage process:

| Step | Action | Timeline |
|------|--------|----------|
| 1 | Borrower identifies disputed item to loan officer | During application/processing |
| 2 | Loan officer documents dispute with borrower's written explanation | Within 2 business days |
| 3 | Credit supplement ordered if needed to update/correct information | Within 3 business days |
| 4 | If not resolvable via supplement, formal dispute filed with CRA | Consumer's option |
| 5 | CRA investigation completed | 30 days (or 45 with additional info) |
| 6 | Updated credit report obtained if dispute results in changes | After resolution |
| 7 | Underwriting re-evaluates with corrected information | Upon receipt |

## Identity Theft and Fraud Prevention

### Red Flags Rule

Financial institutions and creditors must develop and implement a written Identity Theft Prevention Program (Red Flags Program) that:
- Identifies relevant patterns, practices, and specific forms of activity ("red flags") indicating possible identity theft
- Detects red flags incorporated into the program
- Responds appropriately to detected red flags to prevent and mitigate identity theft
- Updates the program periodically to reflect changes in risks

### Common Red Flags in Mortgage Lending

| Category | Red Flag |
|----------|----------|
| **Document Alerts** | Documents appear altered or forged; SSN does not match credit file |
| **Application Alerts** | Applicant's address does not match credit report; phone number matches a known fraud number |
| **Credit Report Alerts** | Fraud alert on credit report; credit freeze in place; recent spike in inquiries |
| **Account Activity** | Multiple applications with same SSN but different names; employer cannot verify employment |
| **Third-Party Alerts** | Identity theft report filed with FTC; law enforcement notification |

### Fraud Alert Handling

When a credit report is obtained with an active fraud alert:
1. **Standard Fraud Alert**: The creditor must take reasonable steps to verify the identity of the applicant before extending credit. This includes contacting the consumer using the phone number in the alert or taking other reasonable steps.
2. **Extended Fraud Alert**: The creditor must contact the consumer in person or via the phone number provided in the alert before extending credit.
3. **Active Duty Alert**: Same requirements as extended fraud alert for military personnel.

## Record Retention

| Record Type | Retention Period | Regulatory Basis |
|------------|-----------------|-----------------|
| Credit reports obtained | 7 years from loan closing or denial | Company policy (FCRA requires reasonable period) |
| Credit authorization forms | 7 years from loan closing or denial | Company policy |
| Adverse action notices (credit-based) | 25 months per Reg B; 7 years per company policy | ECOA/FCRA overlap |
| Credit score disclosures | 7 years from date of disclosure | Company policy |
| Dispute documentation | 7 years from resolution | Company policy |
| Red flag detection records | 5 years from date of detection | Company policy |
| Permissible purpose documentation | 7 years from date credit was accessed | FCRA best practice |
