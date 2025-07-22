@REQ_ID:1074260
Feature: Studies - Define Study - Study Activities - Study Activities Placeholder

    Background: User is logged in and study has been selected
        Given The user is logged in

    Scenario: [Update][Positive Case][Shared Activity Request] User must be able to accept changes to activity request copied from other study
        And The '/studies/Study_000001/activities/list' page is opened
        When Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        When Activity placeholder data is filled in
        And Selected study id is saved
        And Form save button is clicked
        And User waits for 3 seconds
        And The '/studies/Study_000002/activities/list' page is opened
        When Study activity add button is clicked
        When Activity from studies is selected
        And Study by id is selected
        And Form continue button is clicked
        And Activity placeholder is searched for
        And The existing activity request is selected
        And Form save button is clicked
        And Activity placeholder is found
        And The 'Edit' option is clicked from the three dot menu list
        And The study activity request is edited
        And Modal window 'Save' button is clicked
        And The form is no longer available
        And The '/studies/Study_000001/activities/list' page is opened
        And Activity placeholder is found
        And The 'Update activity version' option is clicked for flagged item
        And The user is presented with the changes to request
        And Modal window 'Accept' button is clicked
        And The form is no longer available
        Then The activity request changes are applied

    Scenario: [Update][Positive Case][Shared Activity Request] User must be able to decline and keep changes to activity request copied from other study
        And The '/studies/Study_000001/activities/list' page is opened
        When Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        When Activity placeholder data is filled in
        And Selected study id is saved
        And Form save button is clicked
        And The '/studies/Study_000002/activities/list' page is opened
        When Study activity add button is clicked
        When Activity from studies is selected
        And Study by id is selected
        And Form continue button is clicked
        And Activity placeholder is searched for
        And The existing activity request is selected
        And Form save button is clicked
        And Activity placeholder is found
        And The 'Edit' option is clicked from the three dot menu list
        And The study activity request is edited
        And Modal window 'Save' button is clicked
        And The form is no longer available
        And The '/studies/Study_000001/activities/list' page is opened
        And Activity placeholder is found
        And The 'Update activity version' option is clicked for flagged item
        Then The user is presented with the changes to request
        And Modal window 'Decline and keep' button is clicked
        And The form is no longer available
        Then The activity request changes not applied

    Scenario: [Update][Positive Case][Shared Activity Request] User must be able to decline changes and remove activity request copied from other study
        And The '/studies/Study_000001/activities/list' page is opened
        When Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        When Activity placeholder data is filled in
        And Selected study id is saved
        And Form save button is clicked
        And The '/studies/Study_000002/activities/list' page is opened
        When Study activity add button is clicked
        When Activity from studies is selected
        And Study by id is selected
        And Form continue button is clicked
        And Activity placeholder is searched for
        And The existing activity request is selected
        And Form save button is clicked
        And Activity placeholder is found
        And The 'Edit' option is clicked from the three dot menu list
        And The study activity request is edited
        And Modal window 'Save' button is clicked
        And The form is no longer available
        And The '/studies/Study_000001/activities/list' page is opened
        And Activity placeholder is found
        And The 'Update activity version' option is clicked for flagged item
        And The user is presented with the changes to request
        And Modal window 'Decline and remove' button is clicked
        And The form is no longer available
        Then The activity request is removed from the study
