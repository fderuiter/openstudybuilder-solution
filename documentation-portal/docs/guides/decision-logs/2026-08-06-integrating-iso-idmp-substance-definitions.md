---
title: Integrating ISO IDMP Substance Definitions
date: '2026-08-06'
authors: Clara Smith (Product Owner), David Miller (Technical Lead)
status: Proposed
impact: Medium
description: Incorporating the ISO IDMP substance and product definitions into the terminology library to comply with global regulatory guidelines.
---

# Integrating ISO IDMP Substance Definitions

*This decision record outlines the proposal to adopt ISO IDMP (Identification of Medicinal Products) substance definitions within our Metadata Repository library.*

---

## 1. Title and Metadata
- **Title:** Integrating ISO IDMP Substance Definitions
- **Date:** 2026-08-06
- **Authors:** Clara Smith (Product Owner), David Miller (Technical Lead)
- **Status:** Proposed
- **Impact Level:** Medium

---

## 2. Strategic Context
*Define the strategic, business-driven reason for this decision, including the target outcomes and market positioning.*

- **Problem / Opportunity Statement:**
  Currently, substance data is managed as unstructured free-text fields in our clinical trials records, causing inconsistencies during submissions to European and US health authorities.
- **Business Goal & Hypothesis:**
  Integrating the ISO 11238 standard directly into our terminology reference module will ensure 100% submission compliance, eliminating regulatory queries about substance naming.
- **Value Proposition:**
  Provides clinical trial sponsors with immediate verification of substance compliance at study design time.

---

## 3. Technical Decisions & Alternatives
*Describe the technical architecture details, selected technology or approach, and why it was chosen over alternatives.*

- **Proposed Solution:**
  Add a dedicated `IdmpSubstance` node to the Neo4j schema with properties matching the ISO 11238 standard: substance identifier, substance name, chemical structure reference, and regulatory agency codes.
- **Considered Alternatives:**
  - **Alternative A:** Rely on external terminology server integrations during data export. (Rejected: High external network latency and lack of offline capabilities).
  - **Alternative B:** Keep substance data as simple flat lists. (Rejected: Flat lists cannot represent complex chemical substance hierarchies and active moiety relationships).
- **Justification:**
  Modeling substances as first-class Neo4j nodes allows precise representation of hierarchical relationships (e.g., active moiety to salt) with fast localized graph traversals.

---

## 4. Database Migration Impacts
*MANDATORY - evaluate potential database migration impacts and schema rebuild risks before finalizing the decision. Do not leave this section empty.*

- **Schema Changes Required:**
  Introduce new node label `IdmpSubstance` and relationship type `HAS_ACTIVE_MOIETY`. Add unique constraints on `IdmpSubstance.substance_id`.
- **Migration & Data Loss Risks:**
  Low risk. This is an additive schema migration; no existing nodes or properties will be deleted. We can run this migration dynamically on the live database during a scheduled release.
- **Rollback Strategy:**
  To rollback, we will run a Cypher script to delete all nodes with the `IdmpSubstance` label and drop the unique constraints on `IdmpSubstance.substance_id`.

---

## 5. Standards Compliance Assessments
*MANDATORY - evaluate risks, compliance, and alignment related to industry standards. Follow the guidelines below and complete the assessment.*

### Prompt-Style Guidelines & Risk Evaluation:
- **CDISC Standards:** 
  *Check compatibility with CDISC (e.g., SDTM, ADaM, CDASH, ODM). Will this change modify how CDISC-controlled terminology is represented or stored? Ensure no breaking changes to downstream export tools.*
- **USDM (Unified Study Definition Model) Standards:** 
  *Verify alignment with the TransCelerate USDM reference implementation. Does this decision align with or deviate from the standard USDM study structures? Assess compatibility and future integration risks.*
- **ISO IDMP (Identification of Medicinal Products) Standards:** 
  *Evaluate how this change affects compliance with ISO IDMP. Will drug substance, product, or substance definitions be altered? Ensure compliance with international regulatory submission requirements.*

### Compliance & Risk Assessment:
- **CDISC Alignment Assessment:**
  Compatible. CDISC SDTM allows drug/substance references to be populated from external terminologies, such as the ISO IDMP substance registries.
- **USDM Alignment Assessment:**
  Compatible. USDM includes placeholders for drug identifiers that map perfectly to the proposed `IdmpSubstance` properties.
- **ISO IDMP Alignment Assessment:**
  Full compliance. This change is explicitly designed to implement ISO 11238 and other IDMP standards directly into our library.
