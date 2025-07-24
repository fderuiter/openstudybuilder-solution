@REQ_ID:1074254
Feature: Studies - Define Study - Study Structure - Study Visits - Non Visit

    See shared notes for study visits in file study-visit-intro-notes.txt

    Background: User is logged in and study has been selected
        Given The user is logged in
        When [API] Global anchor term uid is fetched
        Then The study 'Study_000003' has defined epoch

    Scenario: [Create][Non visit] User must be able to create non visit for given study
        Given The '/studies/Study_000003/study_structure/visits' page is opened
        And Epochs for study 'Study_000003' data is loaded
        When The non visit is created
        And The pop up displays 'Visit added'
        Then The non visit is present in the table

    @BUG_ID:2776541
    Scenario: [EDIT][Special visit] User must not be able to edit non visit number
        Given The '/studies/Study_000003/study_structure/visits' page is opened
        When The user opens edit form for non visit 
        Then The visit number field is disabled