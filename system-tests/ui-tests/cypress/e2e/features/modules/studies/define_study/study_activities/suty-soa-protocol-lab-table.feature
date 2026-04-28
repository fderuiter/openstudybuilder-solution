@REQ_ID:1074260
Feature: Studies - Define Study - Study Activities - Schedule of Activities - Protocol - Lab Table

    As a system user,
    I want the system to ensure [Scenario],
    So that I can make complete and consistent specification of study SoA for the protocol.

    Background: User is logged in and study has been selected
        Given The user is logged in
        And A test study is selected
        And The feature flag 'Protocol – Lab' enabled state is set to 'true'

    Scenario: [Test data] User must be able to create data needed for study protocol lab table - lab assemenents
        And [API] The epoch with type 'Pre Treatment' and subtype 'Run-in' exists in selected study
        And [API] The epoch with type 'Treatment' and subtype 'Intervention' exists in selected study
        And [API] Study vists uids are fetched for current study
        When [API] Study visits in current study are cleaned-up
        And [API] The static visit data is fetched
        And [API] The dynamic visit data is fetched: contact mode 'On Site Visit', time reference 'Global anchor visit', type 'Pre-screening', epoch 'Run-in'
        And [API] The visit with following attributes is created: isGlobalAnchor 1, visitWeek 0
        And [API] The visit with following attributes is created: isGlobalAnchor 0, visitWeek 1, minVisitWindow -1, maxVisitWindow 1
        And [API] The dynamic visit data is fetched: contact mode 'On Site Visit', time reference 'Global anchor visit', type 'Randomisation', epoch 'Intervention'
        And [API] The visit with following attributes is created: isGlobalAnchor 0, visitWeek 2, minVisitWindow 3, maxVisitWindow 7
        When [API] All Activities are deleted from study
        When [API] Activity for SoA group 'BIOMARKERS' with activity group 'Laboratory Assessments' is added to the study

    Scenario: [Navigation] User must be able to navigate to Protocol SoA - Lab table page using side menu
        Given The '/studies' page is opened
        When The 'Study Activities' submenu is clicked in the 'Define Study' section
        And The 'Schedule of Activities' tab is selected
        And User switches to the 'protocol_lab_table' view
        Then The current URL is '/activities/soa'

    Scenario: [Table][View] User must be presented with lab assesments activities in the Lab Table view
        And The test study '/activities/soa' page is opened
        When User switches to the 'protocol_lab_table' view
        Then The laboratory assements activities are present in protocol lab table

    Scenario: [Export][CSV] User must be able to export the data in CSV format
        Given The test study '/activities/soa' page is opened
        And User switches to the 'protocol_lab_table' view
        When User clicks export button
        And User selects 'CSV' format to export the table content
        Then The study specific 'protocol_lab_table SoA' file without timestamp is downloaded in 'csv' format

    Scenario: [Export][EXCEL] User must be able to export the data in JSON format
        Given The test study '/activities/soa' page is opened
        And User switches to the 'protocol_lab_table' view
        When User clicks export button
        And User selects 'EXCEL' format to export the table content
        Then The study specific 'protocol_lab_table SoA' file without timestamp is downloaded in 'xlsx' format

    Scenario: [Export][DOCX] User must be able to export the data in XML format
        Given The test study '/activities/soa' page is opened
        And User switches to the 'protocol_lab_table' view
        When User clicks export button
        And User selects 'DOCX' format to export the table content
        Then The study specific 'protocol_lab_table SoA' file without timestamp is downloaded in 'docx' format