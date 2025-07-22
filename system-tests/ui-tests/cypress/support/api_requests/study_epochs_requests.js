const availableEpochsUrl = '/epochs/allowed-configs'
const studyEpochsUrl = (study_uid) =>  `/studies/${study_uid}/study-epochs`
const studyEpochsPreviewUrl = (study_uid) =>  `/studies/${study_uid}/study-epochs/preview`
let epochType, epochSubType, epochTerm

Cypress.Commands.add('getEpochTypeAndSubType', (epoch_type_name, epoch_subtype_name) => {
    cy.sendGetRequest(availableEpochsUrl).then((response) => {
          epochSubType = response.body
            .find(epoch => epoch.type_name == epoch_type_name && epoch.subtype_name == epoch_subtype_name).subtype
          epochType = response.body
            .find(epoch => epoch.type_name == epoch_type_name && epoch.subtype_name == epoch_subtype_name).type
    })
})

Cypress.Commands.add('getEpochTerm', (study_uid) => {
    cy.sendPostRequest(studyEpochsPreviewUrl(study_uid), epochPreviewBody(study_uid)).then((response) => {
      epochTerm = response.body.epoch
    })
})

Cypress.Commands.add('createEpoch', (study_uid) => {
  cy.sendGetRequest(studyEpochsUrl(study_uid)).then((response) => {
    if (!response.body.items.find(item => item.epoch_subtype_ctterm.term_uid == epochSubType)) {
        cy.sendPostRequest(studyEpochsUrl(study_uid), createEpochBody(study_uid))
    } else {
      cy.log('Epoch already exist')
    }
  })
})

const createEpochBody = (study_uid) => {
  return {
    "epoch_type": epochType,
    "epoch": epochTerm,
    "epoch_subtype": epochSubType,
    "start_rule": "C1",
    "end_rule": "C5",
    "description": `DESC${Date.now()}`,
    "color_hash": "#1B5E20",
    "study_uid": study_uid
  }
}

const epochPreviewBody = (study_uid) => {
  return {
    "study_uid": study_uid,
    "epoch_subtype": epochSubType
  }
}