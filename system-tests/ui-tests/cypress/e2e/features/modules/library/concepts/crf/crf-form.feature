@REQ_ID:1070683
Feature: Library - Concepts - CRFs - Forms

    As a user, I want to manage every CRFs Froms in the Library

    Background: User must be logged in
        Given The user is logged in
        And The '/library' page is opened
        And The multilingual CRFs option is toggled off in the settings menu

    Scenario: [Navigation] User must be able to navigate to CRF Forms page
        Given The '/library' page is opened
        When The 'CRFs' submenu is clicked in the 'Concepts' section
        And The 'Forms' tab is selected
        Then The current URL is 'library/crfs/forms'

    Scenario: [Table][Columns][Names] User must be able to see the page table with correct columns
        Given The 'library/crfs/forms' page is opened
        Then A table is visible with following headers
            | headers              |
            | OID                  |
            | Name                 |
            | Implementation Notes |
            | Repeating            |
            | Links                |
            | Version              |
            | Status               |
            
    Scenario: [Table][Columns][Visibility] User must be able to select visibility of columns in the table 
        Given The '/library/crfs/forms' page is opened
        When The first column is selected from Select Columns option for table with actions
        Then The table contain only selected column and actions column

    Scenario: [Create][Positive case] User must be able to add a new CRF form
        Given The 'library/crfs/forms' page is opened
        When The 'add-crf-form' button is clicked
        And The Form definition container is filled with data
        And Form continue button is clicked
        And Form continue button is clicked
        And Form save button is clicked
        Then The pop up displays 'Form created'
        Then Created CRF form is found

    Scenario: [Actions][Edit][version 0.1] User must be able to update CRF form in draft status
        Given The 'library/crfs/forms' page is opened
        And Created CRF form is found
        When The 'Edit' option is clicked from the three dot menu list
        And The Form metadata are updated and saved
        And User goes to Change description step
        And Form save button is clicked
        Then The pop up displays 'Form updated'
        Then Created CRF form is found

    Scenario: [Actions][Approve] User must be able to approve CRF form in draft status
        Given The 'library/crfs/forms' page is opened
        And Created CRF form is found
        When The 'Approve' option is clicked from the three dot menu list
        Then The item has status 'Final' and version '1.0'

    Scenario: [Actions][Inactivate] User must be able to deactivate CRF form in final status
        Given The 'library/crfs/forms' page is opened
        And Created CRF form is found
        When The 'Inactivate' option is clicked from the three dot menu list
        Then The item has status 'Retired' and version '1.0'

    Scenario: [Actions][Reactivate] User must be able to reactivate CRF form in retired status
        Given The 'library/crfs/forms' page is opened
        And Created CRF form is found
        When The 'Reactivate' option is clicked from the three dot menu list
        Then The item has status 'Final' and version '1.0'

    Scenario: [Actions][Edit][version 1.0] User must be able to create new version of currently approved CRF form
        Given The 'library/crfs/forms' page is opened
        And Created CRF form is found
        When The 'New version' option is clicked from the three dot menu list
        Then The item has status 'Draft' and version '1.1'

    Scenario: [Actions][Delete] User must be able to delete CRF Form in draft status
        Given The 'library/crfs/forms' page is opened
        When The 'add-crf-form' button is clicked
        And The Form definition container is filled with data
        And Form continue button is clicked
        And Form continue button is clicked
        And Form save button is clicked
        Then Created CRF form is found
        When The 'Delete' option is clicked from the three dot menu list 
        Then The CRF Form is no longer available

    @manual_test    
    Scenario: User must be able to read change history of selected element
        Given The '/library/crfs/forms' page is opened
        And The 'Show history' option is clicked from the three dot menu list
        When The user clicks on History for particular element
        Then The user is presented with history of changes for that element
        And The history contains timestamps and usernames