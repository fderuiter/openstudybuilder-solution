
import { fillTemplateNameAndContinue } from './library_syntax_templates_common'
const { Given, When, Then } = require('@badeball/cypress-cucumber-preprocessor')

let nameSufix
let objectivePreInstanceName
let preInstanceName
let newObjectiveNameUpdated = Date.now() + 'Updated'
let parameterSelected
let secondParameterSelected

When('Objective template for pre-instantiation is found', () => cy.searchAndCheckPresence(nameSufix, true))

When('The new objective to be used as pre-instantiation is added in the library', () => {
  nameSufix = `template ${Date.now()}`
  objectivePreInstanceName = `Test [Activity] and [ActivityGroup] ${nameSufix}`
  fillTemplateNameAndContinue(objectivePreInstanceName)
  cy.get('[data-cy="not-applicable-checkbox"] input').eq(0).check()
  cy.get('[data-cy="not-applicable-checkbox"] input').eq(1).check()
  cy.clickButton('radio-Yes')
  cy.clickFormActionButton('save')
})

When('The pre-instantiation is created from that objective template', () => {
  cy.selectFirstMultipleSelect('Activity')
  cy.selectFirstMultipleSelect('ActivityGroup')
  cy.get('[data-cy="Activity"] .v-input__control  span').invoke('text').then((text) => {
    parameterSelected = text
    secondParameterSelected = text
  })
  cy.get('.fullscreen-dialog .template-readonly p').invoke('text').then(text => preInstanceName = text)
  cy.clickFormActionButton('continue')
  cy.clickButton('radio-Yes')
  cy.clickFormActionButton('save')
})

Then('The newly added Objective Template Pre-instantiation is visible as a new row in the table', () => {
  cy.clickTab('Pre-instance')
  cy.searchAndCheckPresence(preInstanceName, true)
  cy.checkRowByIndex(0, 'Parent template', preInstanceName)
})

When('The objective pre-instantiation metadata is updated', () => {
  fillTemplateNameAndContinue(newObjectiveNameUpdated)
  cy.selectLastMultipleSelect('template-indication-dropdown')
  cy.selectRadioGroup('template-confirmatory-testing', 'Yes')
  cy.clickFormActionButton('continue')
  cy.fillInput('template-change-description', 'updated for test')
  cy.clickFormActionButton('save')
})

Then('The updated Objective is visible within the table', () => {
  cy.searchAndCheckPresence(newObjectiveNameUpdated, true)
  cy.getRowIndex(0, 'Parent template', newObjectiveNameUpdated)
})
