const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");
const { activity_placeholder_name } = require("./study_activities_steps");
const { getShortUniqueId } = require("../../support/helper_functions");

let topicCode, instanceName, activityName
let existingInstanceName, existingTopicCode, selectedActivityName, selectedCodeSubmissionValue

Then('User can see which activity was selected in the previous step', () => cy.get('.v-alert__content').should('contain.text', activityName))

When('User intercepts available activities requests', () => cy.intercept('/api/concepts/activities/activities?page_number=1&page_size=*').as('getActivities'))

When('User intecepts codelist submission value request', () => cy.intercept('/api/ct/codelists?filters=*').as('codelistRequest'))

When('User intecepts preview request', () => cy.intercept('/api/concepts/activities/activity-instances/preview').as('preview'))

When('User intercepts activity instance creation request with strict_mode verification', () => {
    cy.intercept('POST', '/api/concepts/activities/activity-instances', (req) => {
        expect(req.body).to.have.property('strict_mode', true)
    }).as('createInstanceWithStrictMode')
})

When('User waits for activity instance creation request with strict_mode verification', () => {
    cy.wait('@createInstanceWithStrictMode')
})

When('User intecepts activity groupings request', () => cy.intercept('/api/concepts/activities/activity-instances/*/groupings?version=0.1').as('activityGroupings'))

When('User intecepts activity items request', () => cy.intercept('/api/concepts/activities/activity-instances/*/activity-items?*').as('activityItemClasses'))

When('User waits for available activities requests', () => cy.wait('@getActivities'))

When('User waits for codelist submission value request', () => cy.wait('@codelistRequest'))

When('User waits for preview request', () => cy.wait('@preview'))

When('User waits for activity groupings request', () => cy.wait('@activityGroupings'))

When('User waits for activity items request', () => cy.wait('@activityItemClasses'))

When('User saves activity name created via API', () => cy.getActivityNameByUid().then(name => activityName = name))

Then("User searches for created activity instance", () => cy.searchFor(instanceName))

Then("Created activity instance is displayed in the first table row", () => cy.checkRowByIndex(0, 'Activity Instance', instanceName))

Then("Activity instance is not visible in table", () => cy.searchAndCheckPresence(instanceName, false))

Given("The Activity Instance Wizard Stepper {string} page is displayed", (stepperPage) => {
    cy.contains('.v-stepper-item', stepperPage).should('have.class', 'v-stepper-item--selected')
})

Given("The Activity Instance Attributes edition page is displayed", () => {
    cy.contains('.dialog-title', 'Edit activity instance attributes').should('be.visible')
})

Given("The Activity Instance Groupings edition page is displayed", () => {
    cy.contains('.dialog-title', 'Edit activity instance groupings').should('be.visible')
})

Given("Add activity item class button is clicked", () => cy.get('.v-window-item button').filter(':visible').contains('Add Activity Item Class').eq(0).click())

When("First activity is selected from the activity list", () => cy.get('.v-overlay-container table tbody tr [type="checkbox"]').eq(0).check())

When("The {string} is selected from the Activity instance class field", name => requiredTabSelection('Activity instance', name))

When("The {string} is selected from the Data category field", name => requiredTabSelection('Data category', name))

When("The {string} is selected from the Data SubCategory field", name => requiredTabSelection('Data subcategory (optional)', name))

When('Customize toggle is turn on', () => cy.get('input[aria-label="Customize"]').check())

When("Value {string} is selected for {int} Activity item class field", (value, index) => selectOptionalActivityItemClass(index, value))

When("The {string} is selected from the Activity instance domain field", name => requiredTabSelection('Data domain', name))

Then("The Activity Item Classes selection displayed", () => cy.contains('.v-overlay .v-row .dialog-title', 'Select Activity Item Classes'). should('be.visible'))

Then("The Activity Item Classes selection is not displayed", () => cy.contains('.v-overlay .v-row .dialog-title', 'Select Activity Item Classes'). should('not.exist'))

Then("Warning is displayed for mandatory field {string}", (fieldName) => warningIsDisplayed(fieldName))

Then("Warning about not matching name and sentence case name is displayed", () => warningIsDisplayed('Sentence case name', "Sentence case name can only differ in case compared to name value"))

Then("Warning about already existing topic code is displayed", () => cy.checkSnackbarMessage(`Activity Instance with Topic Code '${existingTopicCode}' already exists`))

Then("Warning about already existing activity name is displayed", () => cy.checkSnackbarMessage(`Activity Instance with Name '${existingInstanceName}' already exists`))

Then("Warning about not selected acitivity is displayed", () => cy.checkSnackbarMessage(`You must select an activity from the list`))

Then("Activity Instance Data field {string} is cleared", (fieldName) => clearField(fieldName))

Then("Automatically assigned activity instance name is saved", () => {
    cy.contains('.v-stepper-window-item .v-input', 'Activity instance name').find('input').invoke('val').then(text => instanceName = text)
})

