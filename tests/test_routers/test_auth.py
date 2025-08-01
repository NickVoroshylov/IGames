from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.routers.auth import login
from app.schemas.auth import JWTTokenResponseModel


@pytest.mark.asyncio
async def test_login_success(mock_user, form_data, mock_db_session):
    with (
        patch("app.routers.auth.user_service.get_user_by_username", return_value=mock_user),
        patch("app.routers.auth.verify_password", return_value=True),
        patch("app.routers.auth.generate_jwt_token", return_value="fake_token"),
    ):
        response: JWTTokenResponseModel = await login(form_data, mock_db_session)
        assert response.access_token == "fake_token"
        assert response.token_type == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password(mock_user, form_data, mock_db_session):
    with (
        patch("app.routers.auth.user_service.get_user_by_username", return_value=mock_user),
        patch("app.routers.auth.verify_password", return_value=False),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await login(form_data, mock_db_session)
        assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_login_user_not_found(form_data, mock_db_session):
    with patch("app.routers.auth.user_service.get_user_by_username", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            await login(form_data, mock_db_session)
        assert exc_info.value.status_code == 401
