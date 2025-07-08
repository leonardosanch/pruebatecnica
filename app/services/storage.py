import boto3
from moto import mock_s3
from fastapi import UploadFile
import uuid
from datetime import datetime
import os

BUCKET_NAME = "kyc-documents-bucket"
AWS_REGION = "us-east-1"


@mock_s3
async def upload_to_s3_mock(file: UploadFile, user_id: str) -> str:
    s3_client = boto3.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id="fake-access-key",
        aws_secret_access_key="fake-secret-key",
    )

    try:
        s3_client.create_bucket(Bucket=BUCKET_NAME)
    except:
        pass

    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".pdf"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    s3_key = f"documents/{user_id}/{timestamp}_{uuid.uuid4()}{file_extension}"

    file_content = await file.read()
    await file.seek(0)

    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=file_content,
        ContentType=file.content_type or "application/pdf",
        Metadata={
            "user_id": user_id,
            "original_filename": file.filename or "document",
            "upload_timestamp": timestamp,
        },
    )

    s3_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"

    return s3_url


@mock_s3
def get_document_from_s3_mock(s3_key: str) -> bytes:
    s3_client = boto3.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id="fake-access-key",
        aws_secret_access_key="fake-secret-key",
    )

    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_key)
    return response["Body"].read()


@mock_s3
def delete_document_from_s3_mock(s3_key: str) -> bool:
    s3_client = boto3.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id="fake-access-key",
        aws_secret_access_key="fake-secret-key",
    )

    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=s3_key)
        return True
    except Exception:
        return False
