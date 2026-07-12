from app.api.files import router as file_router
from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.users import router as user_router
from app.core.config import settings
from app.core.database import Base, engine
from app.models import UploadedFile, User
from app.api.analysis import ( router as analysis_router)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

app.include_router(health_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(file_router)
app.include_router(analysis_router)

@app.get("/")
def home():
    return {
        "message": f"Welcome to {settings.APP_NAME}!",
        "version": settings.APP_VERSION
    }