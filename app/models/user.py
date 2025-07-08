from fastapi import APIRouter, HTTPException, Depends, status, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional
from datetime import datetime
import uuid

from ..models.user import UserCreate, UserResponse, Token
from ..models.document import DocumentResponse, DocumentCreate, DocumentType
from ..services.auth import create_access_token, verify_token
from ..services.kyc import validate_kyc_document
from ..services.storage import upload_to_s3_mock
from ..utils.validators import validate_file_type

router = APIRouter()
security = HTTPBearer()

users_db: Dict[str, dict] = {}


@router.post("/users/", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(
    name: str = Form(...),
    email: str = Form(...),
    document_type: str = Form(...),
    document_number: str = Form(...),
    issue_date: str = Form(...),
    expiry_date: Optional[str] = Form(None),
    file: UploadFile = File(...),
):

    try:
        issue_dt = datetime.fromisoformat(issue_date.replace("Z", "+00:00"))
        expiry_dt = None
        if expiry_date:
            expiry_dt = datetime.fromisoformat(expiry_date.replace("Z", "+00:00"))

        document = DocumentCreate(
            document_type=DocumentType(document_type),
            document_number=document_number,
            issue_date=issue_dt,
            expiry_date=expiry_dt,
        )

        user_obj = UserCreate(name=name, email=email, document=document)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en los datos: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error validando datos: {str(e)}",
        )

    if user_obj.email in [u.get("email") for u in users_db.values()]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email ya registrado"
        )

    validate_file_type(file)

    user_id = str(uuid.uuid4())

    document_validation = validate_kyc_document(user_obj.document)

    if not document_validation["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Documento inválido: {document_validation['error']}",
        )

    s3_url = await upload_to_s3_mock(file, user_id)

    document_response = DocumentResponse(
        id=str(uuid.uuid4()),
        document_type=user_obj.document.document_type,
        document_number=user_obj.document.document_number,
        issue_date=user_obj.document.issue_date,
        expiry_date=user_obj.document.expiry_date,
        is_valid=document_validation["is_valid"],
        s3_url=s3_url,
        created_at=datetime.now(),
    )

    user_data = {
        "id": user_id,
        "name": user_obj.name,
        "email": user_obj.email,
        "document": document_response.dict(),
        "kyc_status": "approved" if document_validation["is_valid"] else "rejected",
        "created_at": datetime.now(),
    }

    users_db[user_id] = user_data

    access_token = create_access_token(data={"sub": user_id})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token_data = verify_token(credentials.credentials)

    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    user_data = users_db[user_id]

    document_response = DocumentResponse(**user_data["document"])

    return UserResponse(
        id=user_data["id"],
        name=user_data["name"],
        email=user_data["email"],
        document=document_response,
        kyc_status=user_data["kyc_status"],
        created_at=user_data["created_at"],
    )
