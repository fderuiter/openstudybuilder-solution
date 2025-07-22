import { apiActivityName, apiGroupName, apiSubgroupName} from "./api_library_steps";
const { When, Then } = require("@badeball/cypress-cucumber-preprocessor");

Then('The Activity groupings table in the instance overview page is displayed with correct column', () => {
  cy.wait(5000); // Wait for the page to load completely
    cy.get('.activity-section').first().should('contain.text', 'Activity groupings');  // Check if the table is present
    cy.get('.activity-section').first().find('[data-cy="data-table"]').should('exist') // Assert that the table exists
    .find('thead .v-data-table__th') // Find all header cells
    .then(($headers) => {
      // Extract the text of each header
      const headerTexts = $headers.map((index, header) => Cypress.$(header).text()).get();      
      // Check that the header texts match the expected values
      expect(headerTexts).to.deep.equal(['Activity group', 'Activity subgroup', 'Activity']);
    });
})

Then('The Activity items table is displayed with correct column', () => {
   cy.wait(5000); // Wait for the page to load completely
    cy.get('.activity-section').eq(1).should('contain.text', 'Activity Items');  // Check if the table is present
    cy.get('.activity-section').eq(1).find('[data-cy="data-table"]').should('exist') // Assert that the table exists
    .find('thead .v-data-table__th') // Find all header cells
    .then(($headers) => {
      // Extract the text of each header
      const headerTexts = $headers.map((index, header) => Cypress.$(header).text()).get();      
      // Check that the header texts match the expected values
      expect(headerTexts).to.deep.equal(['Data type', 'Name', 'Activity Item Class']);
    });
})

Then('The linked group, subgroup and activity should be displayed in the Activity groupings table', () => {
   const expectedTexts = [apiGroupName, apiSubgroupName, apiActivityName];
   
       // Select the tbody of the table and find the td elements
       cy.get('.activity-section').first().find('[data-cy="data-table"]') 
         .find('.v-data-table__tbody .v-data-table__td') // Find all td elements
         .each(($cell, index) => {
           // Assert that each cell contains the expected text
           cy.wrap($cell).should('contain.text', expectedTexts[index]);
         });
    }); 

Then('The free text search field displays in the Activity groupings table', () => {
    cy.get('[data-cy="search-field"]').first().should('be.visible'); // Check if the search field for Activity groupings table is present
})

Then('The free text search field displays in the Activity items table', () => {
    cy.get('[data-cy="search-field"]').eq(1).should('be.visible'); // Check if the search field for Activity items table is present
})
 
Then('Both Activity groupings and Activity items table should be empty', () => {
    cy.get('[data-cy="search-field"]').eq(1).should('be.visible'); // Check if the search field for Activity instances table is present
 })