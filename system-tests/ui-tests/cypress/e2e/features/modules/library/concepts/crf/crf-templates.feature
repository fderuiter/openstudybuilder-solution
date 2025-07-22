@REQ_ID:1070683
Feature: Library - Concepts - CRFs - CRF Templates

    As a user, I want to manage every CRFs Template in the Library

    Background: User must be logged in
        Given The user is logged in
        And The '/library' page is opened
        And The multilingual CRFs option is toggled off in the settings menu

    Scenario: [Navigation] User must be able to navigate to CRF Templates page
        Given The '/library' page is opened
        When The 'CRFs' submenu is clicked in the 'Concepts' section
        And The 'CRF Templates' tab is selected
        Then The current URL is 'library/crfs/templates'

    Scenario: [Table][Columns][Names] User must be able to see the data of the CRF Templates tab
        Given The 'library/crfs/templates' page is opened
        Then A table is visible with following headers
            | headers   |
            | OID       |
            | Name      |
            | Effective |
            | Obsolete  |
            | Version   |
            | Status    |
            
    Scenario: [Table][Columns][Visibility] User must be able to select visibility of columns in the table 
        Given The '/library/crfs/templates' page is opened
        When The first column is selected from Select Columns option for table with actions
        Then The table contain only selected column and actions column

    Scenario: [Create][Positive case] User must be able to add a new CRF Template
        Given The 'library/crfs/templates' page is opened
        When The 'add-crf-template' button is clicked
        And The CRF Template definition container is filled with data and saved
        And Created CRF Template is found
        Then The CRF Template is visible in the table
        And The item has status 'Draft' and version '0.1'

    Scenario: [Create][Mandatory fields] User must not be able to create CRF Template without Name provided
        Given The 'library/crfs/templates' page is opened
        When The 'add-crf-template' button is clicked
        And Form save button is clicked
        Then The validation appears for the CRF Template Name field

    Scenario: [Actions][Edit][version 0.1] User must be able to update CRF Template in draft status
        Given The 'library/crfs/templates' page is opened
        And Created CRF Template is found
        When The 'Edit' option is clicked from the three dot menu list
        And The CRF Template metadata are updated and saved
        Then The CRF Template is visible in the table
        And The item has status 'Draft' and version '0.2'

    Scenario: [Actions][Approve] User must be able to approve CRF Template in draft status
        Given The 'library/crfs/templates' page is opened
        And Created CRF Template is found
        When The 'Approve' option is clicked from the three dot menu list
        Then The item has status 'Final' and version '1.0'

    Scenario: [Actions][Inactivate] User must be able to deactivate CRF Template in final status
        Given The 'library/crfs/templates' page is opened
        And Created CRF Template is found
        When The 'Inactivate' option is clicked from the three dot menu list
        Then The item has status 'Retired' and version '1.0'

    Scenario: [Actions][Reactivate] User must be able to reactivate CRF Template in retired status
        Given The 'library/crfs/templates' page is opened
        And Created CRF Template is found
        When The 'Reactivate' option is clicked from the three dot menu list
        Then The item has status 'Final' and version '1.0'

    Scenario: [Actions][Approve] User must be able to create new version of currently approved CRF Template
        Given The 'library/crfs/templates' page is opened
        And Created CRF Template is found
        When The 'New version' option is clicked from the three dot menu list
        Then The item has status 'Draft' and version '1.1'

    @manual_test    
    Scenario: User must be able to read change history of selected element
        Given The 'library/crfs/templates' page is opened
        And The 'Show history' option is clicked from the three dot menu list
        When The user clicks on History for particular element
        Then The user is presented with history of changes for that element
        And The history contains timestamps and usernames

    Scenario: [Actions][Delete] User must be able to delete CRF Template in draft status
        Given The 'library/crfs/templates' page is opened
        And [API] The CRF Template in draft status exists
        And Created CRF Template is found
        When The 'Delete' option is clicked from the three dot menu list
        Then The CRF Template is no longer available
