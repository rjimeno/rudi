.PHONY: help all setup-dev tests test lint

# Use venv Python if it exists, otherwise fall back to system python3
PYTHON := $(if $(wildcard .venv/bin/python), .venv/bin/python, python3)

help:
	@echo "Makefile commands:"
	@echo "  make all         - Run setup-dev, tests, and lint"
	@echo "  make setup-dev   - Install development dependencies"
	@echo "  make tests       - Run unit and doctests"
	@echo "  make lint        - Lint the code with pylint"


all: setup-dev tests lint

setup-dev:
	@echo "Installing development dependencies..."
	$(PYTHON) -m pip install -r requirements-dev.txt

tests: test

test:
	@echo "Running Rudi tests (unit + doctest)..."
	@if ${PYTHON} -m pytest --version >/dev/null 2>&1; then \
		$(PYTHON) -m pytest tests/ rudi.py -v --doctest-modules; \
	else \
		echo "pytest not installed. Run 'make setup-dev' first."; \
		exit 1; \
	fi

lint:
	@echo "Linting rudi.py..."
	@if $(PYTHON) -m pylint --version >/dev/null 2>&1; then \
		$(PYTHON) -m pylint rudi.py; \
	else \
		echo "pylint not installed. Run 'make setup-dev' first."; \
		exit 1; \
	fi
