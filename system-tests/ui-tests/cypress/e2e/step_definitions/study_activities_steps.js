import { activityName } from "./library_activities_steps";
import { activity_uid, subgroup_uid, group_uid, group_name, requestedActivity_uid } from "../../support/api_requests/library_activities";
import { getCurrentStudyId, getCurrStudyUid } from "./../../support/helper_functions";
const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");
const { getShortUniqueId } = require("../../support/helper_functions");

export let activity_activity, current_activity_uid, study_activity_uid, activity_placeholder_name
export let exchangedActivities = []
let activity_library, activity_soa_group, activity_group, activity_sub_group, edit_placeholder_name, current_study, new_activity_name

When('User sets Activity Placeholder name', () => cy.fillInput('instance-name', activity_placeholder_name = `placeholder_${getShortUniqueId()}`))

When('User sets Activity Placeholder name that is already used', () => cy.fillInput('instance-name', activity_placeholder_name))

When('User sets Activity Placeholder rationale', () => cy.fillInput('activity-rationale', 'Placeholder Test Rationale'))

When('User selects Activity Placeholder SoA group as {string}', (soaGroup) => cy.selectVSelect('flowchart-group', soaGroup))

When('User selects first group for placeholder', () => cy.selectFirstVSelect('activity-group'))

When('User selects second group for placeholder', () => cy.selectSecondVSelect('activity-group'))

When('User selects first subgroup for placeholder', () => cy.selectFirstVSelect('activity-subgroup'))

When('User selects second subgroup for placeholder', () => cy.selectSecondVSelect('activity-subgroup'))

When('User intercepts available studies request', () => cy.intercept('/api/studies/list?minimal_response=false&has_study_activity=true').as('availableStudies'))

When('User waits for available studies request', () => cy.wait('@availableStudies'))

When('Name of Activity from Library for exchaning placeholder is saved', () => cy.getActivityNameByUid().then(name => exchangedActivities.push(name)))

When('Study activity add button is clicked', () => cy.clickButton('add-study-activity'))

Then('The Study Activity is found', () => cy.searchAndCheckPresence(activity_activity, true))

When('Activity placeholder is found', () => cy.searchAndCheckPresence(activity_placeholder_name, true))

Then('The Study Activity Placeholder is not available', () => cy.searchAndCheckPresence(activity_placeholder_name, false))

When('{int} Activity that exchanged the placeholder is found in Study Activities table', (index) => cy.searchAndCheckPresence(exchangedActivities[index -1], true))

Then('The activity request changes are applied', () => cy.searchAndCheckPresence(edit_placeholder_name, true))

Then('The activity request is removed from the study', () => cy.searchAndCheckPresence(edit_placeholder_name, false))

When('Activity placeholder is searched for', () => cy.searchForInPopUp(activity_placeholder_name))

When('{int} Activity for exchanging the placeholder is searched in filters', (index) => cy.get('.border-b').filter(':visible').within(() => { cy.get('input').clear().type(exchangedActivities[index - 1])}))

When('{int} Activity is found and click in the filters', (index) => cy.contains('.v-overlay .v-list-item', exchangedActivities[index - 1]).find('input').check())

//TODO: Issue with finding the filter by the name
When('Activity filter with index {int} is enabled in the form window', (index) => cy.get('.v-overlay [data-cy="filter-field"]').eq(index).click())

When('User clears list of exchanged activities', () => exchangedActivities = [])

When('The second activity is disabled for selection', () => cy.contains('.v-overlay table tbody tr', exchangedActivities[1]).find('input[type=checkbox]').should('be.disabled'))

Given('Study activities for selected study are loaded', () => {
    cy.intercept(`/api/studies/${Cypress.env('TEST_STUDY_UID')}/study-activities?*`).as('getData')
    cy.wait('@getData', { timeout: 30000 })
})

Given('The activity exists in the library', () => {
    cy.log('Handled by import script')
})

When('User tries to add Activity in Draft status', () => {
    cy.searchForInPopUp(activityName)
    cy.waitForTable()
})

When('User search and select activity created via API', () => addLibraryActivityByName())

When('User selects first available activity', () => selectActivityAndGetItsData())

