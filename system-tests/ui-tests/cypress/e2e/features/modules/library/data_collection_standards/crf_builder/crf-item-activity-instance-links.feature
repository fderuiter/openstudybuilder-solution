@REQ_ID:3519343

Feature: Library - Data Collection Standards - CRF Builder - CRF Items - Activity Instance Links

    As a user, I want to manage Activity Instance Links in CRF Items and view the results in the CRF Viewer within the library's data collection standards

    Background: User must be logged in
        Given The user is logged in
        And The homepage is opened

    Scenario: [Create][Form View][Single Link][CRF Item Page] User must be able to add one Activity Instance Link to a CRF Item in Form View and verify result in CRF Viewer
        Given The test CRF item is created with no Activity Instance Link
        And The '/library/crf-builder/items' page is opened
        And User waits for CRF Items data to load
        And Created test CRF Item is found
        When The 'Manage Activity Instance Links' option is clicked from the three dot menu list
        Then The Edit Item page is opened and RESET button is disabled
        And No Activity Instance Links text is visible
        And The default page is Form View
        When I click the Activity Instance Link plus button
        Then Activity Instance Item 1 table is visible
        When User waits for Activity Instance dropdown to load
        And I select a value from the Activity Instance dropdown list
        And User waits for Activity Item Class dropdown to load
        And I select a value from the Activity Item Class dropdown list
        Then The RESET button is enabled
        When The 'save-button' button is clicked
        Then The Edit Item window is closed
        And The current URL is '/library/crf-builder/items'
        When The '/library/crf-builder/odm-viewer' page is opened
        When I select created Form from the Form Name dropdown list
        And I click the GENERATE button
        Then The imported CRF view page should be displayed
        When I click the Activity Instance option from the right top corner
        Then The added Activity Instance Link is displayed under the test item name

    Scenario: [Create][Form View][Multiple Links][CRF Item Page] User must be able to add multiple Activity Instance Links to a CRF Item in Form View and verify result in CRF Viewer
        Given The test CRF item is created with no Activity Instance Link
        And The '/library/crf-builder/items' page is opened
        And User waits for CRF Items data to load
        And Created test CRF Item is found
        When The 'Manage Activity Instance Links' option is clicked from the three dot menu list
        When I click the Activity Instance Link plus button
        Then Activity Instance Item 1 table is visible
        When User waits for Activity Instance dropdown to load
        And I select a value from the Activity Instance dropdown list
        And User waits for Activity Item Class dropdown to load
        And I select a value from the Activity Item Class dropdown list
        When I click the Activity Instance Link plus button
        Then Activity Instance Item 2 table is visible
        When I select a value from the second Activity Instance dropdown list
        And I select a value from the second Activity Item Class dropdown list
        When The 'save-button' button is clicked
        Then The Edit Item window is closed
        And The current URL is '/library/crf-builder/items'
        When The '/library/crf-builder/odm-viewer' page is opened
        When I select created Form from the Form Name dropdown list
        And I click the GENERATE button
        Then The imported CRF view page should be displayed
        When I click the Activity Instance option from the right top corner
        Then All added Activity Instance Links are displayed under the test item name

    Scenario: [Create][Table View][Single Link][CRF Item Page] User must be able to add Activity Instance Links in Table View and verify result in CRF Viewer
        Given The test CRF item is created with no Activity Instance Link
        And The '/library/crf-builder/items' page is opened
        And User waits for CRF Items data to load
        And Created test CRF Item is found
        When The 'Manage Activity Instance Links' option is clicked from the three dot menu list
        Then The Edit Item page is opened and RESET button is disabled
        And The default page is Form View
        When I select the Table View option
        Then The page is switched to Table View
        When I select a value from the Select an Activity Instance dropdown list
        And I select an Activity Item Class from the table
        And The 'save-button' button is clicked
        Then The Edit Item window is closed
        And The current URL is '/library/crf-builder/items'
        When The '/library/crf-builder/odm-viewer' page is opened
        When I select created Form from the Form Name dropdown list
        And I click the GENERATE button
        Then The imported CRF view page should be displayed
        When I click the Activity Instance option from the right top corner
        Then The added Activity Instance Link is displayed under the test item name

    Scenario: [Mandatory Field Validation][Form View][CRF Item Page] User must select both Activity Instance and Activity Item Class to save Activity Instance Link
        Given The test CRF item is created with no Activity Instance Link
        And The '/library/crf-builder/items' page is opened
        And User waits for CRF Items data to load
        And Created test CRF Item is found
        When The 'Manage Activity Instance Links' option is clicked from the three dot menu list
        Then The Edit Item page is opened and RESET button is disabled
        When I click the Activity Instance Link plus button
        Then Activity Instance Item 1 table is visible
        And I am not able to select a value from the Activity Item Class dropdown list before I have selected a value from the Activity Instance dropdown list
        When The 'save-button' button is clicked
        Then I should see alert messages for both Activity Instance and Activity Item Class fields
        When I select a value from the Activity Instance dropdown list and do not select any value from the Activity Item Class dropdown list
        Then I should see a field validation message for the Activity Item Class dropdown list
        When The 'save-button' button is clicked
        Then I should see an alert message for the Activity Item Class field

    Scenario: [Delete][Form View][CRF Item Page] User must be able to delete Activity Instance Link from a CRF Item in Form View and verify result in CRF Viewer
        Given The test CRF item is created with no Activity Instance Link
        And The '/library/crf-builder/items' page is opened
        And User waits for CRF Items data to load
        And Created test CRF Item is found
        When The 'Manage Activity Instance Links' option is clicked from the three dot menu list
        Then The Edit Item page is opened and RESET button is disabled
        When I click the Activity Instance Link plus button
        Then Activity Instance Item 1 table is visible
        And The Delete button is visible
        When I click the Delete button
        Then The page returns to the initial edit item page without Activity Instance Item table
        When I click the Activity Instance Link plus button
        Then Activity Instance Item 1 table is visible
        When I select a value from the Activity Instance dropdown list
        And I select a value from the Activity Item Class dropdown list
        And The 'save-button' button is clicked
        Then The Edit Item window is closed
        And The current URL is '/library/crf-builder/items'
        When The 'Manage Activity Instance Links' option is clicked from the three dot menu list
        Then The Edit Item page is opened with saved linked Activity Instance Item table
        When I click the Delete button
        Then The page returns to the initial edit item page and the RESET button is enabled
        When The 'save-button' button is clicked
        Then The Edit Item window is closed
        And The current URL is '/library/crf-builder/items'
        When The 'Manage Activity Instance Links' option is clicked from the three dot menu list
        Then The Edit Item page is opened without any linked Activity Instance Item table

   @manual_test
    Scenario: [Reset][Form View][CRF Item Page] User must be able to reset Activity Instance Link from a CRF Item and verify page state
        Given The test CRF item is created with no Activity Instance Link
        And The '/library/crf-builder/items' page is opened
        And User waits for CRF Items data to load
        And Created test CRF Item is found
        When The 'Manage Activity Instance Links' option is clicked from the three dot menu list
        Then The Edit Item page is opened and RESET button is disabled
        And No Activity Instance Links text is visible
        And The default page is Form View
        When I click the Activity Instance Link plus button
        Then Activity Instance Item 1 table is visible
        When User waits for Activity Instance dropdown to load
        And I select a value from the Activity Instance dropdown list
        And User waits for Activity Item Class dropdown to load
        And I select a value from the Activity Item Class dropdown list
        Then The RESET button is enabled
        When I click the RESET button
        Then The Activity Instance Item table is removed and the page returns to the initial edit item page

