from fastapi import FastAPI
from app.core.config import settings
from app.api.health import router as health_router
from app.api.users import router as user_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

app.include_router(health_router)
app.include_router(user_router)


@app.get("/")
def home():
    return {
        "message": f"Welcome to {settings.APP_NAME}!",
        "version": settings.APP_VERSION
    }