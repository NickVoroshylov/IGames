from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Date, Float, Integer, String, Text

from app.db import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    release_date = Column(Date, nullable=True)
    rating = Column(Float, default=0, nullable=False)
    times_listed = Column(Integer, default=0, nullable=False)
    reviews_number = Column(Integer, default=0, nullable=False)
    summary = Column(Text, nullable=True)
    plays = Column(Integer, default=0, nullable=False)
    playing = Column(Integer, default=0, nullable=False)
    backlogs = Column(Integer, default=0, nullable=False)
    whitelist = Column(Integer, default=0, nullable=False)

    teams = relationship("GameTeam", back_populates="game", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="game", cascade="all, delete-orphan")
    genres = relationship("GameGenre", back_populates="game", cascade="all, delete-orphan")

    @property
    def game_teams(self) -> list[str]:
        return [team.team.name for team in self.teams]

    @property
    def game_reviews(self) -> list[str]:
        return [review.review for review in self.reviews]

    @property
    def game_genres(self) -> list[str]:
        return [genre.genre.name for genre in self.genres]


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)

    games = relationship("GameGenre", back_populates="genre", cascade="all, delete-orphan")
    liked_by_users = relationship("UserLikedGenres", back_populates="genre", cascade="all, delete-orphan")


class GameGenre(Base):
    __tablename__ = "game_genres"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
    genre_id = Column(Integer, ForeignKey("genres.id"), nullable=False, index=True)

    __table_args__ = (UniqueConstraint("game_id", "genre_id", name="uq_game_genre"),)

    game = relationship("Game", back_populates="genres")
    genre = relationship("Genre", back_populates="games")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)

    games = relationship("GameTeam", back_populates="team", cascade="all, delete-orphan")


class GameTeam(Base):
    __tablename__ = "game_teams"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)

    __table_args__ = (UniqueConstraint("game_id", "team_id", name="uq_game_team"),)

    game = relationship("Game", back_populates="teams")
    team = relationship("Team", back_populates="games")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
    review = Column(Text, nullable=True)

    game = relationship("Game", back_populates="reviews")
