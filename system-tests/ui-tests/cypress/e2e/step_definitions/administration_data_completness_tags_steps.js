const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let currentStudyNumber
let currentTag
let tag1
let tag2
let tag3

Given('A test study {string} for data completion tags test exists', (study_number) => {
    currentStudyNumber = study_number
    cy.createTestStudy(study_number, `Data Completness Tags Tests ${Date.now()}`)
})

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
    selectTagStudy(currentStudyNumber)
    setTag(currentTag)
});

When("The user sets the tag to uncompleted for the study", () => {
    selectTagStudy(currentStudyNumber)
    setTag(currentTag)
});

When("The data completness tag is visible on study list level for selected study", () => {
    cy.searchFor(currentStudyNumber)
    cy.contains(currentTag).should('exist')
});

When("The data completness tag in completed state exists for the study", () => {
    currentTag = Date.now()
    selectTagStudy(currentStudyNumber)
    createTag(currentTag)
    setTag(currentTag)

});

When("The data completness tag is not on study list level for selected study", () => {
    cy.searchFor(currentStudyNumber)
    cy.contains(currentTag).should('not.exist')
});


When("The user creates multiple completion tags", () => {
    tag1 = `Tag1 ${Date.now()}`
    tag2 = `Tag2 ${Date.now()}`
    tag3 = `Tag3 ${Date.now()}`
    createTag(tag1)
    createTag(tag2)
    createTag(tag3)

});

When("Only the completed tag is visible on the study list level for the study", () => {
    cy.searchFor(currentStudyNumber)
});

When("The user sets multiple tags to completed for selected study", () => {
    selectTagStudy(currentStudyNumber)
    setTag(tag1)
    setTag(tag2)
    setTag(tag3)

});


Then('All the completed tags are visible for the study', () => {
    cy.searchFor(currentStudyNumber)
    cy.tableContains(tag1)
    cy.tableContains(tag2)
    cy.tableContains(tag3)
})


function setTag(tag) {
    cy.contains('.v-data-table__tr', tag).within(() => {
        cy.get('input').click()
    })
}

function createTag(tag) {
    cy.fillInput('tag-name', tag)
    cy.clickButton('save-tag')
}

function selectTagStudy(study) {
    cy.selectAutoComplete("select-study-to-tag", study, { defocus: false })
}