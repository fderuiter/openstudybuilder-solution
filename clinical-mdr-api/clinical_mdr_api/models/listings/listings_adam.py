from typing import Annotated, Any, Self

from pydantic import Field

from clinical_mdr_api.models.utils import BaseModel


class StudyEndpntAdamListing(BaseModel):
    STUDYID: Annotated[str, Field()]
    OBJTVLVL: Annotated[
        str | None,
        Field(description="Objective Level", json_schema_extra={"nullable": True}),
    ] = None
    OBJTV: Annotated[
        str, Field(description="Objective", json_schema_extra={"format": "html"})
    ]
    OBJTVPT: Annotated[
        str | None,
        Field(description="Objective Plain Text", json_schema_extra={"nullable": True}),
    ] = None
    ENDPNTLVL: Annotated[
        str | None,
        Field(
            description="Endpoint Level",
            json_schema_extra={"nullable": True},
        ),
    ] = None
    ENDPNTSL: Annotated[
        str | None,
        Field(description="Endpoint Sub-level", json_schema_extra={"nullable": True}),
    ] = None
    ENDPNT: Annotated[
        str | None,
        Field(description="Endpoint Plain", json_schema_extra={"nullable": True}),
    ] = None
    ENDPNTPT: Annotated[
        str | None,
        Field(description="Endpoint Plain Text", json_schema_extra={"nullable": True}),
    ] = None
    UNITDEF: Annotated[
        str | None,
        Field(description="Unit Definition", json_schema_extra={"nullable": True}),
    ] = None
    UNIT: Annotated[str | None, Field(json_schema_extra={"nullable": True})] = None
    TMFRM: Annotated[
        str | None,
        Field(description="Time Frame", json_schema_extra={"nullable": True}),
    ] = None
    TMFRMPT: Annotated[
        str | None,
        Field(
            description="Time Frame Plain Text", json_schema_extra={"nullable": True}
        ),
    ] = None
    RACT: Annotated[
        list[str] | None,
        Field(
            description="Array list for all related Activities as Template Parameter in either Objective or Endpoint",
            json_schema_extra={"nullable": True},
        ),
    ] = None
    RACTSGRP: Annotated[
        list[str] | None,
        Field(
            description="Array list for all related Activity Subgroups as Template Parameter in either Objective or Endpoint",
            json_schema_extra={"nullable": True},
        ),
    ] = None
    RACTGRP: Annotated[
        list[str] | None,
        Field(
            description="Array list for all related Activity Groups as Template Parameter in either Objective or Endpoint",
            json_schema_extra={"nullable": True},
        ),
    ] = None
    RACTINST: Annotated[
        list[str] | None,
        Field(
            description="Array list for all related Activity Instances as Template Parameter in either Objective or Endpoint",
            json_schema_extra={"nullable": True},
        ),
    ] = None

    @classmethod
    def from_query(cls, query_result: dict[Any, Any]) -> Self:
        return cls(
            STUDYID=query_result["STUDYID"],
            OBJTVLVL=query_result["OBJTVLVL"],
            OBJTV=query_result["OBJTV"],
            OBJTVPT=query_result["OBJTVPT"],
            ENDPNTLVL=query_result["ENDPNTLVL"],
            ENDPNTSL=query_result["ENDPNTSL"],
            ENDPNT=query_result["ENDPNT"],
            ENDPNTPT=query_result["ENDPNTPT"],
            UNITDEF=query_result["UNITDEF"],
            UNIT=query_result["UNIT"],
            TMFRM=query_result["TMFRM"],
            TMFRMPT=query_result["TMFRMPT"],
            RACT=query_result["RACT"],
            RACTSGRP=query_result["RACTSGRP"],
            RACTGRP=query_result["RACTGRP"],
            RACTINST=query_result["RACTINST"],
        )


class StudyVisitAdamListing(BaseModel):
    STUDYID: Annotated[str, Field(description="Unique identifier for a study.")]
    VISTPCD: Annotated[str, Field(description="Visit Type Code")]
    AVISITN: Annotated[
        int,
        Field(
            description="1. Clinical encounter number 2. Numeric version of VISIT, used for sorting."
        ),
    ]
    AVISIT: Annotated[
        str | None,
        Field(
            description="""Visit Name. 1. Protocol-defined description of clinical encounter. 2. May
        be used in addition to VISITNUM and/or VISITDY as a text description of the clinical encounter.""",
            json_schema_extra={"nullable": True},
        ),
    ] = None
    AVISIT1N: Annotated[
        int | None,
        Field(
            description="1. Planned study day of VISIT. 2. Due to its sequential nature, used for sorting.",
            json_schema_extra={"nullable": True},
        ),
    ] = None
    VISLABEL: Annotated[
        str | None,
        Field(description="Visit Label", json_schema_extra={"nullable": True}),
    ] = None
    AVISIT1: Annotated[
        str | None,
        Field(description="Planned day", json_schema_extra={"nullable": True}),
    ] = None
    AVISIT2: Annotated[
        str | None,
        Field(description="Planned Week Text", json_schema_extra={"nullable": True}),
    ] = None
    AVISIT2N: Annotated[
        str | None,
        Field(description="Planned Week Number", json_schema_extra={"nullable": True}),
    ] = None

    @classmethod
    def from_query(cls, query_result: dict[Any, Any]) -> Self:
        return cls(
            STUDYID=query_result["STUDYID"],
            VISTPCD=query_result["VISIT_TYPE_NAME"],
            AVISITN=query_result["VISIT_NUM"],
            AVISIT=query_result["VISIT_NAME"],
            AVISIT1N=query_result["DAY_VALUE"],
            VISLABEL=query_result["VISIT_SHORT_LABEL"],
            AVISIT1=query_result["DAY_NAME"],
            AVISIT2=query_result["WEEK_NAME"],
            AVISIT2N=str(query_result["WEEK_VALUE"]),
        )
