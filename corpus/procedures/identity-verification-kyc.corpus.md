---
corpus_id: "CRP-PRC-MTG-002"
title: "Identity Verification Procedure (KYC/BSA)"
slug: "identity-verification-kyc"
doc_type: "procedure"
domain: "Mortgage Lending"
subdomain: "Loan Origination"
tags:
  - "kyc"
  - "bsa"
  - "identity-verification"
  - "ofac"
  - "ssn-validation"
  - "fraud-prevention"
  - "aml"
  - "cip"
applies_to:
  process_ids:
    - "Process_LoanOrigination"
  task_types:
    - "userTask"
    - "serviceTask"
  task_name_patterns:
    - "verify.*identity"
    - "kyc.*check"
    - "ofac.*screen"
    - "validate.*ssn"
    - "identity.*fraud"
  goal_types:
    - "data_production"
    - "decision"
  roles:
    - "loan_processor"
    - "compliance_officer"
    - "intake_specialist"
version: "2.0"
status: "current"
effective_date: "2025-04-01"
review_date: "2026-04-01"
supersedes: null
superseded_by: null
author: "Compliance Department"
last_modified: "2025-03-18"
last_modified_by: "T. Nakamura"
source: "internal"
source_ref: "SOP-KYC-2025-001"
related_corpus_ids:
  - "CRP-PRC-MTG-001"
  - "CRP-PRC-MTG-003"
  - "CRP-RUL-MTG-001"
regulation_refs:
  - "USA PATRIOT Act Section 326"
  - "BSA/AML 31 CFR 1010.220"
  - "OFAC SDN List Screening Requirements"
  - "FinCEN CIP Rule"
  - "Red Flags Rule 16 CFR 681"
policy_refs:
  - "POL-BSA-001"
  - "POL-FRAUD-001"
---

# Identity Verification Procedure (KYC/BSA)

## 1. Scope

This procedure establishes the requirements for verifying the identity of all borrowers, co-borrowers, and guarantors on residential mortgage loan applications. It implements the Customer Identification Program (CIP) requirements under the USA PATRIOT Act and the Bank Secrecy Act (BSA), as well as OFAC screening obligations. The procedure applies to all loan programs and transaction types.

Identity verification must be completed before any credit inquiry is ordered or any substantive underwriting work begins.

## 2. Prerequisites

| # | Prerequisite | Source |
|---|---|---|
| 1 | Completed loan application with borrower name, DOB, and SSN | Application file |
| 2 | Government-issued photo identification | Borrower |
| 3 | Access to SSA verification system (CBSV or SSN Verification Service) | System |
| 4 | Access to OFAC screening tool | System |
| 5 | Current address documentation (utility bill, bank statement, or lease) | Borrower |
| 6 | Identity verification authorization signed by borrower | Borrower |

## 3. Procedure Steps

### Step 1: Verify Social Security Number (SSN)

1.1. Obtain the borrower's full nine-digit Social Security Number from the loan application.

1.2. Submit the SSN for verification against the Social Security Administration (SSA) database using one of the following methods:
- **Consent Based SSN Verification (CBSV):** Preferred method. Requires signed Form SSA-89 from borrower. Returns name/SSN match confirmation.
- **SSN Verification Service (SSNVS):** Batch verification for volume processing. Returns match/no-match only.
- **IRS IVES transcript request:** Tax transcript ordering implicitly validates SSN-to-name association.

1.3. Evaluate the verification result:
- **Match:** SSN, name, and date of birth match SSA records. Proceed to Step 2.
- **No match on name:** May indicate a name change, typographical error, or identity issue. Request explanation and supporting documentation (name change court order, marriage certificate).
- **SSN not issued / deceased indicator:** Immediately escalate to the BSA/AML officer. Do not proceed with the application. File a Suspicious Activity Report (SAR) if fraud is suspected.
- **SSN issued before borrower DOB:** Escalate as potential identity theft or SSN fraud.

1.4. Document the SSN verification result, method used, and date in the LOS compliance tab.

### Step 2: Verify Government-Issued Photo Identification

2.1. Obtain a copy of the borrower's unexpired government-issued photo identification. Acceptable forms of ID include:

| ID Type | Requirements | Notes |
|---------|-------------|-------|
| State driver's license | Current, unexpired, with photo | Most common; verify holographic features |
| State identification card | Current, unexpired, with photo | Accepted in lieu of driver's license |
| US Passport | Current, unexpired | Preferred for non-resident aliens |
| US Passport Card | Current, unexpired | Accepted same as passport |
| Military ID (CAC) | Current, active duty or reserve | Must include photo and DOB |
| Permanent Resident Card (Green Card) | Current, unexpired | Verify USCIS number |

2.2. For each presented ID, verify the following:
- Name matches the loan application (or documented name variation)
- Photo reasonably resembles the borrower (for in-person applications)
- Date of birth matches the application
- ID is not expired (expired IDs are not acceptable under CIP)
- Physical document does not show signs of alteration or tampering
- State or issuing authority is valid

2.3. For remote applications where in-person ID verification is not possible:
- Accept scanned or photographed copies of both front and back of the ID
- Verify the ID through a third-party identity verification service (e.g., document authentication API)
- If third-party verification is unavailable, require notarized copies or in-person verification at a branch or approved settlement agent

2.4. Retain a legible copy of the ID in the loan file. Redact the ID number on any copies that will be stored beyond the active loan processing period, per data minimization requirements.

### Step 3: Conduct OFAC Screening

