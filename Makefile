PYTHON ?= python3
VENV = .venv
PY = $(VENV)/bin/python
CLI = $(PY) scripts/cli.py
COMPOSE = docker compose

.PHONY: configure install dev dev-api dev-web test test-integration lint migrate seed discover-data inspect-gis rank-datasets approve-house approve-senate approve-dbedt ingest-geography ingest-acs ingest-dbedt validate-geography validate-statistics validate-crosswalk build
configure:
	$(PYTHON) scripts/configure.py
install: configure
	$(PYTHON) -m venv $(VENV)
	$(PY) -m pip install -r services/api/requirements.lock
	$(PY) -m pip install --no-deps -e services/api
	npm --prefix apps/web ci --no-audit --no-fund
dev: configure
	$(COMPOSE) up --build
dev-api:
	cd services/api && ../../$(PY) -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
dev-web:
	npm --prefix apps/web run dev
test:
	cd services/api && ../../$(PY) -m pytest -m 'not integration and not live'
	npm --prefix apps/web test
test-integration:
	cd services/api && RUN_POSTGIS_TESTS=1 ../../$(PY) -m pytest -m integration
lint:
	$(VENV)/bin/ruff check --config services/api/pyproject.toml services/api/app services/api/tests pipelines scripts
	npm --prefix apps/web run lint
migrate:
	cd services/api && ../../$(PY) -m alembic upgrade head
seed: ingest-geography ingest-acs
approve-house:
	$(CLI) approve-source --chamber house
approve-senate:
	$(CLI) approve-source --chamber senate
approve-dbedt:
	$(CLI) approve-dbedt --rationale 'Reviewed official DBEDT table 1.06; annual state/county estimates with Maui and Kalawao combined; no district allocation.'
discover-data:
	$(CLI) discover-data
inspect-gis:
	$(CLI) inspect-gis
rank-datasets:
	$(CLI) rank-datasets
ingest-geography:
	$(CLI) ingest-geography
ingest-acs:
	$(CLI) ingest-acs
ingest-dbedt:
	$(CLI) ingest-dbedt
validate-geography:
	$(CLI) validate-geography
validate-statistics:
	$(CLI) validate-statistics
validate-crosswalk:
	$(CLI) validate-crosswalk
build:
	npm --prefix apps/web run build
	$(PY) -m compileall -q services/api/app pipelines scripts

# Opt-in: makes paid model calls through the locally running API.
verify-assistant:
	$(PY) scripts/verify_assistant.py

# Research expansion: cached official captures are reused unless --live is passed to the CLI.
TABLE ?= B17001
ingest-detailed:
	$(CLI) ingest-detailed --table $(TABLE)
ingest-programs:
	$(CLI) ingest-programs

# Opt-in live model + database regression; HTTP/browser verification is separate.
verify-research:
	$(PY) scripts/verify_research_assistant.py --benchmark
