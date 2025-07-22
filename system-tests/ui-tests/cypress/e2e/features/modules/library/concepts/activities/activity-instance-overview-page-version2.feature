@REQ_ID:1070683

Feature: Library - Concepts - Activities - Activity Instance Overview Page (Version 2)
    As a user, I want to verify that the Activity Instance Overview Page version 2 in the Concepts Library, can display correctly.

    Background: 
        Given The user is logged in
        When [API] Activity Instance in status Final with Final group, subgroup and activity linked exists
        And Group name created through API is found
        And Subgroup name created through API is found
        And Activity name created through API is found
        And Instance name created through API is found

    Scenario: Verify that the activities instance overview page version 2 displays correctly
        Given The '/library/activities/activity-instances' page is opened
        When I click on the link for the test instance name in the instance page
        Then The test instance overview page should be opened
        And The Activity groupings table in the instance overview page is displayed with correct column
        And The Activity items table is displayed with correct column
        And The linked group, subgroup and activity should be displayed in the Activity groupings table
        And The free text search field displays in the Activity groupings table
        And The free text search field displays in the Activity items table


    Scenario: Verify that the activities instance overview page version 2 can link to the correct groups, subgroups and activities
        Given The '/library/activities/activity-instances' page is opened
        When I click on the link for the test instance name in the instance page
        Then The test instance overview page should be opened
        When I select the version '0.1' from the Version dropdown list
        Then The correct End date should be displayed
        And The status should be displayed as 'Draft'
        And Both Activity groupings and Activity items table should be empty
        When I select the version '1.0' from the Version dropdown list
        Then The linked group, subgroup and activity should be displayed in the Activity groupings table

@pending_development
    Scenario: Verify that the pagination works in both Activity groupings and Activity items table
        Given The '/library/activities/activity-instances' page is opened
        When I search for the test instance through the filter field
        And I click on the link for the test instance name in the instance page  
        Then The test instance overview page should be opened
        When I select 5 rows per page from dropdown list in the Activity groupings table
        Then The Activity groupings table should be displayed with 5 rows per page
        When I click on the next page button in the Activity groupings table
        Then The Activity grouping table should display the next page within 5 rows per page
        When I select 5 rows per page from dropdown list in the Activity items table
        Then The Activity items table should be displayed with 5 rows per page
        When I click on the next page button in the Activity items table
        Then The Activity items table should display the next page within 5 rows per page

@manual_test
Scenario: Verify that the filter and export functionality work in both Activity groupings and Activity items table
        Given The '/library/activities/activity-instances' page is opened
        When I search for the test instance through the filter field
        And I click on the link for the test instance name in the instance page  
        Then The test instance overview page should be opened
        And The free text search field works in both Activity groupings and Activity items table
        And The Export functionality works in both Activity groupings and Activity items table
        And The Filter functionality works in both Activity groupings and Activity items table