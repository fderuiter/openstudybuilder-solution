const { When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let current_epoch
let current_epoch_uid
let globalAnchor_term_uid

When('[API] Global anchor term uid is fetched', () => cy.getGlobalAnchorUid().then(uid => globalAnchor_term_uid = uid))

When('Epochs for study {string} data is loaded', (study_uid) => {
    cy.intercept(`/api/studies/${study_uid}/study-epochs?page_size=0`).as('getEpochs')
    cy.wait('@getEpochs').its('response.statusCode').should('eq', 200)
})

When('The study {string} has defined epoch', (study_uid) => {
    cy.sendGetRequest(`studies/${study_uid}/study-epochs?page_number=1&page_size=5&total_count=true&study_uid=${study_uid}`).then((response) => {
        if (response.body.total == 0) {
            cy.request({
                method: 'POST',
                url: Cypress.env('API') + '/studies/' + study_uid + '/study-epochs',
                body: { 
                  epoch_type: 'C101526_TREATMENT', 
                  epoch: 'CTTerm_001177', 
                  epoch_subtype: 'C101526_TREATMENT', 
                  start_rule: 'D1', 
                  end_rule: 'D2', 
                  description: `DESC${Date.now()}`,
                  color_hash: '#FF0000FF', 
                  study_uid: study_uid 
                }
            }).then((response) => {
                current_epoch = response.body.epoch_name
                current_epoch_uid = response.body.uid
            })
        } else {
            current_epoch = response.body.items[0].epoch_name
            current_epoch_uid = response.body.items[0].uid

        }
    })
    cy.wait(3000)
})

When('The study {string} has defined visit in that epoch', (study_uid) => {
    cy.sendGetRequest(`studies/${study_uid}/study-visits?page_number=1&page_size=5&total_count=true`).then((response) => {
        if (response.body.total == 0) {
            cy.request('POST', `${Cypress.env('API')}/studies/${study_uid}/study-visits`, {
                is_global_anchor_visit: true,
                study_day_label: "Day 1",
                study_week_label: "Week 1",
                visit_class: "SINGLE_VISIT",
                show_visit: true,
                min_visit_window_value: 0,
                max_visit_window_value: 0,
                visit_subclass:"SINGLE_VISIT",
                visit_window_unit_uid: "UnitDefinition_000364",
                study_epoch_uid: current_epoch_uid,
                epoch_allocation_uid: "CTTerm_000196",
                visit_type_uid: "CTTerm_000182",
                visit_contact_mode_uid: "CTTerm_000080",
                time_value: 0,
                time_reference_uid: globalAnchor_term_uid,
                is_soa_milestone: false,
                time_unit_uid: "UnitDefinition_000364",
            }).then((created_response) => {
                current_epoch = created_response.body.study_epoch.sponsor_preferred_name
                cy.log(`Test visit created within epoch ${current_epoch}`)
            })
        }
    })
})

When('The special visit is created within the same epoch', () => {
    cy.waitForTable()
    cy.clickButton('add-visit')
    cy.contains('.v-radio', 'Special visit').within(() => {
        cy.get('input').click()
    })
    cy.clickFormActionButton('continue')
    cy.selectVSelect('study-period', current_epoch)
    cy.clickFormActionButton('continue')
    cy.get('[data-cy="visit-type"]').click()
    cy.contains('.v-list-item', 'Treatment').first().click()
    cy.get('[data-cy="contact-mode"]').click()
    cy.contains('.v-list-item', 'On Site Visit').first().click()
    cy.get('[data-cy="time-reference"]').click()
    cy.get('.v-overlay__content > .v-list > .v-list-item').first().click()
    cy.intercept('**study-visits').as('createdVisit')
    cy.clickFormActionButton('save')
    cy.waitForTable()
})

When('The discontinuation special visit is created within the same epoch', () => {
    cy.waitForTable()
    cy.clickButton('add-visit')
    cy.contains('.v-radio', 'Special visit').within(() => {
        cy.get('input').click()
    })
    cy.clickFormActionButton('continue')
    cy.selectVSelect('study-period', current_epoch)
    cy.clickFormActionButton('continue')
    cy.get('[data-cy="visit-type"]').click()
    cy.contains('.v-list-item', 'Early discontinuation').first().click()
    cy.get('[data-cy="contact-mode"]').click()
    cy.contains('.v-list-item', 'On Site Visit').first().click()
    cy.get('[data-cy="time-reference"]').click()
    cy.get('.v-overlay__content > .v-list > .v-list-item').first().click()
    cy.intercept('**study-visits').as('createdVisit')
    cy.clickFormActionButton('save')
    cy.waitForTable()
})



Then('The special visit is added without timing and with name defined as {string}', (visit_name) => {
    cy.wait('@createdVisit').then((request) => {
        expect(request.response.body.visit_short_name).to.eq(visit_name)
        expect(request.response.body.visit_class).to.eq('SPECIAL_VISIT')

    })
})

When('The user edits the special visit and saves', () => {
    cy.contains('.v-data-table__tr', 'Special visit').within(() =>{
        cy.clickButton('table-item-action-button')
    })
    cy.clickButton('Edit')
    cy.clickFormActionButton('continue')
    cy.wait(300)
    cy.clickFormActionButton('continue')
    cy.fillInput('visit-description', 'Testing edit functionality')
    cy.clickFormActionButton('save')
})

Then('The special visit is updated correctly', () => {
        cy.tableContains('Testing edit functionality')
})