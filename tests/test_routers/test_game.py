import datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.models import Game, GameGenre, Genre, UserLikedGenres


@pytest.mark.asyncio
async def test_get_games_success(authenticated_editor_client: AsyncClient, db_session):
    game1 = Game(
        title="Game One",
        release_date=datetime.date(2020, 1, 1),
        rating=4.5,
        times_listed=10,
        reviews_number=5,
        plays=100,
        playing=50,
        backlogs=10,
        whitelist=5,
    )
    game2 = Game(
        title="Game Two",
        release_date=datetime.date(2021, 6, 15),
        rating=3.8,
        times_listed=7,
        reviews_number=3,
        plays=200,
        playing=80,
        backlogs=20,
        whitelist=10,
    )
    db_session.add_all([game1, game2])
    await db_session.commit()

    response = await authenticated_editor_client.get("/games/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(game["title"] == "Game One" for game in data)
    assert any(game["title"] == "Game Two" for game in data)


@pytest.mark.asyncio
async def test_get_game_recommendations_success(authenticated_editor_client: AsyncClient, db_session, editor_user):
    genre = Genre(name="RPG")
    db_session.add(genre)
    await db_session.commit()
    await db_session.refresh(genre)

    db_session.add(UserLikedGenres(user_id=editor_user.id, genre_id=genre.id))
    await db_session.commit()

    game = Game(
        title="RPG Game",
        release_date=datetime.date(2019, 5, 20),
        rating=4.0,
        times_listed=5,
        reviews_number=2,
        plays=150,
        playing=70,
        backlogs=15,
        whitelist=3,
    )
    db_session.add(game)
    await db_session.commit()
    await db_session.refresh(game)

    db_session.add(GameGenre(game_id=game.id, genre_id=genre.id))
    await db_session.commit()

    response = await authenticated_editor_client.get("/games/recommendations")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(g["title"] == "RPG Game" for g in data)


@pytest.mark.asyncio
async def test_get_game_recommendations_no_liked_genres(authenticated_editor_client: AsyncClient):
    with patch("app.services.user.UserService.get_user_liked_genre_ids", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = []
        response = await authenticated_editor_client.get("/games/recommendations")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert data == []
