@REQ_ID:1070683
Feature: Library - Concepts - CRFs - Items

    As a user, I want to manage every CRF Item in the Library

    Background: User must be logged in
        Given The user is logged in
        And The '/library' page is opened
        And The multilingual CRFs option is toggled off in the settings menu

    Scenario: [Navigation] User must be able to navigate to the CRF Items page
        Given The '/library' page is opened
        When The 'CRFs' submenu is clicked in the 'Concepts' section
        And The 'Items' tab is selected
        Then The current URL is '/library/crfs/items'

    Scenario: [Table][Columns][Names] User must be able to see the data of the CRF Items tab
        Given The 'library/crfs/items' page is opened
        Then A table is visible with following headers
            | headers              |
            | OID                  |
            | Name                 |
            | Description          |
            | Implementation Notes |
            | Type                 |
            | Length               |
            | SDS Var Name         |
            | Links                |
            | Version              |
            | Status               |
            
    Scenario: [Table][Columns][Visibility] User must be able to select visibility of columns in the table 
        Given The '/library/crfs/items' page is opened
        When The first column is selected from Select Columns option for table with actions
        Then The table contain only selected column and actions column

    Scenario: [Create][Positive case]User must be able to add an Item
        Given The 'library/crfs/items' page is opened
        When The 'add-crf-item' button is clicked
        And The CRF Item definition container is filled with data and saved
        And Form continue button is clicked
        And Form continue button is clicked
        And Form continue button is clicked
        And Form save button is clicked
        And Created CRF Item is found
        Then The CRF Item is visible in the table
        And The item has status 'Draft' and version '0.1'

    Scenario: [Actions][Edit][version 0.1] User must be able to update an existing Item
        Given The 'library/crfs/items' page is opened
        And Created CRF Item is found
        When The 'Edit' option is clicked from the three dot menu list
        And The CRF Item metadata are updated and saved
        And User goes to Change description step
        And Form save button is clicked
        Then The CRF Item is visible in the table
        And The item has status 'Draft' and version '0.2'

    Scenario: [Actions][Approve] User must be able to approve an Item in draft status
        Given The 'library/crfs/items' page is opened
        And Created CRF Item is found
        When The 'Approve' option is clicked from the three dot menu list
        And The item has status 'Final' and version '1.0'

    Scenario: [Actions][Inactivate] User must be able to inactivate currently active Item
        Given The 'library/crfs/items' page is opened
       And Created CRF Item is found
        When The 'Inactivate' option is clicked from the three dot menu list
        And The item has status 'Retired' and version '1.0'

    Scenario: [Actions][Reactivate] User must be able to reactivate currently retired Item
        Given The 'library/crfs/items' page is opened
        And Created CRF Item is found
        When The 'Reactivate' option is clicked from the three dot menu list
        And The item has status 'Final' and version '1.0'

    Scenario: [Actions][New version] User must be able to create a new version of an Item
        Given The 'library/crfs/items' page is opened
        And Created CRF Item is found
        When The 'New version' option is clicked from the three dot menu list
        Then The item has status 'Draft' and version '1.1'

    @manual_test    
    Scenario: User must be able to read change history of selected element
        Given The '/library/crfs/items' page is opened
        And Created CRF Item is found
        And The 'Show history' option is clicked from the three dot menu list
        When The user clicks on History for particular element
        Then The user is presented with history of changes for that element
        And The history contains timestamps and usernames

    Scenario: [Actions][Delete] User must be able to delete CRF Item in draft status
        Given The 'library/crfs/items' page is opened
        And [API] The CRF Item in draft status exists
        And Created CRF Item is found
        When The 'Delete' option is clicked from the three dot menu list
        Then The CRF Item is no longer available
