    @REQ_ID:1074260
    Feature: Studies - Define Study - Study Activities - Study Activities Placeholders

    As a system user,
    I want the system to ensure [Scenario],
    So that I can make complete and consistent specification of study activities.

    Background: User is logged in and study has been selected
        Given The user is logged in
        And A test study is selected

    Scenario: [TestData] Old placeholder activity workflow feature flag is disabled and all activities are deleted from study
        When The '/administration/featureflags' page is opened
        And User switch to 'Studies' feature flags
        And User enables 'streamline_placeholder_activities' feature flag
        And [API] All Activities are deleted from study

    @smoke_test
    Scenario: [Create][Placeholder] User must be able to create a Study Activity placeholder as an activity concept request
        Given The test study '/activities/list' page is opened
        When Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        When Activity placeholder data is filled in
        And Form save button is clicked
        And The form is no longer available
        And Activity placeholder is found
        Then The Study Activity placeholder is visible within the Study Activities table

    Scenario: [Actions][Delete][Placeholder] User must be able to delete a Study Activity placeholder
        Given The test study '/activities/list' page is opened
        And Activity placeholder is found
        When The 'Remove Activity' option is clicked from the three dot menu list
        And Action is confirmed by clicking continue
        Then The Study Activity Placeholder is not available

    Scenario: [Create][Placeholder] User must be able to create a Study Activity placeholder with already existing name if group/subgroup is different
        Given The test study '/activities/list' page is opened
        When Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        And User sets Activity Placeholder name
        When User selects first group for placeholder
        And User selects first subgroup for placeholder
        And User selects Activity Placeholder SoA group as 'EFFICACY'
        And User sets Activity Placeholder rationale
        And Form save button is clicked
        Then The pop up displays 'Study activity added'
        When Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        And User sets Activity Placeholder name that is already used
        When User selects first group for placeholder
        And User selects second subgroup for placeholder
        And User selects Activity Placeholder SoA group as 'EFFICACY'
        And User sets Activity Placeholder rationale
        And Form save button is clicked
        Then The pop up displays 'Study activity added'
        When Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        And User sets Activity Placeholder name that is already used
        When User selects second group for placeholder
        And User selects first subgroup for placeholder
        And User selects Activity Placeholder SoA group as 'EFFICACY'
        And User sets Activity Placeholder rationale
        And Form save button is clicked
        Then The pop up displays 'Study activity added'

    Scenario: [Create][Placeholder] User must be able to reuse already existing placeholder
        When Get study 'CDISC DEV-9877' uid
        When The page 'activities/list' is opened for selected study
        When Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        And User sets Activity Placeholder name that is already used
        When User selects first group for placeholder
        And User selects first subgroup for placeholder
        And User selects Activity Placeholder SoA group as 'EFFICACY'
        And User sets Activity Placeholder rationale
        And Action is confirmed by clicking save
        Then Pop-up displays that there is already existing placeholder with such name, group and subgroup
        And Action is confirmed by clicking continue
        And The form is no longer available
        And Activity placeholder is found

    Scenario: [Actions][Edit][version 0.1][Placeholder] User must be able to edit a Study Activity placeholder
        And [API] Get SoA Group 'BIOMARKERS' id
        When [API] Create Submitted Requested Activity
        And [API] Requested Activity is added to the study
        Given The test study '/activities/list' page is opened
        And Activity placeholder is found
        When The 'Edit' option is clicked from the three dot menu list
        And The SoA group can be changed
        And Modal window 'Save' button is clicked
        And The form is no longer available
        Then The pop up displays 'Study activity updated'
        And Activity placeholder is found
        Then The edited Study Activity data is reflected within the Study Activity table

    @BUG_ID:2722627
    Scenario: [Actions][Edit][version 0.1][Placeholder] User must be able to edit data collection flag
        Given The test study '/activities/list' page is opened
        When Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        When Activity placeholder data is filled in
        And Data collection flag is unchecked
        And Form save button is clicked
        And The form is no longer available
        And Activity placeholder is found
        When The 'Edit' option is clicked from the three dot menu list
        And Data collection flag is checked
        And Modal window 'Save' button is clicked
        And The form is no longer available
        Then The pop up displays 'Study activity updated'
        And Activity placeholder is found
        Then The study activity table is displaying updated value for data collection

    Scenario: [Create][Mandatory fields][Placeholder] User must not be able to create Study Activity placeholder without SoA group selected
        Given The test study '/activities/list' page is opened
        And Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        And The user tries to go further in activity placeholder creation without SoA group chosen
        And Form save button is clicked
        Then The validation appears under empty SoA group selection

    Scenario: [Create][Mandatory fields][Placeholder] User must not be able to create Study Activity placeholder without SoA group selected
        Given The test study '/activities/list' page is opened
        And Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        And The user tries to go further in activity placeholder creation without SoA group chosen
        And Form save button is clicked
        Then The validation appears under empty SoA group selection