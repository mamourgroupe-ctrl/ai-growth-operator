.PHONY: install lint test migrate dev web-install web-build

install:
	python3 -m pip install -e ".[dev]"

lint:
	ruff check apps/api tests
	mypy apps/api/app

test:
	pytest -q

migrate:
	alembic upgrade head

dev:
	uvicorn app.main:app --app-dir apps/api --reload --host 0.0.0.0 --port 8000

web-install:
	npm --prefix apps/web install

web-build:
	npm --prefix apps/web run build