When('User selects first available activity and SoA group', () => selectActivityAndGetItsData('INFORMED CONSENT'))

Then('The Study Activity is visible in table', () => checkIfTableContainsActivity())

Then('The Activity in Draft status is not found', () => cy.contains('.v-sheet table tbody tr', 'No data available'))

When('User selects option to create placeholder without submitting', () => cy.contains('.choice .text', 'Create a placeholder activity without submitting for approval').click())

When('User selects option to create placeholder with submitting', () => cy.contains('.choice .text', 'Request and submit for approval').click())

When('Activity placeholder data is filled in', () => fillPlaceholderData())

When('The activity request approval form is filled with definition', () => {
    cy.get('[data-cy="sponsorform-definition-field"] textarea').not('[readonly]').type('Test')
})

When('Selected study id is saved', () => current_study = getCurrentStudyId())

When('Data collection flag is unchecked', () => cy.get('input[aria-label="Data collection"]').uncheck())

When('Data collection flag is checked', () => cy.get('input[aria-label="Data collection"]').check())

Then('The Study Activity placeholder is visible within the Study Activities table', () => {
    cy.tableContains('Requested')
    cy.tableContains('INFORMED CONSENT')
    cy.tableContains('AE Requiring Additional Data')
    cy.tableContains(activity_placeholder_name)
})

Then('The edited Study Activity data is reflected within the Study Activity table', () => cy.tableContains('EFFICACY'))

When('Activity from studies is selected', () => cy.get('[data-cy="select-from-studies"] input').check())

When('Activity from library is selected', () => cy.get('[data-cy="select-from-library"] input').check({ force: true }))

When('Activity from placeholder is selected', () => cy.get('[data-cy="create-placeholder"] input').check())

Then('The validation appears and Create Activity form stays on Study Selection', () => {
    cy.contains('.v-overlay .v-window-item .v-input', 'Study ID / Acronym').should('contain.text', 'This field is required')
})

When('The user tries to go further without SoA group chosen', () => {
    cy.get('.v-data-table__td--select-row input').not('[aria-disabled="true"]').eq(0).check()
})

When('The user tries to go further in activity placeholder creation without SoA group chosen', () => {
    cy.fillInput('instance-name', `Placeholder Instance Name ${getShortUniqueId()}`)
    cy.fillInput('activity-rationale', 'Placeholder Test Rationale')
})

Then('The validation appears and Create Activity form stays on SoA group selection', () => {
    cy.get('.v-alert').should('contain', 'Every selected Activity needs SoA Group')
    cy.get('[data-cy="flowchart-group"]').should('be.visible')
})

Then('The validation appears under empty SoA group selection', () => {
    cy.get('[data-cy="flowchart-group"]').find('.v-messages').should('contain', 'This field is required')
})

Then('The SoA group can be changed', () => {
    cy.wait(1000)
    cy.selectAutoComplete('flowchart-group', 'EFFICACY')
})

Then('The study activity table is displaying updated value for data collection', () => {
    cy.getCellValue(0, 'Data collection').then(value => cy.wrap(value).should('equal', 'Yes'))
})

Then('Warning that {string} {string} can not be added to the study is displayed', (status, item) => {
    cy.get('.v-alert').should('contain', `has status ${status}. Only Final ${item} can be added to a study.`)
})

When('The existing activity request is selected', () => cy.get('[data-cy="select-activity"] input').check())

When('The study activity request is edited', () => {
    edit_placeholder_name = `Edit name ${getShortUniqueId()}`
    cy.fillInput('instance-name', edit_placeholder_name)
})

When('The study activity request SoA group field is edited', () => {
    cy.get('[data-cy="flowchart-group"]').click()
    cy.contains('.v-list-item', 'HIDDEN').click()
})

When('The study activity request data collection field is edited', () => {
    cy.get('[aria-label="Data collection"]').click()
})

When('The study activity request rationale for activity field is edited', () => {
    cy.fillInput('activity-rationale', "TEST OF UPDATE REDBELL")
})

Then('The updated notification icon and update option are not present', () => {
    cy.get('.v-badge__badge').should('not.exist')
})

When('The user is presented with the changes to request', () => {
    cy.get('[data-cy="form-body"]').should('contain', edit_placeholder_name)
})

