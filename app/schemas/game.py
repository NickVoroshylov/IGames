from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class GameResponseModel(BaseModel):
    title: str
    release_date: date | None
    rating: Decimal
    summary: str | None = None
    times_listed: int
    reviews_number: int
    plays: int
    playing: int
    backlogs: int
    whitelist: int
    game_teams: list[str] | None = None
    game_genres: list[str] | None = None
    game_reviews: list[str] | None = None

    class Config:
        from_attributes = True
