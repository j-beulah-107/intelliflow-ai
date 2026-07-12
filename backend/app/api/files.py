from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.file import UploadedFile
from app.models.user import User

router = APIRouter(
    prefix="/files",
    tags=["Files"],
)

UPLOAD_DIRECTORY = Path("uploads")

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".csv",
    ".png",
    ".jpg",
    ".jpeg",
}

MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    original_name = file.filename or "unknown_file"
    extension = Path(original_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, CSV, PNG, JPG and JPEG files are allowed",
        )

    file_content = await file.read()

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size must not exceed 10 MB",
        )

    stored_name = f"{uuid4().hex}{extension}"
    file_path = UPLOAD_DIRECTORY / stored_name

    UPLOAD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path.write_bytes(file_content)

    uploaded_file = UploadedFile(
        original_name=original_name,
        stored_name=stored_name,
        file_type=file.content_type or "application/octet-stream",
        file_path=str(file_path),
        owner_id=current_user.id,
    )

    db.add(uploaded_file)
    db.commit()
    db.refresh(uploaded_file)

    return {
        "message": "File uploaded successfully",
        "file": {
            "id": uploaded_file.id,
            "original_name": uploaded_file.original_name,
            "file_type": uploaded_file.file_type,
            "owner_id": uploaded_file.owner_id,
        },
    }


@router.get("")
def get_my_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    files = (
        db.query(UploadedFile)
        .filter(UploadedFile.owner_id == current_user.id)
        .order_by(UploadedFile.id.desc())
        .all()
    )

    return files


@router.get("/{file_id}/download")
def download_file(
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

    return FileResponse(
        path=file_path,
        filename=uploaded_file.original_name,
        media_type=uploaded_file.file_type,
    )


@router.delete("/{file_id}")
def delete_file(
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

    if file_path.exists():
        file_path.unlink()

    db.delete(uploaded_file)
    db.commit()

    return {
        "message": "File deleted successfully",
    }