Then('[API] Activity is assigned to the visit {int}', (visitIndex) => cy.assignActivityToVisit(Cypress.env('TEST_STUDY_UID'), study_activity_uid, visitIndex))

Then('[API] Activity is assigned to the visit {int} in selected study', (visitIndex) => cy.assignActivityToVisit(getCurrStudyUid(), study_activity_uid, visitIndex))

Then('[API] All Activities are deleted from study', () => {
    cy.getExistingStudyActivities(Cypress.env('TEST_STUDY_UID')).then(uids => uids.forEach(uid => cy.deleteActivityFromStudy(Cypress.env('TEST_STUDY_UID'), uid)))
})

Then('[API] All Activities are deleted from selected study', () => {
    cy.getExistingStudyActivities(getCurrStudyUid()).then((uids) => uids.forEach((uid) => cy.deleteActivityFromStudy(getCurrStudyUid(), uid)))
})

Then('[API] Get SoA Group {string} id', (name) => cy.getSoaGroupUid(name))

Then('[API] Activity is added to the study', () => addActivityToStudyAndGetValues(Cypress.env('TEST_STUDY_UID')))

Then('[API] Activity is added to the selected study', () => addActivityToStudyAndGetValues(getCurrStudyUid()))

Then('[API] Activity with two subgroups available is added to the study', () => {
    cy.createGroup()
    cy.approveGroup()
    cy.createSubGroup()
    cy.approveSubGroup()
    cy.addActivityToStudy(Cypress.env('TEST_STUDY_UID'), activity_uid, group_uid, subgroup_uid).then((response) => {
        activity_activity = response.body[0].content.activity.name
        current_activity_uid = response.body[0].content.activity.uid
    })
    cy.createSubGroup()
    cy.approveSubGroup()
    cy.createSubGroup()
    cy.approveSubGroup()
    cy.createSubGroup()
    cy.approveSubGroup()
})

Then('[API] Create Unsubmitted Requested Activity', () => {
    activity_placeholder_name = `Placeholder_${getShortUniqueId()}`
    cy.getFinalGroupUid()
    cy.getFinalSubGroupUid()
    cy.createUnsubimittedRequestedActivity(activity_placeholder_name)
    cy.approveRequestedActivity()
})

Then('[API] Create Submitted Requested Activity', () => {
    activity_placeholder_name = `Placeholder_${getShortUniqueId()}`
    cy.getFinalGroupUid()
    cy.getFinalSubGroupUid()
    cy.createSubmittedRequestedActivity(activity_placeholder_name)
    cy.approveRequestedActivity()
})

When('[API] Activity for SoA group {string} with activity group {string} is added to the study', (soa_group, activity_group) => {
    let activity_group_filter_value = activity_group.replace(' ', '+')
    cy.addActivityToCurrentStudyFromActivityGroup(soa_group, activity_group_filter_value).then((activity) => {
        activity_sub_group = activity.body[0].content.activity.activity_groupings[0].activity_subgroup_name
        new_activity_name = activity.body[0].content.activity.name
        cy.assignActivityToVisit(getCurrStudyUid(), activity.body[0].content.study_activity_uid, '0')
        })
})

Then('The laboratory assements activities are present in protocol lab table', () => {
    cy.get('.subGroupLabTable').should('contain', activity_sub_group)
    cy.get('.activity').should('contain', new_activity_name)
})

Then('[API] Requested Activity is added to the study', () => cy.addActivityToStudy(getCurrStudyUid(), requestedActivity_uid, group_uid, subgroup_uid))

When('The user accepts the changes', () => cy.contains('button', 'Accept').click())

When('The user declines the changes', () => cy.contains('button', 'Decline').click())

When('The user opens bulk review changes window', () => cy.contains('Review activity updates').click())

When('The user filters the table by red alert status', () => cy.get('[value="updated"]').click())

When('The user filters the table by yellow alert status', () => cy.get('[value="reviewed"]').click())

Then('The activities with red alert are present', () => {
    cy.get('tbody tr').each(row => cy.wrap(row).find('.mdi-alert-circle-outline').should('exist'))
})

