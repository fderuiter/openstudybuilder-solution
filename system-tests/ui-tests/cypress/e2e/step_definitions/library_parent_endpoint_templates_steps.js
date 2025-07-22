import { fillTemplateNameAndContinue } from './library_syntax_templates_common'
const { Given, When, Then } = require('@badeball/cypress-cucumber-preprocessor')

let defaultEndpointName

When('The endpoint template is found', () => cy.searchAndCheckPresence(defaultEndpointName, true))

When('The endpoint template is not found', () => cy.searchAndCheckPresence(defaultEndpointName, false))

When('The endpoint template is not updated', () => cy.searchAndCheckPresence(defaultEndpointName, false))

Then('The endpoint template name is displayed in the table', () => cy.checkRowByIndex(0, 'Parent template', defaultEndpointName))

Then('The endpoint template name is checked', () => cy.get('[data-cy="template-text-field"] [id="editor"]').invoke('text').should('equal', defaultEndpointName))

When('The endpoint template form is filled with base data', () => fillBaseData(`Endpoint${Date.now()}`))

When('The endpoint metadata update is started', () => fillBaseData(`Update${Date.now()}`))

When('The endpoint template edition form is filled with data', () => fillBaseData(`CancelEdit${Date.now()}`))

When('The endpoint template form is filled with already existing name', () => fillTemplateNameAndContinue(defaultEndpointName))

When('[API] Endpoint template is inactivated', () => cy.inactivateEndpoint())

When('[API] Approve endpoint template', () => cy.approveEndpoint())

When('[API] Create endpoint template', () => {
  createEndpointViaApi()
  cy.getEndpointName().then(name => defaultEndpointName = name.replace('<p>', '').replace('</p>', '').trim())
})

When('[API] Search Test - Create first endpoint template', () => {
  defaultEndpointName = `SearchTest${Date.now()}`
  createEndpointViaApi(defaultEndpointName)
})

When('[API] Search Test - Create second endpoint template', () => createEndpointViaApi(`SearchTest${Date.now()}`))

function createEndpointViaApi(customName = '') {
  cy.getInidicationUid()
  cy.getEndpointCategoryUid()
  cy.getEndpointSubCategoryUid()
  cy.createEndpoint(customName)
}

function fillBaseData(endpointName) {
  defaultEndpointName = endpointName
  fillTemplateNameAndContinue(defaultEndpointName)
}