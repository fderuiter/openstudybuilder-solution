---
title: Aligning Core Study Structure with USDM
date: '2026-08-05'
authors: Alice Vance (Product Owner), Bob Vance (Technical Lead)
status: Approved
impact: High
description: Migrating the study structural representation to match the TransCelerate Unified Study Definition Model (USDM) to support cross-industry clinical trials.
---

# Aligning Core Study Structure with USDM

*This decision record documents our strategic shift and engineering path to align our database representations with the TransCelerate USDM.*

---

## 1. Title and Metadata
- **Title:** Aligning Core Study Structure with USDM
- **Date:** 2026-08-05
- **Authors:** Alice Vance (Product Owner), Bob Vance (Technical Lead)
- **Status:** Approved
- **Impact Level:** High

---

## 2. Strategic Context
*Define the strategic, business-driven reason for this decision, including the target outcomes and market positioning.*

- **Problem / Opportunity Statement:**
  Clients are increasingly requiring their study builders to be interoperable with external clinical systems. Our proprietary internal data structures make integrations complex, leading to expensive customized API layers.
- **Business Goal & Hypothesis:**
  By aligning our underlying model with USDM, we lower integration costs by up to 50% and become instantly compliant with the TransCelerate Digital Data Flow (DDF) initiative.
- **Value Proposition:**
  Dramatically improves our strategic positioning as a modern, standards-first clinical Metadata Repository.

---

## 3. Technical Decisions & Alternatives
*Describe the technical architecture details, selected technology or approach, and why it was chosen over alternatives.*

- **Proposed Solution:**
  Refactor the Neo4j database node labels from our proprietary `StudySegment` and `StudyWorkflow` classes to match the USDM `Study`, `StudyProtocol`, `StudyDesign`, and `Activity` structures.
- **Considered Alternatives:**
  - **Alternative A:** Maintain internal models and translate on-the-fly at the API gate. (Rejected: Adds severe performance overhead and developer maintenance burden).
  - **Alternative B:** Fully migrate to an RDF triple store. (Rejected: High learning curve and lacks our current optimized Neo4j tooling).
- **Justification:**
  Refactoring Neo4j labels directly allows us to preserve the performance of graph traversals while remaining entirely standard-compliant.

---

## 4. Database Migration Impacts
*MANDATORY - evaluate potential database migration impacts and schema rebuild risks before finalizing the decision. Do not leave this section empty.*

- **Schema Changes Required:**
  We must introduce four new node labels (`UsdmStudy`, `UsdmStudyProtocol`, `UsdmStudyDesign`, and `UsdmActivity`) and their corresponding relationship mappings. Legacy `StudySegment` nodes will be phased out.
- **Migration & Data Loss Risks:**
  Since node labels are changing, we cannot perform a live seamless swap without risking mismatched references. We will run an offline migration script during a planned 2-hour maintenance window. Legacy data will be backed up to Cypher export files before the migration to prevent data loss.
- **Rollback Strategy:**
  If the offline migration script fails, we will restore the database from the pre-migration backup snapshot.

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
  This USDM model alignment natively preserves our CDISC-controlled terminology reference nodes. CDISC SDTM/ADaM exports remain unaffected since our export services compile data based on vocabulary mappings rather than structural node layouts.
- **USDM Alignment Assessment:**
  Perfect alignment. This shift directly maps to the USDM v3.0 standard.
- **ISO IDMP Alignment Assessment:**
  Neutral. Substance definition representation remains independent of the study layout structure.
