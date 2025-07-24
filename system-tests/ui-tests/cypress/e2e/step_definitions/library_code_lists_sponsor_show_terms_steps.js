const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");



Then('The {string} page is shown', (pageTitle) => {
    cy.get('.page-title').should('contain.text', pageTitle);
})

