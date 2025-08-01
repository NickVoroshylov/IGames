from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import ADMIN, ADMIN_ACCESS, EDITOR_ACCESS
from app.db import get_async_session
from app.models import User
from app.schemas.user import (
    UserCreateModel,
    UserCreateResponseModel,
    UserResponseModel,
    UserUpdateModel,
)
from app.services.user import UserService
from app.utils.auth import require_roles

router = APIRouter()

user_service = UserService()


@router.get("/self", response_model=UserResponseModel)
async def get_user_self_info(current_user: User = Depends(require_roles(*EDITOR_ACCESS))) -> User:
    """Endpoint to get information about the currently authenticated user."""
    return current_user


@router.get("/{user_id}", response_model=UserResponseModel)
async def get_user_info(
    user_id: int,
    current_user: User = Depends(require_roles(*ADMIN_ACCESS)),
    db: AsyncSession = Depends(get_async_session),
) -> User:
    """Endpoint to get information about a specific user by user_id."""
    if current_user.id == user_id:
        return current_user

    user = await user_service.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserResponseModel)
async def update_user_info(
    user_id: int,
    user_data: UserUpdateModel,
    current_user: User = Depends(require_roles(*EDITOR_ACCESS)),
    db: AsyncSession = Depends(get_async_session),
) -> User:
    """Endpoint to update information for a specific user by user_id."""
    if current_user.id != user_id and current_user.role.name != ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to update this user"
        )

    user = await user_service.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updated_user = await user_service.update_user(user, user_data, db)
    return updated_user


@router.post("/", response_model=UserCreateResponseModel, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateModel,
    current_user: User = Depends(require_roles(*ADMIN_ACCESS)),
    db: AsyncSession = Depends(get_async_session),
) -> UserCreateResponseModel:
    """Endpoint to create a new user."""
    username = user_data.username

    user_exists = await user_service.user_exists(username, db)
    if user_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this username already exists")

    created_user = await user_service.create_user(user_data, db)
    return UserCreateResponseModel(message="User created successfully, please login", user_id=created_user.id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_roles(*ADMIN_ACCESS)),
    db: AsyncSession = Depends(get_async_session),
) -> None:
    """Endpoint to delete a specific user by user_id."""
    deleted = await user_service.delete_user(user_id, db)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return
