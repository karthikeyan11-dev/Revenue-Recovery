.PHONY: help dev up down restart logs test lint format seed build clean

# Python executable inside virtualenv
VENV_PYTHON = backend/venv/bin/python
VENV_PYTEST = backend/venv/bin/pytest
VENV_RUFF = backend/venv/bin/ruff
VENV_BLACK = backend/venv/bin/black

help: ## Show this help message
	@echo "AI Revenue Recovery Orchestrator — Developer Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

up: ## Start PostgreSQL, FastAPI Backend, and React Frontend via Docker Compose
	docker compose up --build -d

down: ## Stop and remove all Docker Compose containers and networks
	docker compose down

restart: ## Restart all Docker Compose services
	docker compose down && docker compose up --build -d

logs: ## Follow Docker Compose container logs
	docker compose logs -f

dev-backend: ## Run FastAPI backend locally with live reloading
	cd backend && ./venv/bin/uvicorn app.main:app --reload --port 8000

dev-frontend: ## Run Vite React frontend locally
	cd frontend && npm run dev

dev: ## Run both backend and frontend locally (requires concurrently or background tasks)
	@echo "Starting backend (port 8000) and frontend (port 5173)..."
	@make -j 2 dev-backend dev-frontend

test: ## Run backend unit & smoke tests with pytest
	@echo "Running backend test suite..."
	cd backend && ./venv/bin/pytest -v

lint-backend: ## Lint backend with ruff and black
	cd backend && ./venv/bin/ruff check . && ./venv/bin/black --check .

lint-frontend: ## Lint frontend with eslint
	cd frontend && npm run lint

lint: lint-backend lint-frontend ## Run all linters (backend ruff/black + frontend eslint)
	@echo "All linters passed successfully!"

format-backend: ## Auto-format backend with ruff and black
	cd backend && ./venv/bin/ruff check . --fix && ./venv/bin/black .

format-frontend: ## Auto-format frontend with prettier
	cd frontend && npx prettier --write "src/**/*.{ts,tsx,css,json}"

format: format-backend format-frontend ## Auto-format all code (backend + frontend)
	@echo "All code formatted successfully!"

seed: ## Run the synthetic data generator stub
	cd backend && ./venv/bin/python -m app.data.synthetic_generator

build-frontend: ## Build frontend static production bundle
	cd frontend && npm run build

build-backend: ## Build backend docker image
	docker build -t revenue-recovery-backend ./backend

build: build-frontend build-backend ## Build both frontend bundle and backend docker image

clean: ## Clean cached python/node build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf frontend/dist
