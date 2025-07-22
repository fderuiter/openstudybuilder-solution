import { apiActivityName, apiGroupName, apiSubgroupName} from "./api_library_steps";
const { When, Then } = require("@badeball/cypress-cucumber-preprocessor");

When('I click on the test activity subgroup name in the activity subgroup page', () => {
  cy.searchAndCheckPresence(apiSubgroupName, true)
  cy.get('table tbody tr td').contains(apiSubgroupName).click()
})

Then('The Activity group table will be displayed with correct column', () => {
   // Check if the "Activity group" header exists
    cy.get('.section-header h3').contains('Activity group').should('exist');

    // Verify that the table under "Activity group" has the expected column names
     cy.get('.groups-table')
        .find('thead tr') // Get the header row of the table
         .within(() => {
            // Check the column names by their index
            cy.get('th').eq(0).contains('Name').should('exist');      // First column
            cy.get('th').eq(1).contains('Version').should('exist');   // Second column
            cy.get('th').eq(2).contains('Status').should('exist');    // Third column
   });
})

Then('The Activities table will be displayed with correct column', () => { 
  // Check the existence of the "Activities" section header
  cy.get('.section-header h3').contains('Activities').should('exist');

  // Verify that the Activities table has the expected column names
  cy.get('.activities-table')
    .find('thead tr') // Get the header row of the Activities table
      .within(() => {
         // Check the column names by their index
          cy.get('th').eq(0).contains('Name').should('exist');      // First column
          cy.get('th').eq(1).contains('Version').should('exist');   // Second column
          cy.get('th').eq(2).contains('Status').should('exist');    // Third column
            });
            
});

Then('The linked groups should be displayed in the Activity group table', () => {   
        // Verify that there is exactly one row in the table
        cy.get('.groups-table tbody tr')
            .should('have.length', 1) // Assert that there is exactly one row
            .then((row) => {
                // Get and verify the content of the table cells
                cy.wrap(row).find('td').then((cells) => {
                    const name = cells.eq(0).text().trim();      // Get the value from the first column
                    const version = cells.eq(1).text().trim();   // Get the value from the second column
                    const status = cells.eq(2).text().trim();    // Get the value from the third column

                    // Define the expected values
                    const expectedName = apiGroupName;      
                    const expectedVersion = '1.0';    
                    const expectedStatus = 'Final';   

                    // Validate the values against the expected values
                    expect(name).to.equal(expectedName);
                    expect(version).to.equal(expectedVersion);
                    expect(status).to.equal(expectedStatus);
                });
            });
    });

Then('The free text search field should be displayed in the Activity group table', () => {
    cy.get('[data-cy="search-field"]').first().should('be.visible'); // Check if the search field for Activity groups table is present
})    
    
Then('The linked activities should be displayed in the Activities table', () => {
  // Verify that there is exactly one row in the Activities table
  cy.get('.activities-table tbody tr')
            .should('have.length', 1) // Assert that there is exactly one row
            .then((row) => {
                // Get and verify the content of the table cells
                cy.wrap(row).find('td').then((cells) => {
                    const name = cells.eq(0).text().trim();      // Get the value from the first column
                    const version = cells.eq(1).text().trim();   // Get the value from the second column
                    const status = cells.eq(2).text().trim();    // Get the value from the third column

                    // Define the expected values for Activities
                    const expectedActivityName = apiActivityName;      // Replace with the expected name
                    const expectedActivityVersion = '1.0';     // Replace with the expected version
                    const expectedActivityStatus = 'Final';    // Replace with the expected status

                    // Validate the values against the expected values
                    expect(name).to.equal(expectedActivityName);
                    expect(version).to.equal(expectedActivityVersion);
                    expect(status).to.equal(expectedActivityStatus);
                });
            });
})   

Then('The free text search field should be displayed in the Activities table', () => {
    cy.get('[data-cy="search-field"]').eq(1).should('be.visible'); // Check if the search field for Activities table is present
})

Then('The Activities table should be empty', () => {
  cy.get('.activities-table tbody tr').should('have.length', 0) 
 })