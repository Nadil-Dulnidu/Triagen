.PHONY: help install install-server install-client dev dev-server dev-worker dev-client docker-up docker-down docker-logs docker-build lint lint-server lint-client format test test-server test-client build build-client db-migrate db-makemigrations db-downgrade clean

# Default target
.DEFAULT_GOAL := help

# ── Help ─────────────────────────────────────────────────────────────
help: ## Show available Makefile targets
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Installation ─────────────────────────────────────────────────────
install: install-server install-client ## Install all dependencies (server + client)

install-server: ## Install Python backend dependencies using uv
	@echo "Installing backend dependencies..."
	cd server && uv sync --dev


install-client: ## Install Next.js frontend dependencies using npm
	@echo "Installing frontend dependencies..."
	cd client && npm install

# ── Local Development ────────────────────────────────────────────────
dev: ## Start full local stack via Docker Compose (PostgreSQL, Redis, API, Worker, Client)
	docker compose up

dev-detached: ## Start full local stack in background via Docker Compose
	docker compose up -d

dev-server: ## Run FastAPI backend server locally with hot-reload
	cd server && uv run uvicorn server.main:create_app --factory --reload --port 8000

dev-worker: ## Run Celery background worker locally
	cd server && uv run celery -A server.infrastructure.celery_app:celery_app worker --loglevel=info --concurrency=2

dev-client: ## Run Next.js frontend dev server locally
	cd client && npm run dev

# ── Docker Compose ───────────────────────────────────────────────────
docker-up: ## Start Docker Compose containers
	docker compose up -d

docker-down: ## Stop and remove Docker Compose containers
	docker compose down

docker-logs: ## View real-time logs from Docker Compose containers
	docker compose logs -f

docker-build: ## Rebuild all Docker Compose images
	docker compose build

# ── Code Quality ─────────────────────────────────────────────────────
lint: lint-server lint-client ## Run linter and type-checks on server and client

lint-server: ## Run Ruff check and format check on backend
	cd server && uv run ruff check .
	cd server && uv run ruff format --check .

lint-client: ## Run ESLint and TypeScript checks on frontend
	cd client && npm run lint
	cd client && npx tsc --noEmit

format: ## Auto-format and fix lint issues across codebase
	cd server && uv run ruff check --fix .
	cd server && uv run ruff format .

# ── Testing ──────────────────────────────────────────────────────────
test: test-server ## Run all tests

test-server: ## Run backend tests with pytest
	cd server && uv run pytest -v

test-coverage: ## Run backend tests with coverage report
	cd server && uv run pytest --cov=server --cov-report=term-missing -v

test-client: ## Run frontend tests
	cd client && npm run test --if-present

# ── Database & Migrations ────────────────────────────────────────────
db-migrate: ## Run Alembic database migrations to latest revision
	cd server && uv run alembic -c migrations/alembic.ini upgrade head

db-makemigrations: ## Generate a new Alembic migration (usage: make db-makemigrations name="add_feature")
	@if [ -z "$(name)" ]; then \
		echo "Error: Migration name required. Example: make db-makemigrations name=\"add_new_table\""; \
		exit 1; \
	fi
	cd server && uv run alembic -c migrations/alembic.ini revision --autogenerate -m "$(name)"

db-downgrade: ## Downgrade database by 1 migration step
	cd server && uv run alembic -c migrations/alembic.ini downgrade -1

# ── Build ────────────────────────────────────────────────────────────
build: build-client ## Build production bundles

build-client: ## Build production Next.js frontend bundle
	cd client && npm run build

# ── Cleanup ──────────────────────────────────────────────────────────
clean: ## Remove temporary files, caches, and build artifacts
	@echo "Cleaning up caches and temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf client/.next client/out 2>/dev/null || true
