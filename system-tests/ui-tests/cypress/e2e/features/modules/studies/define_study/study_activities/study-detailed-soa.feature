@REQ_ID:1074260
Feature: Studies - Define Study - Study Activities - Schedule of Activities - Detailed

    As a system user,
    I want the system to ensure [Scenario],
    So that I can make complete and consistent specification of study SoA.

    Background: User is logged in and study has been selected
        Given The user is logged in
        And A test study is selected

    Scenario: [TestData] Old placeholder activity workflow feature flag is disabled
        When The '/administration/featureflags' page is opened
        Then Old placeholder workflow feature flag is turned off

    Scenario: [TestData] Study visits, epochs and activities are created
        And [API] The epoch with type 'Pre Treatment' and subtype 'Run-in' exists in selected study
        And [API] The epoch with type 'Treatment' and subtype 'Intervention' exists in selected study
        And [API] Study vists uids are fetched for current study
        When [API] Study visits in current study are cleaned-up
        And [API] The static visit data is fetched
        And [API] The dynamic visit data is fetched: contact mode 'On Site Visit', time reference 'Global anchor visit', type 'Pre-screening', epoch 'Run-in'
        And [API] The visit with following attributes is created: isGlobalAnchor 1, visitWeek 0
        And [API] The visit with following attributes is created: isGlobalAnchor 0, visitWeek 1, minVisitWindow -1, maxVisitWindow 1
        And [API] The dynamic visit data is fetched: contact mode 'On Site Visit', time reference 'Global anchor visit', type 'Randomisation', epoch 'Intervention'
        And [API] The visit with following attributes is created: isGlobalAnchor 0, visitWeek 2, minVisitWindow 3, maxVisitWindow 7
        And [API] All Activities are deleted from study
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'INFORMED CONSENT' id
        And [API] Activity is added to the study
        And Activity, Group And Subgroup names are fetch to be used in SoA

    @smoke_test
    Scenario: [Navigation] User must be able to navigate to Detailed SoA page using side menu
        Given The '/studies' page is opened
        When The 'Study Activities' submenu is clicked in the 'Define Study' section
        And The 'Schedule of Activities' tab is selected
        Then The current URL is '/activities/soa'

    @smoke_test
    Scenario: [View] User must be presented with option to switch between Detailed and Protocol view
        When The test study '/activities/soa' page is opened
        When 'Detailed' view is available in SoA
        When 'Protocol' view is available in SoA

    @smoke_test
    Scenario: [View] User must not be presented with option to switch to Operational view
        When The test study '/activities/soa' page is opened
        When 'Operational' view is not available in SoA

    Scenario: [Table][Options] User must be able to see the Detailed SoA table with options listed in this scenario
        And The test study '/activities/soa' page is opened
        Then SoA table is available with Bulk actions, Export and Show version history
        And Search is available in SoA table
        And Button for Expanding SoA table is available

    Scenario: [Table][Options] User must be able to see the Detailed SoA Footnotes table with options listed in this scenario
        Given The test study '/activities/soa' page is opened
        When Add footnote button is available in the detailed SoA
        Then A table is visible with following options
            | options                    |
            | add-study-footnote         |
            | filters-button             |
            | History                    |
            | search-field               |
            
    @smoke_test
    Scenario: [Table][Columns][Names] User must be able to see the Footnotes table with specified headers
        And The test study '/activities/soa' page is opened
        And A table is visible with following headers
            | headers      |
            | #            |
            | Footnote     |
            | Linked to    |

    @smoke_test
    Scenario: [Table][Columns][Names] User must be able to see the SoA table with specified headers
        And The test study '/activities/soa' page is opened
        And SoA table is visible with following headers
            | headers       |
            | Epoch         |
            | Visit         |
            | Study week    |
            | Visit window  |

    Scenario: [Table][Structure][Activity][Detailed SoA] User must be able to view the study activities in the detailed SoA table matrix
        When The test study '/activities/soa' page is opened
        And Detailed SoA table is loaded
        And User expand table
        Then Activity SoA group, group, subgroup and name are visible in the detailed view

    Scenario: [Table][Complexity Score][Detailed SoA]User must be presented with complexity score for given study
        Given The test study '/activities/soa' page is opened
        Then The complexity score presents current score for study based on existing acitvities

    Scenario: [Table][Structure][Epochs][Detailed SoA] User must be able to view the study epochs in the protocol SoA table matrix
        When The test study '/activities/soa' page is opened
        Then Epoch 'Run-in' and epoch 'Intervention' are visible in the detailed view

    Scenario: [Table][Structure][Visits][Detailed SoA] User must be able to view the study visits in the protocol SoA table matrix
        When The test study '/activities/soa' page is opened
        Then Visits 'V1', 'V2', 'V3' are visible in the detailed view

    Scenario: [Table][Structure][Study weeks][Detailed SoA] User must be able to view the study weeks in the protocol SoA table matrix
        When The test study '/activities/soa' page is opened
        Then Study weeks 0, 1, 2 are visible in the detailed view

    Scenario: [Table][Structure][Study visit windows][Detailed SoA] User must be able to view the study visit window in the protocol SoA table matrix
        When The test study '/activities/soa' page is opened
        Then Study visit windows '0', '±1', '+3/+7' are visible in the detailed view

    Scenario: [Table][Structure][Activity][Protocol SoA] User must be able to view the study activities in the protocol SoA table matrix
        When The test study '/activities/soa' page is opened
        And Detailed SoA table is loaded
        And User expand table
        And User clicks eye icon on activity level
        And User clicks eye icon on SoA group level for 'INFORMED CONSENT'
        And User waits for 1 seconds
        And User switches to the 'protocol' view
        And User waits for the protocol SoA table to load
        Then Activity SoA group, group, subgroup and name are visible in the protocol view

    Scenario: [Table][Structure][Epochs][Protocol SoA] User must be able to view the study epochs in the protocol SoA table matrix
        When The test study '/activities/soa' page is opened
        And User switches to the 'protocol' view
        And User waits for the protocol SoA table to load
        Then Epoch 'Run-in' and epoch 'Intervention' are visible in the protocol view

    Scenario: [Table][Structure][Visits][Protocol SoA] User must be able to view the study visits in the protocol SoA table matrix
        When The test study '/activities/soa' page is opened
        And User switches to the 'protocol' view
        And User waits for the protocol SoA table to load
        Then Visits 'V1', 'V2', 'V3' are visible in the protocol view

    Scenario: [Table][Structure][Study weeks][Protocol SoA] User must be able to view the study weeks in the protocol SoA table matrix
        When The test study '/activities/soa' page is opened
        And User switches to the 'protocol' view
        And User waits for the protocol SoA table to load
        Then Study weeks 0, 1, 2 are visible in the protocol view

    Scenario: [Table][Structure][Study visit windows][Protocol SoA] User must be able to view the study visit window in the protocol SoA table matrix
        When The test study '/activities/soa' page is opened
        And User switches to the 'protocol' view
        And User waits for the protocol SoA table to load
        Then Study visit windows '0', '±1', '+3/+7' are visible in the protocol view

    @manual_test
    Scenario: User must be presented with time unit of visits the same as defined in first defined study visity
        And The test study '/activities/soa' page is opened
        And The test study data contains defined visits
        Then The SoA is displaying the data using correct time unit

    Scenario: [Table][Structure][Hide/Unhide][Group] User must me able to hide/unhide group in SoA
        When The test study '/activities/soa' page is opened
        And User switches to the 'protocol' view
        Then Group is visible in the protocol SoA
        And User switches to the 'detailed' view
        And Detailed SoA table is loaded
        And User expand table
        And User clicks eye icon on group level
        And User waits for 1 seconds
        And User switches to the 'protocol' view
        And User waits for the protocol SoA table to load
        Then Group is not visible in the protocol SoA
        And User switches to the 'detailed' view
        And User clicks eye icon on group level
        And User waits for 1 seconds
        And User switches to the 'protocol' view
        Then Group is visible in the protocol SoA

    Scenario: [Table][Structure][Hide/Unhide][Subgroup] User must me able to hide/unhide subgroup in SoA
        When The test study '/activities/soa' page is opened
        And User switches to the 'protocol' view
        Then Subgroup is visible in the protocol SoA
        And User switches to the 'detailed' view
        And Detailed SoA table is loaded
        And User expand table
        And User clicks eye icon on subgroup level
        And User waits for 1 seconds
        And User switches to the 'protocol' view
        And User waits for the protocol SoA table to load
        Then Subgroup is not visible in the protocol SoA
        And User switches to the 'detailed' view
        And User clicks eye icon on subgroup level
        And User waits for 1 seconds
        And User switches to the 'protocol' view
        Then Subgroup is visible in the protocol SoA

    Scenario: [Table][Structure][Hide/Unhide][Activity] User must me able to hide/unhide activity in SoA
        When The test study '/activities/soa' page is opened
        And User switches to the 'protocol' view
        And User waits for the protocol SoA table to load
        Then Activity is visible in the protocol SoA
        And User switches to the 'detailed' view
        And Detailed SoA table is loaded
        And User expand table
        And User clicks eye icon on activity level
        And User waits for 1 seconds
        And User switches to the 'protocol' view
        Then Activity is not visible in the protocol SoA
        And User switches to the 'detailed' view
        And User clicks eye icon on activity level
        And User waits for 1 seconds
        And User switches to the 'protocol' view
        And User waits for the protocol SoA table to load
        Then Activity is visible in the protocol SoA

    @smoke_test
    Scenario: [Actions][Add Activity][From Library] User must be able to add Study Activity from Detailed SoA selecting From Library
        And The test study '/activities/soa' page is opened
        And Detailed SoA table is loaded
        And User expand table
        When Action 'Add activity' is selected for study activity
        And Activity from library is selected
        And Form continue button is clicked
        And User selects first available activity and SoA group
        And Form save button is clicked
        Then The pop up displays 'Study activity added'
        And Detailed SoA table is loaded
        And User expand table
        When User search added activity in detailed SoA
        Then The Activity is visible in the SoA

    Scenario: [Actions][Add Activity][From Study][By Id] User must be able to add Study Activity from Detailed SoA selecting From Study
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'INFORMED CONSENT' id
        And [API] Activity is added to the study
        When Get study 'CDISC DEV-9881' uid
        And Select study with uid saved in previous step
        And The page 'activities/list' is opened for selected study
        And Study activity add button is clicked
        And Form continue button is clicked
        And The user goes through selection from library form
        And Form save button is clicked
        And The page 'activities/soa' is opened for selected study
        And Detailed SoA table is loaded
        And User expand table
        And User intercepts available studies request
        And Action 'Add activity' is selected for first study activity
        And User waits for available studies request
        And Activity from studies is selected
        And User selects select study 'CDISC DEV-9876'
        And Form continue button is clicked
        And User selects first available activity
        And Form save button is clicked
        Then The pop up displays 'Study activity added'
        And Detailed SoA table is loaded
        And User expand table
        When User search added activity in detailed SoA
        Then The Activity is visible in the SoA

    Scenario: [Actions][Add Activity][From Study][By Acronym] User must be able to add Study Activity from Detailed SoA selecting From Study
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'INFORMED CONSENT' id
        And [API] Activity is added to the study
        When Get study 'CDISC DEV-9881' uid
        And Select study with uid saved in previous step
        And The page 'activities/list' is opened for selected study
        And Study activity add button is clicked
        And Form continue button is clicked
        And The user goes through selection from library form
        And Form save button is clicked
        And The page 'activities/soa' is opened for selected study
        And Detailed SoA table is loaded
        And User expand table
        And User intercepts available studies request
        And Action 'Add activity' is selected for first study activity
        And User waits for available studies request
        And Activity from studies is selected
        And User selects select study 'E2E Main Test Study'
        And Form continue button is clicked
        And User selects first available activity
        And Form save button is clicked
        Then The pop up displays 'Study activity added'
        And Detailed SoA table is loaded
        And User expand table
        When User search added activity in detailed SoA
        Then The Activity is visible in the SoA

    Scenario: [Actions][Remove Activity] User must be able to remove Study Activity from Detailed SoA
        And The test study '/activities/soa' page is opened
        And Detailed SoA table is loaded
        And User expand table
        And User search study activity
        When Action 'Remove Activity' is selected for study activity
        And Action is confirmed by clicking continue
        Then The pop up displays 'Study activity removed'
        And The page is reloaded
        And User search study activity
        And No activities are found

    @manual_test
    Scenario: User must be able to change activity grouping for given Study Activity in Detailed SoA
        Given At least '1' activites are present in the selected study
        And The test study '/activities/soa' page is opened
        When Action 'Remove activity' is selected for study activity 
        And The user updates the Activity Group for that Activity in Detailed SoA
        And The user updates the Activity SubGroup for that Activity in Detailed SoA
        And The user provides the rationale for activity request for that Activity in Detailed SoA
        Then The pop up snack displays 'The Study activity Aspartate Aminotransferase has been updated.'
        And The changes are visible in Detailed SoA

    @manual_test
    Scenario: User must be able to exchange activity in given Study in Detailed SoA through selection from studies
        Given At least '1' activites are present in the selected study
        And The test study '/activities/soa' page is opened
        When Action 'Exchange Activity' is selected for study activity
        And The user goes through selection from studies form
        And Form save button is clicked
        Then The newly selected avtivity replaces previous activity in study
        And The scheduling is not affected

    Scenario: [Actions][Exchange Activity] User must be able to exchange activity in given Study in Detailed SoA through selection from library
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'INFORMED CONSENT' id
        And [API] Activity is added to the study
        And Activity, Group And Subgroup names are fetch to be used in SoA
        And The test study '/activities/soa' page is opened
        And Detailed SoA table is loaded
        And User expand table
        And User search study activity
        When Action 'Exchange Activity' is selected for study activity
        And Form continue button is clicked
        And The user goes through selection from library form
        And Form save button is clicked
        And The page is reloaded
        And Detailed SoA table is loaded
        And User expand table
        And User search for new study activity
        Then The newly selected activity replaces previous activity in study
        When User clears study activity search
        And User search study activity
        Then The old activity is no longer available

    Scenario: [Placeholder][Submitted] User must be able to see highlighted (yellow) submitted placeholder in the Detailed SoA
        And [API] Get SoA Group 'BIOMARKERS' id
        When [API] Create Submitted Requested Activity
        And [API] Requested Activity is added to the study
        And The test study '/activities/soa' page is opened
        And Detailed SoA table is loaded
        And User expand table
        And User search study activity placeholder
        Then Row containing submitted placeholder is highlighted with yellow color

    Scenario: [Placeholder][Not-Submitted] User must be able to see highlighted (orange) not-submitted placeholder in the Detailed SoA
        And [API] Get SoA Group 'BIOMARKERS' id
        When [API] Create Unsubmitted Requested Activity
        And [API] Requested Activity is added to the study
        And The test study '/activities/soa' page is opened
        And Detailed SoA table is loaded
        And User expand table
        And User search study activity placeholder
        Then Row containing unsubmitted placeholder is highlighted with orange color

    @manual_test
    Scenario: User must be able to exchange activity in given Study in Detailed SoA by creating an placeholder for new Activity Request
        Given At least '1' activites are present in the selected study
        And The test study '/activities/soa' page is opened
        When Action 'Exchange Activity' is selected for study activity
        And The user goes through creating a placeholder for new Activity Request form
        Then The newly selected avtivity replaces previous activity in study
        And The scheduling is not affected

    @manual_test
    Scenario: User must be able to exchange activity in given Study in Detailed SoA by requesting an activity
        Given At least '1' activites are present in the selected study
        And The test study '/activities/soa' page is opened
        When Action 'Exchange Activity' is selected for study activity
        And The user goes through creating a placeholder for new Activity Request form
        Then The newly selected avtivity replaces previous activity in study

    @manual_test
    Scenario: User must be able to add activity from different activity group than selected
        Given At least '1' activites are present in the selected study
        And The test study '/activities/soa' page is opened
        When The user adds an activity from different group than selected to add activity
        Then The activity is assigned to group user has selected

    @manual_test @pending_implementation 
    Scenario: User must be able to bulk edit activities on Detailed SoA
        Given At least '2' activites are present in the selected study
        And The test study '/activities/soa' page is opened
        When The user edits activities in bulk
        And User intercepts bulk edit request
        And Action is confirmed by clicking save
        Then The data for bulk edited activities is updated

    @manual_test @pending_implementation 
    Scenario: User must be able to remove selection of activity on the form for bulk edit in Detailed SoA
        Given At least '2' activites are present in the selected study
        And The test study '/activities/soa' page is opened
        And Detailed SoA table is loaded
        And User expand table
        When User search study activity
        And Activity checkbox is checked for 0 activity on the list
        And The user selects 'Bulk Edit Activities' action after clicking Bulk actions
        And The user removes selection of one of Activities on the form
        Then The selection disappears from the form

    Scenario: [TestData] User creates data for Bulk scenarios
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'INFORMED CONSENT' id
        And [API] Activity is added to the study
        And Activity name is added to the list
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'INFORMED CONSENT' id
        And [API] Activity is added to the study
        And Activity name is added to the list

    Scenario: [Bulk][Edit] User must be able to open bulk edit activities form on Detailed SoA
        And The test study '/activities/soa' page is opened
        And Detailed SoA table is loaded
        And User expand table
        When User search for 0 activity on the list
        And Activity checkbox is checked for 0 activity on the list
        And The user selects 'Bulk Edit Activities' action after clicking Bulk actions
        Then The bulk edit view is presented to user allowing to update Activity Group and Visits for selected activities

    Scenario: [Bulk][Mandory fields] User must not be able to bulk edit without selecting Activity Group and Visit
        And The test study '/activities/soa' page is opened
        And Detailed SoA table is loaded
        And User expand table
        When User search for 0 activity on the list
        And Activity checkbox is checked for 0 activity on the list
        And The user selects 'Bulk Edit Activities' action after clicking Bulk actions
        And Form save button is clicked
        Then The validation appears for Activity Group field in bulk edit form

    Scenario: [Bulk][Delete] User must be able to bulk delete activities on Detailed SoA
        And The test study '/activities/soa' page is opened
        And Detailed SoA table is loaded
        And User expand table
        When User search for 0 activity on the list
        And Activity checkbox is checked for 0 activity on the list
        And The user selects 'Bulk Remove Activities' action after clicking Bulk actions
        When Batch request is intercepted
        And Action is confirmed by clicking continue
        Then The activities are removed from the study
        
    Scenario: [Actions][Reordering] User must be able to enable reordering of activities in Detailed SoA
        When Activity name list is cleared
        And [API] Group and subgroup are created and approved
        And [API] All Activities are deleted from study
        And [API] Get SoA Group 'TRIAL MATERIAL' id
        And [API] Study Activity based on existing group and subgroup is created and approved
        And [API] Activity is added to the study
        And Activity name is added to the list
        And [API] Study Activity based on existing group and subgroup is created and approved
        And [API] Activity is added to the study
        And Activity name is added to the list
        And [API] Study Activity based on existing group and subgroup is created and approved
        And [API] Activity is added to the study
        And Activity name is added to the list
        And The test study '/activities/soa' page is opened
        And Detailed SoA table is loaded
        And User expand table
        When The user enables the Reorder Activities function for acitivities in the same flowchart group
        And User waits for 2 seconds
        And User intercepts reorder activities request
        And The user updates the order of activities
        And User waits for 1 seconds
        And User clicks Finish reordering button
        And User waits for reorder activities request
        And Detailed SoA table is loaded
        Then The new order of activites is visible

    Scenario: [New study] User must be able to see buttons for adding new activity or visit when Study is empty
        Given The '/studies/select_or_add_study/active' page is opened
        And User waits for the table
        And The Add Study button is clicked
        When New study project id, study number and study acronym are filled in
        And Form save button is clicked
        When The 'Study Activities' submenu is clicked in the 'Define Study' section
        And The 'Schedule of Activities' tab is selected
        Then Text about no added visits and activities is displayed
        And User can click Add visit button
        Then The current URL is '/study_structure/visits'
        When The 'Study Activities' submenu is clicked in the 'Define Study' section
        And The 'Schedule of Activities' tab is selected
        And User can click Add study activity button
        Then The current URL is '/activities/list'

    @smoke_test
    Scenario: [Table][Search][Positive case] User must be able to search study activity
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'INFORMED CONSENT' id
        And [API] Activity is added to the study
        And Activity, Group And Subgroup names are fetch to be used in SoA
        And The test study '/activities/soa' page is opened
        And Detailed SoA table is loaded
        And User expand table
        When User search study activity
        Then Activity is found in table

    Scenario: [Table][Search][Case sensitivity] User must be able to search study activity ingnoring case sensitivity
        And The test study '/activities/soa' page is opened
        And Detailed SoA table is loaded
        And User expand table
        When User search study activity in lowercase
        Then Activity is found in table

    Scenario: [Table][Search][Partial text] User must be able to search activity by only inputing 3 characters
        And The test study '/activities/soa' page is opened
        And Detailed SoA table is loaded
        And User expand table
        When User search study activity by partial name
        Then Activity is found in table

    Scenario: [Table][Search][Negative] User must be able to search non-existing study activity
        Given The test study '/activities/soa' page is opened
        And Detailed SoA table is loaded
        When User search for non-existing activity
        Then No activities are found

    Scenario: [Table][Search][Negative] User must not be able to search activity by activity subgroup
        Given The test study '/activities/soa' page is opened
        And Detailed SoA table is loaded
        When User search study activity by subgroup
        Then No activities are found

    Scenario: [Table][Search][Negative] User must not be able to search activity by activity group
        Given The test study '/activities/soa' page is opened
        And Detailed SoA table is loaded
        When User search study activity by group
        Then No activities are found

    Scenario: [Export][CSV] User must be able to export the data in CSV format
        Given The test study '/activities/soa' page is opened
        When User clicks table export button
        And User selects 'CSV' format to export the table content
        Then The study specific 'detailed SoA' file without timestamp is downloaded in 'csv' format

    Scenario: [Export][EXCEL] User must be able to export the data in JSON format
        Given The test study '/activities/soa' page is opened
        When User clicks table export button
        And User selects 'EXCEL' format to export the table content
        Then The study specific 'detailed SoA' file without timestamp is downloaded in 'xlsx' format

    Scenario: [Export][DOCX] User must be able to export the data in XML format
        Given The test study '/activities/soa' page is opened
        When User clicks table export button
        And User selects 'DOCX' format to export the table content
        Then The study specific 'detailed SoA' file without timestamp is downloaded in 'docx' format

    @manual_test @BUG_ID:2851795
    Scenario:[Edit] User must be presented with all activity groups linked when editing the activity
        Given The test study '/activities/soa' page is opened
        And The activity with more than one activity group exists in the table
        When The user opens the edit form for that activity
        Then The Activity group dropdown is presenting all linked activity groups

    @manual_test @BUG_ID:2844670
    Scenario:[Edit] User must be able to hide groups when activity groups has been changed
        Given The test study '/activities/soa' page is opened
        And The activity with linked activity group is present for the study
        When The user hides that activity group
        Then The group is hidden correctly