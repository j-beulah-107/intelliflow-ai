from fastapi import APIRouter
from app.schemas.user import UserCreate

router = APIRouter()

fake_db = []


@router.post("/users")
def create_user(user: UserCreate):

    new_user = {
        "id": len(fake_db) + 1,
        "name": user.name,
        "email": user.email
    }

    fake_db.append(new_user)

    return new_user


@router.get("/users")
def get_users():
    return fake_db