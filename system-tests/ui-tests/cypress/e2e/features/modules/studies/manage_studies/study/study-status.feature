@REQ_ID:1741028
Feature: Studies - Manage Study - Study Status

    Background: User must be logged in
        Given The user is logged in

    @smoke_test
    Scenario: [Navigation] User must be able to navigate to the Study Status page
        Given A test study is selected
        Given The '/studies' page is opened
        When The 'Study' submenu is clicked in the 'Manage Study' section
        And The 'Study Status' tab is selected
        Then The current URL is '/study_status/study_status'

    @smoke_test
    Scenario: [Table][Columns][Names] User must be able to see the Study Status page table with correct columns
        Given A test study is selected
        Given The test study '/study_status/study_status' page is opened
        Then A table is visible with following headers
            | headers                               |
            | Study status                          |
            | Reason for unlocking study            |
            | Other reason for unlocking            |
            | Reason for locking or releasing study |
            | Change description                    |
            | Protocol Version                      |
            | Metadata version                      |
            | Modified                              |
            | Modified by                           |

    Scenario: [Table][Columns][Visibility] User must be able to use column selection option
        Given The test study '/study_status/study_status' page is opened
        When The first column is selected from Select Columns option for table with actions
        Then The table contain only selected column and actions column

    @pending_implementation
    Scenario: User must not be able to Lock a Study when study number is not defined
        Given A study in draft status without study number is selected
        And The test study '/study_status/study_status' page is opened
        When The study is locked with description provided
        And Form save button is clicked
        And The form is no longer available
        Then The pop up displays 'Cannot lock study without study_number nor study_title'
        And The form is not closed

    @pending_implementation
    Scenario: User must not be able to Lock a Study when study title is not defined
        Given A study in draft status without title is selected
        And The test study '/study_status/study_status' page is opened
        When The study is locked with description provided
        And Form save button is clicked
        And The form is no longer available
        Then The pop up displays 'Cannot lock study without study_number nor study_title'
        And The form is not closed

    @pending_implementation
    Scenario: User must not be able to Lock a Study when the study is a subpart study
        Given A study in draft status defined as a study subpart
        When The test study '/study_status/study_status' page is opened
        Then The action button to lock the study is disabled

    Scenario: [Lock] User must be able to lock study for study specification updates reason
        Given A test study '9901' in draft status with defined title exists
        When The user locks the study for 'Study Specification Updates' reason
        And The user provides protocol major version '1'
        And The user provides protocol minor version '2'
        And Action is confirmed by clicking save
        Then The study is locked with 'Study Specification Updates' as a reason with major protocol version '1' and minor version '2'

    Scenario: [Lock] User must be able to lock study for final protocol reason
        Given A test study '9902' in draft status with defined title exists
        When The user locks the study for 'Final Protocol' reason
        And The user provides protocol major version '1'
        And Action is confirmed by clicking save
        Then The study is locked with 'Final Protocol' as a reason with major protocol version '1' and minor version '0'

    Scenario: [Lock] User must not be able to lock study for final protocol reason without major version defined
        Given A test study '9903' in draft status with defined title exists
        When The user locks the study for 'Final Protocol' reason
        And Action is confirmed by clicking save
        Then The form is not closed

    Scenario: [Lock] User must be able to lock study for other reason
        Given A test study '9904' in draft status with defined title exists
        When The user locks the study for 'Other' reason
        And The user provides protocol major version '1'
        And The user provides protocol minor version '2'
        And The user provides explanation for other reason
        And Action is confirmed by clicking save
        Then The study is locked with 'Other' as a reason with major protocol version '1' and minor version '2'

    Scenario: [Lock] User must not be able to lock study for other reason without reason provided
        Given A test study '9905' in draft status with defined title exists
        When The user locks the study for 'Other' reason
        And The user provides protocol major version '1'
        And The user provides protocol minor version '2'
        And Action is confirmed by clicking save
        Then The form is not closed

    Scenario: [Lock] User must be able to lock study for PORT approval reason
        Given A test study '9906' in draft status with defined title exists
        When The user locks the study for 'PORT Approval' reason
        And The user provides protocol major version '1'
        And The user provides protocol minor version '2'
        And Action is confirmed by clicking save
        Then The study is locked with 'PORT Approval' as a reason with major protocol version '1' and minor version '2'

    Scenario: [Lock] User must be able to lock study for PORT submission reason
        Given A test study '9907' in draft status with defined title exists
        When The user locks the study for 'PORT Submission' reason
        And The user provides protocol major version '1'
        And The user provides protocol minor version '2'
        And Action is confirmed by clicking save
        Then The study is locked with 'Submission' as a reason with major protocol version '1' and minor version '2'

    Scenario: [Lock] User must be able to lock study for protocol QC reason
        Given A test study '9908' in draft status with defined title exists
        When The user locks the study for 'Protocol QC' reason
        And The user provides protocol major version '1'
        And The user provides protocol minor version '2'
        And Action is confirmed by clicking save
        Then The study is locked with 'Protocol QC' as a reason with major protocol version '1' and minor version '2'

    Scenario: [Unlock] User must be able to unlock study for amendment reason
        Given A test study '9909' locked for 'Study Specification Updates' in major version '0' and minor version '1' exists
        When The user unlocks the study for 'Protocol Amendment Updates' reason
        And Action is confirmed by clicking save
        Then The study is unlocked with 'Amendment' as a reason

    Scenario: [Unlock] User must be able to unlock study for other reason
        Given A test study '9911' locked for 'Study Specification Updates' in major version '0' and minor version '1' exists
        When The user unlocks the study for 'Other' reason
        And Action is confirmed by clicking save
        Then The study is unlocked with 'Other' as a reason

    Scenario: [Unlock] User must be able to unlock study for study specification updates reason
        Given A test study '9912' locked for 'Study Specification Updates' in major version '0' and minor version '1' exists
        When The user unlocks the study for 'Study Specification Updates' reason
        And Action is confirmed by clicking save
        Then The study is unlocked with 'Study Specification Updates' as a reason

    Scenario: [Unlock] User must be notified when unlocking a study with protocol version submitted
        Given A test study '9913' locked for 'Final Protocol' in major version '1' and minor version '0' exists
        When The 'unlock-study' button is clicked
        Then The the user is prompted with a notification message 'Note, that this study has been locked to a protocol version. If the study has passed FPFV, you accept that you carry the risk of modifying the study metadata related to the protocol and downstream processing by proceeding. How do you want to proceed?'