Then("Final activity instance name is saved", () => cy.get('.v-container .page-title').invoke('text').then(text => instanceName = text.trim()))

Then("The test_code value is not selected", () => cy.contains('.d-flex .v-input', 'Test Code').next().find('label.v-label').should('contain.text', 'Code submission value'))

Then("The test_code value is automatically populated", () => cy.contains('.d-flex .v-input', 'Test Code').next().find('.v-select__selection').should('not.contain.text', 'Code submission value'))

Then("Sentence case name is lowercased version of instance name", () => {
    cy.contains('.v-stepper-window-item .v-input', 'Activity instance name').find('input').invoke('val').then(nameText => {
        cy.contains('.v-stepper-window-item .v-input', 'Sentence case name').find('input').invoke('val').should('equal', nameText.toLowerCase())
    })
})

When("First available test_name is selected", () => selectActivityItemClass('Test Name'))

When("test_name {string} is selected", (value) => selectSpecificActivityItemClass('Test Name', value))

When("The Instance unit_dimension and standard_unit are selected", () => {
    selectActivityItemClass('Unit dimension')
    selectActivityItemClass('Standardised unit')
})

When("unit_dimension {string} and standard_unit {string} are selected", (unitDimentionValue, standardUnitValue) => {
    selectSpecificActivityItemClass('Unit dimension', unitDimentionValue)
    selectSpecificActivityItemClass('Standardised unit', standardUnitValue, false)
})

When("Activity created via API is searched for", () => cy.searchForInPopUp(activityName))

Then("Correct instance overview page is displayed", () => cy.get('.v-container .page-title').should('contain.text', selectedActivityName))

When("The already used instance name is saved", () => cy.getCellValue(0, 'Activity Instance').then(text => existingInstanceName = text))

When("The already used topic code is saved", () => cy.getCellValue(0, 'Topic code').then(text => existingTopicCode = text))

When("Selected Activity name is saved", () => cy.getCellValueInPopUp(0, 'Activity').then(text => selectedActivityName = text))

When("Selected Code Submission value is saved", () => {
    cy.contains('.d-flex .v-input', 'Test Code').next().find('.v-select__selection').invoke('text').then(val => selectedCodeSubmissionValue = val)
})

When("The instance name is changed to the already used one", () => {
    fillField('Activity instance name', existingInstanceName)
    fillField('Sentence case name', existingInstanceName.toLowerCase())
})

When("The instance name is changed to custom one", () => {
    instanceName = `Instance${getShortUniqueId()}`
    fillField('Activity instance name', instanceName)
    fillField('Sentence case name', instanceName.toLowerCase())
})

When("The sentance case name is set to different value than instance name", () => fillField('Sentence case name', `${getShortUniqueId()}`))

When("The topic code is changed to the already used one", () => fillField('Topic code', existingTopicCode))

Then("Activity Instance Name is identical to selected Activity Name", () => {
    cy.contains('.v-stepper-window-item .v-input', 'Activity instance name').find('input').should('have.value', selectedActivityName)
})

Then("Topic code is uppercased version of Activity Instance Name with _ instead of spaces", () => {
    cy.contains('.v-stepper-window-item .v-input', 'Topic code').find('input').should('contain.value', selectedActivityName.toUpperCase().replaceAll(' ', '_'))
})

Then("ADaM parameter code is four first letters of selected Code submission value of Activity Item Class", () => {
    cy.contains('.v-stepper-window-item .v-input', 'ADaM parameter code').find('input').should('contain.value', selectedCodeSubmissionValue.substring(0, 4))
})

Then("ADaM parameter code input should not exists", () => {
    cy.contains('.v-stepper-window-item .v-input', 'ADaM parameter code').should('not.exist')
})

When("Data from research lab is checked", () => cy.get('input[aria-label="Data from a Research lab"]').check())

Then("Activity Instance Name have Research added to it", () => {
    cy.contains('.v-stepper-window-item .v-input', 'Activity instance name').find('input').should('have.value', `${selectedActivityName} Research`)
})

Then("Topic code have _RESEARCH added to it", () => {
    cy.contains('.v-stepper-window-item .v-input', 'Topic code').find('input').should('have.value', `${selectedActivityName.toUpperCase().replaceAll(' ', '_')}_RESEARCH`)
})

Then("ADaM parameter code have X added to it", () => {
    cy.contains('.v-stepper-window-item .v-input', 'ADaM parameter code').find('input').should('contain.value', `${selectedCodeSubmissionValue.substring(0, 4)}X`)
})

Then('Item classes unit_dimension and standardised unit are not displayed', () => {
    cy.contains('.d-flex .v-input', 'Unit dimension').should('not.exist')
    cy.contains('.d-flex .v-input', 'Standardised unit').should('not.exist')
})

