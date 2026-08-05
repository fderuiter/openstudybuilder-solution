# Accessibility Coding Practices & Interactive Guide

OpenStudyBuilder is committed to continuous WCAG 2.1 AA accessibility compliance across all dynamic user interface views, ensuring layout and interactive elements are completely accessible for people of all abilities, including keyboard-only users and screen reader users.

This guide details our accessibility engineering standards, interactive custom component patterns, and the automated mechanisms that protect our repository from regression.

---

## 1. Core Principles (WCAG 2.1 AA)

To satisfy **WCAG 2.1 Level AA** standards, every custom template and interactive view must adhere to four essential principles:

### A. Perceivable (Text Alternatives, Contrast, Structure)
- **Contrast Ratios:** Standard text must have a minimum contrast ratio of **4.5:1** against its background. Large-scale text (18pt/24px or bold 14pt/18.67px) must have a ratio of **3:1**.
- **Images & Icons:** Provide descriptive `alt` tags or `aria-label` properties on non-text elements unless they are purely decorative (which should use `aria-hidden="true"`).

### B. Operable (Keyboard Access, Navigation, Traps)
- **Keyboard Navigability:** Every interactive element must be reachable and triggerable using standard keyboard controls (e.g., `Tab`, `Shift + Tab`, `Enter`, `Space`).
- **No Keyboard Traps:** Focus must never be locked inside any modal, popup, or dynamic sub-view without a clear, keyboard-accessible mechanism to escape (such as hitting `Escape` or tabbing to a "Close" button).
- **Focus Indicators:** Active keyboard focus states must be highly visible and clear. Never suppress the focus ring with `outline: none;` without providing an equivalent, clear custom visual focus indicator.

### C. Understandable (Predictable, Labels)
- **Accessible Form Elements:** Every input control, select box, checkbox, and text area must be associated with a programmatically linked `<label>` or explicit `aria-label` / `aria-labelledby`.
- **Form Validation:** Error messages must be explicitly announced and programmatically bound to their corresponding input via `aria-describedby`.

### D. Robust (Semantic HTML, ARIA)
- **Semantic Tags First:** Use native HTML elements (`<button>`, `<a>`, `<main>`, `<nav>`, `<header>`) before resorting to generic structural tags with custom ARIA behaviors.

---

## 2. Shared Component Templates & WCAG Compliance

### A. Iconography (`MdiIcon.vue`)
Custom SVG icons must distinguish between decorative icons and semantic icons.

```vue
<!-- Decorative (Ignored by screen readers) -->
<MdiIcon icon="help-circle" :aria-hidden="true" />

<!-- Semantic (Read by screen readers as an image/action) -->
<MdiIcon icon="close" aria-label="Close dialog" />
```

### B. Accessible Form Control Template
Always bind inputs programmatically. Using Vuetify elements requires setting the `label` prop or utilizing explicit HTML labeling rules:

```html
<!-- Native Accessible Association -->
<div class="form-group">
  <label for="study-identifier">Study Identifier</label>
  <input 
    id="study-identifier" 
    type="text" 
    aria-required="true"
    aria-describedby="study-helper-text"
  />
  <span id="study-helper-text" class="helper-text">Enter the 4-digit unique protocol ID.</span>
</div>
```

---

## 3. Interactive Guide & Exercises

Test your understanding of accessibility compliance by interacting with these standard Vue scenarios.

::: tip Interactive Template Challenge
How would you refactor a div with a click event to be accessible?
*Incorrect non-accessible way:*
```html
<div @click="openDetails">Click here for Details</div>
```
*Correct, compliant way:*
```html
<button 
  type="button" 
  @click="openDetails" 
  @keydown.enter="openDetails" 
  @keydown.space.prevent="openDetails"
>
  Click here for Details
</button>
```
:::

---

## 4. Automated Verification Workflows

We employ a two-layer validation framework to continuously enforce these rules in production and local development workflows.

### 1. Static Validation (Prebuild Linting Gate)
We use `eslint-plugin-vuejs-accessibility` to parse Vue templates at compile-time and flag violations.
- Run on-demand locally:
  ```bash
  cd studybuilder
  yarn lint
  ```
- Any commit containing missing tags, unlinked form labels, or missing keyboard event handlers is automatically rejected by the continuous integration build validation pipeline (`build-validation.yml`).

### 2. Dynamic Runtime Auditing (BDD-driven Scans)
For rich interactive states, we execute dynamic audits at runtime via custom Gherkin step definitions inside our automated Cypress test suite.

#### Gherkin Step Definitions
| Step Definition | Behavior |
| --- | --- |
| `When I inject accessibility audit tools` | Injects the axe-core testing engine into the active viewport state. |
| `Then the page should be accessible` | Executes a complete page-level accessibility check. |
| `Then the element "{selector}" should be accessible` | Audits a specific dynamic element. |
| `And I run an accessibility audit for keyboard and contrast violations` | Audits specifically for focus-traps and color contrast thresholds. |

#### Sample BDD Feature Spec
```gherkin
@REQ_ID:ACC_001
Feature: Dynamic Accessibility Audit

    Scenario: Audit the landing page for accessibility and keyboard focus
        Given The user is logged out
        And The homepage is opened
        When I inject accessibility audit tools
        Then the page should be accessible
```
