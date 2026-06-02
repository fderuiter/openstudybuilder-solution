@domain:Protocol_Management
Feature: Study Locking

  @FS-StudyLock-001
  Scenario: Lock a Study in Draft State
    Given a study exists in DRAFT state
    And the study has a study number and study title
    And the study has a selected StudyStandardVersion
    When the user requests to lock the study with reason "Other"
    Then the study is successfully locked
    And the study is in LOCKED state
    And the study version is incremented

  @FS-StudyLock-002
  Scenario: Fail to Lock a Study without Study Number or Title
    Given a study exists in DRAFT state
    And the study is missing the study number
    When the user requests to lock the study with reason "Other"
    Then the study locking fails with error "Both study number and study title must be set before locking."

  @FS-StudyLock-003
  Scenario: Fail to Lock a Subpart Independently
    Given a study subpart exists in DRAFT state
    When the user requests to lock the study with reason "Other"
    Then the study locking fails with error "Study Subparts cannot be locked independently"

  @FS-StudyLock-004
  Scenario: Lock a Study with Final Protocol
    Given a study exists in DRAFT state
    And the study has a study number and study title
    And the study has a selected StudyStandardVersion
    When the user requests to lock the study with reason "Final Protocol" and major version 1 and minor version 0
    Then the study is successfully locked

  @FS-StudyLock-005
  Scenario: Fail to Lock a Study with Final Protocol with invalid version
    Given a study exists in DRAFT state
    And the study has a study number and study title
    When the user requests to lock the study with reason "Final Protocol" and major version 0 and minor version 1
    Then the study locking fails with error "For 'Final Protocol', major version must be a non-zero value and minor version must be 0"
