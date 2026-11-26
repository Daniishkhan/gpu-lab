# Common tasks. Run `make` or `make help` to list them.
VENV := .venv
BIN := $(VENV)/bin
PY ?= $(if $(wildcard $(BIN)/python),$(BIN)/python,python3)

.PHONY: help setup study test one lint check-main progress build serve open

help:
	@echo "make setup      create .venv and install pytest + numpy (zero GPU needed)"
	@echo "make study      launch IDE Study Cockpit (live reload, styled gpu-labs/*.md, auto-pytest)"
	@echo "make test       run every local CPU exercise test"
	@echo "make one K=gpu  run tests whose name matches K (e.g. K=gpu_roofline)"
	@echo "make lint       lint all completed chapters (offline markup, themes, pacing)"
	@echo "make check-main verify all stubs raise NotImplementedError before committing to main"
	@echo "make progress   run tests and show pass counts on subject pages"
	@echo "make build      refresh book/assets/curriculum.js after adding pages or exercises"
	@echo "make serve      serve the static book at http://localhost:8000 (file:// works too)"
	@echo "make open       open book/index.html directly over file://"

setup:
	$(PY) -m venv $(VENV)
	$(BIN)/pip install -q -r requirements-dev.txt
	@echo "Done. Activate with: source $(VENV)/bin/activate"

study:
	$(PY) tools/study.py

test:
	$(PY) -m pytest

one:
	$(PY) -m pytest -k "$(K)"

lint:
	$(PY) tools/check_chapter.py --all

check-main:
	$(PY) tools/check_stubs.py

progress:
	$(PY) tools/build.py --run-tests

build:
	$(PY) tools/build.py

serve:
	@echo "Open http://localhost:8000"
	$(PY) -m http.server 8000 -d book

open:
	open book/index.html