Then('The activities with yellow alert are present', () => {
    cy.get('tbody tr').each(row => cy.wrap(row).find('.mdi-alert-outline').should('exist'))
})

Then('The icon indicates which activity group is present in detailed soa', () => {
    cy.contains('[data-cy="form-body"] td', group_name).find('.mdi-eye-outline').should('exist')
})

Then('The icon indicates which activity name is present in detailed soa', () => {
    cy.contains('[data-cy="form-body"] td', new_activity_name).find('.mdi-eye-outline').should('exist')
})

When('User selects {int} activity from Library to exchange placeholder with', (index) => cy.get('.v-data-table__td--select-row input').eq(index - 1).check())

When('Sets SoA Group as {string} for {int} Activity', (soaGroup, index) => selectSoAGroup(index -1, soaGroup))

When('User selects select study {string}', (value) => {
    cy.contains('.v-overlay .v-window-item .v-input', 'Study ID / Acronym').click()
    cy.get('.v-overlay .v-list-item').should('not.contain', 'No data available')
    cy.contains('.v-overlay .v-window-item .v-input', 'Study ID / Acronym').type(value)
    cy.contains('.v-overlay .v-list-item', value).click()
})

When('Pop-up displays that there is already existing placeholder with such name, group and subgroup', () => {
    cy.contains('.v-overlay .v-card .v-card-text', `An activity named '${activity_placeholder_name}'`).should('be.visible')
    cy.contains('.v-overlay .v-card .v-card-text', `already exists in the library. Do you want to reuse it?`).should('be.visible')
})

function getActivityData(rowIndex) {
    cy.getCellValueInPopUp(rowIndex, 'Library').then((text) => activity_library = text)
    cy.getCellValueInPopUp(rowIndex, 'Activity group').then((text) => activity_group = text)
    cy.getCellValueInPopUp(rowIndex, 'Activity subgroup').then((text) => activity_sub_group = text)
    cy.getCellValueInPopUp(rowIndex, 'Activity').then((text) => activity_activity = text.slice(0, 50))
}

function checkIfTableContainsActivity() {
    cy.wait(1000)
    cy.tableContains(activity_library)
    cy.tableContains(activity_soa_group)
    cy.tableContains(activity_group)
    cy.tableContains(activity_sub_group)
    cy.tableContains(activity_activity)
}

function addLibraryActivityByName() {
    activity_activity = activityName
    cy.waitForTable()
    cy.searchForInPopUp(activity_activity)
    cy.waitForTable()
    cy.get('[data-cy="select-activity"] input').check()
    cy.selectVSelect('flowchart-group', 'INFORMED CONSENT')
}

function selectActivityAndGetItsData(soa_group = null) {
    cy.get('.v-data-table__td--select-row input').each((el, index) => {
        if (el.is(':enabled')) {
            cy.wrap(el).check()
            soa_group ? selectSoAGroup(index, activity_soa_group = 'INFORMED CONSENT')
                      : cy.getCellValueInPopUp(index, 'SoA group').then((text) => activity_soa_group = text)
            getActivityData(index)
            return false
        }
    })
}

function fillPlaceholderData() {
    activity_placeholder_name = `Placeholder ${getShortUniqueId()}`
    cy.selectVSelect('flowchart-group', 'INFORMED CONSENT')
    cy.get('[data-cy="activity-group"] input').clear().type('AE Requiring Additional Data')
    cy.selectFirstVSelect('activity-group')
    cy.selectFirstVSelect('activity-subgroup')
    cy.fillInput('instance-name', activity_placeholder_name)
    cy.fillInput('activity-rationale', 'Placeholder Test Rationale')
}

function selectSoAGroup(rowIndex, soaGroup) {
    cy.get('[data-cy="flowchart-group"]').eq(rowIndex).click()
    cy.contains('.v-overlay .v-list-item', soaGroup).click({ force: true })
}

function addActivityToStudyAndGetValues(studyUid) {
    cy.addActivityToStudy(studyUid, activity_uid, group_uid, subgroup_uid).then((response) => {
        activity_activity = response.body[0].content.activity.name
        current_activity_uid = response.body[0].content.activity.uid
        study_activity_uid = response.body[0].content.study_activity_uid
    })
}
