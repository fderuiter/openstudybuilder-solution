// Import commands.js using ES2015 syntax:
import '@shelex/cypress-allure-plugin'
import '@4tw/cypress-drag-drop'
import './api_requests/authorisation_methods'
import './api_requests/crf_requests'
import './api_requests/ct_requests'
import './api_requests/disease_milestones_requests'
import './api_requests/library_activities'
import './api_requests/library_syntax_templates'
import './api_requests/library_units'
import './api_requests/rest_client'
import './api_requests/study_requests'
import './api_requests/study_activities_requests'
import './api_requests/study_desgin_matirx_requests'
import './api_requests/study_arm_requests'
import './api_requests/study_branch_requests'
import './api_requests/study_cohorts_requests'
import './api_requests/study_criteria_requests'
import './api_requests/study_elements_requests'
import './api_requests/study_epochs_requests'
import './api_requests/study_type_requests'
import './api_requests/study_visits_requests'
import './api_requests/study_compounds_request'
import './browser_operations/study_select_command'
import './front_end_commands/buttons_commands'
import './front_end_commands/drop_down_commands'
import './front_end_commands/elements_assertion_commands'
import './front_end_commands/input_field_commands'
import './front_end_commands/table_commands'
import './front_end_commands/waiting_commands'
import './helper_functions'

Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false
})

//Run that command once prior to the whole test suit
before(function() {
    cy.prepareAuthTokens()
    cy.createAndSetMainTestStudy('9876')
    cy.createTestStudy('9866', 'Study cloning testing')
    cy.createTestStudy('9877', 'Study structure testing')
    cy.createTestStudy('9878', 'Manual structure testing')
    cy.createTestStudy('9879', 'Additional study for testing')
    cy.createTestStudy('9880', 'Study visits testing')
    cy.createTestStudy('9881', 'Empty study')
    // Please note 9900 -> 9914 are reserved for study lock/unlock tests
});