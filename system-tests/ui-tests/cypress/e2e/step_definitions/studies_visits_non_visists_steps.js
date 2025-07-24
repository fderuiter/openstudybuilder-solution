const { When, Then } = require("@badeball/cypress-cucumber-preprocessor");

When('The non visit is created', () => {
    cy.waitForTable()
    cy.clickButton('add-visit')
    cy.contains('.v-radio', 'Non visit').within(() => {
        cy.get('input').click()
    })
    cy.clickFormActionButton('continue')
    cy.selectFirstVSelect('study-period')
    cy.clickFormActionButton('continue')
    cy.intercept('**study-visits').as('createdVisit')
    cy.clickFormActionButton('save')
    cy.waitForTable()
})



Then('The non visit is present in the table', (visit_name) => {
    cy.wait('@createdVisit').then((request) => {
        expect(request.response.body.visit_class).to.eq('NON_VISIT')

    })
})

When('The user opens edit form for non visit', () => {
    cy.searchFor('Non-visit')
    cy.performActionOnSearchedItem('Edit')
    cy.clickFormActionButton('continue')
    cy.clickFormActionButton('continue')
})

Then('The visit number field is disabled', () => {
    cy.get('[data-cy="visit-number"]').should('have.class', 'v-input--disabled')
})