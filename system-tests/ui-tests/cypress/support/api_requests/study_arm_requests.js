import { generateShortUniqueName } from "../helper_functions"
const { getShortUniqueId } = require("../../support/helper_functions");

export let arm_uid
let arm_type_uid, study_arms_uids
const ctTermArmTypeUrl = '/ct/codelists/terms?page_size=100&codelist_submission_value=ARMTTP'
const createArmUrl = (studyUid) => `/studies/${studyUid}/study-arms/batch`
const studyArmsUrl = (studyUid) => `/studies/${studyUid}/study-arms?page_number=1&page_size=0&total_count=true&study_uid=${studyUid}`
const studyArmUrl = (studyUid, armUid) => `/studies/${studyUid}/study-arms/${armUid}`

Cypress.Commands.add('createTestArmIfNoneExists', (study_uid) => {
    cy.request('GET', Cypress.env('API') + '/studies/' + study_uid + '/study-arms?page_number=1&page_size=10&total_count=true&study_uid=' + study_uid).then((response) => {
        if (response.body.total == 0) {
            cy.sendPostRequest(createArmUrl(study_uid), createArmBody(arm_type_uid)).then(response => {
                arm_uid = response.body[response.body.length - 1].content.arm_uid
            })
        }
    })
})

Cypress.Commands.add('createTestArm', (study_uid, customName = '') => {
    if (customName != '') {
        cy.sendGetRequest(studyArmsUrl(study_uid)).then((response) => {
            const existing = response.body.items.find((item) => item.name === customName)
            if (existing) {
                arm_uid = existing.arm_uid ?? existing.uid
                return
            }
            cy.sendPostRequest(createArmUrl(study_uid), createArmBody(arm_type_uid, customName)).then((response) => {
                arm_uid = response.body[0].content.arm_uid
            })
        })
        return
    }
    cy.sendPostRequest(createArmUrl(study_uid), createArmBody(arm_type_uid, customName)).then((response) => {
        arm_uid = response.body[0].content.arm_uid
    })
})

Cypress.Commands.add('getArmTypeUid', (armType_name) => {
    cy.sendGetRequest(ctTermArmTypeUrl).then((response) => {
      arm_type_uid = response.body.items.find(item => item.sponsor_preferred_name == armType_name).term_uid
  })
})

Cypress.Commands.add('getArmsUids', (studyUid) => {
    study_arms_uids = []
    cy.sendGetRequest(studyArmsUrl(studyUid)).then(response => response.body.items.forEach(item => study_arms_uids.push(item.arm_uid)))
})

Cypress.Commands.add('deleteArms', (studyUid) => study_arms_uids.forEach(armUid => cy.sendDeleteRequest(studyArmUrl(studyUid, armUid))))

const createArmBody = (armTypeUid, customName = '') => {
    let armName = customName === '' ? `${generateShortUniqueName('Arm')}` : customName
    return [
        {
            "method": "POST",
            "content": {
                arm_type_uid: armTypeUid,
                code: `Code${getShortUniqueId()}`,
                description: 'TestArm',
                name: armName,
                short_name: armName,
                number_of_subjects: '100',
                randomization_group: `Random${getShortUniqueId()}`
            }
        }
    ]
}