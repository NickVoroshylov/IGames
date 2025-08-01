from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.constants import DEFAULT_USER_ROLE_ID
from app.models import Genre, Role, User, UserLikedGenres
from app.schemas.user import UserCreateModel, UserUpdateModel
from app.utils.hashing import generate_hashed_password


class UserService:
    async def get_user_by_id(self, user_id: int, db: AsyncSession) -> User:
        statement = (
            select(User)
            .options(selectinload(User.role), selectinload(User.liked_genres).selectinload(UserLikedGenres.genre))
            .where(User.id == user_id)
        )

        result = await db.execute(statement)
        user = result.scalar_one_or_none()
        return user

    async def get_user_by_username(self, username: str, db: AsyncSession) -> User | None:
        statement = select(User).where(User.username == username)

        result = await db.execute(statement)
        user = result.scalar_one_or_none()
        return user

    async def user_exists(self, username: str, db: AsyncSession) -> bool:
        return await self.get_user_by_username(username, db) is not None

    async def create_user(self, user_data: UserCreateModel, db: AsyncSession) -> User:
        user_data_dict = user_data.model_dump()
        hashed_password = generate_hashed_password(user_data_dict["password"])

        new_user = User(
            username=user_data_dict["username"], password_hash=hashed_password, role_id=DEFAULT_USER_ROLE_ID
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    async def update_user(self, user: User, user_data: UserUpdateModel, db: AsyncSession) -> User:
        data = user_data.model_dump(exclude_unset=True)

        if "password" in data:
            user.password_hash = generate_hashed_password(data.pop("password"))
        if "username" in data:
            user.username = data["username"]
        if "role_id" in data:
            role_exists = await self.role_exist(data["role_id"], db)
            if not role_exists:
                raise HTTPException(status_code=400, detail="Role not found")
            user.role_id = data["role_id"]
        if "liked_genre_ids" in data:
            genres_exist = await self.genres_exist(data["liked_genre_ids"], db)
            if not genres_exist:
                raise HTTPException(status_code=400, detail="One or more genres not found")

            await db.execute(delete(UserLikedGenres).where(UserLikedGenres.user_id == user.id))
            new_genres = [UserLikedGenres(user_id=user.id, genre_id=genre_id) for genre_id in data["liked_genre_ids"]]
            db.add_all(new_genres)
        await db.commit()
        await db.refresh(user)

        # bad solution which must be updated to optimize performance
        updated_user = await self.get_user_by_id(user.id, db)
        return updated_user

    async def delete_user(self, user_id: int, db: AsyncSession) -> bool:
        try:
            statement = delete(User).where(User.id == user_id)
            result = await db.execute(statement)
            await db.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await db.rollback()
            raise e

    async def get_user_liked_genre_ids(self, user_id: int, db: AsyncSession) -> list[int] | None:
        statement = select(UserLikedGenres.genre_id).where(UserLikedGenres.user_id == user_id)
        result = await db.execute(statement)
        genre_ids = result.scalars().all()
        return genre_ids or None

    # better to move it to GenreService
    async def genres_exist(self, genre_ids: list[int], db: AsyncSession) -> bool:
        if not genre_ids:
            return True
        result = await db.execute(select(Genre.id).where(Genre.id.in_(genre_ids)))
        existed_ids = set(result.scalars().all())
        return set(genre_ids).issubset(existed_ids)

    async def role_exist(self, role_id: int, db: AsyncSession) -> bool:
        statement = select(Role.id).where(Role.id == role_id)
        result = await db.execute(statement)
        role = result.scalars().first()
        return role is not None
