from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import EDITOR_ACCESS
from app.db import get_async_session
from app.models import User
from app.schemas.game import GameResponseModel
from app.services.game import GameService
from app.services.user import UserService
from app.utils.auth import require_roles

router = APIRouter()

game_service = GameService()
user_service = UserService()


@router.get("/", response_model=list[GameResponseModel])
async def get_games(
    current_user: User = Depends(require_roles(*EDITOR_ACCESS)),
    db: AsyncSession = Depends(get_async_session),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Endpoint to retrieve a list of games."""
    games = await game_service.get_games(db, limit, offset)
    return games


@router.get("/recommendations", response_model=list[GameResponseModel])
async def get_game_recommendations(
    current_user: User = Depends(require_roles(*EDITOR_ACCESS)),
    db: AsyncSession = Depends(get_async_session),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Endpoint to retrieve game recommendations."""
    user_liked_genre_ids = await user_service.get_user_liked_genre_ids(current_user.id, db)
    if not user_liked_genre_ids:
        return []
    games = await game_service.get_games_by_genre_ids(user_liked_genre_ids, db, limit=limit, offset=offset)
    return games