3.1. Screen all borrowers, co-borrowers, and guarantors against the following OFAC lists:
- Specially Designated Nationals and Blocked Persons List (SDN List)
- Sectoral Sanctions Identifications List (SSI List)
- Foreign Sanctions Evaders List (FSE List)
- Non-SDN Palestinian Legislative Council List (NS-PLC List)

3.2. Screening must be performed using the borrower's full legal name, any known aliases, and date of birth. The screening tool will check name variations automatically (phonetic matching, transliteration variants).

3.3. Evaluate screening results:
- **No hits:** Document the clear result with the screening date and tool version. Proceed to Step 4.
- **Potential match (false positive):** Review the match details (name similarity score, DOB comparison, country). If clearly a false positive (e.g., different DOB, different country of origin), document the rationale for clearing the match and proceed.
- **Confirmed match or unable to rule out:** Immediately stop all processing. Do not inform the borrower of the OFAC match. Notify the BSA/AML officer within one hour. The BSA officer will contact OFAC's hotline and determine next steps.

3.4. OFAC screening must be performed at the following points in the loan lifecycle:
- Initial application intake (this step)
- Prior to closing (within 3 business days)
- Prior to funding
- Any time a borrower name change is processed

### Step 4: Verify Current Address

4.1. Confirm the borrower's current residential address through at least one of the following:
- Utility bill (electric, gas, water, internet) dated within 60 days
- Bank or brokerage statement dated within 60 days
- Lease agreement currently in effect
- Voter registration card showing current address
- Current mortgage statement (if borrower owns current residence)
- Property tax bill for current residence

4.2. If the application address differs from the ID address, obtain documentation for both addresses and document the reason for the discrepancy (e.g., recent move, mailing address vs. physical address).

4.3. Cross-reference the stated address against the credit report address history. Unexplained addresses on the credit report that were not disclosed on the application require investigation.

### Step 5: Check for Identity Fraud Indicators

5.1. Review the application and supporting documentation for the following red flags:

| Red Flag | Description | Action |
|----------|-------------|--------|
| SSN alert | Credit bureau fraud alert or security freeze on the SSN | Contact borrower at the phone number in the fraud alert; verify identity directly |
| Address inconsistency | Application address differs significantly from ID, credit report, and employer records | Request explanation and supporting documentation |
| Multiple SSN usage | Credit report shows the SSN associated with different names | Escalate to fraud team; request SSA verification |
| New credit file | Credit file less than 12 months old with limited tradelines | May indicate synthetic identity; request additional identification |
| ID document anomalies | Photo appears altered, text alignment irregular, or security features missing | Request alternative ID; consider in-person verification |
| Age / SSN mismatch | SSN issuance date inconsistent with borrower age or location | Verify through SSA; may indicate fraud |
| PO Box only address | Borrower provides only a PO Box with no physical address | Obtain physical residential address; PO Box alone is insufficient |
| Rapid application pattern | Multiple applications across lenders within a short timeframe | Verify intent; may indicate identity theft or loan fraud |

5.2. If two or more red flags are present simultaneously, escalate the file to the Fraud Investigation Unit before proceeding with any further processing.

5.3. For each red flag identified, document the finding, the investigation performed, and the resolution in the compliance notes section of the LOS.

### Step 6: Complete CIP Documentation

6.1. Record the CIP verification results in the LOS compliance module:
- Verification method used for each CIP element (name, DOB, address, SSN)
- Date of verification
- Result of each verification check
- OFAC screening date and result
- Any red flags identified and resolution

6.2. The CIP record must be retained for five years after the loan is closed or the application is withdrawn, per BSA record retention requirements.

6.3. Update the loan file status to reflect successful identity verification. If all checks pass, set the identity verification flag to "Verified" in the LOS.

## 4. Quality Checks

| Check | Criteria | Action if Failed |
|-------|----------|-----------------|
| SSN verification complete | SSA match confirmed before credit pull | Hold credit ordering until SSN verified |
| Photo ID on file | Unexpired government ID scanned and legible | Request new copy or alternative ID |
| OFAC screening current | Screening performed within current business day | Re-screen before proceeding |
| Address verification | At least one acceptable address document on file | Request additional address documentation |
| Red flag review | All applicable red flags reviewed and documented | Complete red flag checklist before proceeding |
| CIP record completeness | All four CIP elements verified and documented | Complete missing verifications |

## 5. Common Pitfalls

1. **Accepting expired identification.** Government-issued ID must be current and unexpired at the time of verification. An ID that expires during the processing period is acceptable if it was valid at verification time, but should be noted.

2. **Skipping OFAC re-screening at closing.** OFAC lists are updated frequently. A clear screening at application does not satisfy the pre-closing screening requirement. Always re-screen within three business days of closing.

3. **Failing to investigate credit report fraud alerts.** When a fraud alert appears on the credit report, the processor must contact the borrower using the phone number specified in the fraud alert, not the number on the application. This is a legal requirement.

4. **Using the borrower's word alone to clear a red flag.** Red flag resolution requires documentary evidence, not just borrower explanations. An unexplained address on the credit report requires utility bills or lease documents, not just a verbal explanation.

5. **Not screening all parties.** OFAC and CIP requirements apply to all parties on the loan, including co-borrowers, guarantors, and signers on a trust. Missing a party creates a compliance gap.

## 6. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.0 | 2025-03-18 | T. Nakamura | Added remote ID verification procedures; updated OFAC list references |
| 1.5 | 2024-08-01 | T. Nakamura | Added synthetic identity red flags; updated SSA verification methods |
| 1.0 | 2023-01-15 | Compliance Department | Initial release |
