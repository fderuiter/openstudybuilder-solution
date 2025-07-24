import { apiGroupName, apiSubgroupName } from "./api_library_steps";
const { When, Then } = require("@badeball/cypress-cucumber-preprocessor");

const clickOnLinkInTable = (name) => cy.get('table tbody tr td').contains(name).click()
const verifyThatValuesPresent = (values) => values.forEach(value => cy.get('.v-table__wrapper').contains(value))
let subgroup2Name

When('I click on the test activity group name in the activity group page', () => {

cy.searchAndCheckPresence(apiGroupName, true)
cy.get('table tbody tr td').contains(apiGroupName).click()

})
 
Then('The Activity subgroups table will be displayed with correct column', () => {
     // Check if the table is present
     cy.get('.group-overview-container').should('contain.text', 'Activity subgroups');

     // Assert that the table exists using the subgroups-table class
     cy.get('.subgroups-table').first().get('[data-cy="data-table"]').first().within(() => {
           cy.get('.v-data-table__thead .v-data-table__td').then(($headers) => {
               // Extract the text of each header
               const headerTexts = $headers.map((index, header) => Cypress.$(header).text().trim()).get();
               // Check that the header texts match the expected values
               expect(headerTexts).to.deep.equal(['Name', 'Definition', 'Version', 'Status']);
           });
       });
})

Then('The linked subgroup should be displayed in the Activity subgroups table', () => {
    cy.get('.group-overview-container').should('contain.text', 'Activity subgroups');
    // Assert that the table exists using the subgroups-table class
    cy.get('.subgroups-table').first().get('[data-cy="data-table"] tbody tr').first().within(() => {      
        cy.get('.v-data-table__td').then(($headers) => {
              // Extract the text of each header
              const headerTexts = $headers.map((index, header) => Cypress.$(header).text().trim()).get();
                cy.wrap($headers[0]).should('contain.text', apiSubgroupName); // First Column Check 
                cy.wrap($headers[2]).should('contain.text', '1.0'); // Version Check
                cy.wrap($headers[3]).should('contain.text', 'Final'); // Status Check
          });
      });
    });

When('I make changes to the group, enter a reason for change and save it', () => {
    cy.fillInput('groupform-activity-group-field', `Update ${apiGroupName}`)
    cy.fillInput('groupform-change-description-field', "Test purpose")
})

Then('The page of the group with {string} status and version {string} should be opened', (status, version) => {
    cy.get('.version-select .v-select__selection-text').should('have.text', version)
    cy.contains('.summary-label', 'Status').siblings('.summary-value').should('have.text', status)
})

Then('The free text search field should be displayed in the Activity subgroups table', () => {
        cy.get('[data-cy="search-field"]').first().should('be.visible'); // Check if the search field for Activity groupings table is present
    })
 
Then('The Activity subgroups table should be empty', () => {
    cy.get('.group-overview-container').should('contain.text', 'Activity subgroups');
    // Assert that the table exists using the subgroups-table class
    cy.get('.subgroups-table').first()
    .should('exist') // Confirm the table is present
    .within(() => {
        // Check for the "No subgroups available." message
        cy.get('tbody .v-data-table-rows-no-data')
          .should('exist') // Ensure the no-data row is present
          .find('span') // Locate the span containing the message
          .should('have.text', 'No subgroups available.'); // Check the text content
        });
    });

When('I click on new version button', () => {
        cy.get('button[title="New version"]').click();
    }) 

Then('The page of the group with final status and version 2.0 should be opened', () => {
        cy.contains('.activity-section .section-header', 'Activity instances').parentsUntil('.activity-section').within(section => {
        cy.wrap(section).get('table tbody tr td').should('have.text', 'No subgroups available.')
    })
    })
      
When('I click on approve button', () => {
        cy.get('button[title="Approve"]').click();
    }) 

When('I create a new subgroup2 and linked to the test group', () => { 
    cy.clickButton('add-activity')
    subgroup2Name = `Sg${Date.now()}`
    cy.get('[data-cy="groupform-activity-group-dropdown"] input').type(apiGroupName)
    cy.selectFirstVSelect('groupform-activity-group-dropdown')
    cy.fillInput('groupform-activity-group-field', subgroup2Name)
    cy.fillInput('groupform-abbreviation-field', 'abbsg2')
    cy.fillInput('groupform-definition-field', 'defsg2') 
    }) 

When('I approve the subgroup2', () => {
        cy.searchAndCheckPresence(subgroup2Name, true)
        cy.performActionOnSearchedItem('Approve')
    }) 

Then('The linked subgroup2 should be displayed in the Activity subgroups table', () => {
    cy.get('.group-overview-container').should('contain.text', 'Activity subgroups');
    // Assert that the table exists using the subgroups-table class
    cy.get('.subgroups-table').first().get('[data-cy="data-table"] tbody tr').first().within(() => {      
        cy.get('.v-data-table__td').then(($headers) => {
              // Extract the text of each header
              const headerTexts = $headers.map((index, header) => Cypress.$(header).text().trim()).get();
                cy.wrap($headers[0]).should('contain.text', subgroup2Name); // First Column Check 
                cy.wrap($headers[2]).should('contain.text', '1.0'); // Version Check
                cy.wrap($headers[3]).should('contain.text', 'Final'); // Status Check
          });
      });
    });

Then('The original test subgroup should Not be displayed in the Activity subgroups table', () => {
    cy.get('.group-overview-container').should('contain.text', 'Activity subgroups');
    // Assert that the table exists using the subgroups-table class
    cy.get('.subgroups-table').first().get('[data-cy="data-table"] tbody tr').first().within(() => {      
        cy.get('.v-data-table__td').then(($headers) => {
              // Extract the text of each header
              const headerTexts = $headers.map((index, header) => Cypress.$(header).text().trim()).get();
                cy.wrap($headers[0]).should('not.contain.text', apiSubgroupName); // First Column Check 
          });
      });
    });   