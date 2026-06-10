from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

class ElectronicSignatureCreateInput(BaseModel):
    meaning_of_signature: Annotated[
        str,
        Field(description="Meaning of the signature (e.g., authorship, review, approval)")
    ]

class ElectronicSignatureResponse(BaseModel):
    uid: str
    date: datetime
    author_id: str
    meaning_of_signature: str
    signed_node_uid: str
