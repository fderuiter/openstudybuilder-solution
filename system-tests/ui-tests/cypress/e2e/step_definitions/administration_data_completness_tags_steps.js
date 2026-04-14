const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let currentStudyNumber
let currentStudyUid
let currentTag
let tag1
let tag2
let tag3

Given('A test study {string} for data completion tags test exists', (study_number) => {
    currentStudyNumber = study_number
    cy.createTestStudy(study_number, `Data Completness Tags Tests ${Date.now()}`)
    cy.getStudyUid(study_number).then(uid => {
        currentStudyUid = uid
    })
})

When("The user selects a study to create a completness tag", () => {
    cy.get(`[data-cy="select-study-to-tag"]`).within(() => cy.get('.v-field__input').click())
    cy.get('.v-overlay__content .v-list', { timeout: 20000 })
        .filter(':visible')
        .should('not.contain', 'No data available')
        .within(() => cy.contains('.v-list-item', currentStudyNumber).click())
});

When("The user provides new completness tag into the text field", () => {
    currentTag = Date.now()
    cy.fillInput('tag-name', currentTag)
});

When("The user clicks save button", () => {
    cy.clickButton('save-tag')
});

Then("The data completness tag is created", () => {
    cy.tableContains(currentTag)
});

When("The data completness tag in uncompleted state exists", () => {
    currentTag = Date.now()
    cy.sendPostRequest('/data-completeness-tags', `{ "name": "${currentTag}"}`)

});

When("The user sets the tag to completed for study", () => {
    cy.get(`[data-cy="select-study-to-tag"]`).within(() => cy.get('.v-field__input').click())
    cy.get('.v-overlay__content .v-list', { timeout: 20000 })
        .filter(':visible')
        .should('not.contain', 'No data available')
        .within(() => cy.contains('.v-list-item', currentStudyNumber).click())
    cy.contains('.v-data-table__tr', currentTag).within(() => {
        cy.get('[data-cy="set-tag"]').click()
    })
});

When("The user sets the tag to uncompleted for the study", () => {
    cy.get(`[data-cy="select-study-to-tag"]`).within(() => cy.get('.v-field__input').click())
    cy.get('.v-overlay__content .v-list', { timeout: 20000 })
        .filter(':visible')
        .should('not.contain', 'No data available')
        .within(() => cy.contains('.v-list-item', currentStudyNumber).click())

    cy.contains('.v-data-table__tr', currentTag).within(() => {
        cy.get('[data-cy="set-tag"]').click()
    })
});

When("The data completness tag is visible on study list level for selected study", () => {
    cy.searchFor(currentStudyNumber)
    cy.contains(currentTag).should('not.exist')
});

When("The data completness tag in completed state exists for the study", () => {
    currentTag = Date.now()
    cy.get(`[data-cy="select-study-to-tag"]`).within(() => cy.get('.v-field__input').click())
    cy.get('.v-overlay__content .v-list', { timeout: 20000 })
        .filter(':visible')
        .should('not.contain', 'No data available')
        .within(() => cy.contains('.v-list-item', currentStudyNumber).click())
    cy.fillInput('tag-name', currentTag)
    cy.clickButton('save-tag')
    cy.contains('.v-data-table__tr', currentTag).within(() => {
        cy.get('[data-cy="set-tag"]').click()
    })

});

When("The data completness tag is not on study list level for selected study", () => {
    cy.searchFor(currentStudyNumber)
    cy.contains(currentTag).should('not.exist')
});


When("The user creates multiple completion tags", () => {
    cy.fillInput('tag-name', 'Tag 1')
    cy.clickButton('save-tag')
    cy.fillInput('tag-name', 'Tag 2')
    cy.clickButton('save-tag')
    cy.fillInput('tag-name', 'Tag 3')
    cy.clickButton('save-tag')
    cy.fillInput('tag-name', 'Tag 4')
    cy.clickButton('save-tag')
});

When("Only the completed tag is visible on the study list level for the study", () => {
    cy.searchFor(currentStudyNumber)
});

When("The user sets multiple tags to complete for selected study", () => {
    cy.get(`[data-cy="select-study-to-tag"]`).within(() => cy.get('.v-field__input').click())
    cy.get('.v-overlay__content .v-list', { timeout: 20000 })
        .filter(':visible')
        .should('not.contain', 'No data available')
        .within(() => cy.contains('.v-list-item', currentStudyNumber).click())

    cy.get('.v-data-table__tr').eq(1).within(() => {
        cy.get('td').eq(1).invoke('text').then((value) => tag1 = value)
        cy.get('.v-selection-control__input').click()
    })
    cy.get('.v-data-table__tr').eq(2).within(() => {
        cy.get('td').eq(1).invoke('text').then((value) => tag2 = value)
        cy.get('.v-selection-control__input').click()
    })
    cy.get('.v-data-table__tr').eq(3).within(() => {
        cy.get('td').eq(1).invoke('text').then((value) => tag3 = value)
        cy.get('.v-selection-control__input').click()
    })
});


Then('All the completed tags are visible for the study', () => {
    cy.searchFor(currentStudyNumber)
    cy.tableContains(tag1)
    cy.tableContains(tag2)
    cy.tableContains(tag3)
})