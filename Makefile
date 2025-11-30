.PHONY: help troubleshoot all setup-dev tests tests-unit tests-integration lint

.DEFAULT_GOAL := help

.DEFAULT:
	@$(MAKE) help

help:
	@echo "Makefile commands:"
	@echo ""
	@echo "  Troubleshooting:"
	@echo "    make troubleshoot - Start a container for troubleshooting"
	@echo ""
	@echo "  Development:"
	@echo "    make setup-dev         - Install development dependencies"
	@echo "    make all               - Run setup-dev, tests, and lint"
	@echo ""
	@echo "  Testing:"
	@echo "    make tests             - Run all tests (unit + integration)"
	@echo "    make tests-unit        - Run unit tests and doctests only (fast)"
	@echo "    make tests-integration - Run Docker-based integration tests (slow, requires Docker)"
	@echo ""
	@echo "  Code quality:"
	@echo "    make lint              - Lint with pylint"
	@echo ""
	@echo "See TESTING.md for testing strategy details."
	@echo ""
	@exit 1 # So only "real" targets succeed (useful for Continuous Integration)

# Use venv Python if it exists, otherwise fall back to system python3
PYTHON := $(if $(wildcard .venv/bin/python), .venv/bin/python, python3)

troubleshoot:
	@echo "Starting a container for troubleshooting..."
	bash tests/troubleshoot/container.sh

all: setup-dev tests lint

setup-dev:
	@echo "Installing development dependencies..."
	$(PYTHON) -m pip install -r requirements-dev.txt

tests: tests-unit tests-integration

tests-unit:
	@echo "Running unit tests and doctests..."
	@if $(PYTHON) -m pytest --version >/dev/null 2>&1; then \
		$(PYTHON) -m pytest tests/ rudi.py -v --doctest-modules; \
	else \
		echo "pytest not installed. Run 'make setup-dev' first."; \
		exit 1; \
	fi

tests-integration:
	@echo "Running integration tests (Docker required)..."
	@if ! command -v docker >/dev/null 2>&1; then \
		echo "Docker not installed or not in PATH."; \
		exit 1; \
	fi
	#@bash tests/integration/test_basic_manifest.sh
	@bash tests/integration/test_default_manifest.sh
	@bash tests/integration/test_evictions.sh
	@bash tests/integration/test_cron_deployment.sh
	@bash tests/integration/test_local_manifest.sh
	@echo ""
	@echo "✓ All integration tests PASSED"

lint:
	@echo "Linting rudi.py..."
	@if $(PYTHON) -m pylint --version >/dev/null 2>&1; then \
		$(PYTHON) -m pylint rudi.py; \
	else \
		echo "pylint not installed. Run 'make setup-dev' first."; \
		exit 1; \
	fi
