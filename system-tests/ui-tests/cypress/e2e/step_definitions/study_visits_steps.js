const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");
import { getCurrStudyUid } from '../../support/helper_functions'

let studyVisits_uid

When('User is presented with correct unscheduled visit name', () => cy.get('[data-cy="visit-name"] input').should('have.value', 'Unscheduled'))

When('User is presented with visit start rule set as {string}', (startRule) => cy.get(`[data-cy="visit-start-rule"] textarea[value="${startRule}"]`).should('be.visible'))

When('User must be able to set vist start rule as {string}', (startRule) => cy.get('[data-cy="visit-start-rule"] [class="v-field__input"]').clear().type(startRule))

When('User waits for the Basic epoch for unscheduled visit to load', () => cy.get('[data-cy="study-period"]').should('contain.text', 'Basic'))

When('User intercepts create visit request', () => cy.intercept('**/study-visits').as('visitRequest'))

When('User search for visit with name {string}', (visitName) => cy.searchAndCheckPresence(visitName, true))

When('Epoch {string} is selected for the visit', (epoch) => cy.selectVSelect('study-period', epoch))

When('First available epoch is selected', () => cy.selectFirstVSelect('study-period'))

When('Time unit {string} is selected for the visit', (timeUnit) => cy.selectVSelect('time-unit', timeUnit))

When('Visit timing {int} is selected for the visit', () => cy.fillInput('visit-timing', 7))

Given('The study visits uid array is cleared', () => cy.cleanStudyVisitsUidArray())

Given('There are at least 3 visits created for the study', () => cy.log('pending implementation'))

When('Anchor visit checkbox is checked', () => cy.get('[data-cy="anchor-visit-checkbox"] input').check())

Given('Add visit button is clicked', () => cy.clickButton('add-visit'))

Given('Visit scheduling type is selected as {string}', (visitType) => cy.get(`[data-cy=${visitType}] input`).check())

When('Visit description is changed to {string}', (value) => cy.fillInput('visit-description', value))

Then('Visit number field is disabled', () => cy.get('[data-cy="visit-number"]').should('have.class', 'v-input--disabled'))

When('Visit Type is selected as {string}', (visitType) => {
    cy.get('[data-cy="visit-type"]').click()
    cy.contains('.v-list-item', visitType).click()
})

When('Contact mode is selected as {string}', (contactMode) => {
    cy.get('[data-cy="contact-mode"]').click()
    cy.contains('.v-list-item', contactMode).click()
})

When('Time reference is selected as {string}', (timeReference) => {
    cy.get('[data-cy="time-reference"]').click()
    cy.contains('.v-list-item-title', timeReference, {matchCase: true}).click()
})

Then('Visits {string} have group displayed as {string} in table', (visits, group) => {
    const visitArray = visits.split(',')
    const visitsIndexes = []
    visitArray.forEach(visit => visitArray.push(visit.trim().replace('V', '') - 1))
    visitsIndexes.forEach(index => cy.checkRowByIndex(index, 'Collapsible visit group', group))
})

Then('The validation appears for missing study period', () => cy.checkIfValidationAppears('study-period'))

Then('The validation appears for missing visit type', () => cy.checkIfValidationAppears('visit-type'))

Then('The validation appears for missing contact mode', () => cy.checkIfValidationAppears('contact-mode'))

Then('The validation appears for missing time reference', () => cy.checkIfValidationAppears('time-reference'))

Then('The validation appears for missing visit timing', () => cy.checkIfValidationAppears('visit-timing'))

Then('It is not possible to edit Time Reference for anchor visit', () => {
    cy.get('[data-cy="time-reference"]').should('have.class', 'v-input--disabled')
})

Then('Visit description is displayed in the table as {string}', (value) => cy.checkRowByIndex(0, 'Visit description', value))

Then('The new Anchor Visit is visible within the Study Visits table', () => {
    cy.checkRowByIndex(0, 'Global anchor visit', 'Yes')
    cy.checkRowByIndex(0, 'Visit name', 'Visit 1')
    cy.checkRowByIndex(0, 'Time reference', 'Global anchor visit')
    cy.checkRowByIndex(0, 'Timing', '0 day')
    cy.checkRowByIndex(0, 'Visit number', '1')
    cy.checkRowByIndex(0, 'Visit short name', 'V1')
    cy.checkRowByIndex(0, 'Study duration days', '0 days')
    cy.checkRowByIndex(0, 'Study duration weeks', '0 weeks')
    cy.checkRowByIndex(0, 'Study day', 'Day 1')
    cy.checkRowByIndex(0, 'Study week', 'Week 1')
    cy.checkRowByIndex(0, 'Week in Study', 'Week 0')
})

Then('Study visit class is {string} and the timing is empty', (visitClass) => {
    cy.checkRowByIndex(0, 'Visit Class', visitClass)
    cy.checkRowByIndex(0, 'Timing', '')
})

