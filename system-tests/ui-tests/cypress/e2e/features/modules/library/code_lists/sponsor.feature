@REQ_ID:1070680
Feature: Library - Code Lists - Sponsor
    As a user, I want to verify that the Code Lists - Sponsor page can be displayed correctly and new sponsor can be added to the Librayr successfully.

    Background: User must be logged in
        Given The user is logged in

@pending_development
    Scenario: [Navigation] User must be able to navigate to the Sponsor page
        Given The '/library' page is opened
        When The 'Sponsor' submenu is clicked in the 'Code Lists' section
        Then The current URL is 'library/sponsor'

@pending_development
    Scenario: [Table][Options] User must be able to see table with correct options
        Given The '/library/sponsor' page is opened
        Then A table is visible with following options
            | options                                                         |
            | Columns                                                         |
            | Export                                                          |
            | Filters                                                         |
            | Add select boxes to table to allow selection of rows for export |
            | search-field                                                    |
           # | search-with-terms                                               | to be implemented
           # | or-field                                                        | to be implemented

@pending_development
    Scenario: [Table][Columns][Names] User must be able to see the columns list on the main page as below
        Given The '/library/sponsor' page is opened
        And A table is visible with following headers
            | headers                     |
            | Library                     |
            | Sponsor preferred name      |
            | Template parameter          |
            | Code list status            |
            | Name modified               |
            | Concept ID                  |
            | Submission value            |
            | Code list name              |
            | NCI Preferred name          |
            | Extensible                  |
            | Attributes status           |
            | Attributes modified         |

