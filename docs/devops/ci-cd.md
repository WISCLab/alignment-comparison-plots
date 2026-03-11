# CI / CD

[![CI](https://github.com/WiscLab/alignment-comparison-plots/actions/workflows/ci.yml/badge.svg)](https://github.com/WiscLab/alignment-comparison-plots/actions/workflows/ci.yml)
[![CD](https://github.com/WiscLab/alignment-comparison-plots/actions/workflows/cd.yml/badge.svg)](https://github.com/WiscLab/alignment-comparison-plots/actions/workflows/cd.yml)

## CI (`ci.yml`)

Runs on every push to `main` / `release` and on all pull requests.

The CI is particularly valuable because it enforces that every new plot function conforms to the shared API defined in [`_types.py`](https://github.com/WiscLab/alignment-comparison-plots/blob/main/src/alignment_comparison_plots/_types.py). Conformance is checked at two levels:

- **Statically** — `mypy` verifies the type annotation on the export in [`__init__.py`](https://github.com/WiscLab/alignment-comparison-plots/blob/main/src/alignment_comparison_plots/__init__.py) matches a protocol
- **At runtime** — `pytest` checks that the annotation is a recognised protocol type *and* that the function signature is a superset of it

This means a contributor cannot add a plot function to `__all__` without either annotating it with a protocol (caught by the test) or having the wrong signature (caught by both).

| Job | Depends on | Description |
|---|---|---|
| `test` | — | Runs `pytest tests/` — protocol conformance checks |
| `typecheck` | `test` | Runs `mypy src/` — static type checking |
| `build-docs` | `typecheck` | Runs `mkdocs build` — verifies the docs build cleanly |
| `deploy-docs` | `build-docs` | Runs `mkdocs gh-deploy` — pushes to GitHub Pages (`main` only) |

Each job only runs if the previous one passes.

## CD (`cd.yml`)

Triggers on GitHub release publish. Builds the package and publishes to PyPI via trusted OIDC publishing — no API token required.

To release:

1. Create a GitHub release with a version tag (e.g. `v0.2.0`)
2. The CD workflow publishes automatically