Then('Visits are no longer grouped in table', () => {
    cy.checkRowByIndex(1, 'Collapsible visit group', '')
    cy.checkRowByIndex(2, 'Collapsible visit group', '')
    cy.checkRowByIndex(3, 'Collapsible visit group', '')
})

Then('The Anchor visit checkbox is disabled', () => {
    cy.wait(1500)
    cy.get('[data-cy="anchor-visit-checkbox"]').should('not.exist')
})

Then('The study epoch field is enabled for editing', () => cy.get('[data-cy="study-period"] .v-field--active').should('exist'))

When('The user tries to update last treatment visit epoch to Screening without updating the timing', () => cy.log('pending implementation'))

Then('Warning about visit window unit selection is displayed', () => cy.get('.v-alert').should('contain.text', "The  visit window unit   (days/weeks) you choose for the  first visit  will apply to all subsequent visits and  can't  be changed later without  deleting all visits.  This means that if you want to change the unit, you'll need to  remove all the subsequent visits  while keeping the first one, update the unit, and then  set up the remaining visits again."))

When('[API] Study vists uids are fetched for study {string}', (study_uid) => cy.getExistingStudyVisits(study_uid).then(uids => studyVisits_uid = uids))

When('[API] Study vists uids are fetched for current study', () => cy.getExistingStudyVisits(`${Cypress.env('TEST_STUDY_UID')}`).then(uids => studyVisits_uid = uids))

When('[API] Study vists uids are fetched for selected study', () => cy.getExistingStudyVisits(getCurrStudyUid()).then(uids => studyVisits_uid = uids))

When('[API] Study visits in study {string} are cleaned-up', (study_uid) => deleteVisits(study_uid))

When('[API] Study visits in selected study are cleaned-up', () => deleteVisits(getCurrStudyUid()))

When('[API] Study visits in current study are cleaned-up', () => deleteVisits(`${Cypress.env('TEST_STUDY_UID')}`))

Given('[API] The epoch with type {string} and subtype {string} exists in selected study', (type, subtype) => {
    createEpochViaAPI(type, subtype)
})

Given('[API] The static visit data is fetched', () => getVisitStaticData())

Given('[API] The dynamic visit data is fetched: contact mode {string}, time reference {string}, type {string}, epoch {string}', (contactMode, timeReference, visitType, epochName) => {
    getVisitDynamicData(contactMode, timeReference, visitType, epochName)
})

Given('[API] Global Anchor visit within epoch {string} exists', (epochName) => cy.createAnchorVisit(getCurrStudyUid(), epochName))

Given('[API] The visit with following attributes is created: isGlobalAnchor {int}, visitWeek {int}', (isGlobalAnchorVisit, visitWeek) => {
    createVisitViaAPI(isGlobalAnchorVisit, visitWeek)
})

Given('[API] The visit with following attributes is created: isGlobalAnchor {int}, visitWeek {int}, minVisitWindow {int}, maxVisitWindow {int}', (isGlobalAnchorVisit, visitWeek, minVisitWindow, maxVisitWindow) => {
    createVisitViaAPI(isGlobalAnchorVisit, visitWeek, minVisitWindow, maxVisitWindow)
})

Given('[API] All visit groups uids are fetched', () => cy.getVisitGroupsUid(getCurrStudyUid()))

Given('[API] All visit groups are removed', () => cy.deleteAllVisitsGroups(getCurrStudyUid()))

Given('[API] Visits group with format {string} is created', (groupFormat) => cy.createVisitsGroup(getCurrStudyUid(), groupFormat))

Then('The study visit is created', () => {
    cy.wait('@visitRequest').then((request) => expect(request.response.statusCode).to.eq(201))
})

function createEpochViaAPI(epochType, epochSubType) {
    cy.getEpochTypeAndSubType(epochType, epochSubType)
    cy.createEpoch(getCurrStudyUid())
}

function getVisitStaticData() {
    cy.getEpochAllocationUid()
    cy.getDayAndWeekTimeUnitUid()
}

function getVisitDynamicData(contactMode, timeReference, visitType, epochName) {
    cy.getContactModeTermUid(contactMode)
    cy.getTimeReferenceUid(timeReference)
    cy.getVisitTypeUid(visitType)
    cy.getEpochUid(getCurrStudyUid(), epochName)
}

function createVisitViaAPI(isGlobalAnchorVisit, visitWeek, minVisitWindow = 0, maxVisitWindowValue = 0) {
    cy.createVisit(getCurrStudyUid(), isGlobalAnchorVisit, visitWeek, minVisitWindow, maxVisitWindowValue)
}

function deleteVisits(study_uid) {
    const studyVisitsSorted_uid = studyVisits_uid.sort().reverse()
    studyVisitsSorted_uid.forEach(visit_uid => cy.deleteVisitByUid(study_uid, visit_uid))
}