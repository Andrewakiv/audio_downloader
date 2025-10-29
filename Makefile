# =========================
# Docker Compose Makefile
# =========================

# Variables
COMPOSE_FILE := docker-compose.yml
PROFILE := backend
ENV_FILE := backend/envs/local/build.env

# Docker commands shortcut
DC := docker compose -f $(COMPOSE_FILE) --profile=$(PROFILE) --env-file $(ENV_FILE)


# =========================
# PHONY Targets
# =========================
.PHONY: build up down restart logs ps


# =========================
# Commands
# =========================

build:
	$(DC) build

up:
	$(DC) up -d

down:
	$(DC) down

restart: down up

logs:
	$(DC) logs -f

ps:
	$(DC) ps
