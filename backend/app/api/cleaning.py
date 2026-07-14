from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.file import UploadedFile
from app.models.user import User
from app.services.data_cleaner import clean_csv

router = APIRouter(
    prefix="/cleaning",
    tags=["Data Cleaning"]
)


@router.post("/{file_id}")
def clean_dataset(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    uploaded_file = (
        db.query(UploadedFile)
        .filter(
            UploadedFile.id == file_id,
            UploadedFile.owner_id ==
            current_user.id
        )
        .first()
    )

    if not uploaded_file:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    file_path = Path(
        uploaded_file.file_path
    )

    if (
        file_path.suffix.lower()
        != ".csv"
    ):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files can be cleaned"
        )

    result = clean_csv(
        str(file_path)
    )

    return result