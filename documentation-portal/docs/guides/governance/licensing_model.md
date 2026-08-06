# Interactive Licensing Model Guide

OpenStudyBuilder is designed to support the clinical study process through a hybrid licensing model. By clarifying our licensing boundaries, we build community trust and make it easier for enterprise partners to integrate OpenStudyBuilder into their compliance and regulatory environments.

---

## The Dual-License Division

Our licensing architecture is split into two distinct boundaries to balance open-source collaboration with corporate flexibility:

1. **Copyleft Core Components (GPLv3)**: Core application logic and standards engines are kept strictly open-source to ensure that improvements to the platform benefit the entire community.
2. **Permissive Integration Points (MIT)**: Integration schemas, APIs, database definitions, and extension tools use the permissive MIT license. This allows enterprise partners to connect their proprietary internal database extensions and internal workflows without triggering copyleft requirements.

---

## Licensing Boundaries & Mapping

The following table outlines the exact licensing division across the different directories and repositories within the OpenStudyBuilder ecosystem:

| System Component | Location in Repository | License Type | Description & Boundary Purpose |
| :--- | :--- | :--- | :--- |
| **OpenStudyBuilder App** | `/studybuilder` | **GPLv3** (Copyleft Core) | The primary user interface application. |
| **Clinical MDR API** | `/clinical-mdr-api` | **GPLv3** (Copyleft Core) | Python-based core API managing metadata workflows and access control. |
| **Standards Import** | `/mdr-standards-import` | **GPLv3** (Copyleft Core) | Python tools for importing CDISC and other standards. |
| **Clinical MDR (Database)** | `/neo4j-mdr-db` | **MIT** (Permissive Integration) | Neo4j metadata repository database schemas. (Excludes third-party Neo4j software). |
| **Clinical MDR API Specification** | `/clinical-mdr-api` (swagger) | **MIT** (Permissive Integration) | OpenAPI swagger definitions to facilitate easy interoperability. |
| **Sponsor Data Import** | `/studybuilder-import` | **MIT** (Permissive Integration) | Python import tools for custom or sponsor-specific reference data. |
| **Data Export** | `/studybuilder-export` | **MIT** (Permissive Integration) | Export scripts and templates for downstream systems. |
| **DB Schema Migration** | `/db-schema-migration` | **MIT** (Permissive Integration) | Tools and migration scripts for database schema evolution. |
| **System Tests** | `/system-tests` | **MIT** (Permissive Integration) | Gherkin-based end-to-end and UI verification tests. |
| **Documentation Portal** | `/documentation-portal` | **CC-BY-4.0** (Content)<br>**MIT** (Source Code) | Online user guides and system documentation. |

---

## Enterprise Compliance & Licensing Safety

A key concern for corporate legal counsel during compliance audits is the risk of "copyleft contamination"—specifically, whether using an open-source platform forces the enterprise to open-source its proprietary internal database extensions or downstream pipelines.

**OpenStudyBuilder resolves this through clear, legally sound boundaries:**
* **No Propagation to Extensions:** The schema layer (`/neo4j-mdr-db`), importer (`/studybuilder-import`), and exporter (`/studybuilder-export`) are licensed under the **MIT license**.
* **Isolated Core:** Because the copyleft core components (GPLv3) communicate via public APIs or isolated processes, they do not contaminate proprietary internal database extensions, vendor modules, or downstream analytical platforms.
* **Safe Integration:** Your enterprise is free to build, run, and maintain proprietary extensions and downstream adapters under any proprietary license of your choosing, without having to open-source your proprietary code.

For any formal compliance inquiries or license questions, please contact our legal and open-source advisors at `openstudybuilder@gmail.com`.
