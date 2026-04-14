@REQ_ID:1074260
Feature: Studies - Define Study - Study Activities - Study Activities Placeholder

    Background: User is logged in and study has been selected
        Given The user is logged in
        And A test study is selected
        And The test study '/activities/list' page is opened

    Scenario: [TestData] Old placeholder activity workflow feature flag is enabled
        When The '/administration/featureflags' page is opened
        Then Old placeholder workflow feature flag is turned on

    Scenario: [Update][Positive Case][Shared Activity Request] User must be able to accept changes to activity request copied from other study
        When Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        And User selects option to create placeholder without submitting
        When Activity placeholder data is filled in
        And Selected study id is saved
        And Form save button is clicked
        And User waits for 3 seconds
        When Get study 'CDISC DEV-9879' uid
        When The page 'activities/list' is opened for selected study
        And User intercepts available studies request
        When Study activity add button is clicked
        And User waits for available studies request
        And Activity from studies is selected
        And User selects select study 'CDISC DEV-9876'
        And Form continue button is clicked
        And Activity placeholder is searched for
        And The existing activity request is selected
        And Form save button is clicked
        And The form is no longer available
        And Activity placeholder is found
        And The 'Edit' option is clicked from the three dot menu list
        And The study activity request is edited
        And Modal window 'Save' button is clicked
        And The form is no longer available
        And The test study '/activities/list' page is opened
        And Activity placeholder is found
        And The 'Update activity version' option is clicked for flagged item
        And The user is presented with the changes to request
        And Modal window 'Accept' button is clicked
        And The form is no longer available
        Then The activity request changes are applied
        And The Study Activity Placeholder is not available

    Scenario: [Update][Positive Case][Shared Activity Request] User must be able to decline and keep changes to activity request copied from other study
        When Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        And User selects option to create placeholder without submitting
        When Activity placeholder data is filled in
        And Selected study id is saved
        And Form save button is clicked
        When Get study 'CDISC DEV-9879' uid
        When The page 'activities/list' is opened for selected study
        And User intercepts available studies request
        When Study activity add button is clicked
        And User waits for available studies request
        And Activity from studies is selected
        And User selects select study 'CDISC DEV-9876'
        And Form continue button is clicked
        And Activity placeholder is searched for
        And The existing activity request is selected
        And Form save button is clicked
        And The form is no longer available
        And Activity placeholder is found
        And The 'Edit' option is clicked from the three dot menu list
        And The study activity request is edited
        And Modal window 'Save' button is clicked
        And The form is no longer available
        And The test study '/activities/list' page is opened
        And Activity placeholder is found
        And The 'Update activity version' option is clicked for flagged item
        Then The user is presented with the changes to request
        And Modal window 'Decline and keep' button is clicked
        And The form is no longer available
        Then Activity placeholder is found

    Scenario: [Update][Positive Case][Shared Activity Request] User must be able to decline changes and remove activity request copied from other study
        When Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        And User selects option to create placeholder without submitting
        When Activity placeholder data is filled in
        And Selected study id is saved
        And Form save button is clicked
        When Get study 'CDISC DEV-9879' uid
        When The page 'activities/list' is opened for selected study
        And User intercepts available studies request
        When Study activity add button is clicked
        And User waits for available studies request
        And Activity from studies is selected
        And User selects select study 'CDISC DEV-9876'
        And Form continue button is clicked
        And Activity placeholder is searched for
        And The existing activity request is selected
        And Form save button is clicked
        And The form is no longer available
        And Activity placeholder is found
        And The 'Edit' option is clicked from the three dot menu list
        And The study activity request is edited
        And Modal window 'Save' button is clicked
        And The form is no longer available
        And The test study '/activities/list' page is opened
        And Activity placeholder is found
        And The 'Update activity version' option is clicked for flagged item
        And The user is presented with the changes to request
        And Modal window 'Decline and keep' button is clicked        
        Then The form is no longer available
        When The 'Remove Activity' option is clicked for flagged item
        And Action is confirmed by clicking continue
        Then The activity request is removed from the study
        And The Study Activity Placeholder is not available

    Scenario: [Positive Case][Shared Activity Request] User must be able to approve activity request created from placeholder
        When Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        And User selects option to create placeholder with submitting
        When Activity placeholder data is filled in
        And Form save button is clicked
        Then Activity placeholder is found
        When The '/library/activities/requested-activities' page is opened
        Then Activity placeholder is found
        When The 'Handle placeholder request' option is clicked from the three dot menu list
        And User waits for 1 seconds
        And The request continue button is clicked
        And The activity request approval form is filled with definition
        And The sponsor continue button is clicked
        And The confirm continue button is clicked
        Then The Study Activity Placeholder is not available
        When The test study '/activities/list' page is opened
        Then Activity placeholder is found
        When The 'Update to approved activity' option is clicked for flagged item
        And Modal window 'Accept' button is clicked
        And The item actions button is clicked
        Then The form is no longer available
        And 'Update to approved activity' action is not available

    Scenario: [Update][Positive Case][Shared Activity Request] User must not be notified of changes when SoA group has been updated
        When Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        And User selects option to create placeholder without submitting
        When Activity placeholder data is filled in
        And Selected study id is saved
        And Form save button is clicked
        And User waits for 3 seconds
        When Get study 'CDISC DEV-9879' uid
        When The page 'activities/list' is opened for selected study
        And User intercepts available studies request
        When Study activity add button is clicked
        And User waits for available studies request
        And Activity from studies is selected
        And User selects select study 'CDISC DEV-9876'
        And Form continue button is clicked
        And Activity placeholder is searched for
        And The existing activity request is selected
        And Form save button is clicked
        And The form is no longer available
        And User waits for table to load
        And Activity placeholder is found
        And The 'Edit' option is clicked from the three dot menu list
        And The study activity request SoA group field is edited
        And Modal window 'Save' button is clicked
        And The form is no longer available
        And The test study '/activities/list' page is opened
        And Activity placeholder is found
        And The updated notification icon and update option are not present

    Scenario: [Update][Positive Case][Shared Activity Request] User must not be notified of changes when Data Collection flag has been updated
        When Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        And User selects option to create placeholder without submitting
        When Activity placeholder data is filled in
        And Selected study id is saved
        And Form save button is clicked
        And User waits for 3 seconds
        When Get study 'CDISC DEV-9879' uid
        When The page 'activities/list' is opened for selected study
        And User intercepts available studies request
        When Study activity add button is clicked
        And User waits for available studies request
        And Activity from studies is selected
        And User selects select study 'CDISC DEV-9876'
        And Form continue button is clicked
        And Activity placeholder is searched for
        And The existing activity request is selected
        And Form save button is clicked
        And The form is no longer available
        And Activity placeholder is found
        And The 'Edit' option is clicked from the three dot menu list
        And The study activity request data collection field is edited
        And Modal window 'Save' button is clicked
        And The form is no longer available
        And The test study '/activities/list' page is opened
        And Activity placeholder is found
        And The updated notification icon and update option are not present

    Scenario: [Update][Positive Case][Shared Activity Request] User must not be notified of changes when Rationale for activity request has been updated
        When Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        And User selects option to create placeholder without submitting
        When Activity placeholder data is filled in
        And Selected study id is saved
        And Form save button is clicked
        And User waits for 3 seconds
        When Get study 'CDISC DEV-9879' uid
        When The page 'activities/list' is opened for selected study
        And User intercepts available studies request
        When Study activity add button is clicked
        And User waits for available studies request
        And Activity from studies is selected
        And User selects select study 'CDISC DEV-9876'
        And Form continue button is clicked
        And Activity placeholder is searched for
        And The existing activity request is selected
        And Form save button is clicked
        And The form is no longer available
        And Activity placeholder is found
        And The 'Edit' option is clicked from the three dot menu list
        And The study activity request rationale for activity field is edited
        And Modal window 'Save' button is clicked
        And The form is no longer available
        And The test study '/activities/list' page is opened
        And Activity placeholder is found
        And The updated notification icon and update option are not present

    @pending_implementation
    Scenario: [Create][Positive case] System must select 'Multiple instances allowed' true as default for placeholder requests
        Given The activity placeholder request is created
        Then The checkbox 'Multiple instances allowed' is set true by default