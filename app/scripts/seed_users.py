import asyncio

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import async_session_maker
from app.models import Genre, Role, User, UserLikedGenres
from app.utils.hashing import generate_hashed_password


async def get_or_create_role(session: AsyncSession, role_name: str) -> Role:
    result = await session.execute(select(Role).where(Role.name == role_name))
    role = result.scalars().first()
    if not role:
        role = Role(name=role_name)
        session.add(role)
        await session.flush()
    return role


async def get_genres_map(session: AsyncSession, genre_names: list[str]) -> dict[str, Genre]:
    if not genre_names:
        return {}
    stmt = select(Genre).where(Genre.name.in_(genre_names))
    result = await session.execute(stmt)
    genres = {genre.name: genre for genre in result.scalars().all()}
    return genres


async def create_user_with_genres(
    session: AsyncSession, username: str, password: str, role_name: str, liked_genre_names: list[str]
):
    role = await get_or_create_role(session, role_name)
    password_hash = generate_hashed_password(password)

    user = User(username=username, password_hash=password_hash, role_id=role.id)
    session.add(user)
    await session.flush()

    genres_map = await get_genres_map(session, liked_genre_names)

    for genre_name in liked_genre_names:
        genre = genres_map.get(genre_name)
        if genre:
            liked = UserLikedGenres(user_id=user.id, genre_id=genre.id)
            session.add(liked)

    await session.commit()
    print(f"Created user {username} with role {role_name} and liked genres: {liked_genre_names}")


async def main():
    async with async_session_maker() as session:
        result = await session.execute(select(func.count(User.id)))
        count = result.scalar_one()
        if count > 0:
            print("Users already seeded, skipping.")
            return

        admin_liked_genres = ["Adventure", "Shooter", "Indie"]
        editor_liked_genres = ["Puzzle", "Simulator", "Indie"]

        await create_user_with_genres(session, "admin", "admin", "admin", admin_liked_genres)
        await create_user_with_genres(session, "editor", "editor", "editor", editor_liked_genres)


if __name__ == "__main__":
    asyncio.run(main())
