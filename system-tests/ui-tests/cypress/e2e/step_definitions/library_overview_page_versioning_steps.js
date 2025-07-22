import { apiActivityName, apiGroupName, apiSubgroupName, apiInstanceName } from "./api_library_steps";
const { Given, When, Then } = require('@badeball/cypress-cucumber-preprocessor');

let activityName, instanceName, groupName, subgroupName
const checkGroupStatusAndVersion = (status, version) => checkStatusAndVersion('Activity group', groupName, status, version)
const checkSubgroupStatusAndVersion = (status, version) => checkStatusAndVersion('Activity subgroups', subgroupName, status, version)
const checkIfTableEmpty = (type) => cy.contains('.v-row', type).find('table tbody').should('be.empty')

Given('[API] Activity, activity instance, group and subgroup names are fetched', () => {
    cy.getActivityNameByUid().then(name => activityName = name)
    cy.getActivityInstanceNameByUid().then(name => instanceName = name)
    cy.getGroupNameByUid().then(name => groupName = name)
    cy.getSubGroupNameByUid().then(name => subgroupName = name)
})

Given('A test activity overview page is opened', () => goToOverviewPageAndVerify(activityName))

Given('A test instance overview page is opened', () => goToOverviewPageAndVerify(instanceName))

Given('A test group overview page is opened', () => goToOverviewPageAndVerify(groupName))

Given('A test subgroup overview page is opened', () => goToOverviewPageAndVerify(subgroupName))

When('I click {string} button', (title) => cy.get(`button.v-btn[title="${title}"]`).click())

When('I make changes to the activity, enter a reason for change and save', () => edit('activity', activityName))

When('I make changes to the instance and save', () => edit('instance', instanceName))

When('I make changes to the group, enter a reason for change and save', () => {
    edit('group', groupName)
    })

When('I make changes to the subgroup, enter a reason for change and save', () => edit('subgroup', subgroupName))

Then('I verify that the activity version is {string} and status is {string}', (version, status) => {
    cy.get('.version-select .v-select__selection-text').should('have.text', version)
    cy.contains('.summary-label', 'Status').siblings('.summary-value').should('have.text', status)
})

Then('I verify that there is an instance linked with status {string} and version {string}', (status, version) => {
    cy.reload()
    cy.contains('.activity-section .section-header', 'Activity instances').parentsUntil('.activity-section').within(section => {
        cy.wrap(section).contains('table tbody tr', instanceName).find('.mdi-chevron-right').click()
        cy.wrap(section).contains('table tbody tr', version).should('contain', status)        
    })
})

Then('I verify that linked Activity Instances table is empty', () => {
    cy.contains('.activity-section .section-header', 'Activity instances').parentsUntil('.activity-section').within(section => {
        cy.wrap(section).get('table tbody tr td').should('have.text', 'No activity instances found for this activity.')
    })
})

Then('I verify that in the table Activity groupings there is an activity with status {string} and version {string}', (status, version) => {
    cy.contains('.activity-section', 'Activity groupings').within(() => {
        cy.checkRowByIndex(0, 'Activity', activityName)
        cy.checkRowByIndex(0, 'Activity', status)
        cy.checkRowByIndex(0, 'Activity', version)
    })
})

Then('I verify that in the table Activities there is an activity with status {string} and version {string}', (status, version) => {
    cy.contains('.my-5', 'Activities').within(() => {
        cy.checkRowByIndex(0, 'Name', activityName)
        cy.checkRowByIndex(0, 'Status', status)
        cy.checkRowByIndex(0, 'Version', version)
    })
})

Then('I verify that no Activities are linked', () => {
    cy.contains('.my-5', 'Activities').within(() => cy.get('table tbody tr').should('have.text', 'No items available'))
})

Then('User verifies that version is {string} and status is {string}', (version, status) => {
    cy.get('.summary-value .version-select .v-select__selection-text').should('have.text', version)
    cy.contains('.summary-label', 'Status').siblings('.summary-value').should('have.text', status)
})

Then('I verify that the group version is {string} and status is {string}', (version, status) => {
    cy.get('.version-select .v-select__selection-text').should('have.text', version)
    cy.contains('.summary-label', 'Status').siblings('.summary-value').should('have.text', status)
})

Then('I verify the definition is {string}', (definition) => cy.contains('.v-col', 'Definition').next().should('have.text', definition))

When('I select the earlier version 2.0 from the version dropdown list', () => {
    cy.get('.v-col:contains("Version") + .v-col .v-select__selection').should('have.text', '2.0');
})

Then('I verify that no {string} is linked', (type) => checkIfTableEmpty(type))

Then('I verify that there is a group with status {string} and version {string}', (status, version) => checkGroupStatusAndVersion(status, version))

Then('I verify that there is a subgroup with status {string} and version {string}', (status, version) => checkSubgroupStatusAndVersion(status, version))

Then('I verify that the test subgroup with status {string} and version {string} is linked', (status, version) => {
    cy.get('.group-overview-container').should('contain.text', 'Activity subgroups');
    // Assert that the table exists using the subgroups-table class
    cy.get('.subgroups-table').first().get('[data-cy="data-table"] tbody tr').first().within(() => {      
        cy.get('.v-data-table__td').then(($headers) => {
              // Extract the text of each header
              const headerTexts = $headers.map((index, header) => Cypress.$(header).text().trim()).get();
                cy.wrap($headers[0]).should('contain.text', apiSubgroupName); // First Column Check 
                cy.wrap($headers[2]).should('contain.text', version); // Version Check
                cy.wrap($headers[3]).should('contain.text', status); // Status Check
          });
      });
    });

function goToOverviewPageAndVerify(name) {
    cy.searchAndCheckPresence(name, true)
    cy.get('table tbody tr td').contains(name).click()
    cy.get('.d-flex.page-title').should('contain.text', name);
    cy.get('button[role="tab"][value="html"]').contains('Overview');
}

function edit(type, name) {
    cy.wait(2000)
    if (type == 'instance') {
        cy.clickFormActionButton('continue')
        cy.clickFormActionButton('continue')
        cy.fillInput('instanceform-instancename-field',  `Update ${name}`)
    }
    else if (type == 'activity') {
        cy.fillInput('activityform-activity-name-field', `Update ${name}`)
        cy.contains('.v-col', 'Reason for change').find('textarea').not('.v-textarea__sizer').type('Test purpose')
    }
    else {
        cy.fillInput('groupform-activity-group-field', `Update ${name}`)
        cy.fillInput('groupform-change-description-field', "Test purpose")
    }
    cy.clickFormActionButton('save')
}

function checkStatusAndVersion(type, name, status, version) {
    cy.get('.v-row').contains(new RegExp(`^${type}$`, "g")).parent().find('table tbody').within(() => {
        cy.contains('tr', status).should('contain', name).should('contain', version)
    })
}
