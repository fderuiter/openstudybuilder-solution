const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

Given("The feature flag {string} enabled state is set to {string}", (feature_flag, state) => enableFlag(feature_flag, state))

When('User switch to {string} feature flags', (name) => cy.contains('.layoutSelector button', name).click())

When('User enables {string} feature flag', (name) => toggleOnOff(name, true))

When('User disables {string} feature flag', (name) => toggleOnOff(name, false))

function toggleOnOff(featureName, on) {
  cy.contains('table tbody tr', featureName).find('.v-switch input').then(el => on ? cy.wrap(el).check() : cy.wrap(el).uncheck())
}

function enableFlag(flagName, state) {
  cy.sendGetRequest('/feature-flags').then((response) => {
    let feature_flag_sn = response.body.find(element => element.feature == flagName).sn
    cy.sendUpdateRequest('PATCH',`feature-flags/${feature_flag_sn}`, { enabled: state })
  })
}