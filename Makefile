# Common tasks. Run `make` or `make help` to list them.
VENV := .venv
BIN := $(VENV)/bin
PY ?= $(if $(wildcard $(BIN)/python),$(BIN)/python,python3)

.PHONY: help setup test one lint progress build serve open

help:
	@echo "make setup      create .venv and install pytest + numpy (zero GPU needed)"
	@echo "make test       run every local CPU exercise test"
	@echo "make one K=gpu  run tests whose name matches K (e.g. K=gpu_roofline)"
	@echo "make lint       lint all completed chapters (offline markup, themes, pacing)"
	@echo "make progress   run tests and show pass counts on subject pages"
	@echo "make build      refresh assets/curriculum.js after adding pages or exercises"
	@echo "make serve      serve the site at http://localhost:8000 (file:// works too)"

setup:
	$(PY) -m venv $(VENV)
	$(BIN)/pip install -q -r requirements-dev.txt
	@echo "Done. Activate with: source $(VENV)/bin/activate"

test:
	$(PY) -m pytest

one:
	$(PY) -m pytest -k "$(K)"

lint:
	$(PY) tools/check_chapter.py --all

progress:
	$(PY) tools/build.py --run-tests

build:
	$(PY) tools/build.py

serve:
	@echo "Open http://localhost:8000"
	$(PY) -m http.server 8000

open:
	open index.html
