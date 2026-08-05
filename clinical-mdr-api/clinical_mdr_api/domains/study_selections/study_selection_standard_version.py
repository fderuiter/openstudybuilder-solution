import datetime
from dataclasses import dataclass

from clinical_mdr_api.domains.study_definition_aggregates.study_metadata import (
    StudyStatus,
)


@dataclass
class StudyStandardVersionVO:
    study_uid: str
    study_status: StudyStatus
    description: str | None
    start_date: datetime.datetime
    author_id: str
    ct_package_uid: str
    automatically_created: bool = False
    uid: str | None = None
    end_date: datetime.datetime | None = None
    snomed_version: str | None = None
    medrt_version: str | None = None
    unii_version: str | None = None
    ucum_version: str | None = None

    def edit_core_properties(
        self,
        ct_package_uid: str,
        description: str | None,
        snomed_version: str | None = None,
        medrt_version: str | None = None,
        unii_version: str | None = None,
        ucum_version: str | None = None,
    ):
        self.ct_package_uid = ct_package_uid
        self.description = description
        self.snomed_version = snomed_version
        self.medrt_version = medrt_version
        self.unii_version = unii_version
        self.ucum_version = ucum_version

    @property
    def possible_actions(self):
        if self.study_status == StudyStatus.DRAFT:
            return ["edit", "delete", "lock"]
        return None


@dataclass
class StudyStandardVersionHistoryVO(StudyStandardVersionVO):
    change_type: str | None = None
