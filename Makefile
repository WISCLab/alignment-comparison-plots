.PHONY: serve-docs build-docs typecheck test help

help:
	@echo "serve-docs  Start a local dev server with live reload at http://127.0.0.1:8000"
	@echo "build-docs  Build the static site into the ./site directory"
	@echo "typecheck   Run mypy on the source"
	@echo "test        Run protocol conformance tests"

serve-docs:  ## Start a local dev server with live reload at http://127.0.0.1:8000
	cp .github/CONTRIBUTING.md docs/devops/contributing.md
	uv run mkdocs serve

build-docs:  ## Build the static site into the ./site directory
	cp .github/CONTRIBUTING.md docs/devops/contributing.md
	uv run mkdocs build

typecheck:  ## Run mypy on the source
	uv run mypy src/

test:  ## Run protocol conformance tests
	uv run pytest tests/
