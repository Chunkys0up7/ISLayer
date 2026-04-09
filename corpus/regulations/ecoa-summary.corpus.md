---
corpus_id: "CRP-REG-MTG-003"
title: "Equal Credit Opportunity Act (ECOA) / Regulation B Summary"
slug: "ecoa-summary"
doc_type: "regulation"
domain: "Mortgage Lending"
subdomain: "Compliance"
tags:
  - regulation
  - ECOA
  - RegB
  - fair-lending
  - discrimination
  - adverse-action
  - compliance
applies_to:
  process_ids:
    - "PRC-MTG-ORIG-001"
    - "PRC-MTG-INCV-001"
  task_types:
    - origination
    - underwriting
    - verification
    - compliance
  task_name_patterns:
    - "*_application_*"
    - "*_underwriting_*"
    - "*_decision_*"
    - "*_adverse_*"
    - "*_income_*"
  goal_types:
    - compliance
    - fair_lending
    - consumer_protection
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
source_ref: "12 CFR Part 1002"
related_corpus_ids:
  - "CRP-REG-MTG-002"
  - "CRP-REG-MTG-001"
  - "CRP-GLO-MTG-001"
regulation_refs:
  - "CRP-REG-MTG-002"
policy_refs:
  - "CRP-POL-MTG-010"
---

# Equal Credit Opportunity Act (ECOA) / Regulation B Summary

## Overview

The Equal Credit Opportunity Act (ECOA), enacted in 1974 and implemented by Regulation B (12 CFR Part 1002), prohibits discrimination in any aspect of a credit transaction. It applies to all creditors, including banks, credit unions, finance companies, and mortgage brokers. ECOA ensures that all consumers have an equal opportunity to obtain credit and that credit decisions are based on creditworthiness, not on personal characteristics unrelated to repayment ability.

ECOA is enforced by the CFPB for larger financial institutions and by the appropriate prudential regulator for others. The Department of Justice may bring pattern-or-practice discrimination cases. Violations can result in actual damages, punitive damages (up to $10,000 individual, or the lesser of $500,000 or 1% of net worth for class actions), and injunctive relief.

## Prohibited Bases of Discrimination

A creditor must not discriminate against an applicant on any of the following bases, at any stage of the credit transaction:

| Prohibited Basis | Examples of Prohibited Conduct |
|-------------------|-------------------------------|
| **Race** | Requiring additional documentation based on the applicant's race; offering less favorable terms |
| **Color** | Treating applicants differently based on skin color |
| **Religion** | Denying credit because of religious affiliation or practices |
| **National Origin** | Requiring citizenship or permanent residency beyond what is needed to establish repayment ability; discriminating based on accent or language |
| **Sex** | Offering different rates or terms based on gender; requiring a co-signer based on sex |
| **Marital Status** | Requiring information about a spouse when the applicant applies individually and qualifies alone; different treatment for married vs. unmarried applicants |
| **Age** | Refusing credit solely because the applicant is elderly; using age to assign a negative factor in credit scoring (exception: age may be used in a demonstrably and statistically sound empirical credit scoring system) |
| **Receipt of Public Assistance** | Denying credit because income derives from public assistance programs such as Social Security, TANF, or disability benefits |
| **Exercise of Rights Under CCPA** | Retaliating against an applicant who has exercised rights under the Consumer Credit Protection Act |

## Application Requirements

### Information Collection Rules

| Information | May Collect? | Conditions |
|-------------|-------------|------------|
| Race, ethnicity, sex | Yes (HMDA only) | Must collect for HMDA-reportable applications; must inform applicant that data is for government monitoring and is optional |
| Marital status | Limited | May only ask: married, unmarried, or separated. Cannot ask if divorced or widowed. May ask for marital status when required for property rights assessment in community property states |
| Spouse's information | Limited | May only request if the spouse will be jointly liable, the applicant is relying on the spouse's income, or the applicant resides in a community property state |
| Child-bearing intentions | No | Never permitted. Cannot ask about birth control, family planning, or child-bearing intentions |
| Alimony/child support income | Conditional | Must disclose to applicant that such income need not be revealed unless the applicant wants it considered for qualifying purposes |
| Age | Limited | May collect for HMDA or to verify legal capacity to contract |
| Immigration status | Limited | May inquire about residency status only to determine the creditor's rights and remedies regarding repayment |

### Application Processing Requirements

