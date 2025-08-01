from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Integer, String

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    role = relationship("Role", back_populates="users")
    liked_genres = relationship("UserLikedGenres", back_populates="user", cascade="all, delete-orphan")

    @property
    def role_name(self) -> str:
        return self.role.name

    @property
    def liked_genres_names(self) -> list[str]:
        return [genre.genre.name for genre in self.liked_genres]


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)

    users = relationship("User", back_populates="role")


class UserLikedGenres(Base):
    __tablename__ = "user_liked_genres"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    genre_id = Column(Integer, ForeignKey("genres.id"), primary_key=True)

    __table_args__ = (UniqueConstraint("user_id", "genre_id", name="uix_user_genre"),)

    user = relationship("User", back_populates="liked_genres")
    genre = relationship("Genre", back_populates="liked_by_users")
