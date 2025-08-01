import pytest
from fastapi import status
from httpx import AsyncClient

from app.models import User


@pytest.mark.asyncio
async def test_get_self_success(authenticated_editor_client: AsyncClient, editor_user: User):
    response = await authenticated_editor_client.get("/user/self")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == editor_user.id
    assert data["username"] == editor_user.username


@pytest.mark.asyncio
async def test_get_user_info_as_admin(authenticated_admin_client: AsyncClient, editor_user: User):
    response = await authenticated_admin_client.get(f"/user/{editor_user.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == editor_user.id


@pytest.mark.asyncio
async def test_get_user_info_unauthorized(authenticated_editor_client: AsyncClient):
    response = await authenticated_editor_client.get("/user/999")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_create_user_success(authenticated_admin_client: AsyncClient):
    response = await authenticated_admin_client.post("/user/", json={"username": "new_user", "password": "newpass"})
    assert response.status_code == status.HTTP_201_CREATED
    assert "user_id" in response.json()


@pytest.mark.asyncio
async def test_create_user_conflict(authenticated_admin_client: AsyncClient, editor_user: User):
    response = await authenticated_admin_client.post(
        "/user/", json={"username": editor_user.username, "password": "pass"}
    )
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_update_user_by_self(authenticated_editor_client: AsyncClient, editor_user: User):
    response = await authenticated_editor_client.patch(f"/user/{editor_user.id}", json={"username": "updated_username"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "updated_username"


@pytest.mark.asyncio
async def test_update_user_forbidden(authenticated_editor_client: AsyncClient):
    response = await authenticated_editor_client.patch("/user/999", json={"username": "hack"})
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete_user_success(authenticated_admin_client: AsyncClient, user_to_delete: User):
    response = await authenticated_admin_client.delete(f"/user/{user_to_delete.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_user_not_found(authenticated_admin_client: AsyncClient):
    response = await authenticated_admin_client.delete("/user/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