Then('Required fields unit_dimension and standardised unit are marked as required', () => {
    cy.contains('.d-flex .v-input', 'Unit dimension').next().should('contain.text', 'This field is required')
    cy.contains('.d-flex .v-input', 'Standardised unit').next().should('contain.text', 'This field is required')
})

Then('Required fields name_submission_value, code_submission_value are marked as required', () => {
    cy.contains('.d-flex .v-input', 'Test Name').next().should('contain.text', 'This field is required')
    cy.contains('.d-flex .v-input', 'Test Code').next().should('contain.text', 'This field is required')
})

Then('Only values for Numeric Findings and MK as data domain are displayed for Activity Item Class selection in the Step 3', () => {
    cy.get('.v-form .v-card-text').filter(':visible').contains('.d-flex .v-input', 'Activity item class').click()
    cy.contains('.v-overlay .v-list-item', 'Analysis Method')
    cy.contains('.v-overlay .v-list-item', 'Directionality')
    cy.contains('.v-overlay .v-list-item', 'Laterality')
    cy.contains('.v-overlay .v-list-item', 'Location')
    cy.contains('.v-overlay .v-list-item', 'Method')
    cy.contains('.v-overlay .v-list-item', 'Position')
    cy.get('.v-form .v-card-text').filter(':visible').contains('.d-flex .v-input', 'Activity item class').click()
})

Then('Only values for Numeric Findings and MK as data domain are displayed for Activity Item Class selection in the Step 4', () => {
    cy.get('.v-form .v-card-text').filter(':visible').contains('.d-flex .v-input', 'Activity item class').click()
    cy.contains('.v-overlay .v-list-item', 'Analysis Method')
    cy.contains('.v-overlay .v-list-item', 'Elapsed Time')
    cy.contains('.v-overlay .v-list-item', 'Evaluation Interval')
    cy.contains('.v-overlay .v-list-item', 'Evaluation Interval Text')
    cy.contains('.v-overlay .v-list-item', 'Evaluator')
    cy.contains('.v-overlay .v-list-item', 'Evaluator Identifier')
    cy.contains('.v-overlay .v-list-item', 'Group Identifier')
})

function selectActivityItemClass(type) {
    cy.contains('.d-flex .v-input', type).next().click()
    cy.get('.v-overlay .v-list-item').eq(0).should('not.have.text', 'No data available')
    cy.get('.v-overlay .v-list-item').eq(0).click()
}

function selectSpecificActivityItemClass(type, value, search = true) {
    cy.contains('.d-flex .v-input', type).next().click()
    cy.get('.v-overlay .v-list-item').should('not.have.text', 'No data available')
    if(search) cy.get('input[placeholder="Search"]').click().type(value)
    cy.get('.v-overlay .v-list-item').should('not.have.text', 'No data available').contains(value).click()
}

function selectOptionalActivityItemClass(index, itemClassName) {
    cy.get('.v-form .v-card-text').filter(':visible').eq(index).contains('.d-flex .v-input', 'Activity item class').click()
    cy.contains('.v-overlay .v-list-item', itemClassName).click()
    cy.get('.v-form .v-card-text').filter(':visible').eq(index).contains('.d-flex .v-input', 'Activity item class').next().click()
    cy.get('.v-overlay .v-list-item').eq(0).should('not.have.text', 'No data available').click()
    cy.wait(1000)
}

function requiredTabSelection(dropdown_name, value) {
    cy.contains('.v-stepper-window-item .v-input', dropdown_name).click()
    cy.contains('.v-overlay .v-list-item', value).click()
}

function warningIsDisplayed(fieldName, message = 'This field is required') {
    // Handle both regular fields and activity item class fields (which are in .d-flex containers)
    // For "Code submission value", it's in a .d-flex container within a v-card
    if (fieldName === 'Code submission value') {
        cy.contains('.v-card .d-flex .v-input', fieldName).parent().contains(message).should('be.visible')
    } else {
        cy.get('body').then($body => {
            const regularField = $body.find(`.v-stepper-window-item .v-input:contains("${fieldName}")`)
            const activityItemField = $body.find(`.d-flex .v-input:contains("${fieldName}")`)
            
            if (regularField.length > 0) {
                cy.contains('.v-stepper-window-item .v-input', fieldName).contains(message).should('be.visible')
            } else if (activityItemField.length > 0) {
                cy.contains('.d-flex .v-input', fieldName).parent().contains(message).should('be.visible')
            } else {
                // Fallback: try to find the field anywhere
                cy.contains('.v-input', fieldName).contains(message).should('be.visible')
            }
        })
    }
}

function clearField(fieldName) {
    cy.contains('.v-stepper-window-item .v-input', fieldName).clear()
}

function fillField(fieldName, value) {
    cy.contains('.v-stepper-window-item .v-input', fieldName).clear().type(value)
}