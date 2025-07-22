@REQ_ID:1070683

Feature: Library - Concepts - Activities - Activity Overview Page (Version 2)
    As a user, I want to verify that the Activity Overview Page version 2 in the Concepts Library, can display correctly.


    Background: 
        Given The user is logged in
        When [API] Activity Instance in status Final with Final group, subgroup and activity linked exists
        And Group name created through API is found
        And Subgroup name created through API is found
        And Activity name created through API is found
        And Instance name created through API is found

    Scenario: Verify that the activities overview page version 2 displays correctly
        Given The '/library/activities/activities' page is opened
        When I click on the test activity name in the activity page
        Then The test activity overview page should be opened
        And The Activity groupings table will be displayed with correct column
        And The Activity instances table will be displayed with correct column
        And The linked group, subgroup and instance should be displayed in the Activity groupings table
        And The free text search field should be displayed in the Activity groupings table
        And The linked instance should be displayed in the Activity instances table 
        And The free text search field should be displayed in the Activity instances table
        When I click on the arrow beside the linked instance name in the Activitiy instance table
        Then The instance can be expanded to show the different versions of the instance

    Scenario: Verify that the activities overview page version 2 can link to the correct groups, subgroups and instances
        Given The '/library/activities/activities' page is opened
        And I click on the test activity name in the activity page  
        Then The test activity overview page should be opened
        When I select the version '0.1' from the Version dropdown list
        Then The correct End date should be displayed
        And The status should be displayed as 'Draft'
        And The instance in both Activity groupings and Activity instances table should be empty
        When I select the version '1.0' from the Version dropdown list
        Then The linked group, subgroup and instance should be displayed in the Activity groupings table
        Then The instance in the Activity Instances table should be displayed in two lines: version 1.0 and 0.1

@manual_test
    Scenario: Verify that the pagination works in both Activity groupings and Activity instances table
        Given The '/library/activities/activities' page is opened
        When I search for the test activity through the filter field
        And I click on the test activity name in the activity page  
        Then The test activity overview page should be opened
        When I select 5 rows per page from dropdown list in the Activity groupings table
        Then The Activity groupings table should be displayed with 5 rows per page
        When I click on the next page button in the Activity groupings table
        Then The Activity groupings table should display the next page within 5 rows per page
        When I select 10 rows per page from the dropdown list in the Activity instances table
        Then The Activity instances table should be displayed with 10 rows per page
        When I click on the next page button in the Activity instances table
        Then The Activity instances table should display the next page with 10 rows per page

@manual_test
Scenario: Verify that the filter and export functionality work in both Activity groupings and Activity instances table
        Given The '/library/activities/activities' page is opened
        When I search for the test activity through the filter field
        And I click on the test activity name in the activity page  
        Then The test activity overview page should be opened
        And The free text search field works in both Activity groupings and Activity instances table
        And The Export functionality works in both Activity groupings and Activity instances table
        And The Filter functionality works in both Activity groupings and Activity instances table