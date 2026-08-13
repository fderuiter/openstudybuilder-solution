# OpenStudyBuilder Living Roadmap

This is the living, public roadmap for OpenStudyBuilder. It outlines our strategic vision, key development priorities, and upcoming milestones. 

To keep development execution and long-term planning aligned, this roadmap is kept in real-time synchronization with our active GitHub project boards.

---

## 1. Active Roadmap Board

For real-time progress, task assignments, and active work items, please visit our main project board:
* **Active GitHub Project Board:** [OpenStudyBuilder Project Board #1](https://github.com/orgs/openstudybuilder/projects/1)

All milestones listed below correspond to active milestones tracked on our GitHub repository and project board.

---

## 2. Core Strategic Goals

Our development roadmap is centered around three core pillars:

1. **Robust Standards & Interoperability:** Enhance support for CDISC controlled terminology, unified standard rules, and seamless integrations with external dictionaries.
2. **GxP Audit Readiness & Integrity:** Ensure every core data model change, study state transition, and API modification maintains robust validation trails and automated verification metrics.
3. **Extensibility & Modular Architecture:** Keep the core clean, secure, and lightweight, encouraging sponsors and developers to build standalone plugins and external tools using the OpenStudyBuilder API.

---

## 3. Key Milestones

### Milestone 1: Representative Product Governance & Steering (Current)
* **Goal:** Replace single-maintainer contact channels with a representative, multi-stakeholder Product Steering Committee (PSC).
* **Key Deliverables:**
  - [x] Update contribution guidelines across all repositories to reference the PSC.
  - [x] Establish the formal Product Request for Comments (RFC) process.
  - [x] Publish the central `ROADMAP.md` living roadmap.
  - [x] Consolidate and retire outdated TODO checklists and unmaintained strategy placeholders.
* **Status:** In Progress / Nearing Completion

### Milestone 2: Study State & Lifecycle Validation Enhancements (Q3 2026)
* **Goal:** Improve consistency checks and verification flows for study transitions and clinical metadata changes.
* **Key Deliverables:**
  - [ ] Implement enhanced audit-logging schemas for clinical state changes.
  - [ ] Add built-in GxP compliance metrics dashboards inside Neodash.
  - [ ] Introduce formal Product RFC review for upcoming data schema migrations.
* **Status:** Planned

### Milestone 3: Modular API Extension Hooks (Q4 2026 - Q1 2027)
* **Goal:** Enable deeper integration with sponsor-specific tools without requiring core modifications.
* **Key Deliverables:**
  - [ ] Implement custom webhook support for core state events.
  - [ ] Expand MIT-licensed helper wrappers and import/export tooling.
* **Status:** Future Backlog

---

## 4. How the Roadmap is Maintained

The Living Roadmap is managed by the **Product Steering Committee (PSC)** using a collaborative and transparent workflow:

1. **Community Proposals:** Proposers use the [Product RFC Template](./documentation-portal/docs/guides/governance/product_rfc_template.md) to suggest major roadmap additions.
2. **Committee Review:** The PSC reviews and votes on proposals during open bi-weekly meetings. Approved proposals are assigned to upcoming milestones.
3. **GitHub Project board Synchronization:** Once approved, items are added as issues/cards to our [GitHub Project Board](https://github.com/orgs/openstudybuilder/projects/1).
4. **Iterative Updates:** This `ROADMAP.md` is updated regularly at the start of each milestone or release cycle to reflect current priority changes, keeping strategic planning completely integrated with everyday execution.
