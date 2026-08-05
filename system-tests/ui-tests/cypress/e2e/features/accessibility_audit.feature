@REQ_ID:ACC_001
Feature: Dynamic Accessibility Audit
    As a QA engineer, I want to run dynamic accessibility scans on pages in active, interactive UI states using human-readable test steps.

    Scenario: Audit the landing page for accessibility and keyboard focus
        Given The user is logged out
        And The homepage is opened
        When I inject accessibility audit tools
        Then the page should be accessible
        And I run an accessibility audit for keyboard and contrast violations
