# CodeCrafts Development Commands

.PHONY: help build up down logs clean install test

help: ## Show this help message
	@echo "CodeCrafts Development Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build all Docker containers
	docker-compose build

up: ## Start all services
	docker-compose up -d

dev: ## Start all services with logs
	docker-compose up

down: ## Stop all services
	docker-compose down

logs: ## Show logs for all services
	docker-compose logs -f

clean: ## Remove all containers, networks, and volumes
	docker-compose down -v --remove-orphans
	docker system prune -f

install: ## Install dependencies (run after cloning)
	cp .env.example .env
	docker-compose build

test-backend: ## Run backend tests
	docker-compose exec backend python -m pytest

test-frontend: ## Run frontend tests
	docker-compose exec frontend npm test

shell-backend: ## Open shell in backend container
	docker-compose exec backend bash

shell-frontend: ## Open shell in frontend container
	docker-compose exec frontend sh

db-shell: ## Open PostgreSQL shell
	docker-compose exec db psql -U codecrafts_user -d codecrafts