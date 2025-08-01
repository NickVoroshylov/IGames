from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db import get_async_session
from app.schemas.auth import JWTTokenResponseModel
from app.services.user import UserService
from app.utils.auth import generate_jwt_token
from app.utils.hashing import verify_password

router = APIRouter()

user_service = UserService()


@router.post("/login", response_model=JWTTokenResponseModel)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session),
):
    user = await user_service.get_user_by_username(form_data.username, db)

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = generate_jwt_token(data={"sub": str(user.id)}, expires_delta=timedelta(minutes=60))
    return JWTTokenResponseModel(access_token=access_token, token_type="bearer")
