const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");
const { generateShortUniqueName } = require("../../support/helper_functions");

// Shared state object (exported for use by CRF tree steps)
const state = {
    collectionName: undefined,
    formName: undefined,
    itemGroupName: undefined,
    itemName: undefined,
    collectionUid: undefined,
    formUid: undefined,
    itemGroupUid: undefined,
    itemUid: undefined,
    selectedActivityInstances: [],
    selectedActivityItemClasses: []
}
module.exports = { state }

// ==================== Setup Steps ====================

Given('The test CRF item is created with no Activity Instance Link', () => {
    state.selectedActivityInstances = [];
    state.selectedActivityItemClasses = [];
    createTestItem();
});

When('Created test CRF Item is found', () => cy.searchAndCheckPresence(state.itemName, true))

// ==================== Edit Item Page Steps ====================

Then('The Edit Item page is opened and RESET button is disabled', () => {
    cy.get('.dialog-title').should('contain', 'Edit Item');
    cy.get('[data-cy="reset-activity-instances"]').should('be.disabled');
});

Then('The default page is Form View', () => {
    cy.get('[data-cy="switch-view"]').should('be.visible');
    cy.get('[data-cy="switch-view"]').find('input').should('be.checked');
});

Then('No Activity Instance Links text is visible', () => {
    cy.get('.v-card-text').should('contain', 'No Activity Instance Links');
    cy.get('.v-col').contains('No Activity Instance Links').should('be.visible');
});

Then('Activity Instance Item {int} table is visible', (tableNumber) => {
    cy.get('.v-card-title').contains(`Activity Instance Item ${tableNumber}`).should('be.visible');
});

Then('The Edit Item window is closed', () => {
    cy.get('.dialog-title').should('not.exist');
    cy.get('.v-dialog').should('not.exist');
    cy.get('table').should('be.visible');
});

// ==================== Button Steps ====================

When('I click the Activity Instance Link plus button', () => {
    cy.clickButton('add-activity-instances');
});

When('I click the Delete button', () => {
    cy.clickButton('remove-activity-instance');
});

When('I click the RESET button', () => {
    cy.clickButton('reset-activity-instances');
});

Then('The Delete button is visible', () => {
    cy.get('[data-cy="remove-activity-instance"]').should('be.visible');
});

Then('The RESET button is enabled', () => {
    cy.get('[data-cy="reset-activity-instances"]').should('be.visible').and('not.be.disabled');
});

Then('The RESET button is disabled', () => {
    cy.get('[data-cy="reset-activity-instances"]').should('be.disabled');
});

// ==================== Form View - Switch & Table View ====================

When('I select the Table View option', () => {
    cy.get('[data-cy="switch-view"]').find('input').uncheck({ force: true });
});

Then('The page is switched to Table View', () => {
    cy.get('[data-cy="switch-view"]').should('be.visible');
    cy.get('[data-cy="switch-view"]').find('input').should('not.be.checked');
});

// ==================== Form View - Dropdown Selections ====================

When('I select a value from the Activity Instance dropdown list', () => {
    cy.get('.v-card-title').contains('Activity Instance Item 1').parent('.v-card').within(() => {
        cy.get('[data-cy="activity-instance"]').find('.v-field__input').click();
    });
    cy.get('.v-overlay__content .v-list-item').first().then($item => {
        state.selectedActivityInstances.push($item.text().trim());
        cy.wrap($item).click();
    });
});

When('I select a value from the Activity Item Class dropdown list', () => {
    cy.get('.v-card-title').contains('Activity Instance Item 1').parent('.v-card').within(() => {
        cy.get('[data-cy="activity-item-class"]').find('.v-field__input').click();
    });
    cy.get('.v-overlay__content .v-list-item').first().then($item => {
        state.selectedActivityItemClasses.push($item.text().trim());
        cy.wrap($item).click();
    });
});

When('I select a value from the second Activity Instance dropdown list', () => {
    cy.get('.v-card-title').contains('Activity Instance Item 2').parent('.v-card').within(() => {
        cy.get('[data-cy="activity-instance"]').find('.v-field__input').click();
    });
    cy.get('.v-overlay__content .v-list-item', { timeout: 10000 }).should('have.length.greaterThan', 0);
    cy.get('.v-overlay__content .v-list-item').last().click();
    cy.get('.v-card-title').contains('Activity Instance Item 2').parent('.v-card').within(() => {
        cy.get('[data-cy="activity-instance"]').find('.v-autocomplete__selection-text').invoke('text').then(text => {
            state.selectedActivityInstances.push(text.trim());
        });
    });
});

