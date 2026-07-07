.PHONY: install run test lint format docker-build docker-run clean

install:
	poetry install

run:
	poetry run uvicorn app.main:app --reload --port 8000

test:
	poetry run pytest -v

lint:
	poetry run flake8 app tests

format:
	poetry run black app tests

docker-build:
	docker build -t diagnosis-api .

docker-run:
	docker run -p 8000:8000 --env-file .env diagnosis-api

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .venv
