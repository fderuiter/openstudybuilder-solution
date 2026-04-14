@REQ_ID:1074260
Feature: Studies - Define Study - Study Activities - Exchange Activity

    As a system user,
    I want the system to ensure [Scenario],
    So that I can make complete and consistent specification of study activities.

    Background: User is logged in and study has been selected
        Given The user is logged in
        And A test study is selected

    Scenario: [TestData] Old placeholder activity workflow feature flag is disabled
        When The '/administration/featureflags' page is opened
        Then Old placeholder workflow feature flag is turned off

    Scenario: [TestData] Study visits, epochs and activities are created
        And [API] All Activities are deleted from study

    Scenario: [Actions][Exchange Activity] User must be able to exchange submitted activity placeholder with more than activity from library
        When User clears list of exchanged activities
        Given [API] Activity in status Draft exists
        And [API] Activity is approved
        And Name of Activity from Library for exchaning placeholder is saved
        Given [API] Activity in status Draft exists
        And [API] Activity is approved
        And Name of Activity from Library for exchaning placeholder is saved
        And [API] Get SoA Group 'BIOMARKERS' id
        When [API] Create Submitted Requested Activity
        And [API] Requested Activity is added to the study
        Given The test study '/activities/list' page is opened
        And Activity placeholder is found
        When The 'Exchange Activity' option is clicked from the three dot menu list
        And Form continue button is clicked
        And User waits for the table
        And Users enables filters in the form window
        And Activity filter with index 2 is enabled in the form window
        When 1 Activity for exchanging the placeholder is searched in filters
        Then 1 Activity is found and click in the filters
        When 2 Activity for exchanging the placeholder is searched in filters
        Then 2 Activity is found and click in the filters
        And User waits for the table
        When User selects 1 activity from Library to exchange placeholder with
        When User selects 2 activity from Library to exchange placeholder with
        And Sets SoA Group as 'INFORMED CONSENT' for 1 Activity
        And Sets SoA Group as 'INFORMED CONSENT' for 2 Activity
        And Form save button is clicked
        And The form is no longer available
        Then The Study Activity Placeholder is not available
        And 1 Activity that exchanged the placeholder is found in Study Activities table
        And 2 Activity that exchanged the placeholder is found in Study Activities table
        
    Scenario: [Actions][Exchange Activity] User must be able to exchange not submitted activity placeholder with more than activity from library
        When User clears list of exchanged activities
        Given [API] Activity in status Draft exists
        And [API] Activity is approved
        And Name of Activity from Library for exchaning placeholder is saved
        Given [API] Activity in status Draft exists
        And [API] Activity is approved
        And Name of Activity from Library for exchaning placeholder is saved
        And [API] Get SoA Group 'BIOMARKERS' id
        When [API] Create Unsubmitted Requested Activity
        And [API] Requested Activity is added to the study
        Given The test study '/activities/list' page is opened
        And Activity placeholder is found
        When The 'Exchange Activity' option is clicked from the three dot menu list
        And Form continue button is clicked
        And User waits for the table
        And Users enables filters in the form window
        And Activity filter with index 2 is enabled in the form window
        When 1 Activity for exchanging the placeholder is searched in filters
        Then 1 Activity is found and click in the filters
        When 2 Activity for exchanging the placeholder is searched in filters
        Then 2 Activity is found and click in the filters
        And User waits for the table
        When User selects 1 activity from Library to exchange placeholder with
        When User selects 2 activity from Library to exchange placeholder with
        And Sets SoA Group as 'INFORMED CONSENT' for 1 Activity
        And Sets SoA Group as 'INFORMED CONSENT' for 2 Activity
        And Form save button is clicked
        And The form is no longer available
        Then The Study Activity Placeholder is not available
        And 1 Activity that exchanged the placeholder is found in Study Activities table
        And 2 Activity that exchanged the placeholder is found in Study Activities table

    Scenario: [Actions][Exchange Activity] User must be able to exchange submitted activity placeholder with more than activity from study
        When User clears list of exchanged activities
        When Get study 'CDISC DEV-9881' uid
        And Select study with uid saved in previous step
        And [API] Study Activity is created and approved
        And Name of Activity from Library for exchaning placeholder is saved
        And [API] Get SoA Group 'INFORMED CONSENT' id
        And [API] Activity is added to the selected study
        And [API] Study Activity is created and approved
        And Name of Activity from Library for exchaning placeholder is saved
        And [API] Get SoA Group 'INFORMED CONSENT' id
        And [API] Activity is added to the selected study
        When Get study 'CDISC DEV-9876' uid
        And Select study with uid saved in previous step
        And [API] Get SoA Group 'BIOMARKERS' id
        When [API] Create Submitted Requested Activity
        And [API] Requested Activity is added to the study
        Given The test study '/activities/list' page is opened
        And Activity placeholder is found
        And User intercepts available studies request
        When The 'Exchange Activity' option is clicked from the three dot menu list
        And User waits for available studies request
        And Activity from studies is selected
        And User selects select study 'CDISC DEV-9881'
        And Form continue button is clicked
        And User waits for the table
        And Users enables filters in the form window
        And Activity filter with index 3 is enabled in the form window
        When 1 Activity for exchanging the placeholder is searched in filters
        Then 1 Activity is found and click in the filters
        When 2 Activity for exchanging the placeholder is searched in filters
        Then 2 Activity is found and click in the filters
        And User waits for the table
        When User selects 1 activity from Library to exchange placeholder with
        When User selects 2 activity from Library to exchange placeholder with
        And Form save button is clicked
        And The form is no longer available
        Then The Study Activity Placeholder is not available
        And 1 Activity that exchanged the placeholder is found in Study Activities table
        And 2 Activity that exchanged the placeholder is found in Study Activities table

    Scenario: [Actions][Exchange Activity] User must be able to exchange not submitted activity placeholder with more than activity from library
        When User clears list of exchanged activities
        When Get study 'CDISC DEV-9881' uid
        And Select study with uid saved in previous step
        And [API] Study Activity is created and approved
        And Name of Activity from Library for exchaning placeholder is saved
        And [API] Get SoA Group 'INFORMED CONSENT' id
        And [API] Activity is added to the selected study
        And [API] Study Activity is created and approved
        And Name of Activity from Library for exchaning placeholder is saved
        And [API] Get SoA Group 'INFORMED CONSENT' id
        And [API] Activity is added to the selected study
        When Get study 'CDISC DEV-9876' uid
        And Select study with uid saved in previous step
        And [API] Get SoA Group 'BIOMARKERS' id
        When [API] Create Unsubmitted Requested Activity
        And [API] Requested Activity is added to the study
        Given The test study '/activities/list' page is opened
        And Activity placeholder is found
        And User intercepts available studies request
        When The 'Exchange Activity' option is clicked from the three dot menu list
        And User waits for available studies request
        And Activity from studies is selected
        And User selects select study 'CDISC DEV-9881'
        And Form continue button is clicked
        And User waits for the table
        And Users enables filters in the form window
        And Activity filter with index 3 is enabled in the form window
        When 1 Activity for exchanging the placeholder is searched in filters
        Then 1 Activity is found and click in the filters
        When 2 Activity for exchanging the placeholder is searched in filters
        Then 2 Activity is found and click in the filters
        And User waits for the table
        When User selects 1 activity from Library to exchange placeholder with
        When User selects 2 activity from Library to exchange placeholder with
        And Form save button is clicked
        And The form is no longer available
        Then The Study Activity Placeholder is not available
        And 1 Activity that exchanged the placeholder is found in Study Activities table
        And 2 Activity that exchanged the placeholder is found in Study Activities table

    Scenario: [Actions][Exchange Activity] User must not be able to exchange activity with more than activity from library
        When User clears list of exchanged activities
        Given [API] Activity in status Draft exists
        And [API] Activity is approved
        And Name of Activity from Library for exchaning placeholder is saved
        Given [API] Activity in status Draft exists
        And [API] Activity is approved
        And Name of Activity from Library for exchaning placeholder is saved
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'BIOMARKERS' id
        And [API] Activity is added to the study
        Given The test study '/activities/list' page is opened
        When The Study Activity is found
        When The 'Exchange Activity' option is clicked from the three dot menu list
        And Form continue button is clicked
        And User waits for the table
        And Users enables filters in the form window
        And Activity filter with index 2 is enabled in the form window
        When 1 Activity for exchanging the placeholder is searched in filters
        Then 1 Activity is found and click in the filters
        When 2 Activity for exchanging the placeholder is searched in filters
        Then 2 Activity is found and click in the filters
        And User waits for the table
        When User selects 1 activity from Library to exchange placeholder with
        Then The second activity is disabled for selection

    Scenario: [Actions][Exchange Activity] User must not be able to exchange activity with more than activity from study
        When User clears list of exchanged activities
        When Get study 'CDISC DEV-9881' uid
        And Select study with uid saved in previous step
        And [API] Study Activity is created and approved
        And Name of Activity from Library for exchaning placeholder is saved
        And [API] Get SoA Group 'INFORMED CONSENT' id
        And [API] Activity is added to the selected study
        And [API] Study Activity is created and approved
        And Name of Activity from Library for exchaning placeholder is saved
        And [API] Get SoA Group 'INFORMED CONSENT' id
        And [API] Activity is added to the selected study
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'BIOMARKERS' id
        And [API] Activity is added to the study
        Given The test study '/activities/list' page is opened
        When The Study Activity is found
        And User intercepts available studies request
        When The 'Exchange Activity' option is clicked from the three dot menu list
        And User waits for available studies request
        And Activity from studies is selected
        And User selects select study 'CDISC DEV-9881'
        And Form continue button is clicked
        And User waits for the table
        And Users enables filters in the form window
        And Activity filter with index 3 is enabled in the form window
        When 1 Activity for exchanging the placeholder is searched in filters
        Then 1 Activity is found and click in the filters
        When 2 Activity for exchanging the placeholder is searched in filters
        Then 2 Activity is found and click in the filters
        And User waits for the table
        When User selects 1 activity from Library to exchange placeholder with
        Then The second activity is disabled for selection

    Scenario: [Actions][Exchange Activity] User must be able to exchange activity placeholder with more than one activity in the Detailed SoA
        When User clears list of exchanged activities
        Given [API] Activity in status Draft exists
        And [API] Activity is approved
        And Name of Activity from Library for exchaning placeholder is saved
        Given [API] Activity in status Draft exists
        And [API] Activity is approved
        And Name of Activity from Library for exchaning placeholder is saved
        And [API] Get SoA Group 'BIOMARKERS' id
        When [API] Create Submitted Requested Activity
        And [API] Requested Activity is added to the study
        And The test study '/activities/soa' page is opened
        And Detailed SoA table is loaded
        And User expand table
        When Action 'Exchange Activity' is selected for study activity placeholder
        And Form continue button is clicked
        And User waits for the table
        And Users enables filters in the form window
        And Activity filter with index 2 is enabled in the form window
        When 1 Activity for exchanging the placeholder is searched in filters
        Then 1 Activity is found and click in the filters
        When 2 Activity for exchanging the placeholder is searched in filters
        Then 2 Activity is found and click in the filters
        And User waits for the table
        When User selects 1 activity from Library to exchange placeholder with
        When User selects 2 activity from Library to exchange placeholder with
        And Sets SoA Group as 'INFORMED CONSENT' for 1 Activity
        And Sets SoA Group as 'INFORMED CONSENT' for 2 Activity
        And Form save button is clicked
        And The form is no longer available
        And Detailed SoA table is loaded
        And Placeholder is no longer available
        And 1 Activity that exchanged the placeholder is found in table
        And 2 Activity that exchanged the placeholder is found in table