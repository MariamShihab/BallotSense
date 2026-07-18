.PHONY: api-dev api-format api-lint api-test web-dev web-check check check-november-sources snapshot-prop36-source prepare-prop36-review promote-prop36-review

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

snapshot-prop36-source:
	$(PYTHON) scripts/snapshot_prop36_master_pdf.py

prepare-prop36-review:
	$(PYTHON) scripts/prepare_prop36_review_packet.py

promote-prop36-review:
	$(PYTHON) scripts/promote_review_packet.py --packet data/review_packets/prop-36-2024.json --output data/corpus/prop-36-2024-approved-chunks.json