When('I select a value from the second Activity Item Class dropdown list', () => {
    cy.get('.v-card-title').contains('Activity Instance Item 2').parent('.v-card').within(() => {
        cy.get('[data-cy="activity-item-class"]').find('.v-field__input').click();
    });
    cy.get('.v-overlay__content .v-list-item').last().then($item => {
        state.selectedActivityItemClasses.push($item.text().trim());
        cy.wrap($item).click();
    });
});

When('User waits for Activity Instance dropdown to load', () => {
    cy.get('.v-card-title').contains('Activity Instance Item 1').parent('.v-card').within(() => {
        cy.get('[data-cy="activity-instance"]').find('.v-field__input').click();
    });
    cy.get('.v-list-item').should('have.length.greaterThan', 0);
    cy.get('body').click();
});

When('User waits for Activity Item Class dropdown to load', () => {
    cy.get('.v-card-title').contains('Activity Instance Item 1').parent('.v-card').within(() => {
        cy.get('[data-cy="activity-item-class"]').find('.v-field__input').click();
    });
    cy.get('.v-list-item').should('have.length.greaterThan', 0);
    cy.get('body').click();
});

// ==================== Table View - Dropdown & Table Selections ====================

When('I select a value from the Select an Activity Instance dropdown list', () => {
    cy.selectFirstVSelect('select-activity-instance');
    cy.get('[data-cy="select-activity-instance"]').find('.v-autocomplete__selection-text').then($el => {
        state.selectedActivityInstances.push($el.text().trim());
    });
});

When('I select an Activity Item Class from the table', () => {
    cy.get('.v-data-table__td--select-row', { timeout: 10000 }).first()
        .find('input[type="checkbox"]').check({ force: true });
});

// ==================== CRF Viewer - Form Selection ====================

When('I select created Form from the Form Name dropdown list', () => {
    expect(state.formName, 'Form name should be defined from test setup').to.not.be.undefined;
    expect(state.formName, 'Form name should not be empty').to.not.be.empty;
    cy.get('.v-label').contains('Form Name').parent().parent().find('.v-field__input').click();
    cy.get('.v-overlay__content .v-list', { timeout: 10000 }).should('be.visible');
    cy.get('.v-overlay__content .v-list-item').contains(state.formName).scrollIntoView().click();
});

When('User waits for CRF Viewer data to load', () => {
    cy.intercept('/api/odms/metadata/report?*').as('getCrfViewerData');
    cy.wait('@getCrfViewerData', { timeout: 60000 });
});

// ==================== CRF Viewer - Verification ====================

When('I click the Activity Instance option from the right top corner', () => {
    cy.get('iframe.frame').its('0.contentDocument.body').should('not.be.empty')
        .then(cy.wrap)
        .find('button')
        .contains('Activity Instance')
        .click();
});

Then('The added Activity Instance Link is displayed under the test item name', () => {
    cy.get('iframe.frame').its('0.contentDocument.body').should('not.be.empty')
        .then(cy.wrap)
        .then($body => {
            cy.wrap($body).contains('h4', state.itemName).should('exist');
            cy.wrap($body).contains('tr', state.itemName).within(() => {
                cy.get('.activity-instance-container').should('be.visible');
                cy.get('.activity-instance-container').should('contain', state.selectedActivityInstances[state.selectedActivityInstances.length - 1]);
            });
        });
});

Then('All added Activity Instance Links are displayed under the test item name', () => {
    cy.get('iframe.frame').its('0.contentDocument.body').should('not.be.empty')
        .then(cy.wrap)
        .then($body => {
            cy.wrap($body).contains('h4', state.itemName).should('exist');
            cy.wrap($body).contains('tr', state.itemName).within(() => {
                cy.get('.activity-instance-container').should('have.length.at.least', 2);
                state.selectedActivityInstances.forEach((instance) => {
                    cy.get('.activity-instance-container').should('contain', instance);
                });
            });
        });
});

// ==================== Validation Steps ====================

