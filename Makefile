SHELL := /bin/bash
PYTHON ?= python3
COMPOSE ?= docker compose

.PHONY: help fmt lint test smoke up-dev up-prod down tree ps-help review-info docs

help:
	@echo "Targets: fmt lint test smoke up-dev up-prod down tree review-info docs"

fmt:
	$(PYTHON) scripts/fmt_repo.py

lint:
	$(PYTHON) scripts/lint_repo.py


docs:
	$(PYTHON) scripts/check_docs_refs.py


test:
	$(PYTHON) -m pytest tests -q

smoke:
	$(PYTHON) -m pytest tests/smoke -q

up-dev:
	$(COMPOSE) -f deploy/compose/docker-compose.base.yml -f deploy/compose/docker-compose.dev.yml -f deploy/compose/docker-compose.rag.yml -f deploy/compose/docker-compose.vllm.yml -f deploy/compose/docker-compose.librechat.yml up -d

up-prod:
	$(COMPOSE) -f deploy/compose/docker-compose.base.yml -f deploy/compose/docker-compose.prod.yml -f deploy/compose/docker-compose.rag.yml -f deploy/compose/docker-compose.vllm.yml -f deploy/compose/docker-compose.librechat.yml -f deploy/compose/docker-compose.observability.yml up -d

down:
	$(COMPOSE) -f deploy/compose/docker-compose.base.yml down

tree:
	@find . -maxdepth 3 | sort

review-info:
	$(PYTHON) -m repo2ctl.cli review-info

ps-help:
	@echo "Use ./scripts/repo2.ps1 on PowerShell."
