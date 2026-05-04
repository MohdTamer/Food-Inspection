#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = Food-Inspection
PYTHON_VERSION = 3.13
PYTHON_INTERPRETER = python
ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
else
    DETECTED_OS := $(shell uname -s)
endif

#################################################################################
# PATHS                                                                         #
#################################################################################
ROOT_DIR = science_the_data/

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## run the main script
.PHONY: run
run:
	poetry run $(PYTHON_INTERPRETER) $(ROOT_DIR)main.py

.PHONY: dashboard
dashboard:
	poetry run streamlit run $(ROOT_DIR)dashboard/app.py

.PHONY: dataset
dataset:
	poetry run $(PYTHON_INTERPRETER) $(ROOT_DIR)dataset.py

## Install Python dependencies
.PHONY: requirements
requirements:
	poetry install
	
## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using ruff (use `make format` to do formatting)
.PHONY: lint
lint:
	poetry run ruff format --check
	poetry run ruff check

## Format source code with ruff
.PHONY: format
format:
	poetry run ruff check --fix
	poetry run ruff format

## Run all unit tests
.PHONY: test-unit
test-unit:
	poetry run python -m pytest tests/ -v

## Run all unit tests with coverage report
.PHONY: test-unit-coverage
test-unit-coverage:
	poetry run python -m pytest tests/ -v --cov=science_the_data --cov-report=term-missing

## Remove pycache and test artifacts
.PHONY: clean-tests
clean-tests:
ifeq ($(DETECTED_OS),Windows)
	@echo Cleaning on Windows...
	@for /r . %%f in (*.pyc *.pyo) do @del /q "%%f" 2>nul || true
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul || true
	@if exist "tests\__pycache__" rd /s /q "tests\__pycache__"
	@if exist "tests\.pytest_cache" rd /s /q "tests\.pytest_cache"
	@echo Cleaned pycache and test artifacts on Windows.
else
	@echo Cleaning on $(DETECTED_OS)...
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf tests/__pycache__
	rm -rf tests/.pytest_cache
	@echo Cleaned pycache and test artifacts on $(DETECTED_OS).
endif

## Set up Python interpreter environment
.PHONY: create_environment
create_environment:
	poetry env use $(PYTHON_VERSION)
	@echo ">>> Poetry environment created. Activate with: "
	@echo '$$(poetry env activate)'
	@echo ">>> Or run commands with:\npoetry run <command>"


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)
