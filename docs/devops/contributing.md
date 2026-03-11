# Contributing

> This file is automatically copied into the documentation site on build.
> The rendered version is available at the [docs site](https://WISCLab.github.io/alignment-comparison-plots/devops/contributing/).

## Adding a plot function

### 1. Implement the function

Add your function to an appropriate module under `src/alignment_comparison_plots/` and export it from `src/alignment_comparison_plots/__init__.py`.

Every plot function must conform to one of the protocols defined in [`src/alignment_comparison_plots/_types.py`](../src/alignment_comparison_plots/_types.py) — the single source of truth for parameter names, types, and defaults.

Annotate the export in `__init__.py` with the appropriate protocol type:

```python
plot_my_function: PlotFunction = _plot_my_function
```

This enforces conformance statically via `make typecheck` (mypy) and at runtime via `make test` (pytest). The CI pipeline will catch any violation automatically — see the [CI / CD docs](https://WISCLab.github.io/alignment-comparison-plots/contributing/ci-cd/) for details.

Key behavioural requirements:

- `save_png` must render offscreen and save without opening a window when provided
- `exec_=False` must return the `QMainWindow` without starting the Qt event loop
- Files must be matched by **basename** — unmatched files should be silently skipped
- No internal path or data validation — callers are responsible for validating inputs

### 2. Add a documentation page

Create `docs/api/my_function.md` following the pattern of the existing pages:

- One-sentence description of what the plot shows
- Example plot image (`![...](../img/my_function.png)`)
- `*Click to zoom.*` hint beneath the image
- Minimal usage example
- `Implements [`PlotFunction`](shared.md#plotfunction).` or the appropriate subprotocol link

Register the page in `mkdocs.yml` under the `API` nav section.

### 3. Add a notebook example

Add a section to `notebooks/examples.ipynb` that:

- Includes a markdown cell describing what the plot shows
- Calls the function with `save_png="../docs/img/my_function.png"` and `exec_=False`
- Produces a saved output at `docs/img/my_function.png`

### 4. Checklist

Before opening a pull request:

- [ ] Function annotated with a protocol from `_types.py` in `__init__.py`
- [ ] `make typecheck` passes
- [ ] `make test` passes
- [ ] `docs/api/my_function.md` created and added to `mkdocs.yml`
- [ ] Example plot saved to `docs/img/my_function.png`
- [ ] Notebook section added to `notebooks/examples.ipynb`
- [ ] `make build-docs` runs without errors
