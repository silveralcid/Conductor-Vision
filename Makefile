# ===== Generic Python Dev Makefile =====
# Works in PowerShell, Git Bash, or WSL
# --------------------------------------

PYTHON := python
.DEFAULT_GOAL := help

## Format, sort imports, and lint
lint:
	@echo 🔧 Formatting and linting...
	$(PYTHON) -m black .
	$(PYTHON) -m isort .
	$(PYTHON) -m flake8
	@echo Code style clean!

## Run tests (pytest)
test:
	@echo 🧪 Running tests...
	$(PYTHON) -m pytest -q
	@echo Tests complete!

## Clean build/test artifacts
clean:
	@echo 🧹 Cleaning caches...
	-@rmdir /s /q __pycache__ 2>nul || true
	-@rmdir /s /q .pytest_cache 2>nul || true
	-@del /s /q *.pyc 2>nul || true
	@echo Clean complete!

## Check installed tool versions
check-tools:
	@echo 🧰 Checking formatter/linter versions...
	$(PYTHON) -m black --version
	$(PYTHON) -m flake8 --version
	$(PYTHON) -m isort --version
	@echo Tools verified!

## Run any Python script (pass file=path)
# Example: make run file=server.py
run:
	@echo 🚀 Running $(file)...
	$(PYTHON) $(file)

## Display available targets
help:
	@echo "Available make targets:"
	@echo "  make lint         - Format, sort imports, and lint"
	@echo "  make test         - Run pytest tests"
	@echo "  make clean        - Remove caches and .pyc files"
	@echo "  make check-tools  - Show black/flake8/isort versions"
	@echo "  make run file=... - Run a specific Python file"

## Display coverage report
coverage:
	$(PYTHON) -m pytest --cov=. --cov-report=term-missing

## Static type check
typecheck:
	@echo 🔍 Running mypy...
	$(PYTHON) -m mypy .
