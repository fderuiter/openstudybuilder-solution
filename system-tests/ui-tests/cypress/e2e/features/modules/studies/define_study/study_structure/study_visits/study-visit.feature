@REQ_ID:1074254
Feature: Studies - Define Study - Study Structure - Study Visits

    See shared notes for study visits in file study-visit-intro-notes.txt

    As a system user,
    I want the system to ensure [Scenario],
    So that I can make complete and consistent specification of study visits.

    Background: User is logged in and study has been selected
        Given The user is logged in

    @smoke_test
    Scenario: [Navigation] User must be able to navigate to Study Visit page using side menu
        Given A test study is selected
        And The '/studies' page is opened
        When The 'Study Structure' submenu is clicked in the 'Define Study' section
        And The 'Study Visits' tab is selected
        Then The current URL is '/study_structure/visits'

    Scenario: [Table][Options] User must be able to see the Study Visit table with following options
        Given The test study '/study_structure/visits' page is opened
        Then A table is visible with following options
            | options                                            |
            | add-visit                                          |
            | edit-study-visits                                  |
            | filters-button                                     |
            | columns-layout-button                              |
            | table-export-button                                |
            | select-rows                                        |
            | search-field                                       |
            | History                                            |

    @smoke_test
    Scenario: [Table][Columns][Names] User must be able to see the Study Visit table with following columns
        Given The test study '/study_structure/visits' page is opened
        And A table is visible with following headers
            | headers                     |
            | Epoch                       |
            | Visit type                  |
            | SoA Milestone               |
            | Visit Class                 |
            | Visit Subclass              |
            | Repeating frequency         |
            | Visit name                  |
            | Anchor visit in visit group |
            | Visit group                 |
            | Global anchor visit         |
            | Contact mode                |
            | Time reference              |
            | Timing                      |
            | Visit number                |
            | Unique visit number         |
            | Visit short name            |
            | Study duration days         |
            | Study duration weeks        |
            | Visit window                |
            | Collapsible visit group     |
            | Show Visit                  |
            | Visit description           |
            | Epoch Allocation Rule       |
            | Visit start rule            |
            | Visit end rule              |
            | Study day                   |
            | Study week                  |
            | Week in Study               |
            | Modified                    |
            | Modified by                 |

    Scenario: [Online help] User must be able to read online help for the page
        Given The test study '/study_structure/visits' page is opened
        And The online help button is clicked
        Then The online help panel shows 'Study Visits' panel with content "A clinical encounter where the the subject interacts with the investigator. There can be one more visits in an Epoch. To edit visit(s) in the table view click on the pencil in the top-right menu."

    Scenario: [Table][Columns][Visibility] User must be able to use column selection option
        When Get study 'CDISC DEV-9881' uid
        And Select study with uid saved in previous step
        When The test study '/study_structure/visits' page is opened
        When The first column is selected from Select Columns option for table with actions
        Then The table contain only selected column and actions column

    Scenario: [Create][Pre-condition] User must not be able to add a new Study Visit when no Study Epoch has been defined
        When Get study 'CDISC DEV-9881' uid
        And Select study with uid saved in previous step
        When The test study '/study_structure/visits' page is opened
        When The 'add-visit' button is clicked
        Then The the user is prompted with a notification message "To add visits, you need to difine the epochs first. Would you like to define epochs?"
        And The 'Add epoch' button is visible
        And The 'Cancel' button is visible

    Scenario: [Create][Mandatory fields] User must not be able to create an visit without epoch selected
        When Get study 'CDISC DEV-0' uid
        And Select study with uid saved in previous step
        And [API] The epoch with type 'Pre Treatment' and subtype 'Run-in' exists in selected study
        And User waits for 3 seconds
        And The page 'study_structure/visits' is opened for selected study
        And User waits for epochs to load
        When Add visit button is clicked
        And Form continue button is clicked
        And Form continue button is clicked
        Then The validation appears for missing study period

    Scenario: [Create][Mandatory fields] User must not be able to create an visit without type, contact mode, time reference and timing defined
        When Get study 'CDISC DEV-0' uid
        And Select study with uid saved in previous step
        And [API] The epoch with type 'Pre Treatment' and subtype 'Run-in' exists in selected study
        And User waits for 3 seconds
        And The page 'study_structure/visits' is opened for selected study
        And User waits for epochs to load
        When Add visit button is clicked
        And Form continue button is clicked
        And First available epoch is selected
        And Form continue button is clicked
        And Form save button is clicked
        Then The validation appears for missing visit type
        And The validation appears for missing contact mode
        And The validation appears for missing time reference
        And The validation appears for missing visit timing
    
    Scenario: [Create][Fields check] User must not be able to select time referece for an anchor visit
        When Get study 'CDISC DEV-9880' uid
        And Select study with uid saved in previous step
        And [API] All visit groups uids are fetched
        And [API] All visit groups are removed
        And [API] Study vists uids are fetched for selected study
        When [API] Study visits in selected study are cleaned-up
        And [API] The epoch with type 'Pre Treatment' and subtype 'Run-in' exists in selected study
        And User waits for 3 seconds
        And The page 'study_structure/visits' is opened for selected study
        And User waits for epochs to load
        When Add visit button is clicked
        And Form continue button is clicked
        And Epoch 'Run-in' is selected for the visit
        And Form continue button is clicked
        And Anchor visit checkbox is checked
        Then It is not possible to edit Time Reference for anchor visit

    Scenario: [Create][First visit][Visit window warning] User must be presented with waring regarding visit window selection
        When Get study 'CDISC DEV-9880' uid
        And Select study with uid saved in previous step
        And [API] The epoch with type 'Pre Treatment' and subtype 'Run-in' exists in selected study
        And The page 'study_structure/visits' is opened for selected study
        And User waits for epochs to load
        And User waits for 3 seconds
        When Add visit button is clicked
        And Form continue button is clicked
        And Epoch 'Run-in' is selected for the visit
        And Form continue button is clicked
        Then Warning about visit window unit selection is displayed

    Scenario: [Create][Not first visit][Visit window warning] User must be presented with waring regarding visit window selection
        When Get study 'CDISC DEV-0' uid
        And Select study with uid saved in previous step
        And The page 'study_structure/visits' is opened for selected study
        And User waits for epochs to load
        When Add visit button is clicked
        And Form continue button is clicked
        And First available epoch is selected
        And Form continue button is clicked
        Then Warning about visit window unit selection is displayed

    @smoke_test
    Scenario: [Create][Anchor visit][Positive case] User must be able to create an anchor visit
        When Get study 'CDISC DEV-9880' uid
        And Select study with uid saved in previous step
        And [API] The epoch with type 'Pre Treatment' and subtype 'Run-in' exists in selected study
        And The page 'study_structure/visits' is opened for selected study
        And User waits for epochs to load
        When Add visit button is clicked
        And Form continue button is clicked
        And Epoch 'Run-in' is selected for the visit
        And Form continue button is clicked
        And Visit Type is selected as 'Randomisation'
        And Contact mode is selected as 'On Site Visit'
        And Time unit 'day' is selected for the visit
        And Anchor visit checkbox is checked
        When Form save button is clicked
        Then The new Anchor Visit is visible within the Study Visits table

    @manual_test
    Scenario: [Create] User must be able to create an information visit with visit 0
        When Get study 'CDISC DEV-0' uid
        And Select study with uid saved in previous step
        And [API] The epoch with type 'Pre Treatment' and subtype 'Run-in' exists in selected study
        And The page 'study_structure/visits' is opened for selected study
        Given A test study is selected
        And The epoch exists in selected study
        When The test study '/study_structure/visits' page is opened
        And The first scheduled visit is created with the visit type as an Information visit
        And The visit timing is set to the lowest timing of all existing visit when compared to the Global Anchor time reference
        Then The Information visit should be created with 0 as Visit number
        And No reordering of existing visits should happen

    Scenario: [Create][Anchor visit][Negative case] User must not be able to create an anchor visit if one already exists
        When Get study 'CDISC DEV-9880' uid
        And Select study with uid saved in previous step
        When The page 'study_structure/visits' is opened for selected study
        And User waits for epochs to load
        When Add visit button is clicked
        And Form continue button is clicked
        And Epoch 'Run-in' is selected for the visit
        And Form continue button is clicked
        Then The Anchor visit checkbox is disabled

    Scenario: [Actions][Edit] User must be able to edit the study visit
        When Get study 'CDISC DEV-9880' uid
        And Select study with uid saved in previous step
        And [API] The static visit data is fetched
        And [API] The dynamic visit data is fetched: contact mode 'On Site Visit', time reference 'Global anchor visit', type 'Randomisation', epoch 'Run-in'
        And [API] The visit with following attributes is created: isGlobalAnchor 0, visitWeek 1
        When The page 'study_structure/visits' is opened for selected study
        When User searches for 'V2'
        And The 'Edit' option is clicked from the three dot menu list
        And Form continue button is clicked
        And Form continue button is clicked
        And Visit description is changed to 'Testing edition'
        And Form save button is clicked
        Then Visit description is displayed in the table as 'Testing edition'

    Scenario: [Actions][Edit][Fields check] User must be able to update study visit epoch
        When Get study 'CDISC DEV-9880' uid
        And Select study with uid saved in previous step
        When The page 'study_structure/visits' is opened for selected study
        When User searches for 'V2'
        And The 'Edit' option is clicked from the three dot menu list
        And Form continue button is clicked
        Then The study epoch field is enabled for editing

    Scenario: [Export][CSV] User must be able to export the data in CSV format
        Given The test study '/study_structure/visits' page is opened
        When User clicks table export button
        And User selects 'CSV' format to export the table content
        And Action is confirmed by clicking continue
        Then The study specific 'StudyVisits' file is downloaded in 'csv' format

    Scenario: [Export][Json] User must be able to export the data in JSON format
        Given The test study '/study_structure/visits' page is opened
        When User clicks table export button
        And User selects 'JSON' format to export the table content
        And Action is confirmed by clicking continue
        Then The study specific 'StudyVisits' file is downloaded in 'json' format

    Scenario: [Export][Xml] User must be able to export the data in XML format
        Given The test study '/study_structure/visits' page is opened
        When User clicks table export button
        And User selects 'XML' format to export the table content
        And Action is confirmed by clicking continue
        Then The study specific 'StudyVisits' file is downloaded in 'xml' format

    Scenario: [Export][Excel] User must be able to export the data in EXCEL format
        Given The test study '/study_structure/visits' page is opened
        When User clicks table export button
        And User selects 'EXCEL' format to export the table content
        And Action is confirmed by clicking continue
        Then The study specific 'StudyVisits' file is downloaded in 'xlsx' format

    @pending_implementation
    Scenario: User must not be able to update study epoch without updating the timing to correct chronological order
        Given The '/studies/Study_000002/study_structure/visits' page is opened
        And There are at least 3 visits created for the study
        When The user tries to update last treatment visit epoch to Screening without updating the timing
        Then The system displays the message "The following visit can't be created as the next Epoch Name 'Treatment' starts at the '1' Study Day"

    @manual_test
    Scenario: User must be able to edit the study information visit with visit 0 to other visit type
        Given The '/studies/Study_000003/study_structure/visits' page is opened
        And A study information visit with visit 0 is created
        When This study information visit is edited to be a different visit type
        Then This visit can no longer be Visit 0
        And Reordering will occur of existing visits

    @manual_test
    Scenario: User must be able to edit the study information visit with visit 0 to same visit type
        Given The '/studies/Study_000003/study_structure/visits' page is opened
        And A study information visit with visit 0 is created
        When This study information visit is edited to the same visit type
        Then This visit should be given the visit number of 0
        When This visit is edited to higher visit timing compare to the Global Anchor time reference
        Then Reordering of other visits will occur

    Scenario: [Actions][Delete] User must be able to delete the study visit
        When Get study 'CDISC DEV-9880' uid
        And Select study with uid saved in previous step
        When The page 'study_structure/visits' is opened for selected study
        And The 'Delete' option is clicked from the three dot menu list
        Then The pop up displays 'Visit deleted'

    @manual_test
    Scenario: User must be able to delete the study information visit with visit 0
        Given The '/studies/Study_000003/study_structure/visits' page is opened
        And A study information visit with visit 0 is created
        When This study information visit is deleted
        Then No reordering of other visits will occur

    @manual_test
    Scenario: User must be able to delete the study information visit without visit 0
        Given The '/studies/Study_000003/study_structure/visits' page is opened
        And A study information visit without visit 0 is created
        When This study information visit is deleted
        Then The reordering of other visits will occur

    Scenario: [Create][Study Vists][Same Day Visits] User must be able to define two visits with same visit day in the same epoch
        Given A test study is selected
        And [API] The epoch with type 'Pre Treatment' and subtype 'Run-in' exists in selected study
        And [API] The epoch with type 'Treatment' and subtype 'Intervention' exists in selected study
        And [API] Study vists uids are fetched for current study
        When [API] Study visits in current study are cleaned-up
        And [API] The static visit data is fetched
        And [API] The dynamic visit data is fetched: contact mode 'On Site Visit', time reference 'Global anchor visit', type 'Pre-screening', epoch 'Run-in'
        And [API] The visit with following attributes is created: isGlobalAnchor 1, visitWeek 0
        And [API] The visit with following attributes is created: isGlobalAnchor 0, visitWeek 1, minVisitWindow -1, maxVisitWindow 1
        And The test study '/study_structure/visits' page is opened
        And User waits for epochs to load
        And User waits for 2 seconds
        And Add visit button is clicked
        And Form continue button is clicked
        And Epoch 'Run-in' is selected for the visit
        And Form continue button is clicked
        And Visit Type is selected as 'Pre-screening'
        And Contact mode is selected as 'On Site Visit'
        And Time reference is selected as 'Global anchor visit'
        And Visit timing 7 is selected for the visit
        And User intercepts create visit request
        When Form save button is clicked
        Then The study visit is created

    Scenario: [Create][Study Vists][Same Day Visits] User must be able to define two visits with same visit day in the neighboring epoch
        Given A test study is selected
        And [API] The epoch with type 'Pre Treatment' and subtype 'Run-in' exists in selected study
        And [API] The epoch with type 'Treatment' and subtype 'Intervention' exists in selected study
        And [API] Study vists uids are fetched for current study
        When [API] Study visits in current study are cleaned-up
        And [API] The static visit data is fetched
        And [API] The dynamic visit data is fetched: contact mode 'On Site Visit', time reference 'Global anchor visit', type 'Pre-screening', epoch 'Run-in'
        And [API] The visit with following attributes is created: isGlobalAnchor 1, visitWeek 0
        And [API] The visit with following attributes is created: isGlobalAnchor 0, visitWeek 1, minVisitWindow -1, maxVisitWindow 1
        And The test study '/study_structure/visits' page is opened
        And User waits for epochs to load
        And User waits for 2 seconds
        And Add visit button is clicked
        And Form continue button is clicked
        And Epoch 'Intervention' is selected for the visit
        And Form continue button is clicked
        And Visit Type is selected as 'Pre-screening'
        And Contact mode is selected as 'On Site Visit'
        And Time reference is selected as 'Global anchor visit'
        And Visit timing 7 is selected for the visit
        And User intercepts create visit request
        When Form save button is clicked
        Then The study visit is created

    Scenario: [Create][Study Vists][Same Day Visits] User must not be able to define more than two visits with same visit day in the same epoch
        Given A test study is selected
        And [API] The epoch with type 'Pre Treatment' and subtype 'Run-in' exists in selected study
        And [API] The epoch with type 'Treatment' and subtype 'Intervention' exists in selected study
        And [API] Study vists uids are fetched for current study
        When [API] Study visits in current study are cleaned-up
        And [API] The static visit data is fetched
        And [API] The dynamic visit data is fetched: contact mode 'On Site Visit', time reference 'Global anchor visit', type 'Pre-screening', epoch 'Run-in'
        And [API] The visit with following attributes is created: isGlobalAnchor 1, visitWeek 0
        And [API] The visit with following attributes is created: isGlobalAnchor 0, visitWeek 1, minVisitWindow -1, maxVisitWindow 1
        And [API] The visit with following attributes is created: isGlobalAnchor 0, visitWeek 1, minVisitWindow -1, maxVisitWindow 1
        And The test study '/study_structure/visits' page is opened
        And User waits for epochs to load
        And User waits for 2 seconds
        And Add visit button is clicked
        And Form continue button is clicked
        And Epoch 'Run-in' is selected for the visit
        And Form continue button is clicked
        And Visit Type is selected as 'Pre-screening'
        And Contact mode is selected as 'On Site Visit'
        And Time reference is selected as 'Global anchor visit'
        And Visit timing 7 is selected for the visit
        When Form save button is clicked
        Then The pop up displays 'There already exists a visit with timing set to 7'

    Scenario: [Create][Study Vists][Same Day Visits] User must not be able to define more than two visits with same visit day in the neighboring epoch
        Given A test study is selected
        And [API] The epoch with type 'Pre Treatment' and subtype 'Run-in' exists in selected study
        And [API] The epoch with type 'Treatment' and subtype 'Intervention' exists in selected study
        And [API] Study vists uids are fetched for current study
        When [API] Study visits in current study are cleaned-up
        And [API] The static visit data is fetched
        And [API] The dynamic visit data is fetched: contact mode 'On Site Visit', time reference 'Global anchor visit', type 'Pre-screening', epoch 'Run-in'
        And [API] The visit with following attributes is created: isGlobalAnchor 1, visitWeek 0
        And [API] The visit with following attributes is created: isGlobalAnchor 0, visitWeek 1, minVisitWindow -1, maxVisitWindow 1
        And [API] The visit with following attributes is created: isGlobalAnchor 0, visitWeek 1, minVisitWindow -1, maxVisitWindow 1
        And The test study '/study_structure/visits' page is opened
        And User waits for epochs to load
        And User waits for 2 seconds
        And Add visit button is clicked
        And Form continue button is clicked
        And Epoch 'Intervention' is selected for the visit
        And Form continue button is clicked
        And Visit Type is selected as 'Pre-screening'
        And Contact mode is selected as 'On Site Visit'
        And Time reference is selected as 'Global anchor visit'
        And Visit timing 7 is selected for the visit
        When Form save button is clicked
        Then The pop up displays 'There already exists a visit with timing set to 7'

    Scenario: [Create][Study Vists][Unscheduled] User must be presented with correct visit name and visit type when creating unscheduled visit
        Given A test study is selected
        And [API] The epoch with type 'No Treatment' and subtype 'Basic' exists in selected study
        And The test study '/study_structure/visits' page is opened
        And User waits for epochs to load
        And User waits for 2 seconds
        And Add visit button is clicked
        And Visit scheduling type is selected as 'UNSCHEDULED_VISIT'
        And Form continue button is clicked
        And User waits for the Basic epoch for unscheduled visit to load
        When Form continue button is clicked
        Then User is presented with correct unscheduled visit name
        And User is presented with visit start rule set as 'Unplanned unscheduled'

    Scenario: [Create][Study Vists][Unscheduled] User must be set visit start rule for unscheduled visit
        Given A test study is selected
        And [API] The epoch with type 'No Treatment' and subtype 'Basic' exists in selected study
        And The test study '/study_structure/visits' page is opened
        And User waits for epochs to load
        And User waits for 2 seconds
        And Add visit button is clicked
        And Visit scheduling type is selected as 'UNSCHEDULED_VISIT'
        And Form continue button is clicked
        And User waits for the Basic epoch for unscheduled visit to load
        When Form continue button is clicked
        Then User must be able to set vist start rule as 'Custom start rule'
        And Form save button is clicked
        When User searches for 'Unscheduled'
        And The 'Edit' option is clicked from the three dot menu list
        And Form continue button is clicked
        And Form continue button is clicked
        And User is presented with visit start rule set as 'Custom start rule'