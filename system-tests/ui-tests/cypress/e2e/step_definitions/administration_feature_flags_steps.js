const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

Given("The toggle is set to on", () => toggleAllOnOff(true));

Given("The toggle is set to off", () => toggleAllOnOff(false));

When("Click the View Listings side-menu", () => cy.get('.v-list-item-title').contains('View Listings').click())

Then("The sub-menu Analysis Study Metadata should exist", () => checkIfItemAvailableInMenu('Analysis Study Metadata (New)', true))

Then("The sub-menu Analysis Study Metadata should not exist", () => checkIfItemAvailableInMenu('Analysis Study Metadata (New)', false))

When('Activity instance wizard feature flag is turned off', () => toggleOnOff('create/edit Activity Instances', false))

When('Activity instance wizard feature flag is turned on', () => toggleOnOff('create/edit Activity Instances', true))

When('Activity instance wizard textual findings feature flag is turned on', () => toggleOnOff('Textual Findings use case in the new wizard stepper', true))

When('Activity instance wizard edit mode feature flag is turned on', () => toggleOnOff('edit mode of the new wizard', true))

When('Old placeholder workflow feature flag is turned on', () => toggleOnOff('enabled restores the old placeholder activity workflow: shows the Requested Activities', true))

When('Old placeholder workflow feature flag is turned off', () => toggleOnOff('enabled restores the old placeholder activity workflow: shows the Requested Activities', false))

When('Study data supplier feature flag is turned on', () => toggleOnOff('This flag toggles on/off the Study Data Suppliers page', true))

When('Userdefined study data supplier feature flag is turned on', () => toggleOnOff('This flag toggles on/off the ability to create a user-defined data supplier from study level', true))

function toggleAllOnOff(on) {
  cy.wait(1000)
  on ? cy.get('table .v-switch input').check() : cy.get('table .v-switch input').uncheck()
}

function checkIfItemAvailableInMenu(name, shouldExists) {
  const condition = shouldExists ? 'be.visible' : 'not.exist'
  cy.get(`[data-cy="${name}"]`).should(condition);
}

function toggleOnOff(featureName, on) {
  cy.contains('table tbody tr', featureName).find('.v-switch input').then(el => on ? cy.wrap(el).check() : cy.wrap(el).uncheck())
}
