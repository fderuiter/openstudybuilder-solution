import { apiActivityName, apiGroupName, apiSubgroupName, apiInstanceName } from "./api_library_steps";
const { When, Then } = require("@badeball/cypress-cucumber-preprocessor");
 
Then('The Activity groupings table will be displayed with correct column', () => {
    cy.get('.v-row.activity-section').first().should('contain.text', 'Activity groupings');  // Check if the table is present
    cy.get('.v-row.activity-section').first().find('[data-cy="data-table"]').should('exist') // Assert that the table exists
    .find('thead .v-data-table__th') // Find all header cells
    .then(($headers) => {
      // Extract the text of each header
      const headerTexts = $headers.map((index, header) => Cypress.$(header).text()).get();      
      // Check that the header texts match the expected values
      expect(headerTexts).to.deep.equal(['Activity group', 'Activity subgroup', 'Activity instances']);
    });
})

Then('The Activity instances table will be displayed with correct column', () => {
    cy.get('.v-row.activity-section').eq(1).should('contain.text', 'Activity instances');  // Check if the table is present
    cy.get('.v-row.activity-section').eq(1).find('[data-cy="data-table"]').should('exist') // Assert that the table exists
    .find('thead .v-data-table__th') // Find all header cells
    .then(($headers) => {
      // Extract the text of each header
      const headerTexts = $headers.map((index, header) => Cypress.$(header).text()).get();      
      // Check that the header texts match the expected values
      expect(headerTexts).to.deep.equal(['Name', 'Version', 'Status', 'Activity Instance class', 'Topic code', 'Adam parameter code']);
    });
})

Then('The linked group, subgroup and instance should be displayed in the Activity groupings table', () => {
    const expectedTexts = [apiGroupName, apiSubgroupName, apiInstanceName];

    // Select the tbody of the table and find the td elements
    cy.get('.v-row.activity-section').first().find('[data-cy="data-table"]') 
      .find('.v-data-table__tbody .v-data-table__td') // Find all td elements
      .each(($cell, index) => {
        // Assert that each cell contains the expected text
        cy.wrap($cell).should('contain.text', expectedTexts[index]);
      });
})

Then('The free text search field should be displayed in the Activity groupings table', () => {
    cy.get('[data-cy="search-field"]').first().should('be.visible'); // Check if the search field for Activity groupings table is present
})

Then('The free text search field should be displayed in the Activity instances table', () => {
    cy.get('[data-cy="search-field"]').eq(1).should('be.visible'); // Check if the search field for Activity instances table is present
})

Then('The linked instance should be displayed in the Activity instances table', () => {
    cy.get('.v-row.activity-section').eq(1).find('[data-cy="data-table"]') 
    .get('tbody.v-data-table__tbody')
    .find('a.text-truncate')
    .should('contain.text', apiInstanceName);
})   

When('I click on the arrow beside the linked instance name in the Activitiy instance table', () => {
    cy.get('.v-row.activity-section').eq(1).find('[data-cy="data-table"]') 
    .get('tbody.v-data-table__tbody').find('button.v-btn').first() 
    .click(); // Click on the arrow beside the linked instance name
}) 

Then('The instance can be expanded to show the different versions of the instance', () => {
    cy.get('.v-row.activity-section').eq(1).find('[data-cy="data-table"]') 
    .get('tbody.v-data-table__tbody .child-row')
    .should('contain.text', 'Draft');
})   

Then('The correct End date should be displayed', () => {
    cy.get('tr') // Start by selecting the relevant row
          .find('div.summary-label:contains("Start date")') // Find the Start date label
          .siblings('div.summary-value') // Get the corresponding value
          .invoke('text') // Get the text value
          .then((startDate) => {
              // Trim the startDate text for accurate comparison
              const trimmedStartDate = startDate.trim();

              // Get the text for End date
              cy.get('tr') // Again, start by selecting the relevant row
                .find('div.summary-label:contains("End date")') // Find the End date label
                .siblings('div.summary-value') // Get the corresponding value
                .invoke('text') // Get the text value
                .then((endDate) => {
                    // Trim the endDate text for accurate comparison
                    const trimmedEndDate = endDate.trim();                 
                    // Assert that the Start date equals End date
                    expect(trimmedStartDate).to.equal(trimmedEndDate);
                });
          });
    }) 
    
