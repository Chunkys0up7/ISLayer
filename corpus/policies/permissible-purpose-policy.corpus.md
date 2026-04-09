---
corpus_id: "CRP-POL-MTG-002"
title: "Permissible Purpose Policy (FCRA Compliance)"
slug: "permissible-purpose-policy"
doc_type: "policy"
domain: "Mortgage Lending"
subdomain: "Credit"
tags:
  - "fcra"
  - "permissible-purpose"
  - "credit-authorization"
  - "compliance"
  - "audit-trail"
  - "prohibited-inquiries"
applies_to:
  process_ids:
    - "Process_LoanOrigination"
  task_types:
    - "userTask"
    - "serviceTask"
  task_name_patterns:
    - "pull.*credit"
    - "credit.*authorization"
    - "permissible.*purpose"
  goal_types:
    - "decision"
  roles:
    - "loan_officer"
    - "loan_processor"
    - "compliance_officer"
version: "1.5"
status: "current"
effective_date: "2025-01-01"
review_date: "2026-01-01"
supersedes: null
superseded_by: null
author: "Compliance Department"
last_modified: "2024-12-10"
last_modified_by: "T. Nakamura"
source: "internal"
source_ref: "POL-CR-002"
related_corpus_ids:
  - "CRP-PRC-MTG-003"
  - "CRP-POL-MTG-001"
  - "CRP-DAT-MTG-002"
regulation_refs:
  - "FCRA 15 U.S.C. 1681b"
  - "FCRA 15 U.S.C. 1681n (civil liability for willful noncompliance)"
  - "FCRA 15 U.S.C. 1681o (civil liability for negligent noncompliance)"
  - "CFPB Supervisory Guidance on FCRA Compliance"
policy_refs:
  - "POL-CR-001"
  - "POL-PRIV-001"
---

# Permissible Purpose Policy (FCRA Compliance)

## 1. Policy Statement

Under the Fair Credit Reporting Act (FCRA), a consumer reporting agency may furnish a consumer report only when the requesting party has a permissible purpose as defined in 15 U.S.C. 1681b. This policy establishes the company's requirements for establishing, documenting, and maintaining permissible purpose for all credit report inquiries made in connection with residential mortgage lending activities.

Violation of permissible purpose requirements exposes the company to civil liability under FCRA sections 1681n (willful noncompliance) and 1681o (negligent noncompliance), as well as regulatory enforcement actions from the CFPB and FTC.

## 2. Permissible Purpose for Mortgage Lending

2.1. The company may obtain a consumer credit report for the following permissible purposes related to mortgage lending:

| Permissible Purpose | FCRA Section | Description |
|---------------------|-------------|-------------|
| Written instruction of the consumer | 1681b(a)(2) | Consumer has provided written authorization for the credit inquiry |
| Credit transaction initiation | 1681b(a)(3)(A) | Consumer has initiated a credit transaction (loan application) |
| Review of existing account | 1681b(a)(3)(A) | Review of a consumer's credit in connection with an existing mortgage held by the company |
| Collection of an account | 1681b(a)(3)(A) | In connection with collection of a delinquent mortgage account |

2.2. For new mortgage loan applications, the permissible purpose is established by the combination of:
- A completed loan application (or the six TRID trigger elements)
- A signed credit authorization form from the consumer

Both elements must be present before a credit inquiry is initiated.

## 3. Credit Authorization Requirements

3.1. **Authorization Form:** The borrower must sign a credit authorization form that includes the following elements:
- Borrower's full legal name and Social Security Number
- Clear statement that the borrower authorizes the company to obtain their credit report
- Statement of the purpose (mortgage loan application)
- Date of authorization
- Borrower's signature (wet signature, electronic signature per E-SIGN Act, or verbal authorization with documented consent)

3.2. **Co-Borrower Authorization:** Each co-borrower must provide their own separate authorization. A primary borrower cannot authorize a credit pull on a co-borrower's behalf.

3.3. **Verbal Authorization:** In situations where a signed form is not immediately available (e.g., phone applications), verbal authorization may be accepted provided:
- The call is recorded and the recording is retained
- The loan officer reads the full credit authorization disclosure verbatim
- The borrower provides affirmative verbal consent
- A signed written authorization is obtained within 10 business days
- The verbal authorization is documented in the LOS with the call recording reference

3.4. **Electronic Authorization:** Electronic signatures on credit authorization forms are acceptable under the E-SIGN Act provided:
- The borrower has consented to electronic signatures
- The e-signature system meets E-SIGN Act requirements (intent to sign, consent, record retention)
- An audit trail of the signing event is maintained

