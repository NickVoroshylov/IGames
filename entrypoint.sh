#!/bin/sh

echo "ENTRYPOINT.SH IS RUNNING"

set -e

echo "Waiting for PostgreSQL..."
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" >/dev/null 2>&1; do
  sleep 1
done

echo "Running alembic migrations..."
alembic upgrade head || { echo "Alembic failed!"; exit 1; }

echo "Seeding database with games..."
python -m app.scripts.seed_games || { echo "Seed games failed!"; exit 1; }

echo "Seeding database with users..."
python -m app.scripts.seed_users || { echo "Seed users failed!"; exit 1; }

echo "Starting app server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
