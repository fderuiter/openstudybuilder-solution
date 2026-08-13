const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

/**
 * Helper to ensure axe-core is injected on the active page.
 */
function ensureAxe() {
  cy.window().then((win) => {
    if (!win.axe) {
      cy.injectAxe();
    }
  });
}

/**
 * Custom violation formatter to produce an actionable error trace.
 */
function handleA11yViolations(violations) {
  const formattedViolations = violations.map(v => {
    const nodesInfo = v.nodes.map(n => {
      return `  - Element: ${n.target.join(', ')}
    HTML: ${n.html}
    Summary: ${n.failureSummary}`;
    }).join('\n');

    return `Rule ID: ${v.id}
Help: ${v.help}
Description: ${v.description}
Impact: ${v.impact}
Nodes Affected:
${nodesInfo}`;
  }).join('\n\n=========================================\n\n');

  const errorMessage = `Dynamic Accessibility Audit Failed! Found ${violations.length} violation(s):\n\n${formattedViolations}\n\nPlease refactor target component templates to meet WCAG 2.1 AA compliance standards.`;
  
  throw new Error(errorMessage);
}

When('I inject accessibility audit tools', () => {
  ensureAxe();
});

Then('I run an accessibility audit', () => {
  ensureAxe();
  cy.checkA11y(null, null, handleA11yViolations);
});

Then('the page should be accessible', () => {
  ensureAxe();
  cy.checkA11y(null, null, handleA11yViolations);
});

Then('the element {string} should be accessible', (selector) => {
  ensureAxe();
  cy.checkA11y(selector, null, handleA11yViolations);
});

Then('I run an accessibility audit for keyboard and contrast violations', () => {
  ensureAxe();
  // Filter rules specifically targeting keyboard-navigation/contrast/traps.
  cy.checkA11y(null, {
    runOnly: {
      type: 'tag',
      values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']
    },
    rules: {
      'color-contrast': { enabled: true },
      'tabindex': { enabled: true },
      'focus-order-semantics': { enabled: true },
      'accesskeys': { enabled: true }
    }
  }, handleA11yViolations);
});

When('I focus on the element {string}', (selector) => {
  cy.get(selector).focus();
});

When('I hover over the element {string}', (selector) => {
  cy.get(selector).trigger('mouseover');
});

When('I trigger mouseenter on the element {string}', (selector) => {
  cy.get(selector).trigger('mouseenter');
});

When('I focus on a footnote-cell checkbox', () => {
  cy.get('.footnote-cell input[type="checkbox"]').first().focus();
});

When('I focus on the action button in the active cell', () => {
  cy.get('.footnote-cell :focus').closest('td').find('.actionButtons button').first().focus();
});

When('I simulate keyboard tab navigation', () => {
  cy.focused().trigger('keydown', { keyCode: 9, which: 9 });
});
