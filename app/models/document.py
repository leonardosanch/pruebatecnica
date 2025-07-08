from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    CC = "CC"
    TI = "TI"
    CE = "CE"


class DocumentCreate(BaseModel):
    document_type: DocumentType
    document_number: str = Field(..., min_length=6, max_length=15)
    issue_date: datetime
    expiry_date: Optional[datetime] = None

    @validator("document_number")
    def validate_document_number(cls, v, values):
        if "document_type" in values:
            doc_type = values["document_type"]
            if doc_type == DocumentType.CC and not v.isdigit():
                raise ValueError("CC debe contener solo números")
            if doc_type == DocumentType.TI and not v.isdigit():
                raise ValueError("TI debe contener solo números")
            if doc_type == DocumentType.CE and len(v) < 8:
                raise ValueError("CE debe tener al menos 8 caracteres")
        return v

    @validator("expiry_date")
    def validate_expiry_date(cls, v, values):
        if v and "issue_date" in values:
            if v <= values["issue_date"]:
                raise ValueError(
                    "Fecha de vencimiento debe ser posterior a fecha de expedición"
                )
            if v < datetime.now():
                raise ValueError("Documento vencido")
        return v


class DocumentResponse(BaseModel):
    id: str
    document_type: DocumentType
    document_number: str
    issue_date: datetime
    expiry_date: Optional[datetime]
    is_valid: bool
    s3_url: Optional[str]
    created_at: datetime
