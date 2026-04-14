import { activity_activity, activity_placeholder_name, exchangedActivities } from "./study_activities_steps";

const { When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let groupName, subgroupName, activityName, new_activity_name
let first_in_order, last_in_order
let activity_list = []

When('User intercepts reorder activities request', () => cy.intercept('**/order').as('orderRequest'))

When('User waits for reorder activities request', () => cy.wait('@orderRequest'))

When('User clicks Finish reordering button', () => cy.contains('.v-btn', 'Finish reordering').click())

When('Detailed SoA table is loaded', () => cy.get('[aria-label="Loading..."]').should('not.exist'))

When ('{string} view is available in SoA', (viewName) => cy.contains('.layoutSelector button', viewName).should('be.visible'))

When ('{string} view is not available in SoA', (viewName) => cy.contains('.layoutSelector button', viewName).should('not.exist'))

When('Action {string} is selected for first study activity', (action) => {
    cy.get('table tbody tr.bg-white').eq(0).within(() => cy.clickButton('table-item-action-button'))
    cy.clickButton(action)
})

When('Action {string} is selected for study activity', (action) => {
    cy.contains('table tbody tr.bg-white', activityName).within(() => cy.clickButton('table-item-action-button'))
    cy.clickButton(action)
})

When('Action {string} is selected for study activity placeholder', (action) => {
    cy.contains('table tbody tr', activity_placeholder_name).within(() => cy.clickButton('table-item-action-button'))
    cy.clickButton(action)
})

When('Activity checkbox is checked for {int} activity on the list', (index) => {
    cy.contains('table tbody tr.bg-white', activity_list[index]).within(() => cy.get('[id^="checkbox"]').check())
})

When('The user goes through selection from library form', () => {
    cy.get('[data-cy="select-activity"]').not('.v-selection-control--disabled').parentsUntil('tr').siblings().eq(4).invoke('text').then((activity_name) => {
        new_activity_name = activity_name.substring(0, 50)
    })
    cy.get('[data-cy="select-activity"]').not('.v-selection-control--disabled').first().click()
    cy.get('[data-cy="flowchart-group"]').not('.v-input--disabled').first().click()
    cy.get('.v-list-item').filter(':visible').first().click()
})

Then('The newly selected activity replaces previous activity in study', () => {
    cy.get('table tbody tr.bg-white .ml-4').invoke('text').then(text => cy.wrap(text.trim()).should('equal', new_activity_name))
})

Then('The old activity is no longer available', () => cy.contains('table tbody tr.bg-white', new RegExp(`^(${activityName})$`, "g")).should('not.exist'))

Then('The Activity is visible in the SoA', () => cy.contains(activity_activity.substring(0, 50)).should('be.visible'))

When('The user selects {string} action after clicking Bulk actions', (action) => {
    cy.get('button .mdi-folder-multiple-outline').click()
    cy.contains('.v-list-item', action).click()
})

Then('The bulk edit view is presented to user allowing to update Activity Group and Visits for selected activities', () => {
    cy.get('[data-cy="form-body"]').should('contain', 'Batch edit study activities')
    cy.get('[data-cy="form-body"]').should('contain', 'Note: The entire row of existing selections will be overwritten with the selection(s) done here')
    cy.get('[data-cy="form-body"]').should('contain', 'Batch editing will overwrite existing choices. Only activities expected to have same schedule should be batch-edited together.')
    cy.get('[data-cy="form-body"]').should('contain', activity_list[0])
})

When('The user edits activities in bulk', () => {
    cy.slectFirstVSelect('bulk-edit-soa-group')
    cy.slectFirstVSelect('bulk-edit-visit')
})

Then('User intercepts bulk edit request', () => cy.intercept('**/soa-edits/batch').as('editRequest'))

Then('The data for bulk edited activities is updated', () => cy.wait('@editRequest').its('response.statusCode').should('equal', 207))

Then('The validation appears for Activity Group field in bulk edit form', () => {
    cy.get('[data-cy="form-body"] .v-input').eq(2).should('contain', 'This field is required')
})

When('Batch request is intercepted', ()=> cy.intercept('**/study-activities/batch').as('deleteRequest'))

Then('The activities are removed from the study', () => cy.wait('@deleteRequest').its('response.statusCode').should('equal', 207))

When('The user enables the Reorder Activities function for acitivities in the same flowchart group', () => {
    cy.contains('tr[class="bg-white"]', activity_list[0]).within(() => cy.clickButton('table-item-action-button'))
    cy.clickButton('Reorder')
})

When('The user updates the order of activities', () => {
    cy.get('.mdi-sort').first().parentsUntil('td').invoke('text').then((text) => last_in_order = text)
    cy.get('.mdi-sort').last().parentsUntil('td').invoke('text').then((text) => first_in_order = text)

    cy.get('.mdi-sort').last().parentsUntil('td').drag('tr.bg-white', {
        source: { x: 0, y: -50 }, // applies to the element being dragged
        target: { position: 'left' }, // applies to the drop target
        force: true, // applied to both the source and target element)
    })
})

Then('The new order of activites is visible', () => {
    cy.get('tr.bg-white').first().should('contain', first_in_order)
    cy.get('tr.bg-white').eq(1).should('contain', last_in_order)
})

Then('Text about no added visits and activities is displayed', () => cy.get('.v-empty-state__title').should('have.text', 'No activities & visits added yet'))

Then('User can click Add visit button', () => cy.contains('button', 'Add visit').click())

Then('User can click Add study activity button', () => cy.contains('button', 'Add study activity').click())

Then('No activities are found', () => cy.get('table[aria-label="SoA table"] .bg-white').should('not.exist'))

Then('Activity is found in table', () => cy.contains('table[aria-label="SoA table"] .bg-white', activityName).should('exist'))

Then('{int} Activity that exchanged the placeholder is found in table', (index) => cy.contains('table[aria-label="SoA table"] .bg-white', exchangedActivities[index - 1]).should('exist'))

When('User search for non-existing activity', () => cy.contains('.v-input__control', 'Search').type('xxx'))

When('User search for {int} activity on the list', (index) => cy.contains('.v-input__control', 'Search').type(activity_list[index]))

When('User search study activity placeholder', () => cy.contains('.v-input__control', 'Search').type(activity_placeholder_name))

When('User search {int} activity that exchanged the placeholder', (index) => cy.contains('.v-input__control', 'Search').find('input').type(exchangedActivities[index - 1]))

When('User search added activity in detailed SoA', () => cy.contains('.v-input__control', 'Search').type(activity_activity))

When('User search study activity', () => cy.contains('.v-input__control', 'Search').type(activityName))

When('User search for new study activity', () => cy.contains('.v-input__control', 'Search').type(new_activity_name))

When('User search study activity in lowercase', () => cy.contains('.v-input__control', 'Search').type(activityName.toLowerCase()))

When('User search study activity by partial name', () => cy.contains('.v-input__control', 'Search').type(activityName.slice(-3)))

When('User search study activity by subgroup', () => cy.contains('.v-input__control', 'Search').type('API_SubGroup'))

When('User search study activity by group', () => cy.contains('.v-input__control', 'Search').type('API_Group'))

When('User clears study activity search', () => cy.contains('.v-input__control', 'Search').find('input').clear())

When('User expand table', () => cy.contains('.v-selection-control', 'Expand table').find('input').check())

When('Row containing submitted placeholder is highlighted with yellow color', () => cy.contains('tr[id*="StudyActivity_"].bg-yellow', activity_placeholder_name).should('be.visible'))

When('Row containing unsubmitted placeholder is highlighted with orange color', () => cy.contains('tr[id*="StudyActivity_"].bg-warning', activity_placeholder_name).should('be.visible'))

When('Placeholder is no longer available', () => cy.contains('tr[id*="StudyActivity_"]', activity_placeholder_name).should('not.exist'))

When('User selects visits {string}', (visitList) => {
    const visitListArray = visitList.split(',')
    visitListArray.forEach(visit => cy.contains('table thead th', visit.trim()).find('input').check())
})

When('Button for collapsing visits is clicked', () => cy.get('button .mdi-arrow-expand-horizontal').click())

When('Button for collapsing visits is not available', () => cy.get('button .mdi-arrow-expand-horizontal').should('not.be.visible'))

When('Option for collapsing in {string} is selected', (value) => cy.get(`input[value="${value}"]`).check({force: true}))

Then('Visits are no longer collapsed in detailed SoA view', () => {
    cy.get('table thead tr').should('not.contain', 'V2-V4')
    cy.get('table thead tr').should('not.contain', 'V2,V3,V4')
})

Then('Visits study weeks are no longer collapsed in detailed SoA view', () => {
    cy.get('table thead tr').should('not.contain', '1-4')
    cy.get('table thead tr').should('not.contain', '1,2,4')
})

Then('Visits are collapsed as {string} in detailed SoA view', (visitsGroup) => cy.contains('table thead tr', visitsGroup))

Then('Visits study weeks are collapsed as {string} in detailed SoA view', (weeksGroup) => cy.contains('table thead tr', weeksGroup))

Then('Visit group delete button is clicked', () => cy.get('button[title="Delete this group"]').click())

Then('Error message is displayed for collapsing visits with different epochs', () => cy.checkSnackbarMessage("Given Visits can't be collapsed as they exist in different Epochs"))

Then('Add footnote button is available in the detailed SoA', () => cy.get(`[title="Add SoA footnotes"]`).should('be.visible'))

Then('SoA table is available with Bulk actions, Export and Show version history', () => {
    cy.get('button .mdi-folder-multiple-outline').should('be.visible')
    cy.get('[data-cy="table-export-button"]').should('be.visible')
    cy.get('.mb-4 button .mdi-history').should('be.visible')
})

Then('Search is available in SoA table', () => cy.contains('.v-label', 'Search').parent().within(() => cy.get('input').should('exist')))

Then('Button for Expanding SoA table is available', () => cy.contains('.v-selection-control', 'Expand table').should('be.visible'))

Then('SoA table is visible with following headers', (options) => {
    options.rows().forEach(option => cy.contains('table tr th.header.zindex25', `${option}`).should('be.visible'))
})

Then('Activity, Group And Subgroup names are fetch to be used in SoA', () => {
    cy.getGroupNameByUid().then(name => groupName = name)
    cy.getSubGroupNameByUid().then(name => subgroupName = name)
    cy.getActivityNameByUid().then(name => activityName = name)
})

Then('Activity name is added to the list', () => cy.getActivityNameByUid().then(name => activity_list.push(name)))

Then('Activity name list is cleared', () => activity_list = [])

Then('Group is visible in the protocol SoA', () => cy.contains('th.group', groupName).should('be.visible'))

Then('Subgroup is visible in the protocol SoA', () => cy.contains('th.subGroup', subgroupName).should('be.visible'))

Then('Activity is visible in the protocol SoA', () => cy.contains('th.activity', activityName).should('be.visible'))

Then('Group is not visible in the protocol SoA', () => cy.contains('th.group', groupName).should('not.exist'))

Then('Subgroup is not visible in the protocol SoA', () => cy.contains('th.subGroup', subgroupName).should('not.exist'))

Then('Activity is not visible in the protocol SoA', () => cy.contains('th.activity', activityName).should('not.exist'))

When('User switches to the {string} view', (view) => cy.get(`button[value="${view}"]`).click())

When('User clicks eye icon on SoA group level for {string}', (flowchart) => cy.contains('tr.flowchart', flowchart).find('.v-icon--size-x-small').click())

When('User clicks eye icon on group level', () => cy.contains('tr.group', groupName).find('.v-icon--size-x-small').click())

When('User clicks eye icon on subgroup level', () => cy.contains('tr.subgroup', subgroupName).find('.v-icon--size-x-small').click())

When('User clicks eye icon on activity level', () => cy.contains('tr[id*="StudyActivity_"]', activityName).find('.v-icon--size-x-small').click())

When('User waits for the protocol SoA table to load', () => cy.get('[id="protocolFlowchart"]').should('be.visible'))

Then('Activity SoA group, group, subgroup and name are visible in the detailed view', () => verifySoATable('table[aria-label="SoA table"] tbody tr'))

Then('Epoch {string} and epoch {string} are visible in the detailed view', (epoch1, epoch2) => {
    cy.contains('table[aria-label="SoA table"] thead tr th', 'Epoch').should('be.visible')
        .next().should('contain.text', epoch1).should('be.visible')
            .next().next().should('contain.text', epoch2).should('be.visible')
})

Then('Visits {string}, {string}, {string} are visible in the detailed view', (visit1, visit2, visit3) => {
    verifySoATableHeaders('table[aria-label="SoA table"] thead tr th', 'Visit', visit1, visit2, visit3)
})

Then('Study weeks {int}, {int}, {int} are visible in the detailed view', (week1, week2, week3) => {
    verifySoATableHeaders('table[aria-label="SoA table"] thead tr th', 'Study week', week1, week2, week3)
})

Then('Study visit windows {string}, {string}, {string} are visible in the detailed view', (window1, window2, window3) => {
    verifySoATableHeaders('table[aria-label="SoA table"] thead tr th', 'Visit window (days)', window1, window2, window3)
})

Then('Activity SoA group, group, subgroup and name are visible in the protocol view', () => verifySoATable('[id="protocolFlowchart"] table tbody tr'))

Then('Epoch {string} and epoch {string} are visible in the protocol view', (epoch1, epoch2) => {
    cy.contains('[id="protocolFlowchart"] table thead tr th', 'Procedure').should('be.visible')
        .next().should('contain.text', epoch1).should('be.visible')
            .next().should('contain.text', epoch2).should('be.visible')
})

Then('Visits {string}, {string}, {string} are visible in the protocol view', (visit1, visit2, visit3) => {
    verifySoATableHeaders('[id="protocolFlowchart"] table thead tr th', 'Visit short name', visit1, visit2, visit3)
})

Then('Study weeks {int}, {int}, {int} are visible in the protocol view', (week1, week2, week3) => {
    verifySoATableHeaders('[id="protocolFlowchart"] table thead tr th', 'Study week', week1, week2, week3)
})

Then('Study visit windows {string}, {string}, {string} are visible in the protocol view', (window1, window2, window3) => {
    verifySoATableHeaders('[id="protocolFlowchart"] table thead tr th', 'Visit window (days)', window1, window2, window3)
})

Then('[API] Study Activity based on existing group and subgroup is created and approved', () => (cy.createActivity(), cy.approveActivity()))

Then('[API] Group and subgroup are created and approved', () => {
    cy.createGroup(), cy.approveGroup()
    cy.createSubGroup(), cy.approveSubGroup()
})


function verifySoATable(tableLocator) {
    cy.contains(`${tableLocator}`, 'INFORMED CONSENT').should('be.visible')
        .next().should('contain.text', groupName).should('be.visible')
            .next().should('contain.text', subgroupName).should('be.visible')
                .next().should('contain.text', activityName).should('be.visible')
}

function verifySoATableHeaders(tableLocator, key, v1, v2, v3) {
    cy.contains(tableLocator, key).should('be.visible')
        .next().should('contain.text', v1).should('be.visible')
            .next().should('contain.text', v2).should('be.visible')
                    .next().should('contain.text', v3).should('be.visible')
}