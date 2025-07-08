from fastapi import UploadFile, HTTPException, status
import magic
import os

ALLOWED_MIME_TYPES = [
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
]

ALLOWED_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png", ".gif"]

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_file_type(file: UploadFile):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre de archivo requerido",
        )

    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido. Permitidos: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo MIME no permitido. Permitidos: {', '.join(ALLOWED_MIME_TYPES)}",
        )


def validate_file_size(file: UploadFile):
    if hasattr(file, "size") and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Archivo muy grande. Máximo permitido: {MAX_FILE_SIZE / (1024*1024):.1f}MB",
        )


def validate_email_format(email: str) -> bool:
    import re

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_document_number_format(doc_type: str, doc_number: str) -> bool:
    if doc_type == "CC":
        return doc_number.isdigit() and 7 <= len(doc_number) <= 10
    elif doc_type == "TI":
        return doc_number.isdigit() and 8 <= len(doc_number) <= 11
    elif doc_type == "CE":
        return (
            len(doc_number) >= 8
            and doc_number.replace("-", "").replace(" ", "").isalnum()
        )
    return False
