from typing import Annotated

from pydantic import ConfigDict, Field

from clinical_mdr_api.models.utils import BaseModel, PostInputModel


class CompactActivityItemClass(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: Annotated[
        str, Field(json_schema_extra={"source": "has_activity_item_class.uid"})
    ]
    name: Annotated[
        str | None,
        Field(
            json_schema_extra={
                "source": "has_activity_item_class.has_latest_value.name",
                "nullable": True,
            },
        ),
    ] = None


class CompactCTTerm(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: Annotated[
        str | None,
        Field(json_schema_extra={"source": "has_ct_term.uid", "nullable": True}),
    ] = None
    name: Annotated[
        str | None,
        Field(
            json_schema_extra={
                "source": "has_ct_term.has_name_root.has_latest_value.name",
                "nullable": True,
            },
        ),
    ] = None


class CompactUnitDefinition(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: Annotated[
        str | None,
        Field(
            json_schema_extra={"source": "has_unit_definition.uid", "nullable": True}
        ),
    ] = None
    name: Annotated[
        str | None,
        Field(
            json_schema_extra={
                "source": "has_unit_definition.has_latest_value.name",
                "nullable": True,
            },
        ),
    ] = None
    dimension_name: Annotated[
        str | None,
        Field(
            json_schema_extra={
                "source": "has_unit_definition.has_latest_value.has_ct_dimension.has_name_root.has_latest_value.name",
                "nullable": True,
            },
        ),
    ] = None


class CompactOdmForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: Annotated[
        str | None,
        Field(json_schema_extra={"source": "has_odm_form.uid", "nullable": True}),
    ] = None
    oid: Annotated[
        str | None,
        Field(
            json_schema_extra={
                "source": "has_odm_form.has_latest_value.oid",
                "nullable": True,
            },
        ),
    ] = None
    name: Annotated[
        str | None,
        Field(
            json_schema_extra={
                "source": "has_odm_form.has_latest_value.name",
                "nullable": True,
            },
        ),
    ] = None


class CompactOdmItemGroup(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: Annotated[
        str | None,
        Field(json_schema_extra={"source": "has_odm_item_group.uid", "nullable": True}),
    ] = None
    oid: Annotated[
        str | None,
        Field(
            json_schema_extra={
                "source": "has_odm_item_group.has_latest_value.oid",
                "nullable": True,
            },
        ),
    ] = None
    name: Annotated[
        str | None,
        Field(
            json_schema_extra={
                "source": "has_odm_item_group.has_latest_value.name",
                "nullable": True,
            },
        ),
    ] = None


class CompactOdmItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: Annotated[
        str | None,
        Field(json_schema_extra={"source": "has_odm_item.uid", "nullable": True}),
    ] = None
    oid: Annotated[
        str | None,
        Field(
            json_schema_extra={
                "source": "has_odm_item.has_latest_value.oid",
                "nullable": True,
            },
        ),
    ] = None
    name: Annotated[
        str | None,
        Field(
            json_schema_extra={
                "source": "has_odm_item.has_latest_value.name",
                "nullable": True,
            },
        ),
    ] = None


class ActivityItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    activity_item_class: Annotated[CompactActivityItemClass, Field()]
    ct_terms: list[CompactCTTerm] = Field(default_factory=list)
    unit_definitions: list[CompactUnitDefinition] = Field(default_factory=list)
    is_adam_param_specific: Annotated[bool, Field()]
    odm_forms: list[CompactOdmForm] = Field(default_factory=list)
    odm_item_groups: list[CompactOdmItemGroup] = Field(default_factory=list)
    odm_items: list[CompactOdmItem] = Field(default_factory=list)


class ActivityItemCreateInput(PostInputModel):
    activity_item_class_uid: Annotated[str, Field(min_length=1)]
    ct_term_uids: Annotated[list[str], Field()]
    unit_definition_uids: Annotated[list[str], Field()]
    is_adam_param_specific: Annotated[bool, Field()]
    odm_form_uids: list[str] = Field(default_factory=list)
    odm_item_group_uids: list[str] = Field(default_factory=list)
    odm_item_uids: list[str] = Field(default_factory=list)
