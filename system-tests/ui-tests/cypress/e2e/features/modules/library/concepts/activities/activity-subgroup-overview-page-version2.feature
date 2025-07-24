@REQ_ID:1070683

Feature: Library - Concepts - Activities - Activity Subgroup Overview Page (Version 2)
    As a user, I want to verify that the Activity Subgroup Overview Page version 2 in the Concepts Library, can display correctly.

    Background: 
        Given The user is logged in
        When [API] Activity Instance in status Final with Final group, subgroup and activity linked exists
        And Group name created through API is found
        And Subgroup name created through API is found
        And Activity name created through API is found

    Scenario: Verify that the activity subgroup overview page version 2 displays correctly
        Given The '/library/activities/activity-subgroups' page is opened
        When I click on the test activity subgroup name in the activity subgroup page
        Then The test subgroup overview page should be opened
        And The Activity group table will be displayed with correct column
        And The Activities table will be displayed with correct column
        And The linked groups should be displayed in the Activity group table
        And The free text search field should be displayed in the Activity group table
        And The linked activities should be displayed in the Activities table
        And The free text search field should be displayed in the Activities table     

    Scenario: Verify that the activities subgroup overview page version 2 can link to the correct subgroup
        Given The '/library/activities/activity-subgroups' page is opened
        When I click on the test activity subgroup name in the activity subgroup page
        Then The test subgroup overview page should be opened
        When I select the version '0.1' from the Version dropdown list
        Then The correct End date should be displayed
        And The status should be displayed as 'Draft'
        And The linked groups should be displayed in the Activity group table
        And The Activities table should be empty
        When I select the version '1.0' from the Version dropdown list
        Then The linked groups should be displayed in the Activity group table
        And The linked activities should be displayed in the Activities table

@manual_test
    Scenario: Verify that the pagination works in both Activity group and Activities table
        Given The '/library/activities/activity-subgroups' page is opened
        When I search for the test activity subgroup through the filter field
        When I click on the test activity subgroup name in the activity subgroup page
        Then The test subgroup overview page should be opened
        When I select 5 rows per page from dropdown list in the Activity group table
        Then The Activity group table should be displayed with 5 rows per page
        When I click on the next page button in the Activity group table
        Then The Activities table should display the next page within 5 rows per page
        When I select 5 rows per page from dropdown list in the Activities table
        Then The Activities table should be displayed with 5 rows per page
        When I click on the next page button in the Activities table
        Then The Activities table should display the next page within 5 rows per page

@manual_test
Scenario: Verify that the filter and export functionality work in both Activity group and Activities table
        Given The '/library/activities/activity-subgroups' page is opened
        When I search for the test activity subgroup through the filter field
        When I click on the test activity subgroup name in the activity subgroup page
        Then The test subgroup overview page should be opened
        And The free text search field works in both Activity group and Activities table
        And The Export functionality works in both Activity group and Activities table
        And The Filter functionality works in both Activity group and Activities table
