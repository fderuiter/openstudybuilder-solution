const { Given, When, Then } = require('@badeball/cypress-cucumber-preprocessor')
import { getCurrentDateFormatted } from '../../support/helper_functions'


const release_description = 'Test release description'
const lock_description = 'Test lock description'
let new_version
let locked_date
let released_date

let currentStudyNumber

When('The study is released with description provided', () => {
  released_date = getCurrentDateFormatted()
  cy.getCellValue(0, 'Version').then((current_version) => {
    new_version = current_version == NaN ? 0 : parseFloat(current_version)
  })
  cy.clickButton('release-study')
  cy.fillInput('release-description', release_description)
})

When('The study is locked with description provided', () => {
  locked_date = getCurrentDateFormatted()
  cy.getCellValue(0, 'Version').then((current_version) => {
    new_version = current_version == NaN ? 0 : parseFloat(current_version)
  })
  cy.clickButton('lock-study')
  cy.fillInput('release-description', lock_description)
})

When('The study is unlocked', () => {
  cy.clickButton('unlock-study')
  released_date = getCurrentDateFormatted()
})

Then('A the first row is showing Draft without Version and description, with the current timestamp', () => {
  cy.checkRowByIndex(0, 'Study status', 'Draft')
  cy.checkRowByIndex(0, 'Version', '')
  cy.checkRowByIndex(0, 'Release description', '')
  cy.checkRowByIndex(0, 'Modified', released_date)
})

Then('A row for the Released Study Status is displayed with a current time stamp and Release description and version incremented by 0.1', () => {
  cy.checkRowByIndex(1, 'Study status', 'Released')
  cy.checkRowByIndex(1, 'Version', (new_version + 0.1).toFixed(1))
  cy.checkRowByIndex(1, 'Release description', release_description)
  cy.checkRowByIndex(1, 'Modified', released_date)
})

Then('A row for the Locked Study Status is displayed with a current time stamp and Lock description and version rounded up to full number', () => {
  cy.checkRowByIndex(0, 'Study status', 'Locked')
  cy.checkRowByIndex(0, 'Version', Math.ceil(new_version))
  cy.checkRowByIndex(0, 'Release description', lock_description)
  cy.checkRowByIndex(0, 'Modified', locked_date)
})

Then('A row for the Released Study Status is displayed with a current time stamp and Lock description and version rounded up to full number', () => {
  cy.checkRowByIndex(1, 'Study status', 'Released')
  cy.checkRowByIndex(1, 'Version', Math.ceil(new_version))
  cy.checkRowByIndex(1, 'Release description', lock_description)
  cy.checkRowByIndex(1, 'Modified', locked_date)
})

Given('A test study {string} in draft status with defined title exists', (study_number) => {
  currentStudyNumber = study_number
  cy.createTestStudy(study_number, `lock/release testing ${Date.now()}`)
  cy.getStudyUid(study_number).then(uid => {
    cy.setStudyTitle(uid, 'test title', 'test short title')
    cy.visit(`studies/${uid}/study_status/study_status`)
  })
})

Given('A test study {string} locked for {string} in major version {string} and minor version {string} exists', (study_number, reason, major_version, minor_version) => {
  currentStudyNumber = study_number
  cy.createTestStudy(study_number, `unlock testing ${Date.now()}`)
  cy.getStudyUid(study_number).then(uid => {
    cy.setStudyTitle(uid, 'test title', 'test short title')
    cy.lockStudy(study_number, reason, major_version, minor_version)
    cy.visit(`studies/${uid}/study_status/study_status`)
  })
})

When('The user locks the study for {string} reason', (reason) => {
  cy.intercept('**/locks').as('lockRequest')
  cy.clickButton('lock-study')
  cy.selectVSelect('change-reason', reason)
})

When('The user unlocks the study for {string} reason', (reason) => {
  cy.intercept('**/unlocks').as('unlockRequest')
  cy.clickButton('unlock-study')
  cy.selectVSelect('change-reason', reason)
})

When("The user provides protocol major version {string}", (major_version) => {
  cy.get('[data-cy="major-version"]').clear().type(major_version)

})

When("The user provides protocol minor version {string}", (minor_version) => {
  cy.get('[data-cy="minor-version"]').clear().type(minor_version)

})

When("The user provides explanation for other reason", () => {
  cy.fillTextBox('lock-release-other-reason', 'Test reason')
})

Then('The study is locked with {string} as a reason with major protocol version {string} and minor version {string}', (reason, major_version, minor_version) => {
  cy.wait('@lockRequest').then(() => {
    cy.checkRowByIndex(0, 'Reason for locking or releasing study', reason)
    cy.checkRowByIndex(0, 'Protocol Version', `${major_version}.${minor_version}`)
  })
})

Then('The study is unlocked with {string} as a reason', (reason) => {
  cy.wait('@unlockRequest').then(() => {
    cy.checkRowByIndex(0, 'Reason for unlocking study', reason)
  })
})