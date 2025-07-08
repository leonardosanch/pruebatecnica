from datetime import datetime, timedelta
from typing import Dict
from ..models.document import DocumentCreate, DocumentType


def validate_kyc_document(document: DocumentCreate) -> Dict[str, any]:
    result = {"is_valid": True, "error": None, "warnings": []}

    current_date = datetime.now()

    if document.issue_date > current_date:
        result["is_valid"] = False
        result["error"] = "Fecha de expedición no puede ser futura"
        return result

    if document.document_type == DocumentType.CC:
        if len(document.document_number) < 7 or len(document.document_number) > 10:
            result["is_valid"] = False
            result["error"] = "CC debe tener entre 7 y 10 dígitos"
            return result

        years_since_issue = (current_date - document.issue_date).days / 365
        if years_since_issue > 10:
            result["is_valid"] = False
            result["error"] = "CC muy antigua, debe renovarse"
            return result

    elif document.document_type == DocumentType.TI:
        if len(document.document_number) < 8 or len(document.document_number) > 11:
            result["is_valid"] = False
            result["error"] = "TI debe tener entre 8 y 11 dígitos"
            return result

        age_estimation = (current_date - document.issue_date).days / 365
        if age_estimation > 18:
            result["warnings"].append("TI para persona mayor de edad")

    elif document.document_type == DocumentType.CE:
        if not document.expiry_date:
            result["is_valid"] = False
            result["error"] = "CE debe tener fecha de vencimiento"
            return result

        if document.expiry_date <= current_date:
            result["is_valid"] = False
            result["error"] = "CE vencida"
            return result

        days_to_expire = (document.expiry_date - current_date).days
        if days_to_expire < 30:
            result["warnings"].append("CE próxima a vencer")

    if document.issue_date < (current_date - timedelta(days=365 * 20)):
        result["warnings"].append("Documento muy antiguo")

    return result
