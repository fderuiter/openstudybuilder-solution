# OpenStudyBuilder Contribution Guidelines

We welcome community involvement, feedback, and collaboration on OpenStudyBuilder! To align strategic development, ensure balanced public interest, and satisfy GxP compliance requirements, all contributions are coordinated under a representative **Product Steering Committee (PSC)** and a formal **Product RFC process**.

For more detailed information, please refer to our:
* **Product Steering Committee Charter:** [Contribution Charter](./documentation-portal/docs/guides/governance/contribution_charter.md)
* **Living Roadmap:** [Living Roadmap](./ROADMAP.md)

---

## 1. Feedback & Discussions

If you have feedback, ideas, or questions, we encourage you to join the conversation through our community channels:
* **Slack Workspace:** Join our [Slack Workspace](https://join.slack.com/t/openstudybuilder/shared_invite/zt-19mtauzic-Jvrhtmy7hGstgyiIvB1Wsw) to chat with developers and steering members.
* **GitHub Discussions & Issues:** Submit feedback, report bugs, or propose enhancements directly on our GitHub Issues or Discussions pages.
* **Product Steering Committee Contacts:** You can contact the committee or its chair via GitHub or at `psc@openstudybuilder.org` *(replaces the legacy OpenStudyBuilder@gmail.com contact inbox)*.

---

## 2. Proposing Major Changes (Product RFC Process)

For major functional contributions, schema changes, or key updates, developers must submit a **Product Request for Comments (RFC)**:
* **Why this is required:** To maintain GxP compliance, audit readiness, and technical integration, all major features must undergo representative review and validation planning before implementation begins.
* **Template & Submission:** Use our [Product RFC Template](./documentation-portal/docs/guides/governance/product_rfc_template.md). RFCs must be co-sponsored by representatives from at least two active sponsor organizations to prevent single-entity dominance.
* **Exemptions:** Routine maintenance, minor bug fixes, documentation updates, and critical security patches are **exempt** from the Product RFC process and may be submitted as standard pull requests to ensure operational agility.

---

## 3. Code Contributions & GxP Compliance

Due to the GxP validation evidence and strict chain-of-custody tracking required for clinical trial regulatory compliance, we do not accept ad-hoc, direct pull requests to core repositories without alignment.
* Coding contributions are routed through our collaborative validation pipeline, ensuring proper automated testing (Gherkin-based end-to-end and integration tests) is completed before any code merges into the core repositories.
* Standalone extensions, import/export wrappers, and third-party tools are highly encouraged and can be developed independently under the MIT license! We would love to link your extensions in our documentation, so please reach out via our steering channels.
