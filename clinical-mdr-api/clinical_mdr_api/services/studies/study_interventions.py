"""Study Protocol Interventions service"""

import logging
from typing import Any, Mapping

from docx.enum.style import WD_STYLE_TYPE

from clinical_mdr_api.models.study_selections.study_selection import (
    StudyCompoundDosing,
    StudySelectionArm,
    StudySelectionCompound,
)
from clinical_mdr_api.services.studies.study_arm_selection import (
    StudyArmSelectionService,
)
from clinical_mdr_api.services.studies.study_compound_dosing_selection import (
    StudyCompoundDosingSelectionService,
)
from clinical_mdr_api.services.studies.study_compound_selection import (
    StudyCompoundSelectionService,
)
from clinical_mdr_api.services.utils.table_f import (
    TableCell,
    TableRow,
    TableWithFootnotes,
    table_to_docx,
    table_to_html,
)

# For future LOCALIZATION
_gettext = {
    "intervention_or_arm_name": "Intervention/Arm name",
    "intervention_name": "Intervention name",
    "intervention_type": "Intervention type",
    "investigational_or_non_investigational": "Investigational or non-investigational",
    "pharmaceutical_form": "Pharmaceutical form",
    "route_of_administration": "Route of administration",
    "medical_device": "Medical-device (if applicable)",
    "trial_product_strength": "Trial product strength",
    "dose_and_frequency": "Dose and dose frequency",
    "dosing_and_administration": "Dosing instructions and administration",
    "transfer_from_other_therapy": "Transfer from other therapy",
    "sourcing": "Sourcing",
    "packaging_and_labelling": "Packaging and labelling",
    "authorisation_status_in": "Authorisation status in",
    "medical_device_template": "Administered using {device} with a {dispensed_in}",
    "trial_product_strength_template": "{value} {unit}",
    "None": "None",
    "study_interventions": "Study Interventions",
    "no_information": "-",
    "not_specified": "Not Specified",
}.get

log = logging.getLogger(__name__)

# pylint: disable=no-member
DOCX_STYLES = {
    "table": ("SB Table Condensed", WD_STYLE_TYPE.TABLE),
    "header1": ("Table Header lvl1", WD_STYLE_TYPE.PARAGRAPH),
    "header2": ("Table Header lvl2", WD_STYLE_TYPE.PARAGRAPH),
    None: ("Table Text", WD_STYLE_TYPE.PARAGRAPH),
}


