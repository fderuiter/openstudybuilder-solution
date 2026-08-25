from datetime import datetime
from typing import Any, Annotated
from pydantic import BaseModel, Field


class LineageInfo(BaseModel):
    parent_template_uid: Annotated[str | None, Field(json_schema_extra={"nullable": True})] = None
    parent_template_version: Annotated[str | None, Field(json_schema_extra={"nullable": True})] = None
    sync_status: Annotated[str, Field(description="Current sync status: IN_SYNC, NEEDS_REVIEW, RETIRED")] = "IN_SYNC"
    requires_review: Annotated[bool, Field(description="Whether reconciliation review is needed")] = False


class DiffItem(BaseModel):
    field: Annotated[str, Field(description="Field identifier/key")]
    label: Annotated[str, Field(description="Human-readable field label")]
    category: Annotated[str, Field(description="Category: Metadata, Design, Population, Selections")] = "Metadata"
    change_type: Annotated[str, Field(description="Change type: ADDED, MODIFIED, REMOVED")] = "MODIFIED"
    current_value: Annotated[Any | None, Field(json_schema_extra={"nullable": True})] = None
    template_value: Annotated[Any | None, Field(json_schema_extra={"nullable": True})] = None


class ReconciliationDiffResponse(BaseModel):
    study_uid: Annotated[str, Field(description="Study UID")]
    parent_template_uid: Annotated[str | None, Field(json_schema_extra={"nullable": True})] = None
    parent_template_version: Annotated[str | None, Field(json_schema_extra={"nullable": True})] = None
    current_template_version: Annotated[str | None, Field(json_schema_extra={"nullable": True})] = None
    sync_status: Annotated[str, Field(description="Current sync status")] = "IN_SYNC"
    diffs: Annotated[list[DiffItem], Field(description="List of field diffs")] = Field(default_factory=list)
    total_diffs: Annotated[int, Field(description="Total count of diffs")] = 0


class ReconciliationRequest(BaseModel):
    selected_fields: Annotated[list[str], Field(description="List of field keys selected to be merged")]
    comments: Annotated[str | None, Field(json_schema_extra={"nullable": True})] = None


class FieldDecision(BaseModel):
    field: Annotated[str, Field(description="Field key")]
    decision: Annotated[str, Field(description="ACCEPTED or REJECTED")]
    old_value: Annotated[Any | None, Field(json_schema_extra={"nullable": True})] = None
    new_value: Annotated[Any | None, Field(json_schema_extra={"nullable": True})] = None


class ReconciliationAuditRecord(BaseModel):
    uid: Annotated[str, Field(description="Audit record UID")]
    study_uid: Annotated[str, Field(description="Study UID")]
    parent_template_uid: Annotated[str, Field(description="Parent template UID")]
    parent_template_version: Annotated[str, Field(description="Parent template version after reconciliation")]
    timestamp: Annotated[datetime, Field(description="Reconciliation timestamp")]
    user_id: Annotated[str, Field(description="User ID who executed reconciliation")]
    decisions: Annotated[list[FieldDecision], Field(description="Field level decisions")] = Field(default_factory=list)
    comments: Annotated[str | None, Field(json_schema_extra={"nullable": True})] = None
