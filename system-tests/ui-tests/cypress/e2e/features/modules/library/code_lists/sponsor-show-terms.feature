@REQ_ID:1070679
Feature: Library - Code Lists - Sponsor - Show Terms
    As a user, I want to verify that the Sponsor - Show Terms page can be displayed correctly and new terms can be added to the selected sponsor successfully.

    Background: User must be logged in
        Given The user is logged in

@pending_development
    Scenario: [Table][Options] User must be able to see table with correct options 
        Given The '/library/sponsor' page is opened
        When The 'Show terms' option is clicked from the three dot menu list
        Then The 'Terms listing' page is shown
        Then A table is visible with following options
            | options                                                         |
            | Columns                                                         |
            | Export                                                          |
            | Filters                                                         |
            | Add select boxes to table to allow selection of rows for export |
            | search-field                                                    |
            # | show-removed-terms                                            | to be implemented

@pending_development
    Scenario: [Table][Columns][Names] User must be able to see the columns list on the main page as below
        Given The '/library/sponsor' page is opened
        When The 'Show terms' option is clicked from the three dot menu list
        Then The 'Terms listing' page is shown
        And A table is visible with following headers
            | headers                     |
            | Order                       |
            | Submission value            |
            | Added date                  |
            | Removed date                |
            | Library                     |
            | Sponsor name                |
            | Name status                 |
            | Name date                   |
            | Concept ID                  |
            | NCI Preferred name          |
            | Definition                  |
            | Attributes status           |
            | Attributes date             |

@pending_development
    Scenario: [Table][Pagination] User must be able to use table pagination
        Given The '/library/sponsor' page is opened
        When The user switches pages of the table
        Then The table page presents correct data

@pending_development
    Scenario: User must be able to add existed terms to the selected sponsor
        Given The '/library/sponsor' page is opened
        When Click 'show terms' option from the three dot menu list for a selected sponsor
        Then The 'Code List Summary' page is opened
        When The user clicks on the 'Add term' button
        Then The Add term page is opened
        And The default selection is 'Select an existing one'
        When The user clicks on the 'CONTINUE' button
        Then The 'Select an existing term' page is opened
        When The user selects a term from the list
        And The user clicks on the 'CONTINUE' button
        Then The 'Enter term order and submission value' page is opened
        When The user fills in Submission value and Order fields
        And The user clicks on the 'SAVE' button
        Then The new added term is displayed in the table successfully

@pending_development
    Scenario: User must give a unique submission value for the newly added term
        Given The '/library/sponsor' page is opened
        When Click 'show terms' option from the three dot menu list for a selected sponsor
        Then The 'Code List Summary' page is opened
        When The user clicks on the 'Add term' button
        Then The Add term page is opened
        And The default selection is 'Select an existing one'
        When The user clicks on the 'CONTINUE' button
        Then The 'Select an existing term' page is opened
        When The user selects a term from the list
        And The user clicks on the 'CONTINUE' button
        Then The 'Enter term order and submission value' page is opened
        When The user fills in the Submission value field with a value that already exists in the table
        Then An error message is displayed indicating that the submission value already exists

@pending_development
     Scenario: User must be able to add new terms to the selected sponsor
        Given The '/library/sponsor' page is opened
        When Click 'show terms' option from the three dot menu list for a selected sponsor
        Then The 'Code List Summary' page is opened
        When The user clicks on the 'Add term' button
        Then The Add term page is opened
        When The user select 'Create a new one'
        When The user clicks on the 'CONTINUE' button
        Then The 'Manage sponsor term preferred name' page is opened
        When The user fills in the 'Sponsor preferred name' field
        And The user click on the 'Sponsor sentence case name' field
        Then The 'Sponsor sentence case name' field is filled automatically by the small letters of the 'Sponsor preferred name' field
        When The user clicks on the 'CONTINUE' button
        Then The 'Manage term attribute values' page is opened
        When The user fills in NCI preferred name and Definition fields
        And The user clicks on the 'CONTINUE' button
        Then The 'Enter term order and submission value' page is opened
        When The user fills in Submission value and Order fields
        And The user clicks on the 'SAVE' button
        Then The Term Detail page is opened
        And All the filled fields of Term are displayed correctly

@pending_development
    Scenario: User must enter an integer value in the Order field for the newly added term
        Given The '/library/sponsor' page is opened
        When Click 'show terms' option from the three dot menu list for a selected sponsor
        Then The 'Code List Summary' page is opened
        When The user clicks on the 'Add term' button
        Then The Add term page is opened
        When The user select 'Create a new one'
        When The user clicks on the 'CONTINUE' button
        Then The 'Manage sponsor term preferred name' page is opened
        When The user fills in the 'Sponsor preferred name' field
        And The user click on the 'Sponsor sentence case name' field
        Then The 'Sponsor sentence case name' field is filled automatically by the small letters of the 'Sponsor preferred name' field
        When The user clicks on the 'CONTINUE' button
        Then The 'Manage term attribute values' page is opened
        When The user fills in NCI preferred name and Definition fields
        And The user clicks on the 'CONTINUE' button
        Then The 'Enter term order and submission value' page is opened
        When The user fills in correct Submission value
        And The user fills in the Order field with a non-integer value
        Then An error message is displayed indicating that the Order field must be an integer

   @pending_development
    Scenario: Verify all the mandatory fields are required when adding a new term to the sponsor
        Given The '/library/sponsor' page is opened
        When Click 'show terms' option from the three dot menu list for a selected sponsor
        Then The 'Code List Summary' page is opened
        When The user clicks on the 'Add term' button
        Then The Add term page is opened
        When The user select 'Create a new one'
        When The user clicks on the 'CONTINUE' button
        Then The 'Manage sponsor term preferred name' page is opened
        When The user clicks on the 'CONTINUE' button
        Then An error message is displayed indicating that the 'Sponsor preferred name' field is required
        When The user fills in the 'Sponsor preferred name' field
        And The user clicks on the 'CONTINUE' button
        Then The 'Manage term attribute values' page is opened
        When The user clicks on the 'CONTINUE' button
        Then An error message is displayed indicating that the 'NCI preferred name' field is required
        And An error message is displayed indicating that the 'Definition' field is required
        When The user fills in NCI preferred name and Definition fields
        And The user clicks on the 'CONTINUE' button
        Then The 'Enter term order and submission value' page is opened
        When The user fills in Submission value and Order fields
        When The user clicks on the 'SAVE' button
        Then The error message is displayed indicating that the 'Submission value' field is required
        And The error message is displayed indicating that the 'Order' field is required