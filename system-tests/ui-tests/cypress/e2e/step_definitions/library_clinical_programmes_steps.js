const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let programmeName, projectName

When('Clinical programme is found', () => cy.searchAndCheckPresence(programmeName, true))

When('Clinical programme is no longer available', () => cy.searchAndCheckPresence(programmeName, false))

When('Click on the + button to create a new clinical programme', () => cy.clickButton('add-clinical-programme'))

When('Input a clinical programme name', () => fillName(`Programme ${Date.now()}`))

Given('A test clinical programme exists and is not linked to any project', () => fillName(`Programme ${Date.now()}`))

When('Update the clinical programme name to a new one', () => fillName(`Update ${Date.now()}`))

When('User tries to update programme name', () => cy.fillInput('clinical-programme-name', 'Update'))

Given ('Create project and link it to the programme', () => {
    projectName = `Test project ${Date.now()}` 
    cy.selectAutoComplete('template-activity-group', programmeName)
    cy.fillInput('project-name', projectName)
    cy.fillInput('project-number', Date.now())
    cy.fillInput('project-description', `Test description ${Date.now()}`)
});

function fillName(name) {
    programmeName = name
    cy.fillInput('clinical-programme-name', programmeName) 
}