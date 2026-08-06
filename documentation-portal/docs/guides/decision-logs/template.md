# Unified Decision Record Template

*This template combines strategic product context and technical architecture decisions to prevent unexpected database schema rebuilds and standards misalignments.*

---

## 1. Title and Metadata
- **Title:** [Brief, descriptive title of the decision]
- **Date:** [YYYY-MM-DD]
- **Authors:** [Name of Product Owner and Technical Lead]
- **Status:** [Draft / Proposed / Approved / Rejected / Superseded]
- **Impact Level:** [Low / Medium / High]

---

## 2. Strategic Context
*Define the strategic, business-driven reason for this decision, including the target outcomes and market positioning.*

- **Problem / Opportunity Statement:**
  [What is the strategic driver or customer pain point being addressed?]
- **Business Goal & Hypothesis:**
  [What do we expect to achieve by making this pivot or decision?]
- **Value Proposition:**
  [How does this align with our overall product-positioning?]

---

## 3. Technical Decisions & Alternatives
*Describe the technical architecture details, selected technology or approach, and why it was chosen over alternatives.*

- **Proposed Solution:**
  [Details of the architectural or implementation design.]
- **Considered Alternatives:**
  - **Alternative A:** [Description and why it was rejected]
  - **Alternative B:** [Description and why it was rejected]
- **Justification:**
  [Why is the proposed solution superior?]

---

## 4. Database Migration Impacts
*MANDATORY - evaluate potential database migration impacts and schema rebuild risks before finalizing the decision. Do not leave this section empty.*

- **Schema Changes Required:**
  - **Placeholder:** Describe any new node labels, relationship types, or properties that must be introduced.
- **Migration & Data Loss Risks:**
  - **Placeholder:** Assess whether this schema change requires deleting/re-importing existing node data or if the schema can be migrated safely with zero downtime.
- **Rollback Strategy:**
  - **Placeholder:** Outline steps required to revert the Neo4j database schema or Cypher constraints to their previous states.

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
  - **Placeholder:** Evaluate compatibility with CDISC standards and explain any mapping adjustments needed.
- **USDM Alignment Assessment:**
  - **Placeholder:** Note if the study design or structure matches the TransCelerate USDM classes and attributes.
- **ISO IDMP Alignment Assessment:**
  - **Placeholder:** Assess drug-level and substance-level representation against ISO IDMP definitions.
