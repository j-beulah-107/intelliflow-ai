from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from PIL import Image, ImageStat, UnidentifiedImageError
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
from app.services.image_captioner import generate_image_caption
from app.services.report_generator import generate_csv_report


router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)


def analyse_image_metadata(file_path: Path) -> dict:
    """
    Analyse the technical properties of an uploaded image.
    """

    try:
        with Image.open(file_path) as image:
            width, height = image.size
            image_format = (
                image.format
                or file_path.suffix.replace(".", "")
            )
            colour_mode = image.mode

            rgb_image = image.convert("RGB")
            grayscale_image = rgb_image.convert("L")

            brightness_score = round(
                ImageStat.Stat(
                    grayscale_image
                ).mean[0],
                2,
            )

            if width > height:
                orientation = "Landscape"
            elif height > width:
                orientation = "Portrait"
            else:
                orientation = "Square"

            aspect_ratio = (
                round(width / height, 2)
                if height
                else 0
            )

            megapixels = round(
                (width * height) / 1_000_000,
                2,
            )

            file_size_bytes = (
                file_path.stat().st_size
            )

            file_size_kb = round(
                file_size_bytes / 1024,
                2,
            )

            if brightness_score < 85:
                brightness_level = "Dark"
            elif brightness_score < 170:
                brightness_level = "Balanced"
            else:
                brightness_level = "Bright"

            metadata_report = (
                f"This is a {orientation.lower()} image "
                f"with a resolution of {width} × {height} pixels. "
                f"Its format is {image_format.upper()} and its "
                f"colour mode is {colour_mode}. "
                f"The estimated brightness is "
                f"{brightness_level.lower()}."
            )

            return {
                "width": width,
                "height": height,
                "resolution": f"{width} × {height}",
                "megapixels": megapixels,
                "format": image_format.upper(),
                "colour_mode": colour_mode,
                "orientation": orientation,
                "aspect_ratio": aspect_ratio,
                "brightness_score": brightness_score,
                "brightness_level": brightness_level,
                "file_size_bytes": file_size_bytes,
                "file_size_kb": file_size_kb,
                "metadata_report": metadata_report,
            }

    except UnidentifiedImageError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The uploaded image could not be read.",
        ) from exc

    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "The image appears to be damaged "
                "or unsupported."
            ),
        ) from exc


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
            UploadedFile.owner_id
            == current_user.id,
        )
        .first()
    )

    if not uploaded_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    file_path = Path(
        uploaded_file.file_path
    )

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stored file is missing",
        )

    extension = (
        file_path.suffix.lower()
    )

    if extension == ".pdf":
        extracted_text = extract_pdf_text(
            str(file_path)
        ).strip()

        if not extracted_text:
            raise HTTPException(
                status_code=(
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                ),
                detail=(
                    "No readable text was found "
                    "in this PDF"
                ),
            )

        summary = summarize_text(
            extracted_text
        )

        return {
            "file_id": uploaded_file.id,
            "original_name": (
                uploaded_file.original_name
            ),
            "type": "pdf",
            "summary": summary,
            "preview": extracted_text[:1000],
            "character_count": len(
                extracted_text
            ),
        }

    if extension == ".csv":
        csv_summary = summarize_csv(
            str(file_path)
        )

        report = generate_csv_report(
            csv_summary
        )

        return {
            "file_id": uploaded_file.id,
            "original_name": (
                uploaded_file.original_name
            ),
            "type": "csv",
            "summary": csv_summary,
            "report": report,
        }

    if extension in {
        ".png",
        ".jpg",
        ".jpeg",
    }:
        image_summary = (
            analyse_image_metadata(
                file_path
            )
        )

        try:
            ai_caption = (
                generate_image_caption(
                    file_path
                )
            )

        except Exception as exc:
            ai_caption = (
                "AI description could not be generated."
            )

            print(
                "Image-captioning error:",
                exc,
            )

        return {
            "file_id": uploaded_file.id,
            "original_name": (
                uploaded_file.original_name
            ),
            "type": "image",
            "summary": image_summary,
            "message": image_summary[
                "metadata_report"
            ],
            "ai_caption": ai_caption,
        }

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=(
            "This file type is not "
            "supported for analysis"
        ),
    )