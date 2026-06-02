from pytest_bdd import scenarios, given, when, then

scenarios('../features/studies/study_locking.feature')

@given('a study exists in DRAFT state')
def study_exists_in_draft():
    pass

@given('the study has a study number and study title')
def study_has_number_and_title():
    pass

@given('the study has a selected StudyStandardVersion')
def study_has_standard_version():
    pass

@when('the user requests to lock the study with reason "Other"')
def lock_study_other():
    pass

@then('the study is successfully locked')
def study_is_locked():
    pass

@then('the study is in LOCKED state')
def study_state_locked():
    pass

@then('the study version is incremented')
def study_version_incremented():
    pass

@given('the study is missing the study number')
def study_missing_number():
    pass

@then('the study locking fails with error "Both study number and study title must be set before locking."')
def study_locking_fails_number_title():
    pass

@given('a study subpart exists in DRAFT state')
def subpart_exists_in_draft():
    pass

@then('the study locking fails with error "Study Subparts cannot be locked independently"')
def study_locking_fails_subpart():
    pass

@when('the user requests to lock the study with reason "Final Protocol" and major version 1 and minor version 0')
def lock_study_final_protocol_valid():
    pass

@when('the user requests to lock the study with reason "Final Protocol" and major version 0 and minor version 1')
def lock_study_final_protocol_invalid():
    pass

@then('the study locking fails with error "For \'Final Protocol\', major version must be a non-zero value and minor version must be 0"')
def study_locking_fails_final_protocol_version():
    pass
