from typing import Any

from neomodel import db

from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
    VersionRoot,
    VersionValue,
)
from clinical_mdr_api.domain_repositories.models.odm import OdmFormRoot, OdmFormValue
from clinical_mdr_api.domain_repositories.odms.generic_repository import (
    OdmGenericRepository,
)
from clinical_mdr_api.domains.odms.form import OdmFormAR, OdmFormRefVO, OdmFormVO
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryItemStatus,
    LibraryVO,
)
from clinical_mdr_api.models.odms.common_models import (
    OdmAliasModel,
    OdmTranslatedTextModel,
)
from clinical_mdr_api.models.odms.form import OdmForm
from clinical_mdr_api.services._utils import ensure_transaction
from common.utils import convert_to_datetime


class FormRepository(OdmGenericRepository[OdmFormAR]):
    root_class = OdmFormRoot
    value_class = OdmFormValue
    return_model = OdmForm

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        root: VersionRoot,
        library: Library,
        relationship: VersionRelationship,
        value: VersionValue,
        **_kwargs,
    ) -> OdmFormAR:
        return OdmFormAR.from_repository_values(
            uid=root.uid,
            odm_vo=OdmFormVO.from_repository_values(
                oid=value.oid,
                name=value.name,
                sdtm_version=value.sdtm_version,
                repeating=value.repeating,
                translated_texts=[
                    OdmTranslatedTextModel(
                        text_type=translated_text_value.text_type,
                        language=translated_text_value.language,
                        text=translated_text_value.text,
                    )
                    for translated_text_value in value.has_translated_text.all()
                ],
                aliases=[
                    OdmAliasModel(name=alias_value.name, context=alias_value.context)
                    for alias_value in value.has_alias.all()
                ],
                item_group_uids=[
                    item_group_root.uid
                    for item_group_value in value.item_group_ref.all()
                    if (item_group_root := item_group_value.has_root.single())
                ],
                vendor_element_uids=[
                    vendor_element_root.uid
                    for vendor_element_value in value.has_vendor_element.all()
                    if (vendor_element_root := vendor_element_value.has_root.single())
                ],
                vendor_attribute_uids=[
                    vendor_attribute_root.uid
                    for vendor_attribute_value in value.has_vendor_attribute.all()
                    if (
                        vendor_attribute_root := vendor_attribute_value.has_root.single()
                    )
                ],
                vendor_element_attribute_uids=[
                    vendor_element_attribute_root.uid
                    for vendor_element_attribute_value in value.has_vendor_element_attribute.all()
                    if (
                        vendor_element_attribute_root := vendor_element_attribute_value.has_root.single()
                    )
                ],
            ),
            library=LibraryVO.from_input_values_2(
                library_name=library.name,
                is_library_editable_callback=lambda _: library.is_editable,
            ),
            item_metadata=self._library_item_metadata_vo_from_relation(relationship),
        )

    def _create_aggregate_root_instance_from_cypher_result(
        self, input_dict: dict[str, Any]
    ) -> OdmFormAR:
        major, minor = input_dict["version"].split(".")
        odm_form_ar = OdmFormAR.from_repository_values(
            uid=input_dict["uid"],
            odm_vo=OdmFormVO.from_repository_values(
                oid=input_dict.get("oid"),
                name=input_dict["name"],
                sdtm_version=input_dict.get("sdtm_version"),
                repeating=input_dict.get("repeating"),
                translated_texts=[
                    OdmTranslatedTextModel(
                        text_type=translated_text["text_type"],
                        language=translated_text["language"],
                        text=translated_text["text"],
                    )
                    for translated_text in input_dict["translated_texts"]
                ],
                aliases=[
                    OdmAliasModel(name=alias["name"], context=alias["context"])
                    for alias in input_dict["aliases"]
                ],
                item_group_uids=input_dict["item_group_uids"],
                vendor_element_uids=input_dict["vendor_element_uids"],
                vendor_attribute_uids=input_dict["vendor_attribute_uids"],
                vendor_element_attribute_uids=input_dict[
                    "vendor_element_attribute_uids"
                ],
            ),
            library=LibraryVO.from_input_values_2(
                library_name=input_dict["library_name"],
                is_library_editable_callback=(
                    lambda _: input_dict["is_library_editable"]
                ),
            ),
            item_metadata=LibraryItemMetadataVO.from_repository_values(
                change_description=input_dict["change_description"],
                status=LibraryItemStatus(input_dict.get("status")),
                author_id=input_dict["author_id"],
                author_username=input_dict.get("author_username"),
                start_date=convert_to_datetime(value=input_dict["start_date"]),
                end_date=None,
                major_version=int(major),
                minor_version=int(minor),
            ),
        )

        return odm_form_ar

    def specific_alias_clause(self, **kwargs) -> str:
        return """
WITH *,
odm_value.oid AS oid,
toString(odm_value.repeating) AS repeating,
odm_value.sdtm_version AS sdtm_version,

[(odm_value)-[:HAS_TRANSLATED_TEXT]->(dv:OdmTranslatedText) | {text_type: dv.text_type, language: dv.language, text: dv.text}] AS translated_texts,

[(odm_value)-[:HAS_ALIAS]->(av:OdmAlias) | {name: av.name, context: av.context}] AS aliases,

[(odm_value)-[igref:ITEM_GROUP_REF]->(igv:OdmItemGroupValue)<-[:HAS_VERSION]-(igr:OdmItemGroupRoot) |
{uid: igr.uid, name: igv.name, order: igref.order, mandatory: igref.mandatory}] AS item_groups,

[(odm_value)-[hve:HAS_VENDOR_ELEMENT]->(vev:OdmVendorElementValue)<-[:HAS_VERSION]-(ver:OdmVendorElementRoot) |
{uid: ver.uid, name: vev.name, value: hve.value}] AS vendor_elements,

[(odm_value)-[hva:HAS_VENDOR_ATTRIBUTE]->(vav:OdmVendorAttributeValue)<-[:HAS_VERSION]-(var:OdmVendorAttributeRoot) |
{uid: var.uid, name: vav.name, value: hva.value}] AS vendor_attributes,

[(odm_value)-[hvea:HAS_VENDOR_ELEMENT_ATTRIBUTE]->(vav:OdmVendorAttributeValue)<-[:HAS_VERSION]-(var:OdmVendorAttributeRoot) |
{uid: var.uid, name: vav.name, value: hvea.value}] AS vendor_element_attributes

WITH *,
apoc.coll.toSet([item_group in item_groups | item_group.uid]) AS item_group_uids,
apoc.coll.toSet([vendor_element in vendor_elements | vendor_element.uid]) AS vendor_element_uids,
apoc.coll.toSet([vendor_attribute in vendor_attributes | vendor_attribute.uid]) AS vendor_attribute_uids,
apoc.coll.toSet([vendor_element_attribute in vendor_element_attributes | vendor_element_attribute.uid]) AS vendor_element_attribute_uids
"""

    def _get_or_create_value(
        self,
        root: VersionRoot,
        ar: OdmFormAR,
        force_new_value_node: bool = False,
    ) -> VersionValue:
        current_latest = root.has_latest_value.single()
        old_item_group_ref_nodes = (
            current_latest.item_group_ref.all() if current_latest else []
        )
        new_item_group_ref_nodes = [
            old_item_group_root.has_latest_value.single()
            for old_item_group_ref_node in old_item_group_ref_nodes
            if (old_item_group_root := old_item_group_ref_node.has_root.single())
        ]

        new_value = super()._get_or_create_value(root, ar, force_new_value_node)

        for old_item_group_ref_node, new_item_group_ref_node in zip(
            old_item_group_ref_nodes, new_item_group_ref_nodes
        ):
            params = current_latest.item_group_ref.relationship(old_item_group_ref_node)
            new_value.item_group_ref.connect(
                new_item_group_ref_node,
                {
                    "order_number": params.order_number,
                    "mandatory": params.mandatory,
                    "collection_exception_condition_oid": params.collection_exception_condition_oid,
                    "vendor": params.vendor,
                },
            )

        if ar.should_disconnect_relationships:
            for old_item_group_ref_node in old_item_group_ref_nodes:
                current_latest.item_group_ref.disconnect(old_item_group_ref_node)

        self.manage_vendor_relationships(
            current_latest, new_value, ar.should_disconnect_relationships
        )
        self.connect_translated_texts(ar.odm_vo.translated_texts, new_value)
        self.connect_aliases(ar.odm_vo.aliases, new_value)

        return new_value

    def _create_new_value_node(self, ar: OdmFormAR) -> OdmFormValue:
        value_node = super()._create_new_value_node(ar=ar)

        value_node.save()

        value_node.oid = ar.odm_vo.oid
        value_node.sdtm_version = ar.odm_vo.sdtm_version
        value_node.repeating = ar.odm_vo.repeating

        return value_node

    def _has_data_changed(self, ar: OdmFormAR, value: OdmFormValue) -> bool:
        are_odm_properties_changed = super()._has_data_changed(ar=ar, value=value)

        translated_text_nodes = {
            OdmTranslatedTextModel(
                text_type=translated_text_node.text_type,
                language=translated_text_node.language,
                text=translated_text_node.text,
            )
            for translated_text_node in value.has_translated_text.all()
        }
        alias_nodes = {
            OdmAliasModel(name=alias_node.name, context=alias_node.context)
            for alias_node in value.has_alias.all()
        }

        are_rels_changed = (
            set(ar.odm_vo.translated_texts) != translated_text_nodes
            or set(ar.odm_vo.aliases) != alias_nodes
        )

        return (
            are_odm_properties_changed
            or are_rels_changed
            or ar.odm_vo.oid != value.oid
            or ar.odm_vo.sdtm_version != value.sdtm_version
            or ar.odm_vo.repeating != value.repeating
        )

    def find_by_uid_with_study_event_relation(
        self, uid: str, study_event_uid: str, study_event_version: str
    ) -> OdmFormRefVO:
        rs, _ = db.cypher_query(
            """
            MATCH (:OdmStudyEventRoot {uid: $study_event_uid})-[:HAS_VERSION {version: $study_event_version}]->(:OdmStudyEventValue)
            -[ref:FORM_REF]->(value:OdmFormValue)

            MATCH (value)<-[hv_rel:HAS_VERSION]-(:OdmFormRoot {uid: $uid})
            WITH value, ref, hv_rel
            ORDER BY hv_rel.start_date DESC
            WITH value, ref, collect(hv_rel) AS hv_rels

            RETURN
                value.oid AS oid,
                value.name AS name,
                hv_rels[0].version AS version,
                ref.order_number AS order_number,
                ref.mandatory AS mandatory,
                ref.locked AS locked,
                ref.collection_exception_condition_oid AS collection_exception_condition_oid
            """,
            params={
                "uid": uid,
                "study_event_uid": study_event_uid,
                "study_event_version": study_event_version,
            },
        )

        return OdmFormRefVO.from_repository_values(
            uid=uid,
            oid=rs[0][0],
            name=rs[0][1],
            study_event_uid=study_event_uid,
            version=rs[0][2],
            order_number=rs[0][3],
            mandatory=rs[0][4],
            locked=rs[0][5],
            collection_exception_condition_oid=rs[0][6],
        )

    @ensure_transaction(db)
    def _connect_relationships_to_new_value_node(
        self, root: VersionRoot, _: VersionValue
    ) -> None:
        """
        - Upgrades all incoming FORM_REF relationships to the second latest version to point
        to the latest version of OdmFormValue, preserving relationship properties.
        """
        db.cypher_query(
            f"""
            MATCH (root:{self.root_class.__name__} {{uid: $root_uid}})-[ver_rel:HAS_VERSION]->(value:{self.value_class.__name__})

            WITH root, ver_rel, value
            ORDER BY ver_rel.start_date DESC, ver_rel.end_date DESC
            LIMIT 2
            WITH root, collect(value) AS values
            WITH root, values[0] as latest_value, values[1] as second_latest_value

            MATCH (:OdmStudyEventRoot)-[p_ver_rel:HAS_VERSION]->(parent_value:OdmStudyEventValue)-[ref_rel:FORM_REF]->(second_latest_value)
            WHERE p_ver_rel.end_date IS NULL AND p_ver_rel.status = "Draft"

            WITH latest_value, ref_rel, parent_value,
                ref_rel.order_number AS order_number,
                ref_rel.mandatory AS mandatory,
                ref_rel.locked AS locked,
                ref_rel.collection_exception_condition_oid AS collection_exception_condition_oid

            CREATE (parent_value)-[new_ref_rel:FORM_REF]->(latest_value)

            SET new_ref_rel.order_number = order_number,
                new_ref_rel.mandatory = mandatory,
                new_ref_rel.locked = locked,
                new_ref_rel.collection_exception_condition_oid = collection_exception_condition_oid

            DELETE ref_rel
            """,
            {"root_uid": root.uid},
        )

    @ensure_transaction(db)
    def get_hydrated_forms_by_study(self, study_uid: str) -> dict[str, list[Any]]:
        from datetime import datetime, timezone
        from clinical_mdr_api.models.odms.form import OdmForm
        from clinical_mdr_api.models.odms.common_models import (
            OdmTranslatedTextModel,
            OdmAliasModel,
            OdmRefVendor,
            OdmRefVendorAttributeModel,
        )
        from clinical_mdr_api.models.odms.item_group import (
            OdmItemGroup,
            OdmItemGroupRefModel,
        )
        from clinical_mdr_api.models.odms.item import (
            OdmItem,
            OdmItemRefModel,
        )
        from clinical_mdr_api.models.controlled_terminologies.ct_codelist_attributes import (
            CTCodelistAttributes,
            CTCodelistAttributesSimpleModel,
        )
        from common.utils import booltostr

        query = """
        MATCH (study_root:StudyRoot {uid: $study_uid})-[:LATEST|HAS_VERSION]->(study_value:StudyValue)-[:HAS_STUDY_VISIT]->(study_visit:StudyVisit)
        MATCH (se_root:OdmStudyEventRoot {uid: study_visit.uid})-[:LATEST|HAS_VERSION]->(se_value:OdmStudyEventValue)-[:FORM_REF]->(form_value:OdmFormValue)
        MATCH (form_root:OdmFormRoot)-[:LATEST|HAS_VERSION]->(form_value)

        WITH DISTINCT form_root, form_value
        OPTIONAL MATCH (library:Library)-[:CONTAINS_ODM]->(form_root)

        CALL {
            WITH form_root, form_value
            MATCH (form_root)-[hv:HAS_VERSION]->(form_value)
            WITH hv
            ORDER BY
                toInteger(split(hv.version, '.')[0]) ASC,
                toInteger(split(hv.version, '.')[1]) ASC,
                hv.end_date ASC,
                hv.start_date ASC
            RETURN hv AS form_version_rel
        }

        OPTIONAL MATCH (author:User) WHERE author.user_id = form_version_rel.author_id

        WITH *,
        [(form_value)-[:HAS_TRANSLATED_TEXT]->(tt:OdmTranslatedText) | {text_type: tt.text_type, language: tt.language, text: tt.text}] AS form_translated_texts,
        [(form_value)-[:HAS_ALIAS]->(al:OdmAlias) | {name: al.name, context: al.context}] AS form_aliases

        CALL {
            WITH form_value
            OPTIONAL MATCH (form_value)-[ig_ref:ITEM_GROUP_REF]->(ig_value:OdmItemGroupValue)<-[:LATEST|HAS_VERSION]-(ig_root:OdmItemGroupRoot)
            WHERE ig_value IS NOT NULL
            
            CALL {
                WITH ig_root, ig_value
                MATCH (ig_root)-[ig_hv:HAS_VERSION]->(ig_value)
                WITH ig_hv
                ORDER BY
                    toInteger(split(ig_hv.version, '.')[0]) ASC,
                    toInteger(split(ig_hv.version, '.')[1]) ASC,
                    ig_hv.end_date ASC,
                    ig_hv.start_date ASC
                RETURN ig_hv AS ig_version_rel
            }
            
            WITH ig_root, ig_value, ig_ref, ig_version_rel,
            [(ig_value)-[:HAS_TRANSLATED_TEXT]->(ig_tt:OdmTranslatedText) | {text_type: ig_tt.text_type, language: ig_tt.language, text: ig_tt.text}] AS ig_translated_texts,
            [(ig_value)-[:HAS_ALIAS]->(ig_al:OdmAlias) | {name: ig_al.name, context: ig_al.context}] AS ig_aliases
            
            CALL {
                WITH ig_value
                OPTIONAL MATCH (ig_value)-[i_ref:ITEM_REF]->(i_value:OdmItemValue)<-[:LATEST|HAS_VERSION]-(i_root:OdmItemRoot)
                WHERE i_value IS NOT NULL
                
                CALL {
                    WITH i_root, i_value
                    MATCH (i_root)-[i_hv:HAS_VERSION]->(i_value)
                    WITH i_hv
                    ORDER BY
                        toInteger(split(i_hv.version, '.')[0]) ASC,
                        toInteger(split(i_hv.version, '.')[1]) ASC,
                        i_hv.end_date ASC,
                        i_hv.start_date ASC
                    RETURN i_hv AS i_version_rel
                }
                
                WITH i_root, i_value, i_ref, i_version_rel,
                [(i_value)-[:HAS_TRANSLATED_TEXT]->(i_tt:OdmTranslatedText) | {text_type: i_tt.text_type, language: i_tt.language, text: i_tt.text}] AS i_translated_texts,
                [(i_value)-[:HAS_ALIAS]->(i_al:OdmAlias) | {name: i_al.name, context: i_al.context}] AS i_aliases
                
                OPTIONAL MATCH (i_value)-[:HAS_CODELIST]->(cl_root:CTCodelistRoot)-[:HAS_ATTRIBUTES_ROOT]->(cl_attr_root:CTCodelistAttributesRoot)-[:LATEST]->(cl_attr_value:CTCodelistAttributesValue)
                
                RETURN collect({
                    uid: i_root.uid,
                    oid: i_value.oid,
                    name: i_value.name,
                    datatype: i_value.datatype,
                    length: i_value.length,
                    significant_digits: i_value.significant_digits,
                    sas_field_name: i_value.sas_field_name,
                    sds_var_name: i_value.sds_var_name,
                    origin: i_value.origin,
                    comment: i_value.comment,
                    prompt: i_value.prompt,
                    order_number: toInteger(i_ref.order_number),
                    mandatory: i_ref.mandatory,
                    collection_exception_condition_oid: i_ref.collection_exception_condition_oid,
                    method_oid: i_ref.method_oid,
                    role: i_ref.role,
                    version: i_version_rel.version,
                    translated_texts: i_translated_texts,
                    aliases: i_aliases,
                    codelist: CASE WHEN cl_root IS NOT NULL THEN {
                        uid: cl_root.uid,
                        oid: cl_root.uid,
                        codelist_uid: cl_root.uid,
                        name: cl_attr_value.name,
                        datatype: cl_attr_value.datatype,
                        sas_format_name: cl_attr_value.sas_format_name,
                        submission_value: cl_attr_value.submission_value,
                        extensible: coalesce(cl_attr_value.extensible, false),
                        preferred_term: cl_attr_value.preferred_term,
                        synonyms: split(coalesce(cl_attr_value.synonyms, ""), "|"),
                        is_ordinal: coalesce(cl_attr_value.is_ordinal, false),
                        allows_multi_choice: cl_attr_value.allows_multi_choice
                    } ELSE null END
                }) AS items_list
            }
            
            RETURN collect({
                uid: ig_root.uid,
                oid: ig_value.oid,
                name: ig_value.name,
                repeating: toString(ig_value.repeating),
                is_reference_data: toString(ig_value.is_reference_data),
                sas_dataset_name: ig_value.sas_dataset_name,
                origin: ig_value.origin,
                purpose: ig_value.purpose,
                comment: ig_value.comment,
                order_number: toInteger(ig_ref.order_number),
                mandatory: ig_ref.mandatory,
                collection_exception_condition_oid: ig_ref.collection_exception_condition_oid,
                version: ig_version_rel.version,
                translated_texts: ig_translated_texts,
                aliases: ig_aliases,
                items: items_list
            }) AS item_groups_list
        }

        RETURN
            form_root.uid AS uid,
            form_value.oid AS oid,
            form_value.name AS name,
            toString(form_value.repeating) AS repeating,
            form_value.sdtm_version AS sdtm_version,
            coalesce(library.name, "Sponsor") AS library_name,
            form_version_rel.start_date AS start_date,
            form_version_rel.end_date AS end_date,
            form_version_rel.status AS status,
            form_version_rel.version AS version,
            form_version_rel.change_description AS change_description,
            coalesce(author.username, form_version_rel.author_id) AS author_username,
            form_translated_texts AS translated_texts,
            form_aliases AS aliases,
            item_groups_list AS item_groups
        """
        results, _ = db.cypher_query(query, {"study_uid": study_uid})

        forms_list = []
        item_groups_dict = {}
        items_dict = {}
        codelists_dict = {}

        for row in results:
            form_uid = row[0]
            form_oid = row[1]
            form_name = row[2]
            form_repeating_val = row[3]
            form_sdtm_version = row[4]
            form_library_name = row[5]
            form_start_date = row[6] or datetime.now(timezone.utc)
            form_end_date = row[7]
            form_status = row[8] or "Draft"
            form_version = row[9] or "0.1"
            form_change_description = row[10] or "Created"
            form_author_username = row[11] or "unknown"
            form_translated_texts = row[12] or []
            form_aliases = row[13] or []
            form_item_groups = row[14] or []

            tt_models = [
                OdmTranslatedTextModel(
                    text_type=tt["text_type"],
                    language=tt["language"],
                    text=tt["text"]
                )
                for tt in form_translated_texts
            ]
            alias_models = [
                OdmAliasModel(
                    name=al["name"],
                    context=al["context"]
                )
                for al in form_aliases
            ]

            ig_ref_models = []
            for ig in form_item_groups:
                ig_uid = ig["uid"]
                if not ig_uid:
                    continue
                
                ig_ref_models.append(
                    OdmItemGroupRefModel(
                        uid=ig_uid,
                        oid=ig["oid"],
                        name=ig["name"],
                        version=ig["version"],
                        order_number=ig["order_number"],
                        mandatory=booltostr(ig["mandatory"]),
                        collection_exception_condition_oid=ig["collection_exception_condition_oid"],
                        vendor=OdmRefVendor(attributes=[])
                    )
                )

                if ig_uid not in item_groups_dict:
                    ig_tt_models = [
                        OdmTranslatedTextModel(
                            text_type=tt["text_type"],
                            language=tt["language"],
                            text=tt["text"]
                        )
                        for tt in (ig["translated_texts"] or [])
                    ]
                    ig_alias_models = [
                        OdmAliasModel(
                            name=al["name"],
                            context=al["context"]
                        )
                        for al in (ig["aliases"] or [])
                    ]

                    i_ref_models = []
                    for item in (ig["items"] or []):
                        item_uid = item["uid"]
                        if not item_uid:
                            continue
                        
                        i_ref_models.append(
                            OdmItemRefModel(
                                uid=item_uid,
                                oid=item["oid"],
                                name=item["name"],
                                version=item["version"],
                                order_number=item["order_number"],
                                mandatory=booltostr(item["mandatory"]),
                                collection_exception_condition_oid=item["collection_exception_condition_oid"],
                                method_oid=item["method_oid"],
                                role=item["role"],
                                role_codelist_oid=None,
                                vendor=OdmRefVendor(attributes=[])
                            )
                        )

                        if item_uid not in items_dict:
                            item_tt_models = [
                                OdmTranslatedTextModel(
                                    text_type=tt["text_type"],
                                    language=tt["language"],
                                    text=tt["text"]
                                )
                                for tt in (item["translated_texts"] or [])
                            ]
                            item_alias_models = [
                                OdmAliasModel(
                                    name=al["name"],
                                    context=al["context"]
                                )
                                for al in (item["aliases"] or [])
                            ]

                            cl_simple_model = None
                            if item["codelist"]:
                                cl = item["codelist"]
                                cl_simple_model = CTCodelistAttributesSimpleModel(
                                    uid=cl["uid"],
                                    name=cl["name"],
                                    datatype=cl["datatype"],
                                    sas_format_name=cl["sas_format_name"],
                                    submission_value=cl["submission_value"],
                                    extensible=cl["extensible"],
                                    preferred_term=cl["preferred_term"],
                                    synonyms=cl["synonyms"],
                                    is_ordinal=cl["is_ordinal"],
                                    allows_multi_choice=cl["allows_multi_choice"]
                                )

                                cl_uid = cl["uid"]
                                if cl_uid not in codelists_dict:
                                    codelists_dict[cl_uid] = CTCodelistAttributes(
                                        codelist_uid=cl["uid"],
                                        name=cl["name"] or "",
                                        submission_value=cl["submission_value"] or "",
                                        definition=cl["preferred_term"] or "",
                                        extensible=cl["extensible"] or False,
                                        is_ordinal=cl["is_ordinal"] or False,
                                        catalogue_names=[],
                                        child_codelist_uids=[],
                                        library_name=form_library_name,
                                        start_date=form_start_date,
                                        end_date=form_end_date,
                                        status=form_status,
                                        version=form_version,
                                        change_description=form_change_description,
                                        author_username=form_author_username,
                                        possible_actions=[]
                                    )

                            items_dict[item_uid] = OdmItem(
                                uid=item_uid,
                                oid=item["oid"],
                                name=item["name"],
                                datatype=item["datatype"],
                                length=item["length"],
                                significant_digits=item["significant_digits"],
                                sas_field_name=item["sas_field_name"],
                                sds_var_name=item["sds_var_name"],
                                origin=item["origin"],
                                comment=item["comment"],
                                prompt=item["prompt"],
                                library_name=form_library_name,
                                start_date=form_start_date,
                                end_date=form_end_date,
                                status=form_status,
                                version=item["version"],
                                change_description=form_change_description,
                                author_username=form_author_username,
                                translated_texts=item_tt_models,
                                aliases=item_alias_models,
                                unit_definitions=[],
                                codelist=cl_simple_model,
                                terms=[],
                                activity_instances=[],
                                vendor_elements=[],
                                vendor_attributes=[],
                                vendor_element_attributes=[],
                                possible_actions=[]
                            )

                    item_groups_dict[ig_uid] = OdmItemGroup(
                        uid=ig_uid,
                        oid=ig["oid"],
                        name=ig["name"],
                        repeating=booltostr(ig["repeating"]),
                        is_reference_data=booltostr(ig["is_reference_data"]),
                        sas_dataset_name=ig["sas_dataset_name"],
                        origin=ig["origin"],
                        purpose=ig["purpose"],
                        comment=ig["comment"],
                        library_name=form_library_name,
                        start_date=form_start_date,
                        end_date=form_end_date,
                        status=form_status,
                        version=ig["version"] or "0.1",
                        change_description=form_change_description,
                        author_username=form_author_username,
                        translated_texts=ig_tt_models,
                        aliases=ig_alias_models,
                        sdtm_domains=[],
                        items=i_ref_models,
                        vendor_elements=[],
                        vendor_attributes=[],
                        vendor_element_attributes=[],
                        possible_actions=[]
                    )

            form_model = OdmForm(
                uid=form_uid,
                oid=form_oid,
                name=form_name,
                repeating=booltostr(form_repeating_val),
                sdtm_version=form_sdtm_version,
                library_name=form_library_name,
                start_date=form_start_date,
                end_date=form_end_date,
                status=form_status,
                version=form_version,
                change_description=form_change_description,
                author_username=form_author_username,
                translated_texts=tt_models,
                aliases=alias_models,
                item_groups=ig_ref_models,
                vendor_elements=[],
                vendor_attributes=[],
                vendor_element_attributes=[],
                possible_actions=[]
            )
            forms_list.append(form_model)

        return {
            "forms": forms_list,
            "item_groups": list(item_groups_dict.values()),
            "items": list(items_dict.values()),
            "codelists": list(codelists_dict.values()),
        }