1. **Completeness Notification**: If an application is incomplete, the creditor must notify the applicant within 30 days and specify what additional information is needed, or provide an adverse action notice.
2. **Counteroffer**: If a creditor makes a counteroffer (approved but at different terms than requested), the applicant must be given the opportunity to accept or reject. If the applicant does not accept, the creditor must provide an adverse action notice.
3. **Withdrawn Applications**: If an applicant withdraws, no adverse action notice is required, but the file must document the voluntary nature of the withdrawal.

## Adverse Action Notices

### When Required

An adverse action notice must be provided when the creditor:
- Denies the credit application
- Approves at terms materially different from those requested (and the applicant does not accept)
- Revokes or changes the terms of an existing credit arrangement
- Refuses to extend additional credit as requested

### Timing

| Scenario | Notice Deadline |
|----------|----------------|
| Completed application, adverse action | Within 30 days of receiving the completed application |
| Incomplete application | Within 30 days of receiving the application, notify of incompleteness or provide adverse action notice |
| Counteroffer not accepted | Within 90 days of the counteroffer notification |
| Existing account, adverse action | Within 30 days of taking the adverse action |

### Required Content

The adverse action notice must include:

1. **Statement of Action Taken**: Clear description of the adverse action (e.g., denial, unfavorable term change)
2. **Specific Reasons or Right to Request**: Either the specific principal reasons for the action (up to 4) or a disclosure of the applicant's right to request specific reasons within 60 days
3. **ECOA Notice**: Statement that federal law prohibits discrimination and that the applicant may contact the CFPB
4. **Creditor Identification**: Name and address of the creditor
5. **Credit Score Disclosure**: If a credit score was used, must disclose the score, range, key factors, and the source of the score

### Specific Reasons for Denial

Reasons must be specific and accurately reflect the factors actually considered. Generic reasons are insufficient. Examples of acceptable specific reasons:

- Income insufficient for the amount of credit requested
- Excessive obligations in relation to income (DTI too high)
- Unable to verify employment
- Length of employment insufficient
- Insufficient credit history
- Delinquent past or present credit obligations
- Number of recent inquiries on credit report
- Value or type of collateral not sufficient (LTV too high)
- Length of residence insufficient

## Income Verification and ECOA Compliance

Income verification processes must comply with ECOA by ensuring equal treatment regardless of income source:

### Protected Income Sources

The following income sources must be considered on equal footing with traditional employment income when evaluating an application:

- Social Security benefits
- Disability benefits (SSDI, private disability insurance)
- Pension and retirement income
- Alimony and child support (if applicant elects to disclose)
- Public assistance income (TANF, SNAP, housing assistance)
- VA benefits
- Part-time employment income
- Investment and rental income

### Income Verification Standards

- Apply the same documentation standards regardless of income source. Do not require additional verification steps for public assistance income that are not required for employment income.
- If verbal verification of employment is performed, apply the same standard to all applicants. Do not selectively perform verbal VOE based on demographic characteristics.
- When calculating qualifying income, apply consistent methods for the same income types across all applicants. Bonus, overtime, and commission income must be evaluated using the same criteria for all applicants.

## Fair Lending Monitoring

### Statistical Testing

Organizations must conduct regular fair lending analyses to detect potential disparate treatment or disparate impact:

| Analysis Type | Frequency | Description |
|---------------|-----------|-------------|
| **Denial Rate Analysis** | Quarterly | Compare denial rates across protected classes, controlling for creditworthiness factors |
| **Pricing Analysis** | Quarterly | Compare APR and fee levels across protected classes for approved loans |
| **Exception Monitoring** | Monthly | Review underwriting exceptions and overrides for patterns of disparate treatment |
| **Comparative File Review** | Semi-annually | Matched-pair analysis of similarly situated applicants from different protected classes |
| **Regression Analysis** | Annually | Multivariate regression on pricing and denial outcomes to identify unexplained disparities |

### Red Flags

- Statistically significant differences in denial rates between protected classes after controlling for credit factors
- Pricing overrides that disproportionately benefit or harm a protected class
- Different documentation requirements applied inconsistently based on applicant demographics
- Marketing or referral patterns that exclude or concentrate protected classes
- Steering applicants to specific products based on demographic characteristics rather than qualification

## Record Retention

Under Regulation B, creditors must retain the following records:

| Record Type | Retention Period |
|------------|-----------------|
| Applications (completed and incomplete) | 25 months after notification of action taken |
| HMDA reporters: applications and records | 36 months after notification |
| Adverse action notices | 25 months after notification |
| Prescreened solicitation records | 25 months from date of solicitation |
| Self-testing records | 25 months after the self-test is completed |
| Information collected for government monitoring (HMDA) | 36 months from date of application |
