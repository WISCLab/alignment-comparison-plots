# alignment-comparison-plots

A high-level toolkit for visualising and comparing forced-alignment outputs.
Point it at two sets of Praat TextGrid files and get interactive Qt charts with a single function call.

## Install

```bash
pip install alignment-comparison-plots
# or with uv
uv add alignment-comparison-plots
```

Requires Python ≥ 3.11. PyQt6 is included as a dependency and handles the GUI.
TextGrid parsing uses [Praat-textgrids](https://github.com/Legisign/Praat-textgrids) (`praat-textgrids`).

## Quickstart

Every plot function is imported from the top-level package and shares the same core API:

```python
import glob
from alignment_comparison_plots import (
    plot_phoneme_counts,
    plot_phoneme_overlap,
    plot_phoneme_overlap_rate,
    plot_phoneme_pair_scatter,
)

paths_a = glob.glob("/path/to/alignment_a/**/*.TextGrid", recursive=True)
paths_b = glob.glob("/path/to/alignment_b/**/*.TextGrid", recursive=True)

# Build shared kwargs once and unpack into each call
SHARED = dict(
    paths_a=paths_a,
    paths_b=paths_b,
    label_a="W2TG Reference",
    label_b="MFA Hypothesis",
    aggregate_emphasis=True,  # strip stress/tone numbers: AH1 → AH
)

plot_phoneme_counts(**SHARED)
plot_phoneme_overlap(**SHARED)
plot_phoneme_overlap_rate(**SHARED, threshold=0.5)
plot_phoneme_pair_scatter(**SHARED)
```

Each function opens a native Qt window and blocks until it is closed.

## PyQt integration

### Scripts

In a plain Python script the plot functions manage the `QApplication` and event loop for you; just call and go:

```python
from PyQt6.QtWidgets import QApplication
import sys

# If you need to open multiple windows in the same process, create the
# QApplication yourself and call app.exec() once at the end instead of
# relying on the implicit one inside each plot function.
app = QApplication(sys.argv)

w1 = plot_phoneme_counts(**SHARED)    # returns the QMainWindow
w2 = plot_phoneme_overlap(**SHARED)
w1.show()
w2.show()

sys.exit(app.exec())
```

> **Note:** The top-level `plot_*` convenience functions call `sys.exit(app.exec())`
> internally, which is fine for single-window scripts. For multi-window scripts,
> use the underlying window classes directly (`PhonemeCountWindow`,
> `PhonemeOverlapWindow`, etc.) and drive the event loop yourself.

### Jupyter / IPython notebooks

The plot functions block the kernel because they start the Qt event loop synchronously.
Enable Qt integration before importing so Jupyter shares its own event loop:

```python
# In a cell before any imports — enables non-blocking Qt windows
%gui qt

from alignment_comparison_plots import plot_phoneme_counts, plot_phoneme_overlap
```

With `%gui qt` active, windows open immediately without blocking subsequent cells.
Do **not** call `sys.exit()` or `app.exec()` yourself when running under `%gui qt`.

### Existing Qt applications

If you are embedding plots inside a larger PyQt6 application, create
`QApplication` before calling any plot function and do not let the plot functions
manage the event loop:

```python
from PyQt6.QtWidgets import QApplication
from alignment_comparison_plots.phoneme_counts import PhonemeCountWindow
from alignment_comparison_plots.phoneme_overlap import (
    PhonemeOverlapWindow,
    compute_phoneme_overlap,
)

app = QApplication.instance()  # reuse the already-running application

overlap = compute_phoneme_overlap(paths_a, paths_b)
window = PhonemeOverlapWindow(overlap, label_a="Ref", label_b="Hyp")
window.show()
# your existing app.exec() call drives the loop
```

## Configuration

### Path validation

**The library does not validate paths.** Functions will raise errors or silently produce
empty charts if paths are missing, malformed, or point to the wrong tier. Validate your
path lists before passing them in; the right checks depend on the use case.

### File matching

`paths_a` and `paths_b` are plain `list[str]` values; any glob, directory walk, or
hand-built list works. Files are **matched by basename**, so both lists must contain
files with identical names (one per recording). Unmatched files are silently skipped.

## Plot functions

| Function | What it shows |
|---|---|
| `plot_phoneme_counts` | Side-by-side bar chart of how many times each phoneme appears in each set. Use to check whether the two aligners produce similar phoneme distributions. |
| `plot_phoneme_overlap` | Mean IoU per phoneme across paired files. Bars sorted ascending left→right; colour interpolates red (poor) → green (perfect). |
| `plot_phoneme_overlap_rate` | Percentage of reference intervals whose best same-label hypothesis match meets the IoU threshold. |
| `plot_phoneme_pair_scatter` | Grid scatter of (reference phoneme, hypothesis phoneme) pairs. Bubble size ∝ count; colour = mean IoU. On-diagonal = label agreement; off-diagonal = substitutions. |

## Notebooks

Runnable examples with annotated cells: [`notebooks/examples.ipynb`](notebooks/examples.ipynb)

## License

MIT
