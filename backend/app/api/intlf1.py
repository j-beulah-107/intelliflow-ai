from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.file import UploadedFile
from app.models.user import User

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    files = (
        db.query(UploadedFile)
        .filter(UploadedFile.owner_id == current_user.id)
        .all()
    )

    pdf_count = 0
    csv_count = 0
    image_count = 0

    for uploaded_file in files:
        extension = Path(uploaded_file.original_name).suffix.lower()

        if extension == ".pdf":
            pdf_count += 1
        elif extension == ".csv":
            csv_count += 1
        elif extension in {".png", ".jpg", ".jpeg"}:
            image_count += 1

    return {
        "total_files": len(files),
        "pdf_files": pdf_count,
        "csv_files": csv_count,
        "image_files": image_count,
    }