class StudyInterventionsService:
    def get_table(self, study_uid: str) -> TableWithFootnotes:
        compounds = self._get_study_compounds(study_uid)
        arms = self._get_arms_for_compounds(study_uid)
        dosings = self._get_compound_dosings(study_uid)
        table = self.mk_table(compounds, arms, dosings)
        return table

    def get_html(self, study_uid: str) -> str:
        table = self.get_table(study_uid)
        return table_to_html(table)

    def get_docx(self, study_uid: str):
        table = self.get_table(study_uid)
        docx = table_to_docx(table, DOCX_STYLES)
        return docx

    @staticmethod
    def _dosage_forms_txt(cmp: StudySelectionCompound) -> str:
        from clinical_mdr_api.services.concepts.pharmaceutical_products_service import (
            PharmaceuticalProductService,
        )
        p_uids = [pp.uid for pp in cmp.medicinal_product.pharmaceutical_products] if cmp.medicinal_product else []
        forms = []
        for uid in p_uids:
            try:
                full_pp = PharmaceuticalProductService().get_by_uid(uid)
                if full_pp and full_pp.dosage_forms:
                    for df in full_pp.dosage_forms:
                        if df.term_name and df.term_name not in forms:
                            forms.append(df.term_name)
            except Exception as e:
                log.warning(f"Error fetching pharmaceutical product {uid}: {e}")
        return "\n".join(forms) if forms else ""

    @staticmethod
    def _routes_of_admin_txt(cmp: StudySelectionCompound) -> str:
        from clinical_mdr_api.services.concepts.pharmaceutical_products_service import (
            PharmaceuticalProductService,
        )
        p_uids = [pp.uid for pp in cmp.medicinal_product.pharmaceutical_products] if cmp.medicinal_product else []
        routes = []
        for uid in p_uids:
            try:
                full_pp = PharmaceuticalProductService().get_by_uid(uid)
                if full_pp and full_pp.routes_of_administration:
                    for roa in full_pp.routes_of_administration:
                        if roa.term_name and roa.term_name not in routes:
                            routes.append(roa.term_name)
            except Exception as e:
                log.warning(f"Error fetching pharmaceutical product {uid}: {e}")
        return "\n".join(routes) if routes else ""

    @staticmethod
    def _strength_txt(cmp: StudySelectionCompound) -> str:
        from clinical_mdr_api.services.concepts.pharmaceutical_products_service import (
            PharmaceuticalProductService,
        )
        p_uids = [pp.uid for pp in cmp.medicinal_product.pharmaceutical_products] if cmp.medicinal_product else []
        strengths = []
        for uid in p_uids:
            try:
                full_pp = PharmaceuticalProductService().get_by_uid(uid)
                if full_pp and full_pp.formulations:
                    for formulation in full_pp.formulations:
                        for ingredient in formulation.ingredients:
                            if ingredient.strength:
                                val = ingredient.strength.value
                                unit = ingredient.strength.unit_label
                                val_str = str(int(val)) if val == int(val) else str(val)
                                str_rep = f"{val_str} {unit}" if unit else val_str
                                if str_rep not in strengths:
                                    strengths.append(str_rep)
            except Exception as e:
                log.warning(f"Error fetching pharmaceutical product strength {uid}: {e}")
        return "\n".join(strengths) if strengths else ""

    @staticmethod
    # pylint: disable=unused-argument
    def mk_table(
        compounds: list[StudySelectionCompound],
        arms: Mapping[str, list[StudySelectionArm]],
        dosings: Mapping[str, list[StudyCompoundDosing]],
    ) -> TableWithFootnotes:
        table = TableWithFootnotes(
            num_header_rows=1,
            num_header_cols=1,
            title=_gettext("study_interventions"),
            id="StudyInterventionsTable",
        )

        table.rows.append(
            row := TableRow(
                cells=[
                    TableCell(
                        text=_gettext("intervention_or_arm_name"), style="header1"
                    )
                ]
            )
        )
        for cmp in compounds:
            row.cells.append(
                TableCell(
                    text=StudyInterventionsService._arm_txt(cmp, arms), style="header2"
                )
            )

        table.rows.append(
            row := TableRow(
                cells=[TableCell(text=_gettext("intervention_name"), style="header2")]
            )
        )
        for cmp in compounds:
            name_val = cmp.compound.name if cmp.compound and cmp.compound.name else ""
            row.cells.append(
                TableCell(text=name_val if name_val else _gettext("not_specified"))
            )

        table.rows.append(
            row := TableRow(
                cells=[TableCell(text=_gettext("intervention_type"), style="header2")]
            )
        )
        for cmp in compounds:
            type_val = cmp.type_of_treatment.term_name if cmp.type_of_treatment and cmp.type_of_treatment.term_name else ""
            row.cells.append(
                TableCell(text=type_val if type_val else _gettext("not_specified"))
            )

        table.rows.append(
            row := TableRow(
                cells=[
                    TableCell(
                        text=_gettext("investigational_or_non_investigational"),
                        style="header2",
                    )
                ]
            )
        )
        for _ in compounds:
            row.cells.append(TableCell(text=_gettext("not_specified")))

        table.rows.append(
            row := TableRow(
                cells=[TableCell(text=_gettext("pharmaceutical_form"), style="header2")]
            )
        )
        for cmp in compounds:
            df_text = StudyInterventionsService._dosage_forms_txt(cmp)
            row.cells.append(
                TableCell(text=df_text if df_text else _gettext("not_specified"))
            )

        table.rows.append(
            row := TableRow(
                cells=[
                    TableCell(text=_gettext("route_of_administration"), style="header2")
                ]
            )
        )
        for cmp in compounds:
            roa_text = StudyInterventionsService._routes_of_admin_txt(cmp)
            row.cells.append(
                TableCell(text=roa_text if roa_text else _gettext("not_specified"))
            )

        table.rows.append(
            row := TableRow(
                cells=[TableCell(text=_gettext("medical_device"), style="header2")]
            )
        )
        for cmp in compounds:
            device_term = cmp.delivery_device
            dispenser_term = cmp.dispensed_in or cmp.dispenser

            device_name = device_term.term_name if device_term else None
            dispenser_name = dispenser_term.term_name if dispenser_term else None

            if not device_name and not dispenser_name:
                cell_text = _gettext("not_specified")
            else:
                mapping = {
                    "device": device_name if device_name else _gettext("None"),
                    "dispensed_in": dispenser_name if dispenser_name else _gettext("None"),
                }
                cell_text = _gettext("medical_device_template").format_map(mapping)
            row.cells.append(TableCell(text=cell_text))

        table.rows.append(
            row := TableRow(
                cells=[
                    TableCell(text=_gettext("trial_product_strength"), style="header2")
                ]
            )
        )
        for cmp in compounds:
            strength_text = StudyInterventionsService._strength_txt(cmp)
            row.cells.append(
                TableCell(text=strength_text if strength_text else _gettext("not_specified"))
            )

        table.rows.append(
            row := TableRow(
                cells=[TableCell(text=_gettext("dose_and_frequency"), style="header2")]
            )
        )
        for cmp in compounds:
            row.cells.append(
                TableCell(text=StudyInterventionsService._dosing_txt(cmp, dosings))
            )

        table.rows.append(
            row := TableRow(
                cells=[
                    TableCell(
                        text=_gettext("dosing_and_administration"), style="header2"
                    )
                ]
            )
        )
        for cmp in compounds:
            row.cells.append(
                TableCell(text=cmp.other_info if cmp.other_info else _gettext("not_specified"))
            )

        table.rows.append(
            row := TableRow(
                cells=[
                    TableCell(
                        text=_gettext("transfer_from_other_therapy"), style="header2"
                    )
                ]
            )
        )
        for _ in compounds:
            row.cells.append(TableCell(text=_gettext("not_specified")))

        table.rows.append(
            row := TableRow(
                cells=[TableCell(text=_gettext("sourcing"), style="header2")]
            )
        )
        for _ in compounds:
            row.cells.append(TableCell(text=_gettext("not_specified")))

        table.rows.append(
            row := TableRow(
                cells=[
                    TableCell(text=_gettext("packaging_and_labelling"), style="header2")
                ]
            )
        )
        for _ in compounds:
            row.cells.append(TableCell(text=_gettext("not_specified")))

        table.rows.append(
            row := TableRow(
                cells=[
                    TableCell(text=_gettext("authorisation_status_in"), style="header2")
                ]
            )
        )
        for _ in compounds:
            row.cells.append(TableCell(text=_gettext("not_specified")))

        return table

    @staticmethod
    def _dosing_txt(compounds, dosings):
        freq_str = ""
        if compounds.dose_frequency and compounds.dose_frequency.term_name:
            freq_str = compounds.dose_frequency.term_name
        
        parts = []
        for dosing in dosings.get(compounds.study_compound_uid, []):
            dose_str = ""
            if dosing.dose_value:
                val = dosing.dose_value.value
                val_str = str(int(val)) if val == int(val) else str(val)
                unit = dosing.dose_value.unit_label if dosing.dose_value.unit_label else ""
                dose_str = f"{val_str} {unit}".strip()
            
            if dose_str and freq_str:
                parts.append(f"{dose_str} {freq_str}".strip())
            elif dose_str:
                parts.append(dose_str)
            elif freq_str:
                parts.append(freq_str)
                
        return "\n".join(parts) or _gettext("not_specified")

    @staticmethod
    def _arm_txt(compound, arms):
        return "\n".join(
            arm.name for arm in arms.get(compound.study_compound_uid, [])
        ) or _gettext("no_information")

    def _get_study_compounds(self, study_uid) -> list[StudySelectionCompound]:
        return (
            StudyCompoundSelectionService()
            .get_all_selection(
                study_uid=study_uid,
            )
            .items
        )

    def _get_arms_for_compounds(
        self, study_uid
    ) -> Mapping[str, list[StudySelectionArm]]:
        arms = {
            arm.arm_uid: arm
            for arm in StudyArmSelectionService()
            .get_all_selection(
                study_uid=study_uid,
            )
            .items
        }

        mapping = StudyCompoundSelectionService().get_compound_uid_to_arm_uids_mapping(
            study_uid
        )

        return {
            compound_uid: [arms[arm_uid] for arm_uid in arm_uids]
            for compound_uid, arm_uids in mapping.items()
        }

    def _get_compound_dosings(
        self, study_uid: str
    ) -> dict[str, list[StudyCompoundDosing]]:
        results = (
            StudyCompoundDosingSelectionService()
            .get_all_compound_dosings(study_uid)
            .items
        )

        mapping: dict[str, Any] = {}
        for dosing in results:
            key = dosing.study_compound.study_compound_uid
            mapping.setdefault(key, []).append(dosing)

        return mapping
