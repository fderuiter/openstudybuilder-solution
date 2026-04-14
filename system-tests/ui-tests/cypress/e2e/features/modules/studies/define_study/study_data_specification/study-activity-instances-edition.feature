@REQ_ID:1074260
Feature: Studies - Define Study - Study Data Specifications - Study Activity Instances - Edition

    As a system user,
    I want the system to ensure [Scenario],
    So that I can make complete and consistent specification of study activity instances.

    Background: User is logged in and study has been selected
        Given The user is logged in
        And A test study is selected

    Scenario: [Test data] User creates test data via API
        Given [API] The epoch with type 'Pre Treatment' and subtype 'Run-in' exists in selected study
        And [API] The epoch with type 'Treatment' and subtype 'Intervention' exists in selected study
        And [API] All visit groups uids are fetched
        And [API] All visit groups are removed
        And [API] Study vists uids are fetched for selected study
        And [API] Study visits in selected study are cleaned-up
        And [API] The static visit data is fetched
        And [API] The dynamic visit data is fetched: contact mode 'On Site Visit', time reference 'Global anchor visit', type 'Pre-screening', epoch 'Run-in'
        And [API] The visit with following attributes is created: isGlobalAnchor 1, visitWeek 0
        And [API] The dynamic visit data is fetched: contact mode 'On Site Visit', time reference 'Global anchor visit', type 'Randomisation', epoch 'Run-in'
        And [API] The visit with following attributes is created: isGlobalAnchor 0, visitWeek 1
        And [API] The visit with following attributes is created: isGlobalAnchor 0, visitWeek 2
        And [API] All Activities are deleted from study
        And [API] Get SoA Group 'INFORMED CONSENT' id
        And [API] Get class uid for activity instance creation
        And [API] Group and subgroup are created and approved to be used for activity creation
        And [API] Activity with data collection set to 1 and 'FirstActivity' included in the name is created and approved
        And [API] Activity Instance is created and approved
        And [API] Activity is added to the study
        And [API] Activity is assigned to the visit 0
        And [API] Activity is assigned to the visit 1
        And [API] Activity with data collection set to 1 and 'SecondActivity' included in the name is created and approved
        And [API] Activity Instance is created and approved
        And [API] Activity is added to the study
        And [API] Activity is assigned to the visit 0
        And [API] Activity with data collection set to 1 and 'MissingInstance' included in the name is created and approved
        And [API] Activity is added to the study
        And [API] Activity is assigned to the visit 0
        And [API] Activity with data collection set to 0 and 'NoDataCollection' included in the name is created and approved
        And [API] Activity is added to the study
        And [API] Activity is assigned to the visit 0
        And [API] Activity with data collection set to 1 and 'RequiredForActivity' included in the name is created and approved
        And [API] The activity instance with isRequriedForActivity set to true is created and approved
        And [API] Activity is added to the study
        And [API] Activity with data collection set to 1 and 'DefaultForActivity' included in the name is created and approved
        And [API] The activity instance with isDefaultForActivity set to true is created and approved
        And [API] Activity is added to the study
        When The '/administration/featureflags' page is opened
        Then Study data supplier feature flag is turned on
        And Userdefined study data supplier feature flag is turned on
        When User intercepts data supplier request
        And The test study '/data-suppliers' page is opened
        And The 'Overview' tab is selected
        And The Edit button is clicked
        And User waits for 1 seconds
        And All data suppliers are removed
        And Data supplier type is set to 'EDC System'
        And The + button is clicked
        And I select the value with index 0 from the Data supplier dropdown menu
        Then The Save button is clicked

    Scenario: [Edit Instance Relationship][Data collection - yes][Required Instance] User must be presented with Library Instance Status set to Required in the Edit Instance Relationship form if linked Instance is Mandatory for Activity
        Given The test study '/data_specifications/instances' page is opened
        And User searches for 'RequiredForActivity'
        When The 'Edit Activity - Instance relationship' option is clicked from the three dot menu list
        Then Library Instance Status is set to 'Required' in the edition form

    Scenario: [Edit Instance Relationship][Data collection - yes][Defaulted Instance] User must be presented with Library Instance Status set to Defaulted in the Edit Instance Relationship form if linked Instance is Default for Activity
        Given The test study '/data_specifications/instances' page is opened
        And User searches for 'DefaultForActivity'
        When The 'Edit Activity - Instance relationship' option is clicked from the three dot menu list
        Then Library Instance Status is set to 'Defaulted' in the edition form

    Scenario: [Edit Instance Relationship][Data collection - yes][NotRequired and NotDefaulted Instance]  User must be presented with empty Library Instance Status in the Edit Instance Relationship form if linked Instance is neither Default nor Mandatory for Activity
        Given The test study '/data_specifications/instances' page is opened
        And User searches for 'FirstActivity'
        When The 'Edit Activity - Instance relationship' option is clicked from the three dot menu list
        Then Library Instance Status is set to '' in the edition form

    Scenario: [Edit Instance Relationship][Data collection - no][Instance not applicable] User must not be able to edit Instance Relationship if Study Activity has data collection set to No
        Given The test study '/data_specifications/instances' page is opened
        And User searches for 'NoDataCollection'
        When The 'Edit Activity - Instance relationship' option is clicked from the three dot menu list
        Then Data is not available available for Instance Relationship

    Scenario: [Edit Instance Relationship][Data collection - yes][Missing Instance] User must not be able to edit Instance Relationship if Study Activity has data collection set to Yes, but no Activity Instance is linked to it
        Given The test study '/data_specifications/instances' page is opened
        And User searches for 'MissingInstance'
        When The 'Edit Activity - Instance relationship' option is clicked from the three dot menu list
        Then Data is not available available for Instance Relationship

    Scenario: [Important Flag][Data collection - yes][Linked Instance] User must be able to see that by default Study Activity Instance, linked to the Study Activity with data collection set to Yes, is marked as not Important
        Given The test study '/data_specifications/instances' page is opened
        When User searches for 'FirstActivity'
        Then Important is set to empty string in the Study Activity Instance table

    Scenario: [Edit Instance Relationship][Important Flag][Data collection - yes][Linked Instance] User must be able to mark Study Activity Instance as Important if linked Study Activity data collection is set to Yes
        Given The test study '/data_specifications/instances' page is opened
        And User searches for 'FirstActivity'
        When The 'Edit Activity - Instance relationship' option is clicked from the three dot menu list
        And User waits for the table
        And Important checkbox is checked in the edition form
        And Form save button is clicked
        Then Important is set to 'Yes' in the Study Activity Instance table

    Scenario: [Edit Instance Relationship][Important Flag][Multiple Important Instances] User must be able to mark more than one Study Activity Instance as Important
        Given The test study '/data_specifications/instances' page is opened
        And User searches for 'SecondActivity'
        When The 'Edit Activity - Instance relationship' option is clicked from the three dot menu list
        And User waits for the table
        And Important checkbox is checked in the edition form
        And Form save button is clicked
        Then Important is set to 'Yes' in the Study Activity Instance table
    
    Scenario: [Edit Instance Relationship][Important Flag][Data collection - yes][Linked Instance] User must be able to unmark Study Activity Instance as Important if linked Study Activity data collection is set to Yes and Importat is set to Yes
        Given The test study '/data_specifications/instances' page is opened
        And User searches for 'FirstActivity'
        When The 'Edit Activity - Instance relationship' option is clicked from the three dot menu list
        And User waits for the table
        And Important checkbox is unchecked in the edition form
        And Form save button is clicked
        Then Important is set to empty string in the Study Activity Instance table

    Scenario: [Edit Instance Relationship][Baseline flags][Data collection - yes] User must able to assign Baseline flag is Study Activity has data collection set to Yes and Activity Instance is linked to it
        Given The test study '/data_specifications/instances' page is opened
        And User searches for 'FirstActivity'
        When The 'Edit Activity - Instance relationship' option is clicked from the three dot menu list
        And User waits for the table
        And User waits for 1 seconds
        And 'Baseline flags' dropdown is activated in the edition form
        And 'Visit 2' visit is clicked from the dropdown
        And 'Visit 3' visit is clicked from the dropdown
        And Form save button is clicked
        Then Baseline flag value is set to 'Visit 2, Visit 3' in the table

    Scenario: [Edit Instance Relationship][Baseline flags][Data collection - yes] User must able to unassign Baseline flag is Study Activity has data collection set to Yes and Activity Instance is linked to it
        Given The test study '/data_specifications/instances' page is opened
        And User searches for 'FirstActivity'
        When The 'Edit Activity - Instance relationship' option is clicked from the three dot menu list
        And User waits for the table
        And 'Baseline flags' dropdown is activated in the edition form
        And 'Visit 2' visit is clicked from the dropdown
        And Form save button is clicked
        Then Baseline flag value is set to 'Visit 2' in the table

    Scenario: [Edit Instance Relationship][Data Supplier][Data collection - yes] User must be able to add Data Supplier to if linked Study Activity data collection is set to Yes
        Given The test study '/data_specifications/instances' page is opened
        And User searches for 'FirstActivity'
        When The 'Edit Activity - Instance relationship' option is clicked from the three dot menu list
        And User waits for the table
        And 'Data Supplier' dropdown is activated in the edition form
        And Previously added Data Supplier is clicked from the dropdown
        And Origin Type and Origin Source are automatically populated in the edition form 
        And Form save button is clicked
        Then Selected data supplier is visible in the table
        And Automatically populated Origin Type is visible in the table
        And Automatically populated Origin Source is visible in the table

    Scenario: [Edit Mode][Data collection - no][Instance not applicable] User must not be able to edit Instance Relationship if Study Activity has data collection set to No
        Given The test study '/data_specifications/instances' page is opened
        And User waits for the table
        When The pencil button is clicked
        And User waits for 1 seconds
        Then User searches for 'NoDataCollection' and confirms no results returned

    Scenario: [Edit Mode][Data collection - yes][Missing Instance] User must not be able to edit Instance Relationship if Study Activity has data collection set to Yes, but no Activity Instance is linked to it
        Given The test study '/data_specifications/instances' page is opened
        And User waits for the table
        When The pencil button is clicked
        And User waits for 1 seconds
        Then User searches for 'MissingInstance' and confirms no results returned

    Scenario: [Edit Mode][Important Flag][Data collection - yes] User must be able to mark Study Activity Instance as Important if linked Study Activity data collection is set to Yes
        Given The test study '/data_specifications/instances' page is opened
        And User waits for the table
        When The pencil button is clicked
        And User waits for 1 seconds
        And User searches for 'FirstActivity'
        And User waits for the table
        And Important checkbox is checked in the edition mode
        And The Edition mode is saved and closed
        Then The pop up displays '1 Study Activity Instance(s) updated'
        And User waits for the table
        And User searches for 'FirstActivity'
        And Important is set to 'Yes' in the Study Activity Instance table

    Scenario: [Edit Mode][Baseline flags][Data collection - yes] User must able to assign Baseline flag is Study Activity has data collection set to Yes and Activity Instance is linked to it
        Given The test study '/data_specifications/instances' page is opened
        And User waits for the table
        When The pencil button is clicked
        And User waits for 1 seconds
        And User searches for 'SecondActivity'
        And User waits for the table
        And 'Baseline visits' dropdown is activated in the edition mode
        And 'Visit 2' visit is clicked from the dropdown in the edition mode
        And The Edition mode is saved and closed
        Then The pop up displays '1 Study Activity Instance(s) updated'
        And User waits for the table
        And User searches for 'SecondActivity'
        And Baseline flag value is set to 'Visit 2' in the table
        
    Scenario: [Edit Mode][Data Supplier][Data collection - yes] User must be able to add Data Supplier to if linked Study Activity data collection is set to Yes
        Given The test study '/data_specifications/instances' page is opened
        And User waits for the table
        When The pencil button is clicked
        And User waits for 1 seconds
        And User searches for 'SecondActivity'
        And User waits for the table
        And 'Data Supplier' dropdown is activated in the edition mode
        And Previously added Data Supplier is clicked from the dropdown in the edition mode
        And Origin Type and Origin Source are automatically populated in the edition mode
        And The Edition mode is saved and closed
        Then The pop up displays '1 Study Activity Instance(s) updated'
        And User waits for the table
        And User searches for 'SecondActivity'
        And Selected data supplier is visible in the table
        And Automatically populated Origin Type is visible in the table
        And Automatically populated Origin Source is visible in the table

    Scenario: [Edit Mode][Cancel] User must be able to cancel edit mode and made changes will not be applied to Study Activity Instance
        Given The test study '/data_specifications/instances' page is opened
        And User waits for the table
        When The pencil button is clicked
        And User waits for 1 seconds
        And User searches for 'FirstActivity'
        And User waits for the table
        And Important checkbox is unchecked in the edition mode
        And The Edition mode is canceled and closed
        And User searches for 'FirstActivity'
        Then Important is set to 'Yes' in the Study Activity Instance table