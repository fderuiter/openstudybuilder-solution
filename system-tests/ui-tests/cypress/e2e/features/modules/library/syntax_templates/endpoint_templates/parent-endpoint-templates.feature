@REQ_ID:1070684
Feature: Library - Syntax Templates - Endpoints - Parent

    As a user, I want to manage every Endpoint template under the Syntax Template Library
    Background: User must be logged in
        Given The user is logged in

    Scenario: [Navigation] User must be able to navigate to the Endpoint template under the Syntax template Library
        Given The '/library' page is opened
        When The 'Endpoints' submenu is clicked in the 'Syntax Templates' section
        Then The current URL is '/library/endpoint_templates'

    Scenario: [Table][Columns][Names] User must be able to see the table with correct columns
        Given The '/library/endpoint_templates' page is opened
        And A table is visible with following headers
            | headers         |
            | Sequence number |
            | Parent template |
            | Modified        |
            | Status          |
            | Version         |

    Scenario: [Table][Columns][Visibility] User must be able to select visibility of columns in the table 
        Given The '/library/endpoint_templates' page is opened
        When The first column is selected from Select Columns option for table with actions
        Then The table contain only selected column and actions column

    Scenario: [Create][Sequence number] System must generate sequence number for Endpoint Templates when they are created
        Given The 'library/endpoint_templates' page is opened
        And [API] Create endpoint template
        And The endpoint template is found
        When The latest sequence number is saved
        And [API] Create endpoint template
        And The endpoint template is found
        Then Sequence number is incremented

    # If approval is for version +1.0 and any instantiations exist then a cascade update and approval is needed
    @pending_implementation
    Scenario: Template Instantiations must be update when parent template has been updated
        Given The test Endpoint Parent Template exists with a status as 'Draft'
        When The'Approve' option is clicked from the three dot menu list
        Then all related endpoint template instantiations must be cascade updated to new version and approved
        And the displayed pop-up snack must include information on number of updated endpoint template instantiations

    Scenario: [Create][Positive case] User must be able to create Endpoint template
        Given The 'library/endpoint_templates' page is opened
        And The Add template button is clicked
        When The endpoint template form is filled with base data
        And Template indexes are set for 'endpoint'
        And Form save button is clicked
        And The endpoint template is found
        Then The item has status 'Draft' and version '0.1'
        And The endpoint template name is displayed in the table

    Scenario: [Create][N/A indexes] User must be able to create Endpoint template with NA indexes
        Given The 'library/endpoint_templates' page is opened
        And The Add template button is clicked
        When The endpoint template form is filled with base data
        And Indexes are set as not applicable
        And Form save button is clicked
        And The pop up displays 'Endpoint template added'
        And The endpoint template is found
        And The item has status 'Draft' and version '0.1'
        And The 'Edit' option is clicked from the three dot menu list
        And User goes to Index template step
        Then The template has not applicable selected for all indexes

    Scenario: [Actions][Edit][0.1 version] User must be able to edit initial version of the Endpoint template
        Given The 'library/endpoint_templates' page is opened
        And [API] Create endpoint template
        And The endpoint template is found
        When The 'Edit' option is clicked from the three dot menu list
        And The endpoint metadata update is started
        And Template indexes are cleared and updated for 'endpoint'
        And Form continue button is clicked
        And Template change description is provided
        And Form save button is clicked
        And The pop up displays 'Endpoint template updated'
        And The endpoint template is found
        Then The item has status 'Draft' and version '0.2'
        And The 'Edit' option is clicked from the three dot menu list
        And The endpoint template name is checked
        And User goes to Index template step
        Then Template indexes are verified

    Scenario: [Create][Mandatory fields] User must not be able to create Endpoint template without: Template Text
        Given The 'library/endpoint_templates' page is opened
        And The Add template button is clicked
        When The Template is added without template text
        Then The validation appears for Template name
        And The form is not closed

    Scenario: [Create][Mandatory fields] User must not be able to create Endpoint template with not unique Template Text
        Given The 'library/endpoint_templates' page is opened
        And [API] Create endpoint template
        And The Add template button is clicked
        And The endpoint template form is filled with already existing name
        And Indexes are set as not applicable
        And Form save button is clicked
        Then The pop up displays 'already exists'
        And The form is not closed

    Scenario: [Create][Mandatory fields] User must not be able to create Endpoint template without: Indication or Disorder
        Given The 'library/endpoint_templates' page is opened
        And The Add template button is clicked
        And The endpoint template form is filled with base data
        When Template indexes are set for 'endpoint'
        And Indication or Disorder index is cleared
        And Form save button is clicked
        Then The validation appears for Indication or Disorder field
        And The form is not closed

    Scenario: [Create][Mandatory fields] User must not be able to create Endpoint template without: Endpoint Category
        Given The 'library/endpoint_templates' page is opened
        And The Add template button is clicked
        And The endpoint template form is filled with base data
        When Template indexes are set for 'endpoint'
        And Category index is cleared for 'endpoint' template
        And Form save button is clicked
        Then The validation appears for 'endpoint' template category field
        And The form is not closed

    Scenario: [Create][Mandatory fields] User must not be able to create Endpoint template without: Endpoint Subcategory
        Given The 'library/endpoint_templates' page is opened
        And The Add template button is clicked
        And The endpoint template form is filled with base data
        When Template indexes are set for 'endpoint'
        And Subcategory index is cleared for 'endpoint' template
        And Form save button is clicked
        Then The validation appears for 'endpoint' template subcategory field
        And The form is not closed

    Scenario: [Create][Syntax validation] User must be able to verify syntax when creating Endpoint template
        Given The 'library/endpoint_templates' page is opened
        And The Add template button is clicked
        When The new template name is prepared with a parameters
        And The syntax is verified
        Then The pop up displays "This syntax is valid"

    Scenario: [Create][Hide parameters] User must be able to hide parameter of the Endpoint template
        Given The 'library/endpoint_templates' page is opened
        And The Add template button is clicked
        When The new template name is prepared with a parameters
        And Form continue button is clicked
        And The user hides the parameter in the next step
        Then The parameter is not visible in the text representation

    Scenario: [Create][Select parameter] User must be able to select parameter of the Endpoint template
        Given The 'library/endpoint_templates' page is opened
        And The Add template button is clicked
        When The new template name is prepared with a parameters
        And Form continue button is clicked
        And The user picks the parameter from the dropdown list
        Then The parameter value is visible in the text representation

    Scenario: [Actions][Delete] User must be able to delete the Draft Endpoint template in version below 1.0
        Given The 'library/endpoint_templates' page is opened
        And [API] Create endpoint template
        And The endpoint template is found
        When The 'Delete' option is clicked from the three dot menu list
        Then The pop up displays "Endpoint template has been deleted"
        And The endpoint template is not found

    Scenario: [Actions][Approve] User must be able to approve the Draft Endpoint template
        Given The 'library/endpoint_templates' page is opened
        And [API] Create endpoint template
        And The endpoint template is found
        When The 'Approve' option is clicked from the three dot menu list
        Then The pop up displays 'Template is now in Final state'
        And The item has status 'Final' and version '1.0'

    Scenario: [Actions][Edit indexing] User must be able to edit indexing of Final Endpoint template
        Given The 'library/endpoint_templates' page is opened
        And [API] Create endpoint template
        And [API] Approve endpoint template
        And The endpoint template is found
        When The 'Edit indexing' option is clicked from the three dot menu list
        And Template indexes are updated for 'endpoint'
        And Form save button is clicked
        And The pop up displays 'Indexing properties updated'
        And The endpoint template is found
        And The 'Edit indexing' option is clicked from the three dot menu list
        Then Template indexes are verified

    Scenario: [Actions][Edit][Mandatory fields] User must not be able to save changes to Endpoint template without: Change description
        Given The 'library/endpoint_templates' page is opened
        And [API] Create endpoint template
        And The endpoint template is found
        When The 'Edit' option is clicked from the three dot menu list
        And User goes to Change description step
        When The template change description is cleared
        And Form save button is clicked
        Then The validation appears for change description field
        And The form is not closed

    Scenario: [Actions][New version] User must be able to add a new version of the Final Endpoint template
        Given The 'library/endpoint_templates' page is opened
        And [API] Create endpoint template
        And [API] Approve endpoint template
        And The endpoint template is found
        When The 'New version' option is clicked from the three dot menu list
        Then The pop up displays 'New version created'
        And The item has status 'Draft' and version '1.1'

    Scenario: [Actions][Edit][1.1 version] User must be able to edit new version of the Endpoint template
        Given The 'library/endpoint_templates' page is opened
        And [API] Create endpoint template
        And [API] Approve endpoint template
        And The endpoint template is found
        When The 'New version' option is clicked from the three dot menu list
        Then The item has status 'Draft' and version '1.1'
        When The 'Edit' option is clicked from the three dot menu list
        And The endpoint metadata update is started
        And Template indexes are cleared and updated for 'endpoint'
        And Form continue button is clicked
        And Template change description is provided
        And Form save button is clicked
        And The pop up displays 'Endpoint template updated'
        And The endpoint template is found
        Then The item has status 'Draft' and version '1.2'
        When The 'Approve' option is clicked from the three dot menu list
        Then The item has status 'Final' and version '2.0'

    Scenario: [Actions][Inactivate] User must be able to inactivate the Final Endpoint template
        Given The 'library/endpoint_templates' page is opened
        And [API] Create endpoint template
        And [API] Approve endpoint template
        And The endpoint template is found
        When The 'Inactivate' option is clicked from the three dot menu list
        Then The pop up displays 'Template inactivated'
        And The item has status 'Retired' and version '1.0'

    Scenario: [Actions][Reactivate] User must be able to reactivate the Retired Endpoint template
        Given The 'library/endpoint_templates' page is opened
        And [API] Create endpoint template
        And [API] Approve endpoint template
        And [API] Endpoint template is inactivated
        And The endpoint template is found
        When The 'Reactivate' option is clicked from the three dot menu list
        Then The pop up displays 'Template is now in Final state'
        And The item has status 'Final' and version '1.0'

    @manual_test
    Scenario: User must be able to view the history for the Endpoint template with a status as 'Retired'
        Given The 'library/endpoint_templates' page is opened
        And [API] Create endpoint template
        And [API] Approve endpoint template
        And [API] Endpoint template is inactivated
        And The endpoint template is found
        When The 'Reactivate' option is clicked from the three dot menu list
        Then The 'History for template' window is displayed with the following column list with values
            | Column | Header                 |
            | 1      | Indication or disorder |
            | 2      | Criterion category     |
            | 3      | Criterion sub-category |
            | 4      | Template               |
            | 5      | Guidance text          |
            | 6      | Status                 |
            | 7      | Version                |
            | 8      | Change type            |
            | 9      | User                   |
            | 10     | From                   |
            | 11     | To                     |

    @manual_test
    Scenario: User must be able to read change history of output
        Given The 'library/endpoint_templates' page is opened
        When The user opens version history
        Then The user is presented with version history of the output containing timestamp and username

    @manual_test
    Scenario: User must be able to read change history of selected element
        Given The 'library/endpoint_templates' page is opened
        And The 'Show history' option is clicked from the three dot menu list
        When The user clicks on History for particular element
        Then The user is presented with history of changes for that element
        And The history contains timestamps and usernames

    Scenario: [Cancel][Creation] User must be able to Cancel creation of the Endpoint template
        Given The 'library/endpoint_templates' page is opened
        And The Add template button is clicked
        And The endpoint template form is filled with base data
        And Indexes are set as not applicable
        When Fullscreen wizard is closed by clicking cancel button
        And Action is confirmed by clicking continue
        Then The form is no longer available
        And The endpoint template is not found

    Scenario: [Cancel][Edition] User must be able to Cancel edition of the Endpoint template
        Given The 'library/endpoint_templates' page is opened
        And [API] Create endpoint template
        And The endpoint template is found
        When The 'Edit' option is clicked from the three dot menu list
        When The endpoint template edition form is filled with data
        And Fullscreen wizard is closed by clicking cancel button
        And Action is confirmed by clicking continue
        Then The form is no longer available
        And The endpoint template is not updated

    Scenario: [Cancel][Indexing edition] User must be able to Cancel indexes edition of the Endpoint template
        Given The 'library/endpoint_templates' page is opened
        And [API] Create endpoint template
        And [API] Approve endpoint template
        And The endpoint template is found
        When The 'Edit indexing' option is clicked from the three dot menu list
        When The indication indexes edition is initiated
        And Modal window form is closed by clicking cancel button
        Then The form is no longer available
        When The 'Edit indexing' option is clicked from the three dot menu list
        And The indexes are not updated

    Scenario: [Actions][Availability][Draft item] User must only have access to aprove, edit, delete, history actions for Drafted version of the Endpoint template
        Given The 'library/endpoint_templates' page is opened
        And [API] Create endpoint template
        And The endpoint template is found
        When The item actions button is clicked
        Then Only actions that should be avaiable for the Draft item are displayed

    Scenario: [Actions][Availability][Final item] User must only have access to: new version, inactivate, history actions for Final version of the Endpoint template
        Given The 'library/endpoint_templates' page is opened
        And [API] Create endpoint template
        And [API] Approve endpoint template
        And The endpoint template is found
        When The item actions button is clicked
        Then Only actions that should be avaiable for the Final item are displayed

    Scenario: [Actions][Availability][Final item] User must have access to edit indexing, create pre-instantiation actions for Final version of the Endpoint template
        Given The 'library/endpoint_templates' page is opened
        And [API] Create endpoint template
        And [API] Approve endpoint template
        And The endpoint template is found
        When The item actions button is clicked
        Then 'Edit indexing' action is available
        And 'Create pre-instantiation' action is available

    Scenario: [Actions][Availability][Retired item] User must only have access to reactivate, history actions for Retired version of the Endpoint template
        Given The 'library/endpoint_templates' page is opened
        And [API] Create endpoint template
        And [API] Approve endpoint template
        And [API] Endpoint template is inactivated
        And The endpoint template is found
        And The item actions button is clicked
        Then Only actions that should be avaiable for the Retired item are displayed

    Scenario: [Table][Search][Postive case] User must be able to search created Endpoint template
        Given The 'library/endpoint_templates' page is opened
        When [API] Search Test - Create first endpoint template
        And [API] Search Test - Create second endpoint template
        Then The endpoint template is found
        And The existing item is searched for by partial name
        Then More than one result is found 

    Scenario: [Table][Search][Negative case] User must be able to search not existing endpoint and table will correctly filtered
        Given The 'library/endpoint_templates' page is opened
        When The not existing item is searched for
        Then The item is not found and table is correctly filtered

    Scenario: [Table][Search][Case sensitivity] User must be able to search item ignoring case sensitivity
        Given The 'library/endpoint_templates' page is opened
        When The existing item in search by lowercased name
        And More than one result is found

    Scenario: [Table][Search][Filtering] User must be able to combine search and filters to narrow table results
        Given The 'library/endpoint_templates' page is opened
        When The user adds status to filters
        And The user changes status filter value to 'Final'
        And The existing item is searched for by partial name
        And The item is not found and table is correctly filtered
        And The user changes status filter value to 'Draft'
        And The existing item is searched for by partial name
        Then More than one result is found

    Scenario Outline: [Table][Filtering] User must be able to filter the table by text fields
        Given The 'library/endpoint_templates' page is opened
        When The user filters field '<name>'
        Then The table is filtered correctly

        Examples:
            | name                  |
            | Indication or disorder |
            | Endpoint category     |
            | Endpoint sub-category |

    Scenario: [Table][Pagination] User must be able to use table pagination        
        Given The '/library/endpoint_templates' page is opened
        When The user switches pages of the table
        Then The table page presents correct data