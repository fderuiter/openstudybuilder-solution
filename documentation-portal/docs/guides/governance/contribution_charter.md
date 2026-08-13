# Contribution Charter

OpenStudyBuilder welcomes community involvement, feedback, and collaboration. To align with regulatory standards, protect the platform's audit readiness, maintain security, and coordinate strategic growth, we operate under a structured contribution charter and a representative **Product Steering Committee (PSC)**.

---

## 1. Product Steering Committee (PSC) Governance

The Product Steering Committee is established to coordinate product priorities, align long-term strategic direction, maintain the living product roadmap, and ensure all major functional contributions meet high quality and GxP compliance standards.

### Membership Rules
* **Multi-Stakeholder Representation:** The PSC is composed of representatives from active sponsor organizations, core maintainers, and key community contributors.
* **Preventing Single-Entity Dominance:** To ensure balanced, public-interest steering, the committee must include representatives from at least three distinct active sponsor organizations. No single company or organization may hold a majority of voting seats on the committee.
* **Committee Chair:** The committee elects a Chair from among its members on an annual basis to facilitate meetings and organize the agenda.

### Voting Procedures
* **Quorum:** A quorum is achieved when representatives from at least two-thirds of the represented active sponsor organizations are present.
* **Standard Decisions:** Routine decisions, minor roadmap adjustments, and standard RFC approvals require a simple majority vote of the active members present.
* **Major Changes:** Alterations to this charter, core data model overhauls, or major API deprecations require a supermajority (two-thirds) vote.

### Meeting Cadence
* **Schedule:** The PSC meets bi-weekly (or monthly as decided by the committee) in public, open meetings.
* **Transparency:** Meeting schedules, agendas, and minutes are published openly in the repository's GitHub Issues and Discussions to foster community transparency and participation.

---

## 2. Why Direct Core Pull Requests Are Restricted

External developers often ask why direct, ad-hoc source code pull requests (PRs) to core repositories (such as `/studybuilder` and `/clinical-mdr-api`) are restricted. This policy is mandatory due to the **GxP (Good Practice) compliance constraints** governing the clinical trial ecosystem:

* **Regulatory Compliance:** OpenStudyBuilder is designed to drive clinical study specification, planning, and setup. Under GxP environments, every line of core code must have fully documented, reproducible verification and validation (V&V) evidence.
* **Strict Chain of Custody:** To remain audit-ready for regulatory authorities, we must maintain a strictly controlled chain of custody for all modifications in the core application logic.
* **Ad-hoc Contributions:** Unstructured, direct pull requests bypass our strict quality gateways and release-management pipelines, potentially invalidating the system's compliance status for enterprise users.

---

## 3. The Product RFC Process

For major functional or architectural contributions, OpenStudyBuilder requires a formal **Product Request for Comments (RFC)** process. This process ensures the feature aligns with the living roadmap, maintains GxP compliance, and does not bypass existing code quality, security, or testing gates.

### RFC Lifecycle
1. **Drafting:** The proposer drafts a formal document using our [Product RFC Template](./product_rfc_template.md).
2. **Co-Sponsorship:** The proposer aligns with other active sponsor organizations to secure necessary co-sponsorships to prevent single-entity dominance.
3. **Submission & Community Review:** The RFC is submitted via GitHub Discussions as a new proposal for community feedback.
4. **Steering Review:** The PSC reviews the proposal during a public meeting, assessing GxP impact, architectural fit, and automated testing requirements.
5. **Approval:** Once approved by the PSC, the proposal is integrated into the Living Roadmap, and the code can be safely developed through approved compliance pipelines.

### Verification and Compliance Guardrails
* **Quality Gates:** Approved RFC implementations must conform to all existing repository standards, including linter/formatter rules and test-coverage requirements.
* **Security Gates:** All code must pass automated security scans (SAST, DAST, SCA) before release.
* **GxP Compliance Validation:** The RFC process must enforce formal validation assessments, Gherkin-based automated end-to-end testing, and audit trail validation within our compliance-controlled testing environments.

### Process Exemptions
Routine maintenance, minor bug fixes, clean-ups, documentation updates, and critical security patches are **exempt** from the Product RFC process. These changes can be merged via the standard pull request flow to maintain operational agility.

---

## 4. Steering Committee & Community Contact Channels

To align on prospective changes, discuss roadmap updates, or submit feedback, please use the following formal steering committee channels:

### 1. Steering & Roadmap Alignment
* **Product Steering Committee Contact:** Get in touch with the committee via GitHub Issues, Discussions, or contact the committee chair at `psc@openstudybuilder.org` *(replaces the legacy OpenStudyBuilder@gmail.com inbox)*.
* **Living Roadmap:** Track our current and future strategic milestones on our [Living Roadmap](../../../ROADMAP.md) and active [GitHub Project Boards](https://github.com/orgs/openstudybuilder/projects/1).
* **Slack Workspace:** Join our active community conversations on [Slack](https://join.slack.com/t/openstudybuilder/shared_invite/zt-19mtauzic-Jvrhtmy7hGstgyiIvB1Wsw) to collaborate in real-time.
* **Events & Conferences:** Meet our team in person at industry events. Check [upcoming events](https://novo-nordisk.gitlab.io/nn-public/openstudybuilder/project-description/intro_events/) to connect with us.

### 2. Standalone Extensions & Components
Because OpenStudyBuilder is built on a modular API architecture, you do not need to modify the core to expand its features. We strongly encourage developing standalone, external components:
* **MIT Integration Safety:** Standalone components, import/export wrappers, or database helper scripts can be built under the permissive MIT license as completely independent repositories.
* **We Will Link Your Work:** If you develop a standalone extension, let us know! We would love to feature and link your project in the OpenStudyBuilder Documentation Portal.
