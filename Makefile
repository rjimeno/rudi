.PHONY: help all setup-dev tests lint

# Use venv Python if it exists, otherwise fall back to system python3
PYTHON := $(if $(wildcard .venv/bin/python), .venv/bin/python, python3)

all: setup-dev tests lint

setup-dev:
	@echo "Installing development dependencies..."
	$(PYTHON) -m pip install -r requirements-dev.txt

tests:
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

help:
	@echo "Available targets:"
	@echo "  make setup-dev - Install development dependencies (pytest, pylint)"
	@echo "  make tests     - Run unit tests and doctests"
	@echo "  make lint      - Run pylint on rudi.py"
	@echo "  make help      - Show this help message"
	@echo ""