Then('The status should be displayed as {string}', (status) => {
    cy.get('tr') // Start by selecting the relevant row
          .find('div.summary-label:contains("Status")') // Find the Status label
          .siblings('div.summary-value') // Get the corresponding value
          .invoke('text') // Get the text value
          .then((status1) => {
              // Trim the status text for accurate comparison
              const trimmedStatus = status1.trim();
              // Assert that the status is "Draft"
              expect(trimmedStatus).to.equal(status);
          });
    });
 
Then('The instance in both Activity groupings and Activity instances table should be empty', () => {
   //Check table Activity groupings
    const expectedTexts = [apiGroupName, apiSubgroupName]; // Only the first two expected values for checking

    // Select the tbody of the table and find the td elements
    cy.get('.v-row.activity-section').first().find('[data-cy="data-table"]') 
    .find('.v-data-table__tbody .v-data-table__td') // Find all td elements
    .then($cells => {
    // Ensure there are exactly 3 cells to check against
    expect($cells).to.have.length(3, 'There should be exactly 3 columns');

    // Assert that the first cell contains expected first value
    cy.wrap($cells[0]).should('contain.text', expectedTexts[0]); // First Column Check

    // Assert that the second cell contains expected second value
    cy.wrap($cells[1]).should('contain.text', expectedTexts[1]); // Second Column Check

    // Assert that the third cell does not contain any text
    cy.wrap($cells[2]).should('contain.text', 'No activity instances available'); // Third Column Check
        });

    //Check table Activity instances
    cy.get('.v-row.activity-section').eq(1)
    .find('[data-cy="data-table"]')
    .find('tbody.v-data-table__tbody') // Find the tbody of the data table
    .should('exist') // Ensure that the tbody exists
    .find('tr.v-data-table-rows-no-data') // Find the row with 'no data' class
    .should('exist') // Ensure that this row exists in the table
    .and('contain.text', 'No activity instances found for this activity'); 
 })

When('I select the version {string} from the Version dropdown list', (version) => {
    // Click to open the version selection dropdown
    cy.get('.version-select .v-input__control').click();
        
    // Find and select the value
    cy.get('.v-list-item').contains(version).click();
    
    // Verify that the correct value is selected
    cy.get('.v-select__selection-text').should('contain', version);
})

Then('The instance in the Activity Instances table should be displayed in two lines: version 1.0 and 0.1', () => {
    // Ensure that the data in the table is loaded before performing checks
    cy.get('.v-row.activity-section').eq(1).within((section) => {
        cy.wrap(section).contains('tr', 'Loading items...', {timeout: 50000}).should('not.exist');
    });
    // Proceed with checking the instances in the table
    cy.get('.v-row.activity-section').eq(1)
    .find('[data-cy="data-table"]') // Locate the data table
    .find('tbody.v-data-table__tbody') // Find the tbody of the data table
    .should('exist') // Ensure that the tbody exists
    .find('tr') // Find all rows within the tbody
    .each(($row) => {
    cy.wrap($row).within(() => {
      // Check for the instance name in the link
      cy.get('td.data-cell').eq(0).find('.text-truncate', {timeout: 50000}).should('contain.text', apiInstanceName); // Check for the instance name
      // Verify version cell in the appropriate column 
      cy.get('td.data-cell').eq(1).should('contain.text', '1.0'); 
      // Verify the status cell for 'Final'
      cy.get('td.data-cell').eq(2).should('contain.text', 'Final'); 
    });
  });

    // Click on the arrow beside the linked instance name
    cy.get('.v-row.activity-section').eq(1).find('[data-cy="data-table"]') 
    .get('tbody.v-data-table__tbody').find('button.v-btn').first() 
    .click(); 

    cy.get('.v-row.activity-section').eq(1).find('[data-cy="data-table"]') 
    .get('tbody.v-data-table__tbody .child-row')
    .should('contain.text', apiInstanceName)
    .and('contain.text', '0.1')
    .and('contain.text', 'Draft');
})
