.PHONY: help install dev test lint run migrate seed docker-up docker-down

help:
	@echo "CryptoScope AI - Management Commands"
	@echo "  install      Install dependencies"
	@echo "  dev          Run FastAPI dev server with auto-reload"
	@echo "  test         Run complete test suite (unit, integration, leakage)"
	@echo "  lint         Run code linters and type checkers"
	@echo "  migrate      Run database migrations"
	@echo "  seed         Seed initial market data and models"
	@echo "  bot          Start Telegram intelligence bot"
	@echo "  docker-up    Start full stack with Docker Compose"
	@echo "  docker-down  Stop full stack"

install:
	pip install -e ".[dev]"

dev:
	uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

leakage-test:
	pytest tests/leakage/ -v

lint:
	ruff check .
	mypy core/ services/ ml/

bot:
	python -m apps.telegram.bot

seed:
	python scripts/seed_db.py

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down
