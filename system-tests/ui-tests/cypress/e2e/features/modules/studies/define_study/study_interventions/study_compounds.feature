@REQ_ID:1074257
Feature: Studies - Define Study - Study Interventions - Study Compounds

    Background: User is logged in and study has been selected
        Given The user is logged in
        And A test study is selected

    Scenario: [Test data] Study compunds feature flag is enabled, data for compound creation is fetched and existing compounds are deleted
        Given The '/administration/featureflags' page is opened
        And User switch to 'Studies' feature flags
        And User enables 'compounds_studies' feature flag
        And [API] Study compound simple data is fetched
        And [API] Study compound alias data is fetched
        And [API] Study compound medical product data is fetched
        And [API] Study compound type of treatment data is fetched is created
        And The study compounds data is cleaned for testing purspose

    Scenario: [Navigaion] User must be able to navigate to the Study Compounds page
        Given The '/studies' page is opened
        When The 'Study Interventions' submenu is clicked in the 'Define Study' section
        And The 'Study Compounds' tab is selected
        Then The current URL is '/study_interventions/study_compounds'

    Scenario: [Table][Columns][Names] User must be able to see the page table with correct columns
        Given The test study '/study_interventions/study_compounds' page is opened
        Then A table is visible with following headers
            | headers            |
            | #                  |
            | Type of treatment  |
            | Reason for missing |
            | Compound           |
            | Sponsor compound   |
            | Compound alias     |
            | Medicinal product  |
            | Dose frequency     |

    Scenario: [Table][Columns][Visibility] User must be able to use column selection option
        Given The test study '/study_interventions/study_compounds' page is opened
        When The first column is selected from Select Columns option for table with actions
        Then The table contain only selected column and actions column

    Scenario: [Create] User must be able to create a study compound
        Given The test study '/study_interventions/study_compounds' page is opened
        When User clicks add study compund button
        And User select first type of treatment
        And Form continue button is clicked
        And User select first compund
        And User select first medicinal product
        And Form continue button is clicked
        And User fills other information
        And User intercepts compund create request
        When Form save button is clicked
        Then The study compound is present in the compounds table

    Scenario: [Edit] User must be able to edit a study compound
        Given [API] Study compound is created
        Given The test study '/study_interventions/study_compounds' page is opened
        When User searches the compound by the uid
        And The 'Edit' option is clicked from the three dot menu list
        And User select last type of treatment
        And Form continue button is clicked
        And User select last medicinal product
        And Form continue button is clicked
        And User intercepts compund update request
        When Form save button is clicked
        Then The study compound is present in the compounds table

    Scenario: [Create][Form behaviour] Compound definition must be automatically populated when selecting study compound
        Given The test study '/study_interventions/study_compounds' page is opened
        When User clicks add study compund button
        And User select first type of treatment
        And Form continue button is clicked
        And User intercepts compund aliases request
        And User intercepts compunds request
        And User select first compund
        Then The compound alias data is automatically populated from library
        And The sponsor compound data is automatically populated from library

    Scenario: [Create][Form behaviour] Pharmacological and Medicinal Product data must be automatically populated when selecting medicinal product
        Given The test study '/study_interventions/study_compounds' page is opened
        When User clicks add study compund button
        And User select first type of treatment
        And Form continue button is clicked
        And User intercepts medicial products request
        And User intercepts pharmaceutical products request
        And User select first compund
        And User select first medicinal product
        Then The Pharmaceutical Product data is automatically populated from library
        And The Medicinal Product data is automatically populated from library

    Scenario: [Create] User must not be able to create a study compound without the type of treatment selected
        Given The test study '/study_interventions/study_compounds' page is opened
        When User clicks add study compund button
        And Form continue button is clicked
        Then The user cannot save the form

    Scenario: [Create] User must not be able to create a study compound without the compound selected
        Given The test study '/study_interventions/study_compounds' page is opened
        When User clicks add study compund button
        And User select first type of treatment
        And Form continue button is clicked
        And Form continue button is clicked
        Then The user cannot save the form

    Scenario: [Create] User must not be able to create a study compound without the medicinal product selected
        Given The test study '/study_interventions/study_compounds' page is opened
        When User clicks add study compund button
        And User select first type of treatment
        And Form continue button is clicked
        And User select first compund
        And Form continue button is clicked
        Then The user cannot save the form

    Scenario: [Delete] User must be able to delete a study compound
        Given [API] Study compound is created
        Given The test study '/study_interventions/study_compounds' page is opened
        When User searches the compound by the uid
        When The 'Delete' option is clicked from the three dot menu list
        And User intercepts compund delete request
        And Action is confirmed by clicking continue
        Then The study compound is removed
        And The pop up displays 'Study compound deleted'

    Scenario: [Export][CSV] User must be able to export the data in CSV format
        Given The test study '/study_interventions/study_compounds' page is opened
        When User clicks table export button
        And User selects 'CSV' format to export the table content
        And Action is confirmed by clicking continue
        Then The study specific 'StudyCompounds' file is downloaded in 'csv' format

    Scenario: [Export][Json] User must be able to export the data in JSON format
        Given The test study '/study_interventions/study_compounds' page is opened
        When User clicks table export button
        And User selects 'JSON' format to export the table content
        And Action is confirmed by clicking continue
        Then The study specific 'StudyCompounds' file is downloaded in 'json' format

    Scenario: [Export][Xml] User must be able to export the data in XML format
        Given The test study '/study_interventions/study_compounds' page is opened
        When User clicks table export button
        And User selects 'XML' format to export the table content
        And Action is confirmed by clicking continue
        Then The study specific 'StudyCompounds' file is downloaded in 'xml' format

    Scenario: [Export][Excel] User must be able to export the data in EXCEL format
        Given The test study '/study_interventions/study_compounds' page is opened
        When User clicks table export button
        And User selects 'EXCEL' format to export the table content
        And Action is confirmed by clicking continue
        Then The study specific 'StudyCompounds' file is downloaded in 'xlsx' format

