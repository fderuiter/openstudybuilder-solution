import unittest
from unittest.mock import MagicMock

from clinical_mdr_api.services.ddf.usdm_mapper import USDMMapper


class TestUSDMActivityConditionality(unittest.TestCase):
    def setUp(self):
        self.mock_get_activities = MagicMock()
        self.mapper = USDMMapper(
            get_osb_study_design_cells=MagicMock(),
            get_osb_study_arms=MagicMock(),
            get_osb_study_epochs=MagicMock(),
            get_osb_study_elements=MagicMock(),
            get_osb_study_endpoints=MagicMock(),
            get_osb_study_visits=MagicMock(),
            get_osb_study_activities=self.mock_get_activities,
            get_osb_activity_schedules=MagicMock(),
        )

    def test_non_conditional_activity_export(self):
        # Activity with no instructions or footnotes
        activity = MagicMock()
        activity.study_activity_uid = "sa_1"
        activity.is_conditional = False
        activity.activity_instruction_texts = []
        activity.footnote_texts = []
        activity.study_activity_subgroup.activity_subgroup_name = "Subgroup 1"
        activity.activity.uid = "act_1"
        activity.activity.name = "Blood Draw"

        self.mock_get_activities.return_value = MagicMock(items=[activity])

        study = MagicMock(uid="study_1")
        mapped_activities = self.mapper._get_study_activities(study)

        self.assertEqual(len(mapped_activities), 1)
        usdm_act = mapped_activities[0]
        self.assertEqual(len(usdm_act.definedProcedures), 1)

        conditions = self.mapper._get_study_conditions(study)
        self.assertEqual(len(conditions), 0)

    def test_conditional_activity_with_instructions_export(self):
        # Activity with connected instructions
        activity = MagicMock()
        activity.study_activity_uid = "sa_2"
        activity.is_conditional = True
        activity.activity_instruction_texts = ["Fasting for 10 hours required"]
        activity.footnote_texts = []
        activity.study_activity_subgroup.activity_subgroup_name = "Subgroup 2"
        activity.activity.uid = "act_2"
        activity.activity.name = "Glucose Test"

        self.mock_get_activities.return_value = MagicMock(items=[activity])

        study = MagicMock(uid="study_2")
        mapped_activities = self.mapper._get_study_activities(study)

        self.assertEqual(len(mapped_activities), 1)
        usdm_act = mapped_activities[0]

        conditions = self.mapper._get_study_conditions(study)
        self.assertEqual(len(conditions), 1)
        self.assertEqual(conditions[0].text, "Fasting for 10 hours required")
        self.assertEqual(conditions[0].name, "Activity Condition Rule")
        self.assertIn(usdm_act.id, conditions[0].appliesToIds)

    def test_conditional_activity_with_footnotes_export(self):
        # Activity with connected footnotes
        activity = MagicMock()
        activity.study_activity_uid = "sa_3"
        activity.is_conditional = True
        activity.activity_instruction_texts = []
        activity.footnote_texts = ["If subject shows mild symptoms"]
        activity.study_activity_subgroup.activity_subgroup_name = "Subgroup 3"
        activity.activity.uid = "act_3"
        activity.activity.name = "ECG Monitoring"

        self.mock_get_activities.return_value = MagicMock(items=[activity])

        study = MagicMock(uid="study_3")
        mapped_activities = self.mapper._get_study_activities(study)

        self.assertEqual(len(mapped_activities), 1)
        usdm_act = mapped_activities[0]

        conditions = self.mapper._get_study_conditions(study)
        self.assertEqual(len(conditions), 1)
        self.assertEqual(conditions[0].text, "If subject shows mild symptoms")
        self.assertEqual(conditions[0].name, "Activity Condition Rule")
        self.assertIn(usdm_act.id, conditions[0].appliesToIds)
