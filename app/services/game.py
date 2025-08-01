from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Game, GameGenre, GameTeam


class GameService:
    async def get_games(self, db: AsyncSession, limit: int, offset: int) -> Sequence[Game]:
        statement = (
            select(Game)
            .options(
                selectinload(Game.genres).selectinload(GameGenre.genre),
                selectinload(Game.teams).selectinload(GameTeam.team),
                selectinload(Game.reviews),
            )
            .limit(limit)
            .offset(offset)
        )

        result = await db.execute(statement)
        games = result.scalars().all()
        return games

    async def get_games_by_genre_ids(
        self, genre_ids: list[int], db: AsyncSession, limit: int, offset: int
    ) -> Sequence[Game]:
        statement = (
            select(Game)
            .join(GameGenre, GameGenre.game_id == Game.id)
            .where(GameGenre.genre_id.in_(genre_ids))
            .options(
                selectinload(Game.genres).selectinload(GameGenre.genre),
                selectinload(Game.teams).selectinload(GameTeam.team),
                selectinload(Game.reviews),
            )
            .distinct()
            .order_by(Game.rating.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(statement)
        games = result.scalars().all()
        return games
