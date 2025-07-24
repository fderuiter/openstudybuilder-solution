const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let crfItemName, crfItemOid

When('Created CRF Item is found', () => cy.searchAndCheckPresence(crfItemName, true))

Then('The CRF Item is no longer available', () => cy.searchAndCheckPresence(crfItemName, false))

Given('[API] The CRF Item in draft status exists', () => {
    crfItemName = `API_CrfItem${Date.now()}`
    cy.createCrfItem(crfItemName, `API_Oid${Date.now()}`)
})

Then("The CRF Item is visible in the table", () => {
    cy.checkRowByIndex(0, 'OID', crfItemOid)
    cy.checkRowByIndex(0, 'Name',crfItemName)
})

When('The CRF Item definition container is filled with data and saved', () => {
    crfItemName = `CrfItem${Date.now()}`
    crfItemOid = `Oid${Date.now()}`
    cy.fillInput('item-oid', crfItemOid)
    cy.fillInput('item-name', crfItemName)
    cy.fixture('crfItem.js').then(item => cy.selectVSelect('item-data-type', item.details.data_type))
})

When('The CRF Item metadata are updated and saved', () => {
    crfItemName += 'Update'
    crfItemOid += 'Update'
    cy.fillInput('item-oid', crfItemOid)
    cy.fillInput('item-name', crfItemName)
})
