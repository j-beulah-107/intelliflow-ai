from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse
)
from app.core.security import hash_password

router = APIRouter()


@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(
            user.password
        )
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user": new_user
    }


@router.get(
    "/users",
    response_model=list[UserResponse]
)
def get_users(
    db: Session = Depends(get_db)
):
    return db.query(User).all()


@router.get(
    "/users/me",
    response_model=UserResponse
)
def get_my_profile(
    current_user: User = Depends(
        get_current_user
    )
):
    return current_user


@router.put(
    "/users/me",
    response_model=UserResponse
)
def update_my_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    current_user.name = user_data.name
    current_user.email = user_data.email

    db.commit()
    db.refresh(current_user)

    return current_user


@router.delete("/users/me")
def delete_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    db.delete(current_user)
    db.commit()

    return {
        "message":
        "User deleted successfully"
    }