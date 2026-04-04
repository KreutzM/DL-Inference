#!/usr/bin/env bash
set -euo pipefail
docker compose -f deploy/compose/docker-compose.base.yml up -d
