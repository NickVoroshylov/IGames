.PHONY: migrate makemigrations upgrade downgrade

runserver:
	poetry run uvicorn main:app --reload --app-dir app

build:
	docker compose build && docker compose up -d

run:
	docker compose up -d

stop:
	docker compose down

migrate:
	poetry run alembic upgrade head

lint:
	ruff format . && ruff check --fix .