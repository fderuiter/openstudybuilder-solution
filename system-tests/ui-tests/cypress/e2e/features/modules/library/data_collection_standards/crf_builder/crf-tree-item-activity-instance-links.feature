@REQ_ID:3519343

Feature: Library - Data Collection Standards - CRF Builder - CRF Tree - Activity Instance Links

    As a user, I want to manage Activity Instance Links in CRF Tree and view the results in the CRF Viewer within the library's data collection standards

    Background: User must be logged in
        Given The user is logged in
        And The homepage is opened

    Scenario: [Create][Table View][Single Link][CRF Tree Page] User must be able to add one Activity Instance Link to a CRF Item in Table View and verify result in CRF Viewer
        Given The test CRF item is created with no Activity Instance Link
        And The '/library/crf-builder/crf-tree' page is opened
        When I click the expand button beside created test Collection to expand the CRF Tree
        And I click the expand button beside created test Form form to expand the form
        And I click the expand button beside created test Item Group to expand the item group
        Then I can see the Created test CRF Item in the list
        When The 'Manage Activity Instance Links' option is clicked from the three dot menu list of the created test CRF item
        Then The Edit Item page is opened
        And The default page is Table View
        When I select a value from the Select an Activity Instance dropdown list
        And I select a value from the Activity Item Class table
        And The 'save-button' button is clicked
        Then The Edit Item window is closed
        When The '/library/crf-builder/odm-viewer' page is opened
        When I select created Form from the Form Name dropdown list
        And I click the GENERATE button
        Then The imported CRF view page should be displayed
        When I click the Activity Instance option from the right top corner
        Then The added Activity Instance Link is displayed under the test item name
   
    Scenario: [Create][Table View][Multiple Links][CRF Tree Page] User must be able to add multiple Activity Instance Links to a CRF Item in Table View and verify result in CRF Viewer
        Given The test CRF item is created with no Activity Instance Link
        And The '/library/crf-builder/crf-tree' page is opened
        When I click the expand button beside created test Collection to expand the CRF Tree
        And I click the expand button beside created test Form form to expand the form
        And I click the expand button beside created test Item Group to expand the item group
        Then I can see the Created test CRF Item in the list
        When The 'Manage Activity Instance Links' option is clicked from the three dot menu list of the created test CRF item
        Then The Edit Item page is opened
        And The default page is Table View
        When I select a value from the Select an Activity Instance dropdown list
        And I select a value from the Activity Item Class table
        And I select another value from the Select an Activity Instance dropdown list
        And I select a value from the Activity Item Class table
        And The 'save-button' button is clicked
        Then The Edit Item window is closed
        And The current URL is '/library/crf-builder/crf-tree'
        When The '/library/crf-builder/odm-viewer' page is opened
        When I select created Form from the Form Name dropdown list
        And I click the GENERATE button
        Then The imported CRF view page should be displayed
        When I click the Activity Instance option from the right top corner
        Then The added two Activity Instance Links are displayed under the test item name

    Scenario: [Create][Form View][CRF Tree Page] User must be able to add Activity Instance Links in Form View and verify result in CRF Viewer
        Given The test CRF item is created with no Activity Instance Link
        And The '/library/crf-builder/crf-tree' page is opened
        When I click the expand button beside created test Collection to expand the CRF Tree
        And I click the expand button beside created test Form form to expand the form
        And I click the expand button beside created test Item Group to expand the item group
        Then I can see the Created test CRF Item in the list
        When The 'Manage Activity Instance Links' option is clicked from the three dot menu list of the created test CRF item
        Then The Edit Item page is opened
        And The default page is Table View
        When I select the Form View option
        Then The page is switched to Form View
        When I click the Activity Instance Link plus button
        Then Activity Instance Item 1 table is visible
        When I select a value from the Activity Instance dropdown list
        And I select a value from the Activity Item Class dropdown list
        And The 'save-button' button is clicked 
        Then The Edit Item window is closed
        And The current URL is '/library/crf-builder/crf-tree'
        When The '/library/crf-builder/odm-viewer' page is opened
        When I select created Form from the Form Name dropdown list
        And I click the GENERATE button
        Then The imported CRF view page should be displayed
        When I click the Activity Instance option from the right top corner
        Then The added Activity Instance Link is displayed under the test item name

 @manual_test
    Scenario: [Mandatory Field Validation][CRF Tree Page] User must select both Activity Instance and Activity Item Class to save Activity Instance Link
        Given The test CRF item is created with no Activity Instance Link
        And The '/library/crf-builder/crf-tree' page is opened
        When I click the expand button beside created test Collection to expand the CRF Tree
        And I click the expand button beside created test Form form to expand the form
        And I click the expand button beside created test Item Group to expand the item group
        Then I can see the Created test CRF Item in the list
        When The 'Manage Activity Instance Links' option is clicked from the three dot menu list of the created test CRF item
        Then The Edit Item page is opened
        And The default page is Table View
        When I select a value from the Activity Instance dropdown list
        And I do not select a value from the Activity Item Class dropdown list
        And The 'save-button' button is clicked
        Then I should see a validation message for the Activity Item Class dropdown list indicating that selection is required
        And The Edit Item window remains open
        When I switch to the Form View
        Then I can see no linked Activity Item Class in the Form View
