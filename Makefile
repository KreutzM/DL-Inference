SHELL := /bin/bash
PYTHON ?= python3
COMPOSE ?= docker compose

.PHONY: help fmt lint test smoke up-dev up-prod down tree

help:
	@echo "Targets: fmt lint test smoke up-dev up-prod down tree"

fmt:
	@echo "TODO: run formatting tools (ruff format / prettier / yamlfix)"

lint:
	@echo "TODO: run lint tools (ruff / mypy / yamllint / markdownlint)"

test:
	$(PYTHON) -m pytest tests -q

smoke:
	$(PYTHON) -m repo2ctl.cli smoke

up-dev:
	$(COMPOSE) -f deploy/compose/docker-compose.base.yml 		-f deploy/compose/docker-compose.dev.yml 		-f deploy/compose/docker-compose.rag.yml 		-f deploy/compose/docker-compose.vllm.yml 		-f deploy/compose/docker-compose.librechat.yml up -d

up-prod:
	$(COMPOSE) -f deploy/compose/docker-compose.base.yml 		-f deploy/compose/docker-compose.prod.yml 		-f deploy/compose/docker-compose.rag.yml 		-f deploy/compose/docker-compose.vllm.yml 		-f deploy/compose/docker-compose.librechat.yml 		-f deploy/compose/docker-compose.observability.yml up -d

down:
	$(COMPOSE) -f deploy/compose/docker-compose.base.yml down

tree:
	@find . -maxdepth 3 | sort

ps-help:
	@echo "Use ./scripts/repo2.ps1 <command> on PowerShell."
