import ast
import csv
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import async_session_maker
from app.models import Game, GameGenre, GameTeam, Genre, Review, Team

CSV_FILE_PATH = "app/data/games.csv"


def parse_flexible_list(value: str) -> list[str]:
    if not value:
        return []

    value = value.strip()

    if value.startswith("[") and value.endswith("]"):
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                return [str(x).strip() for x in parsed if str(x).strip()]
        except (ValueError, SyntaxError):
            pass

    return [v.strip() for v in value.split(";") if v.strip()]


async def collect_unique_genres_and_teams(csv_path: str):
    all_genres = set()
    all_teams = set()

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            genres = parse_flexible_list(row.get("Genres", ""))
            teams = parse_flexible_list(row.get("Team", ""))
            all_genres.update(genres)
            all_teams.update(teams)

    return all_genres, all_teams


async def load_or_create_entities(session, model, names: set):
    if not names:
        return {}

    stmt = select(model).where(model.name.in_(names))
    result = await session.execute(stmt)
    existing = {obj.name: obj for obj in result.scalars().all()}

    new_names = names - existing.keys()
    new_entities = [model(name=name) for name in new_names]

    session.add_all(new_entities)
    await session.flush()

    for entity in new_entities:
        existing[entity.name] = entity

    return existing


async def load_data(session: AsyncSession, csv_path: str):
    all_genres, all_teams = await collect_unique_genres_and_teams(csv_path)

    genres_map = await load_or_create_entities(session, Genre, all_genres)
    teams_map = await load_or_create_entities(session, Team, all_teams)

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            # skip empty rows
            title = row.get("Title", "").strip()
            if not title:
                continue

            # process release date
            raw_date = row.get("Release Date", "")
            if "TBD" in raw_date or not raw_date.strip():
                release_date = None
            else:
                release_date = datetime.strptime(raw_date, "%b %d, %Y").date()

            # create game instance
            game = Game(
                title=title,
                release_date=release_date,
                rating=float(row.get("Rating") or 0),
                times_listed=parse_human_readable_number(row.get("Times Listed")),
                reviews_number=parse_human_readable_number(row.get("Number of Reviews")),
                summary=row.get("Summary") or None,
                plays=parse_human_readable_number(row.get("Plays")),
                playing=parse_human_readable_number(row.get("Playing")),
                backlogs=parse_human_readable_number(row.get("Backlogs")),
                whitelist=parse_human_readable_number(row.get("Wishlist")),
            )
            session.add(game)
            await session.flush()

            # process genres
            for genre_name in parse_flexible_list(row.get("Genres", "")):
                genre = genres_map.get(genre_name)
                if genre:
                    session.add(GameGenre(game_id=game.id, genre_id=genre.id))

            # process teams
            for team_name in parse_flexible_list(row.get("Team", "")):
                team = teams_map.get(team_name)
                if team:
                    session.add(GameTeam(game_id=game.id, team_id=team.id))

            # process reviews
            for review_text in parse_flexible_list(row.get("Reviews", "")):
                session.add(Review(game_id=game.id, review=review_text))

        await session.commit()


def parse_human_readable_number(value) -> int:
    if isinstance(value, int):
        return value
    if value is None:
        return 0

    s = str(value).strip().upper()

    if s.endswith("K"):
        return int(float(s[:-1]) * 1_000)
    elif s.endswith("M"):
        return int(float(s[:-1]) * 1_000_000)
    elif s.endswith("B"):
        return int(float(s[:-1]) * 1_000_000_000)
    elif s.replace(",", "").isdigit():
        return int(s.replace(",", ""))
    else:
        return 0


async def main():
    async with async_session_maker() as session:
        result = await session.execute(select(func.count(Game.id)))
        count = result.scalar_one()
        if count > 0:
            print("Games already seeded, skipping.")
            return

        await load_data(session, CSV_FILE_PATH)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
