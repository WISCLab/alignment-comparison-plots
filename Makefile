.PHONY: serve-docs build-docs help

help:
	@echo "serve-docs  Start a local dev server with live reload at http://127.0.0.1:8000"
	@echo "build-docs  Build the static site into the ./site directory"

serve-docs:  ## Start a local dev server with live reload at http://127.0.0.1:8000
	uv run mkdocs serve

build-docs:  ## Build the static site into the ./site directory
	uv run mkdocs build
