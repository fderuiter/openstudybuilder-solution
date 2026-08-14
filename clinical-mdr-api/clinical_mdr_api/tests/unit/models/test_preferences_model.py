from clinical_mdr_api.domain_repositories.preferences_registry import (
    PREFERENCE_KEYS,
    PREFERENCE_DEFINITIONS,
)
from clinical_mdr_api.models.preferences import PreferencesFields


def test_active_study_preference_registered():
    """Verify that active_study is registered in PREFERENCE_KEYS."""
    assert "active_study" in PREFERENCE_KEYS
    
    active_study_defn = next(
        (defn for defn in PREFERENCE_DEFINITIONS if defn.key == "active_study"),
        None,
    )
    assert active_study_defn is not None
    assert active_study_defn.preference_type == "enum"
    assert active_study_defn.default == ""


def test_preferences_fields_validation():
    """Verify PreferencesFields correctly validates active_study."""
    fields = PreferencesFields(active_study="study-12345")
    assert fields.active_study == "study-12345"

    fields_empty = PreferencesFields(active_study="")
    assert fields_empty.active_study == ""

    fields_none = PreferencesFields(active_study=None)
    assert fields_none.active_study is None
