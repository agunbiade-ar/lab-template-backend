from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from models import LabTemplate

class TemplateField(BaseModel):
    label: str = Field(..., example="WBC")
    name: str = Field(..., example="wbc")
    type: Literal["text", "number", "textarea", "select", "radio", "checkbox"]
    unit: Optional[str] = Field(None, example="x10^9/L")
    range: Optional[str] = Field(None, example="4.0–11.0")
    options: Optional[List[str]] = Field(None, example=["Negative", "1:80", "1:160"])

class LabTemplateBase(BaseModel):
    name: str = Field(..., example="Widal Test")
    facility_id: Optional[int] = None
    fields: List[TemplateField]

class LabTemplateCreate(LabTemplateBase):
    created_by: Optional[int] = None


class LabTemplateRead(LabTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
