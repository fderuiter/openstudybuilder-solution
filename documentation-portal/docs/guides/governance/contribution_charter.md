# Contribution Charter

OpenStudyBuilder welcomes community involvement, feedback, and collaboration. To align with regulatory standards, protect the platform's audit readiness, and maintain security, we operate under a structured contribution charter.

---

## Why Direct Core Pull Requests Are Not Accepted

External developers and contributors often ask why we do not accept direct, ad-hoc source code pull requests (PRs) to the core repositories (such as `/studybuilder` and `/clinical-mdr-api`). 

This policy is necessary because of the **GxP (Good Practice) compliance constraints** governing the clinical trial ecosystem:
* **Regulatory Compliance:** OpenStudyBuilder is designed to drive clinical study specification, planning, and setup. Under GxP environments, every line of core code must have fully documented, reproducible verification and validation (V&V) evidence.
* **Strict Chain of Custody:** To remain audit-ready for regulatory authorities, we must maintain a strictly controlled chain of custody for all modifications in the core application logic.
* **Ad-hoc Contributions:** Unstructured, direct pull requests bypass our strict quality gateways and release-management pipelines, potentially invalidating the system's compliance status for enterprise users.

---

## The Collaborative Validation Process

To maintain GxP alignment while enabling innovation, we employ a **collaborative validation process** for any new core features or modifications:

1. **Direct Communication & Alignment:** Before writing any core code, contributors must discuss the proposed changes directly with the core maintenance team.
2. **Review & Validation Planning:** The maintenance team will collaborate with you to define the necessary GxP validation evidence, quality gateways, and automated test cases.
3. **Co-development or Vendor Routing:** Coding contributions are then either implemented through approved development channels, sponsored vendors, or directly by Novo Nordisk's verified engineering team.
4. **Final Verification:** All code undergoes formal system verification and Gherkin-based end-to-end tests inside our compliance-controlled environments before being merged.

---

## Alternative Feedback & Contribution Channels

Even though direct core pull requests are restricted, we highly encourage other forms of active participation through alternative channels:

### 1. Direct Discussion & Proposals
If you have identified a valuable feature or bug fix:
* **Slack Workspace:** Join our active community conversations on [Slack](https://join.slack.com/t/openstudybuilder/shared_invite/zt-19mtauzic-Jvrhtmy7hGstgyiIvB1Wsw) to share ideas or seek support.
* **Email Communication:** Get in touch with our team at `OpenStudyBuilder@gmail.com` to discuss prospective collaborations or schedule direct alignment sessions.
* **Events & Conferences:** Meet our team in person at industry events. Check [upcoming events](https://novo-nordisk.gitlab.io/nn-public/openstudybuilder/project-description/intro_events/) to see where you can connect with us.

### 2. Standalone Extensions & Components
Because OpenStudyBuilder is built on a modular API architecture, you do not need to modify the core to expand its features. We strongly encourage developing standalone, external components:
* **MIT Integration Safety:** Standalone components, import/export wrappers, or database helper scripts can be built under the permissive MIT license as completely independent repositories.
* **We Will Link Your Work:** If you develop a standalone extension, let us know! We would love to feature and link your project in the OpenStudyBuilder Documentation Portal.

---

For any questions about GxP compliance or the collaborative validation process, please reach out to us at `OpenStudyBuilder@gmail.com`.
