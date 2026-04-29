const { When, Then } = require("@badeball/cypress-cucumber-preprocessor");
const { state } = require("./library_crf_item_activity_instance_links_steps");

// ==================== CRF Tree Navigation Steps ====================

When('I click the expand button beside created test Collection to expand the CRF Tree', () => {
    cy.contains('td', state.collectionName).parent('tr').find('button').first().click();
});

When('I click the expand button beside created test Form form to expand the form', () => {
    cy.contains('td', state.formName).should('be.visible');
    cy.contains('td', state.formName).parent('tr').find('button').first().click();
});

When('I click the expand button beside created test Item Group to expand the item group', () => {
    cy.contains('td', state.itemGroupName).should('be.visible');
    cy.contains('td', state.itemGroupName).parent('tr').find('button').first().click();
});

Then('I can see the Created test CRF Item in the list', () => {
    cy.contains('span', state.itemName).should('be.visible');
});

When('The \'Manage Activity Instance Links\' option is clicked from the three dot menu list of the created test CRF item', () => {
    cy.get('.text-crfItem').parent('span').contains(state.itemName).closest('.v-row')
        .find('[data-cy="table-item-action-button"]').click({ force: true });
    cy.get('[data-cy="Manage Activity Instances"]', { timeout: 10000 }).click({ force: true });
});

// ==================== CRF Tree - Edit Item Page Steps ====================

Then('The Edit Item page is opened', () => {
    cy.get('.dialog-title').should('contain', 'Edit Item');
});

Then('The default page is Table View', () => {
    cy.get('[data-cy="switch-view"]').should('be.visible');
    cy.get('[data-cy="switch-view"]').find('input').should('not.be.checked');
});

// ==================== CRF Tree - Table View Steps ====================

When('I select another value from the Select an Activity Instance dropdown list', () => {
    cy.selectLastVSelect('select-activity-instance');
    cy.get('[data-cy="select-activity-instance"]').find('.v-autocomplete__selection-text').then($el => {
        state.selectedActivityInstances.push($el.text().trim());
    });
});

When('I select a value from the Activity Item Class table', () => {
    cy.get('.v-data-table__td--select-row', { timeout: 10000 }).first()
        .find('input[type="checkbox"]').check({ force: true });
});

// ==================== CRF Tree - Form View Switch ====================

When('I select the Form View option', () => {
    cy.get('[data-cy="switch-view"]').find('input').check({ force: true });
});

Then('The page is switched to Form View', () => {
    cy.get('[data-cy="switch-view"]').should('be.visible');
    cy.get('[data-cy="switch-view"]').find('input').should('be.checked');
});

When('I do not select a value from the Activity Item Class dropdown list', () => {
    // No action needed - verifying empty state
});

Then('I can see no linked Activity Item Class in the Form View', () => {
    cy.get('.v-card-title').contains('Activity Instance Item 1').parent('.v-card').within(() => {
        cy.get('[data-cy="activity-item-class"]').find('.v-field__input').should('have.value', '');
    });
});

// ==================== CRF Tree - Verification ====================

Then('The added two Activity Instance Links are displayed under the test item name', () => {
    cy.get('iframe.frame').its('0.contentDocument.body').should('not.be.empty')
        .then(cy.wrap)
        .then($body => {
            cy.wrap($body).contains('h4', state.itemName).should('exist');
            cy.wrap($body).contains('tr', state.itemName).within(() => {
                cy.get('.activity-instance-container').should('have.length.at.least', 2);
            });
        });
});

// ==================== CRF Tree - Validation Steps ====================

Then('The Edit Item window remains open', () => {
    cy.get('.dialog-title').should('contain', 'Edit Item');
});

When('I switch to the Form View', () => {
    cy.get('[data-cy="switch-view"]').find('input').check({ force: true });
});
