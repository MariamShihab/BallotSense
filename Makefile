.PHONY: api-dev api-format api-lint api-test web-dev web-check check check-november-sources

PYTHON ?= .venv/bin/python
NPM ?= npm

api-dev:
	uvicorn ballotsense_api.main:app --reload

api-format:
	$(PYTHON) -m ruff format ballotsense_api tests

api-lint:
	$(PYTHON) -m ruff check ballotsense_api tests

api-test:
	$(PYTHON) -m pytest

web-dev:
	$(NPM) --prefix web run dev

web-check:
	$(NPM) --prefix web run check

check: api-lint api-test web-check

check-november-sources:
	$(PYTHON) scripts/check_november_sources.py
