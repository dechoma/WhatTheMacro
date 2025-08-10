SHELL := /bin/bash

COMPOSE := docker compose

.PHONY: help test test-docker compose-build compose-up compose-down compose-logs restart

help:
	@echo "Available targets:"
	@echo "  test           - Use uv to create venv, install deps, and run backend tests"
	@echo "  test-docker    - Start backend container and run pytest inside it"
	@echo "  compose-build  - Build Docker images"
	@echo "  compose-up     - Build and start all services (detached)"
	@echo "  compose-down   - Stop and remove services"
	@echo "  compose-logs   - Tail compose logs"
	@echo "  restart        - Restart all services"

test:
	@command -v uv >/dev/null 2>&1 || (echo "uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh" && exit 1)
	cd backend && \
	uv venv && \
	uv pip install -r requirements.txt -r requirements-test.txt && \
	uv run -m pytest -q

test-docker:
	$(COMPOSE) up -d backend && \
	$(COMPOSE) exec -T backend sh -lc 'pip install -q pytest pytest-mock httpx || true; python -m pytest -q'

compose-build:
	$(COMPOSE) build

compose-up:
	$(COMPOSE) up -d --build

compose-down:
	$(COMPOSE) down

compose-logs:
	$(COMPOSE) logs -f

restart: compose-down compose-up


