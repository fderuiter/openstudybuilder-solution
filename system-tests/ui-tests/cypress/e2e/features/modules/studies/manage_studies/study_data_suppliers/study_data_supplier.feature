@REQ_ID:3459562
Feature: Study - Manage Study - Study Data Suppliers
    As a user, I want to manage the data suppliers in the Study

    Background:
        Given The user is logged in
        And A test study is selected
        And Data supplier type is set to 'EDC System'

    Scenario: [Test data] User must be able to enabler feature flags and delete all existing data suppliers for given study
        Given The '/administration/featureflags' page is opened
        And User switch to 'Studies' feature flags
        And User enables 'study_data_suppliers' feature flag
        And User enables 'study_data_suppliers_create_from_study' feature flag
        Given User intercepts data supplier request
        Given The test study '/data-suppliers' page is opened
        And The 'Overview' tab is selected
        When The Edit button is clicked
        And User waits for 1 seconds
        And All data suppliers are removed
        Then The Save button is clicked 

    @smoke_test
    Scenario: [Navigation] User must be able to navigate to the List Study Data Supplier tab in the Study Data Suppliers page
        Given The '/studies' page is opened
        When The 'Study Data Suppliers' submenu is clicked in the 'Manage Study' section
        And The 'Overview' tab is selected
        Then The current URL is '/data-suppliers'

    Scenario: [Table][Columns][Names] User must be able to see the Study Data Supplier Overview table with correct columns
        Given The '/studies' page is opened
        When The 'Study Data Suppliers' submenu is clicked in the 'Manage Study' section
        And The 'List Study Data Supplier' tab is selected
        And A table is visible with following headers
            | headers                  |
            | #                        |
            | Study data supplier type |
            | Data supplier name       |
            | Description              |
            | Library                  |
            | Origin type              |
            | Origin Source            |
            | UI base URL              |
            | API base URL             |
            | Modified                 |
            | Modified by              |

    Scenario: [Create New][Positive case] User must be able to create a new data supplier in Study
        Given The test study '/data-suppliers' page is opened
        And The 'Overview' tab is selected
        When The Edit button is clicked
        Then The Edit Study Data Supplier page is opened
        And User waits for 1 seconds
        When The + button is clicked
        And User clicks ADD USER DEFINED DATA SUPPLIER button
        Then The Add User Defined Data Supplier form is opened
        When I fill in the Name
        And Form save button is clicked
        Then The form is no longer available
        Then The selected Data supplier value is visible in the dropdown
        When The Save button is clicked
        Then The newly added data supplier should be displayed
        When The 'List Study Data Supplier' tab is selected
        And Data supplier is searched and found
        Then The newly added data supplier should be displayed in the table with correct data

    Scenario: [Add Existing one][Positive case] User must be able to add one existing data supplier to the data supplier type
        Given The test study '/data-suppliers' page is opened
        And The 'Overview' tab is selected
        When The Edit button is clicked
        Then The Edit Study Data Supplier page is opened
        And User waits for 1 seconds
        When The + button is clicked
        When I select the value with index 0 from the Data supplier dropdown menu
        Then The selected Data supplier value is visible in the dropdown
        When The Save button is clicked
        Then The newly added data supplier should be displayed
        When The 'List Study Data Supplier' tab is selected
        And Data supplier is searched and found
        Then The newly added data supplier should be displayed in the table with correct data
     
    Scenario: [Remove][Positive case] User must be able to remove the data supplier from data supplier type in study
        Given The test study '/data-suppliers' page is opened
        And The 'Overview' tab is selected
        When The Edit button is clicked
        Then The Edit Study Data Supplier page is opened
        And User waits for 1 seconds
        When The Remove button is clicked for user defined supplier
        Then The selected Data supplier value line is removed from the Supplier data type table
        When The Save button is clicked
        Then The removed data suppliers should not exist in the corresponding Supplier data type table
        When The 'List Study Data Supplier' tab is selected
        Then User defined data supplier is searched and not found

      Scenario: [Add Existing multiple][Positive case] User must be able to add multiple existing data suppliers to the same data supplier type
        Given The test study '/data-suppliers' page is opened
        And The 'Overview' tab is selected
        When The Edit button is clicked
        Then The Edit Study Data Supplier page is opened
        And User waits for 1 seconds
        When The + button is clicked
        When I select the value with index 1 from the Data supplier dropdown menu
        Then The selected Data supplier value is visible in the dropdown
        When The + button is clicked
        When I select the value with index 2 from the Data supplier dropdown menu
        Then The selected Data supplier value is visible in the dropdown
        When The Save button is clicked
        Then Both data suppliers should be displayed on the overview page
        When The 'List Study Data Supplier' tab is selected
        Then Both data suppliers are searched and correct data is displayed in the table
        
    Scenario: [Add Existing][Positive case] User must be able to add same existing data supplier to the different data supplier type
        Given The test study '/data-suppliers' page is opened
        And The 'Overview' tab is selected
        When The Edit button is clicked
        Then The Edit Study Data Supplier page is opened
        And User waits for 1 seconds
        When The + button is clicked
        Then I select the user defined value from the Data supplier dropdown menu
        And Data supplier type is set to 'Lab Data Exchange Files'
        When The + button is clicked
        Then I select the user defined value from the Data supplier dropdown menu
        When The Save button is clicked
        Then The user defined supplier value should be added for 'EDC System'
        And The user defined supplier value should be added for 'Lab Data Exchange Files'
        When The 'List Study Data Supplier' tab is selected
        Then The user defined supplier type should be found in the table for 'EDC System' and 'Lab Data Exchange Files'
