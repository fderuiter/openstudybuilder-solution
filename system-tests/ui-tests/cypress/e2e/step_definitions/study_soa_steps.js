const { When, Then } = require('@badeball/cypress-cucumber-preprocessor')
import { getCurrStudyUid } from '../../support/helper_functions'


When('expand table and Show SoA groups is available on the page', () => {
    cy.get('.mb-4').should('contain', 'Expand table')
    cy.get('.mb-4').should('contain', 'Show SoA groups')
})

Then('The complexity score presents current score for study based on existing acitvities', () => {
    cy.sendGetRequest(`/studies/${getCurrStudyUid()}/complexity-score`).then((response) => {
          cy.contains('Complexity score: ').should('contain', response.body)
    })    
    
})

When('The SoA Splitting is enabled', () => {
    cy.wait(500)
    cy.contains('Split SoA').click({force: true})

})

When('The user splits the SoA by {string}', (visitNumber) => {
    splitSoa(visitNumber, '**/soa-splits')
})

When('The user unsplits the SoA by {string}', (visitNumber) => {
    splitSoa(visitNumber, '**/soa-splits/**')
})

When('The SoA split is created on {string}', (visitNumber) => {
    cy.wait('@splitRequest').then((request) => {
        expect(request.response.statusCode).to.eq(200)
    })
    cy.contains('.split-class', visitNumber).within(() => {
        cy.get('.mdi-content-cut').should('exist')
    })
})

Then('The SoA split on {string} is removed', (visitNumber) => {
    cy.wait('@splitRequest').then((request) => {
        expect(request.response.statusCode).to.eq(200)
    })
    cy.contains('.split-class', visitNumber).should('not.exist')
})

When('the SoA View is switched to {string}', (view) => {
    cy.get(`button[value="${view}]"`).click()
})

function splitSoa(visitNumber, interceptPath) {
    cy.intercept(interceptPath).as('splitRequest')
    cy.contains('.v-btn__content', visitNumber).click()
}