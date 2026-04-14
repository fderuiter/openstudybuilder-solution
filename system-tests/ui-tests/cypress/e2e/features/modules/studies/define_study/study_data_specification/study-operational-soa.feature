@REQ_ID:1898007
Feature: Studies - Define Study - Study Data Specifications - Operational SoA

    As a system user,
    I want the system to ensure [Scenario],
    So that I can make complete and consistent specification of the Study Operational SoA.

    # Note, data collection specification is not impemented yet, so currently only the study activity instance and operational SoA is supported.
    # See also file: study-activity-instance.feature

    Background: User is logged in and study has been selected
        Given The user is logged in
        And A test study is selected

    Scenario: [TestData] Old placeholder activity workflow feature flag is disabled
        When The '/administration/featureflags' page is opened
        Then Old placeholder workflow feature flag is turned off
        
    Scenario: [TestData] All activities are deleted from test study
        And [API] All Activities are deleted from study

    @smoke_test
    Scenario: [Navigation] User must be able to navigate to Operational SoA page using side menu
        Given The '/studies' page is opened
        When The 'Data Specifications' submenu is clicked in the 'Define Study' section
        When The 'Operational SoA' tab is selected
        Then The current URL is '/data_specifications/operational'

    @smoke_test
    Scenario: [Table][Columns][Names] User must be able to see the Operational SoA matrix table with options listed in this scenario
        Given The test study '/data_specifications/operational' page is opened
        Then expand table and Show SoA groups is available on the page
        And A table is visible with following headers
            | headers             |
            | Activities          |
            | Epoch               |
            | Visit               |
            | Study week          |
            | Window              |
            | Topic Code          |
            | ADaM Param Code     |


    Scenario: [Placeholder][Submitted] User must be able to see highlighted (yellow) submitted placeholder in the Operational SoA
        And [API] Get SoA Group 'BIOMARKERS' id
        When [API] Create Submitted Requested Activity
        And [API] Requested Activity is added to the study
        And The test study '/data_specifications/operational' page is opened
        And User waits Operational SoA table
        And User expand table
        Then Row containing submitted placeholder is highlighted with yellow color in Operational SoA 

    Scenario: [Placeholder][Not-Submitted] User must be able to see highlighted (orange) not-submitted placeholder in the Operational SoA
        And [API] Get SoA Group 'BIOMARKERS' id
        When [API] Create Unsubmitted Requested Activity
        And [API] Requested Activity is added to the study
        And The test study '/data_specifications/operational' page is opened
        And User waits Operational SoA table
        And User expand table
        Then Row containing unsubmitted placeholder is highlighted with orange color in Operational SoA

    @pending_implementation
    Scenario: User must be able to view the study activity instances in the Operational SoA table matrix including SoA groups
        Given The test study '/data_specifications/operational' page is opened
        When The test study activity instances is selected for the study
        And the option to 'Show SoA groups' is enabled
        Then The Operational SoA table matrix display rows for each test study activity instance grouped by activity, activity group, activity subgroup and SoA group

    @pending_implementation
    Scenario: User must be able to view the study activity instance in the Operational SoA table matrix without SoA groups
        Given The test study '/data-specification/detailed-detailed-operational-soa' page is opened
        When The test study activity instances is selected for the study
        And the option to 'Show SoA groups' is disabled
        Then The Operational SoA table matrix display rows for each test study activity instance grouped by activity, activity group and activity subgroup

    @pending_implementation
    Scenario: User must be able to view the study activity instance attributes in the Operational SoA table matrix
        Given The test study '/data-specification/detailed-detailed-operational-soa' page is opened
        When The test study activity instances is selected for the study
        And the option to 'Show Activity instance attributes' is enabled
        Then The Operational SoA table matrix display rows for each test study activity instance including the attributes: topic code, ADaM Param Code

    @pending_implementation
    Scenario: User must be able to view details of a specific study activity instance in the Operational SoA table matrix
        Given The test study '/data-specification/detailed-detailed-operational-soa' page is opened
        When The test study activity instances is selected for the study
        And the hyperlink for a study activity instances is selected
        Then a new tab opens with the library details overview of the selected activity instance