import re
from datetime import datetime
from io import BytesIO
from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, File, Path, Query, Response, UploadFile
from fastapi.responses import StreamingResponse

from clinical_mdr_api.domains._utils import ObjectStatus
from clinical_mdr_api.domains.concepts.utils import ExporterType, TargetType
from clinical_mdr_api.routers import _generic_descriptions
from clinical_mdr_api.services.concepts.odms.odm_clinspark_import import (
    OdmClinicalXmlImporterService,
)
from clinical_mdr_api.services.concepts.odms.odm_csv_exporter import (
    OdmCsvExporterService,
)
from clinical_mdr_api.services.concepts.odms.odm_xml_exporter import (
    OdmXmlExporterService,
)
from clinical_mdr_api.services.concepts.odms.odm_xml_importer import (
    OdmXmlImporterService,
)
from clinical_mdr_api.services.concepts.odms.odm_xml_stylesheets import (
    OdmXmlStylesheetService,
)
from common.auth import rbac
from common.auth.dependencies import security
from common.exceptions import ValidationException

# Prefixed with "/concepts/odms/metadata"
router = APIRouter()


MAPPER_DESCRIPTION = """
Optional CSV file providing mapping rules between a legacy vendor extension and its OpenStudyBuilder equivalent.\n\n
Only CSV format is supported.\n\n
Following headers must exist: `type`, `parent`, `from_name`, `to_name`, `to_alias`, `from_alias` and `alias_context`\n\n
Allowed values for `type` are: `attribute` and `element`\n\n
Allowed values for `to_alias` and `from_alias` are: `true` and `false`. Anything other than `true` is considered `false`\n\n
If `to_alias` is true `type` must be `attribute`\n\n
If `to_alias` is true `to_name` is ignored\n\n
If `from_alias` is true `alias_context` must be provided\n\n
If `parent` is empty or `*` is given then the mapping will apply to all occurrences in the entire XML file"""


@router.post(
    "/xmls/export",
    dependencies=[security, rbac.LIBRARY_READ],
    summary="Export ODM XML",
    status_code=200,
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/xml": {}, "application/pdf": {}},
        },
        403: _generic_descriptions.ERROR_403,
        404: _generic_descriptions.ERROR_404,
    },
    response_class=Response,
)
def get_odm_document(
    target_uid: str,
    target_type: TargetType,
    allowed_namespaces: Annotated[
        list[str] | None,
        Query(
            description="Names of the Vendor Namespaces to export or `*` to export all available Vendor Namespaces. If not specified, no Vendor Namespaces will be exported."
        ),
    ] = None,
    status: Annotated[ObjectStatus, Query()] = ObjectStatus.LATEST_FINAL,
    pdf: Annotated[
        bool, Query(description="Whether or not to export the ODM as a PDF.")
    ] = False,
    stylesheet: str | None = None,
    mapper_file: Annotated[
        UploadFile | None, File(description=MAPPER_DESCRIPTION)
    ] = None,
):
    if allowed_namespaces is None:
        allowed_namespaces = []
    odm_xml_export_service = OdmXmlExporterService(
        target_uid,
        target_type,
        status,
        allowed_namespaces,
        pdf,
        stylesheet,
        mapper_file,
    )
    rs = odm_xml_export_service.get_odm_document()

    if pdf:
        buffer_io = BytesIO()
        buffer_io.write(rs)
        pdf_bytes = buffer_io.getvalue()
        buffer_io.close()
        return Response(
            pdf_bytes,
            headers={
                "Content-Disposition": f"attachment; filename=CRF - {datetime.now()}.pdf"
            },
            media_type="application/pdf",
        )

    return Response(
        content=rs,
        media_type="application/xml",
        headers={
            "Content-Disposition": f'attachment; filename="odm_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xml"',
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.post(
    "/csvs/export",
    dependencies=[security, rbac.LIBRARY_READ],
    summary="Export ODM CSV",
    status_code=200,
    responses={
        200: {"description": "Successful Response", "content": {"text/csv": {}}},
        403: _generic_descriptions.ERROR_403,
        404: _generic_descriptions.ERROR_404,
    },
    response_class=StreamingResponse,
)
def get_odm_csv(target_uid: str, target_type: TargetType):
    odm_csv_exporter_service = OdmCsvExporterService(target_uid, target_type)
    csv_data = odm_csv_exporter_service.get_odm_csv()

    return StreamingResponse(
        iter(csv_data),
        200,
        {"Content-Disposition": "attachment; filename=odm_metadata.csv"},
        "text/csv",
    )


@router.post(
    "/xmls/import",
    dependencies=[security, rbac.LIBRARY_WRITE],
    summary="Import ODM XML",
    status_code=201,
    responses={
        403: _generic_descriptions.ERROR_403,
        404: _generic_descriptions.ERROR_404,
    },
)
def store_odm_xml(
    xml_file: Annotated[
        UploadFile, File(description="The ODM XML file to upload. Supports ODM V1.")
    ],
    exporter: Annotated[
        ExporterType,
        Query(
            description="The system that exported this ODM XML file.",
        ),
    ] = ExporterType.OSB,
    mapper_file: Annotated[
        UploadFile | None, File(description=MAPPER_DESCRIPTION)
    ] = None,
):
    if exporter == ExporterType.OSB:
        odm_xml_importer_service = OdmXmlImporterService(xml_file, mapper_file)
    else:
        odm_xml_importer_service = OdmClinicalXmlImporterService(xml_file, mapper_file)

    return odm_xml_importer_service.store_odm_xml()


@router.get(
    "/xmls/stylesheets",
    dependencies=[security, rbac.LIBRARY_READ],
    summary="Listing of all available ODM XML Stylesheet names",
    status_code=200,
    responses={
        403: _generic_descriptions.ERROR_403,
        404: _generic_descriptions.ERROR_404,
    },
)
def get_available_stylesheet_names() -> list[str]:
    return OdmXmlStylesheetService.get_available_stylesheet_names()


@router.get(
    "/xmls/stylesheets/{stylesheet}",
    dependencies=[security, rbac.LIBRARY_READ],
    summary="Get a specific ODM XML Stylesheet",
    status_code=200,
    responses={
        200: {"description": "Successful Response", "content": {"application/xml": {}}},
        403: _generic_descriptions.ERROR_403,
        404: _generic_descriptions.ERROR_404,
    },
    response_class=Response,
)
def get_specific_stylesheet(
    stylesheet: Annotated[str, Path(description="Name of the ODM XML Stylesheet.")],
):
    # Validate stylesheet parameter to prevent XSS
    if not re.match("^[a-zA-Z0-9-]+$", stylesheet):
        raise ValidationException(
            msg="Stylesheet name must only contain letters, numbers and hyphens."
        )

    rs = OdmXmlStylesheetService.get_specific_stylesheet(stylesheet)

    # URL-encode the filename for safe inclusion in header
    safe_filename = quote(f"{stylesheet}.xsl", safe="")

    return Response(
        content=rs,
        media_type="application/xml",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename}"',
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'none'",
        },
    )