## 4. Documentation and Audit Trail

4.1. For every credit report ordered, the following must be documented and retained in the loan file:

| Documentation Item | Description | Retention Location |
|-------------------|-------------|-------------------|
| Signed credit authorization | Physical or electronic authorization form | LOS document management |
| Application evidence | URLA or evidence of the six TRID trigger elements | LOS document management |
| Order timestamp | Date and time the credit report was ordered | LOS credit module (auto-populated) |
| Ordering user | ID of the person who ordered the report | LOS credit module (auto-populated) |
| Permissible purpose code | System code indicating the permissible purpose category | LOS credit module |
| Report receipt | Credit report received and linked to file | LOS document management |

4.2. **Audit Trail Integrity:** The LOS credit ordering module automatically logs all credit inquiry actions. These logs are immutable and cannot be modified by end users. Any discrepancy between the logs and the loan file documentation must be investigated by Compliance.

4.3. **Retention Period:** Credit authorization forms and permissible purpose documentation must be retained for:
- Funded loans: Duration of the loan plus 5 years after payoff
- Withdrawn or denied applications: 25 months from the date of the application (per ECOA record retention)
- Whichever period is longer applies

## 5. Prohibited Inquiries

5.1. The following credit inquiries are prohibited and constitute violations of this policy and FCRA:

| Prohibited Action | Description | FCRA Risk |
|-------------------|-------------|-----------|
| Pre-screening without firm offer | Pulling credit to pre-screen consumers without making a firm offer of credit | 1681b(c) violation |
| Marketing pulls | Using credit data to target consumers for marketing purposes without prescreened offer | 1681b violation |
| Curiosity pulls | Accessing a consumer's credit report without a business purpose or consumer request | 1681b violation; willful noncompliance |
| Post-withdrawal pulls | Ordering a credit report after the borrower has withdrawn their application | Permissible purpose has terminated |
| Unauthorized co-borrower pulls | Pulling credit on a co-borrower without their own separate authorization | 1681b(a)(2) violation |
| Personal credit checks | Employees accessing credit reports for personal reasons | 1681b violation; termination offense |
| Third-party requests | Pulling credit at the request of a real estate agent, builder, or other third party without borrower authorization | 1681b violation |
| Repeat pulls without purpose | Ordering a new credit report when a valid, current report already exists and no business reason requires a new pull | Unnecessary inquiry; may constitute FCRA violation |

5.2. Any employee who knowingly initiates a prohibited credit inquiry is subject to disciplinary action up to and including termination, and may be personally liable under FCRA.

## 6. Adverse Action Requirements

6.1. When a credit report is obtained and results in a negative credit decision (denial, counteroffer, or change in terms), the company must provide an adverse action notice per ECOA Regulation B and FCRA:

- Notice must be provided within 30 days of the credit decision
- Notice must include the specific reasons for the adverse action (up to four reasons)
- Notice must include the name, address, and phone number of each credit bureau that provided data used in the decision
- Notice must inform the consumer of their right to obtain a free copy of their credit report within 60 days
- Notice must inform the consumer of their right to dispute inaccurate information

6.2. If the credit report was a factor in the adverse action, the reasons stated must relate to the credit report findings (e.g., "derogatory credit history," "insufficient credit references," "excessive obligations in relation to income").

## 7. Compliance Monitoring

7.1. The Compliance Department monitors permissible purpose compliance through:

| Monitoring Activity | Frequency | Responsible Party |
|--------------------|-----------|--------------------|
| Random file audits for authorization documentation | Monthly | Compliance Analyst |
| LOS credit inquiry log review | Quarterly | Compliance Manager |
| Adverse action notice review | Quarterly | Compliance Analyst |
| Employee training completion verification | Annually | HR / Compliance |
| Complaint review (CFPB, state AG, direct) | Ongoing | Compliance Officer |

7.2. **Deficiency Findings:** When a permissible purpose deficiency is identified:
- The finding is documented in the compliance tracking system
- The responsible branch or employee is notified within 5 business days
- Corrective action must be completed within 30 days
- Repeat findings within 12 months trigger escalation to senior management

7.3. **FCRA Training:** All employees with access to the credit ordering system must complete annual FCRA compliance training. Training must cover permissible purpose, prohibited inquiries, adverse action requirements, and data security obligations.

## 8. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.5 | 2024-12-10 | T. Nakamura | Added verbal authorization requirements; expanded prohibited inquiries; updated retention periods |
| 1.0 | 2023-05-01 | Compliance Department | Initial release |
