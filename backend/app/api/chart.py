from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.file import UploadedFile
from app.models.user import User
from app.services.chart_generator import generate_csv_charts

router = APIRouter(
    prefix="/charts",
    tags=["Charts"],
)


@router.post("/{file_id}")
def create_charts(
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

    if file_path.suffix.lower() != ".csv":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Charts can only be generated from CSV files",
        )

    charts = generate_csv_charts(
        str(file_path)
    )

    return {
        "message": "Charts generated successfully",
        "charts": charts,
    }


@router.get("/{chart_name}")
def view_chart(chart_name: str):
    chart_path = Path("generated_charts") / chart_name

    if not chart_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart not found",
        )

    return FileResponse(
        path=chart_path,
        media_type="image/png",
        filename=chart_name,
    )