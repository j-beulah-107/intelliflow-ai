from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analysis import router as analysis_router
from app.api.auth import router as auth_router
from app.api.chart import router as chart_router
from app.api.cleaning import router as cleaning_router
from app.api.dashboard import router as dashboard_router
from app.api.files import router as file_router
from app.api.health import router as health_router
from app.api.users import router as user_router
from app.core.config import settings
from app.core.database import Base, engine
from app.models import UploadedFile, User

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(cleaning_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(file_router)
app.include_router(analysis_router)
app.include_router(chart_router)
app.include_router(dashboard_router)


@app.get("/")
def home():
    return {
        "message": f"Welcome to {settings.APP_NAME}!",
        "version": settings.APP_VERSION,
    }