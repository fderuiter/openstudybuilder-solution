import { fillTemplateNameAndContinue } from './library_syntax_templates_common'
const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let defaultCriteriaName

Then('The Criteria is visible in the Criteria Templates Table', () => cy.checkRowByIndex(0, 'Parent template', defaultCriteriaName))

Then('Wait for criteria to be created and search for it', () => confirmCriteriaCreated())

Then('The criteria is found', () => cy.searchAndCheckPresence(defaultCriteriaName, true))

Then('The criteria is not found', () => cy.searchAndCheckPresence(defaultCriteriaName, false))

When('The criteria template form is filled with base data', () => fillBaseDataAndContinue(`Criteria${Date.now()}`))

When('The criteria metadata update is initiated', () => fillBaseDataAndContinue(`Updated${Date.now()}`))

When('The criteria template edition form is filled with data', () => fillBaseDataAndContinue(`Cancel${Date.now()}`))

Then('[API] {string} Criteria in status Draft exists', (type) => createCriteriaViaApi(type))

Then('[API] Criteria is approved', () => cy.approveCriteria())

Then('[API] Criteria is inactivated', () => cy.inactivateCriteria())

Then('Criteria created via API is searched for', () => {
    cy.intercept('/api/criteria-templates?page_number=1&*').as('getCriteria')
    cy.wait('@getCriteria', {timeout: 20000})
    cy.searchAndCheckPresence(defaultCriteriaName, true)
})

When('[API] Search Test - Create first {string} criteria template', (type) => {
  defaultCriteriaName = `SearchTest${Date.now()}`
  createCriteriaViaApi(type, defaultCriteriaName)
})

When('[API] Search Test - Create second {string} criteria template', (type) => createCriteriaViaApi(type, `SearchTest${Date.now()}`))

function fillBaseDataAndContinue(name) {
    defaultCriteriaName = name
    fillTemplateNameAndContinue(name)
    cy.intercept('/api/criteria-templates?page_number=1&*').as('getCriteria')
}

function confirmCriteriaCreated() {
    cy.wait('@getCriteria', {timeout: 20000})
    cy.waitForTable()
    cy.searchAndCheckPresence(defaultCriteriaName, true)
}

function createCriteriaViaApi(type, customName = '') {
    if (type == 'Inclusion') cy.getInclusionCriteriaUid()
        else if (type == 'Exclusion') cy.getExclusionCriteriaUid()
            else if (type == 'Dosing') cy.getDosingCriteriaUid()
                else if (type == 'Withdrawal') cy.getWithdrawalCriteriaUid()
                    else if (type == 'Run-in') cy.getRunInCriteriaUid()
                        else if (type == 'Randomisation') cy.getRandomizationCriteriaUid()
    cy.getInidicationUid()
    cy.getCriteriaCategoryUid()
    cy.getCriteriaSubCategoryUid()
    cy.createCriteria(customName)
    cy.getCriteriaName().then(name => defaultCriteriaName = name.replace('<p>', '').replace('</p>', '').trim())
}