Then('I should see alert messages for both Activity Instance and Activity Item Class fields', () => {
    cy.get('.v-alert.bg-error').should('contain', 'Activity Instance UID of Activity Instances #1 must be at least 1 character(s)');
    cy.get('.v-alert.bg-error').should('contain', 'Activity Item Class UID of Activity Instances #1 must be at least 1 character(s)');
});

When('I select a value from the Activity Instance dropdown list and do not select any value from the Activity Item Class dropdown list', () => {
    cy.get('.v-card-title').contains('Activity Instance Item 1').parent('.v-card').within(() => {
        cy.get('[data-cy="activity-instance"]').find('.v-field__input').click();
    });
    cy.get('.v-overlay__content .v-list-item').first().then($item => {
        state.selectedActivityInstances.push($item.text().trim());
        cy.wrap($item).click();
    });
    cy.get('.v-card-title').contains('Activity Instance Item 1').parent('.v-card').within(() => {
        cy.get('[data-cy="activity-item-class"]').find('.v-field__input').click();
    });
    cy.get('body').click();
});

Then('I should see a field validation message for the Activity Item Class dropdown list', () => {
    cy.checkIfValidationAppears('activity-item-class');
});

Then('I should see an alert message for the Activity Item Class field', () => {
    cy.get('.v-alert.bg-error').should('contain', 'Activity Item Class UID of Activity Instances #1 must be at least 1 character(s)');
});

Then('I am not able to select a value from the Activity Item Class dropdown list before I have selected a value from the Activity Instance dropdown list', () => {
    cy.get('[data-cy="activity-item-class"]').should('have.class', 'v-input--readonly');
});

// ==================== Delete & Reset Steps ====================

Then('The page returns to the initial edit item page without Activity Instance Item table', () => {
    cy.get('.v-card-title').contains('Activity Instance Item 1').should('not.exist');
    cy.get('.v-col').contains('No Activity Instance Links').should('be.visible');
});

Then('The Edit Item page is opened with saved linked Activity Instance Item table', () => {
    cy.get('.dialog-title').should('contain', 'Edit Item');
    cy.get('.v-card-title').contains('Activity Instance Item 1').should('be.visible');
    cy.get('.v-card-title').contains('Activity Instance Item 1').parent('.v-card').within(() => {
        cy.get('[data-cy="activity-instance"]').find('.v-field__input').should('not.be.empty');
    });
});

Then('The page returns to the initial edit item page and the RESET button is enabled', () => {
    cy.get('.v-card-title').contains('Activity Instance Item 1').should('not.exist');
    cy.get('.v-col').contains('No Activity Instance Links').should('be.visible');
    cy.get('[data-cy="reset-activity-instances"]').should('be.visible').and('not.be.disabled');
});

Then('The Edit Item page is opened without any linked Activity Instance Item table', () => {
    cy.get('.dialog-title').should('contain', 'Edit Item');
    cy.get('.v-card-title').contains('Activity Instance Item 1').should('not.exist');
    cy.get('.v-col').contains('No Activity Instance Links').should('be.visible');
    cy.get('[data-cy="reset-activity-instances"]').should('be.disabled');
});

Then('The Activity Instance Item table is removed and the page returns to the initial edit item page', () => {
    cy.get('.v-card-title').contains('Activity Instance Item 1').should('not.exist');
    cy.get('.v-col').contains('No Activity Instance Links').should('be.visible');
    cy.get('[data-cy="reset-activity-instances"]').should('be.disabled');
});

// ==================== Helper Functions ====================

function createTestItem() {
    state.collectionName = generateShortUniqueName('C_');
    cy.createCrfCollection(state.collectionName).then(collectionResponse => state.collectionUid = collectionResponse.body.uid)
    state.formName = generateShortUniqueName('F_');
    cy.createCrfForm(state.formName).then(formResponse => state.formUid = formResponse.body.uid)
    state.itemGroupName = generateShortUniqueName('IG_');
    cy.createCrfItemGroup(state.itemGroupName).then(itemGroupResponse => state.itemGroupUid = itemGroupResponse.body.uid)
    state.itemName = generateShortUniqueName('I_');
    cy.createCrfItem(state.itemName).then(itemResponse => state.itemUid = itemResponse.body.uid)
    cy.then(() => cy.linkFormToCollection(state.formUid, state.collectionUid))
    cy.then(() => cy.linkItemGroupToForm(state.formUid, state.itemGroupUid))
    cy.then(() => cy.linkItemToItemGroup(state.itemGroupUid, state.itemUid))
}
