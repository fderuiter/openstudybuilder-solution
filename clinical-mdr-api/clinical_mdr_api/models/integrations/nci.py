from pydantic import BaseModel, Field

class NCIConcept(BaseModel):
    code: str = Field(description="The NCI concept ID/code")
    name: str = Field(description="The preferred name of the concept")
