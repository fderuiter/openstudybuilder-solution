const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let formNameDefault, formOidDefault

When('Created CRF form is found', () => cy.searchAndCheckPresence(formNameDefault, true))

Then('The CRF Form is no longer available', () => cy.searchAndCheckPresence(formOidDefault, false))

When('The Form definition container is filled with data', () => changeFormData(`CrfForm${Date.now()}`, `CrfForm${Date.now()}`))

When('The Form metadata are updated and saved', () => changeFormData(`Update ${formNameDefault}`, `Update ${formOidDefault}`))

function changeFormData(formName, formOid) {
    formOidDefault = formName
    formNameDefault = formOid
    cy.fillInput('form-oid-name', formNameDefault)
    cy.fillInput('form-oid', formOidDefault)
}