PYTHON ?= .venv/bin/python
PACKAGE_NAME := kalshi-csv
VERSION := $(shell $(PYTHON) -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
WHEEL := dist/kalshi_csv-$(VERSION)-py3-none-any.whl

.PHONY: all test build install verify-installed help

all: test install verify-installed

test:
	PYTHONPATH=src $(PYTHON) -m pytest -q

build:
	$(PYTHON) -m build

install: build
	$(PYTHON) -m pip install --force-reinstall --no-deps $(WHEEL)

verify-installed:
	$(PYTHON) -c "import kalshi_csv, pathlib, zipfile; v=kalshi_csv.__version__; assert v=='$(VERSION)', v; z=zipfile.ZipFile('$(WHEEL)'); names=set(z.namelist()); required={'kalshi_csv/themes.json','kalshi_csv/templates/modern.html','kalshi_csv/static/modern.css','kalshi_csv/static/dashboard.js','kalshi_csv/static/alpine.min.js','kalshi_csv/static/ALPINE-LICENSE.md'}; missing=required-names; assert not missing, missing; print(f'Installed {v} with all dashboard assets.')"

help:
	@echo "Targets:"
	@echo "  make all             Test, build, install, and verify (default)"
	@echo "  make test            Run the test suite against the checkout"
	@echo "  make build           Build the wheel and source distribution"
	@echo "  make install         Build and force-reinstall the matching wheel"
	@echo "  make verify-installed  Check installed version and packaged assets"
	@echo ""
	@echo "Override the interpreter with: make PYTHON=python3"
