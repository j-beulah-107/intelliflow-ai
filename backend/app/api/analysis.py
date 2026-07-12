from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.file import UploadedFile
from app.models.user import User
from app.services.file_processor import (
    extract_pdf_text,
    summarize_csv,
    summarize_text,
)

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)


@router.get("/{file_id}")
def analyze_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    uploaded_file = (
        db.query(UploadedFile)
        .filter(
            UploadedFile.id == file_id,
            UploadedFile.owner_id == current_user.id,
        )
        .first()
    )

    if not uploaded_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    file_path = Path(uploaded_file.file_path)

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stored file is missing",
        )

    extension = file_path.suffix.lower()

    if extension == ".pdf":
        extracted_text = extract_pdf_text(
            str(file_path)
        ).strip()

        if not extracted_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No readable text was found in this PDF",
            )

        summary = summarize_text(extracted_text)

        return {
            "file_id": uploaded_file.id,
            "original_name": uploaded_file.original_name,
            "type": "pdf",
            "summary": summary,
            "preview": extracted_text[:1000],
            "character_count": len(extracted_text),
        }

    if extension == ".csv":
        csv_summary = summarize_csv(
            str(file_path)
        )

        return {
            "file_id": uploaded_file.id,
            "original_name": uploaded_file.original_name,
            "type": "csv",
            "summary": csv_summary,
        }

    if extension in {".png", ".jpg", ".jpeg"}:
        return {
            "file_id": uploaded_file.id,
            "original_name": uploaded_file.original_name,
            "type": "image",
            "message": "Image analysis will be added in the next milestone",
        }

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="This file type is not supported for analysis",
    )