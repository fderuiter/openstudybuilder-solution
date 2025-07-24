import { fillTemplateNameAndContinue, changeIndex } from './library_syntax_templates_common'
const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let defaultActivityName

Then('The Activity Instruction template is visible in the table', () => cy.checkRowByIndex(0, 'Parent template', defaultActivityName))

When("The Activity Group index is cleared", () => cy.clearField('template-activity-group'))

When("The Activity Subgroup index is cleared", () => cy.clearField('template-activity-sub-group'))

When("The Activity index is cleared", () => cy.clearField('template-activity-activity'))

Then("The validation appears for Activity field", () => cy.checkIfValidationAppears('template-activity-activity'))

Then("The validation appears for activity template group field", () => cy.checkIfValidationAppears(`template-activity-group`))

Then("The validation appears for activity template subgroup field", () => cy.checkIfValidationAppears(`template-activity-sub-group`))

Then("The activity instruction is found", () => cy.searchAndCheckPresence(defaultActivityName, true))

Then("The parent activity is no longer available", () => cy.searchAndCheckPresence(defaultActivityName, false))

When('The activity instruction is saved and searched for', () => saveActivityInstructionAndSearch())

Then('Activity Instruction is searched for', () => saveActivityInstructionAndSearch(false))

When('The activity instruction template form is filled with already existing name', () => fillTemplateNameAndContinue(defaultActivityName))

When('The mandatory indexes are filled', () => changeMandatoryIndexes(false, false))

When('All activity instruction indexes are filled in', () => changeIndexes(false, false))

When('All activity instruction indexes are cleared and filled in', () => changeIndexes(true, true))

When('The activity instruction template form is filled with base data', () => fillBaseData(`ActivityInstruction${Date.now()}`))

When('The activity template metadata update is started', () => fillBaseData(`Update${Date.now()}`))

When('The activity template edition form is filled with data', () => fillBaseData(`CancelEdit${Date.now()}`))

Then('[API] Activity Instruction in status Draft exists', () => createActivityInstructionViaApi())

Then('[API] Activity Instruction is approved', () => cy.approveActivityInstruction())

Then('[API] Activity Instruction is inactivated', () => cy.inactivateActivityInstruction())

When('[API] Search Test - Create first activity instruction template', () => {
  defaultActivityName = `SearchTest${Date.now()}`
  createActivityInstructionViaApi(defaultActivityName)
})

When('[API] Search Test - Create second activity instruction template', () => createActivityInstructionViaApi(`SearchTest${Date.now()}`))

function createActivityInstructionViaApi(customName = '') {
  cy.getInidicationUid()
  cy.createActivityInstruction(customName)
  cy.getActivityInstructionName().then(name => defaultActivityName = name.replace('<p>', '').replace('</p>', '').trim())
}

function saveActivityInstructionAndSearch(save = true) {
  cy.intercept('/api/activity-instruction-templates?page_number=1&*').as('getTemplate')
  if (save) cy.clickFormActionButton('save')
  cy.wait('@getTemplate', {timeout: 20000})
  cy.waitForTable()
  cy.searchAndCheckPresence(defaultActivityName, true)
}

function changeIndexes(update, clear) {
  cy.wait(1000)
  changeMandatoryIndexes(update, clear)
  changeIndex('template-indication-dropdown', update, clear)
  changeIndex('template-activity-activity', update, clear)
}

function changeMandatoryIndexes(update, clear) {
  changeIndex('template-activity-group', update, clear)
  changeIndex('template-activity-sub-group', update, clear)
}

function fillBaseData(name) {
  defaultActivityName = name
  fillTemplateNameAndContinue(name)
}