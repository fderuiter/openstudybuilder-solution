@REQ_ID:1074254
Feature: Studies - Define Study - Study Structure - Study Visits - Special Visits

    See shared notes for study visits in file study-visit-intro-notes.txt

    Background: User is logged in and study has been selected
        Given The user is logged in
        When [API] Global anchor term uid is fetched
        Then The study 'Study_000003' has defined epoch
        And The study 'Study_000003' has defined visit in that epoch

    Scenario: [Create][Special visit] User must be able to create special visit for given epoch
        Given The '/studies/Study_000003/study_structure/visits' page is opened
        And Epochs for study 'Study_000003' data is loaded
        When The special visit is created within the same epoch
        And The pop up displays 'Visit added'
        Then The special visit is added without timing and with name defined as 'V1A'
        And The special visit is created within the same epoch
        And The pop up displays 'Visit added'
        Then The special visit is added without timing and with name defined as 'V1B'

    Scenario: [Create][Discontinuation visit] User must be able to create discontinuation special visit for given epoch
        Given The '/studies/Study_000003/study_structure/visits' page is opened
        When The discontinuation special visit is created within the same epoch
        Then The special visit is added without timing and with name defined as 'V1X'

    @BUG_ID:2844670
    Scenario: [EDIT][Special visit] User must be able to edit special visit
        Given The '/studies/Study_000003/study_structure/visits' page is opened
        When The user edits the special visit and saves
        Then The special visit is updated correctly