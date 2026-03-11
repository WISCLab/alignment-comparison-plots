# alignment-comparison-plots

[![GitHub](https://img.shields.io/badge/GitHub-WiscLab/alignment--comparison--plots-181717?logo=github)](https://github.com/WiscLab/alignment-comparison-plots)

Qt-based forced-alignment evaluation toolkit for Praat TextGrid corpora.

>[!NOTE]
The analyses implemented here were originally developed in R by [@tjmahr](https://github.com/tjmahr). This package adapts his work for python.

## Install

```bash
pip install alignment-comparison-plots
```

Requires Python ≥ 3.11.

## Plot functions

| Function | What it shows |
|---|---|
| `plot_phoneme_counts` | Side-by-side phoneme frequency distributions |
| `plot_phoneme_overlap` | Mean IoU per phoneme, colour-coded red→green |
| `plot_phoneme_overlap_rate` | % of reference intervals meeting an IoU threshold |
| `plot_phoneme_pair_scatter` | Substitution grid — bubble size ∝ count, colour = mean IoU |

## Usage

All functions share the same core parameters:

```python
import glob

paths_a = glob.glob("/path/to/alignment_a/**/*.TextGrid", recursive=True)
paths_b = glob.glob("/path/to/alignment_b/**/*.TextGrid", recursive=True)

SHARED = dict(
    paths_a=paths_a,
    paths_b=paths_b,
    label_a="W2TG Reference",
    label_b="MFA Hypothesis",
    aggregate_emphasis=True,  # strip stress numbers: AH1 → AH
)
```

### Export to PNG (no display required)

Pass `save_png=` and `exec_=False` to render offscreen and save without opening a window.

```python
from alignment_comparison_plots import (
    plot_phoneme_counts,
    plot_phoneme_overlap,
    plot_phoneme_overlap_rate,
    plot_phoneme_pair_scatter,
)

plot_phoneme_counts(**SHARED, save_png="counts.png", exec_=False)
plot_phoneme_overlap(**SHARED, save_png="overlap.png", exec_=False)
plot_phoneme_overlap_rate(**SHARED, threshold=0.5, save_png="overlap_rate.png", exec_=False)
plot_phoneme_pair_scatter(**SHARED, save_png="pair_scatter.png", exec_=False)
sys.exit(0)  # QApplication keeps the process alive without an event loop
```

### Embed in a PyQt6 application

Pass `exec_=False` to get the `QMainWindow` back without starting the event loop,
then parent or lay it out however you need.

```python
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QWidget
from alignment_comparison_plots import plot_phoneme_counts, plot_phoneme_overlap
import sys

app = QApplication(sys.argv)

container = QWidget()
layout = QHBoxLayout(container)

counts_window = plot_phoneme_counts(**SHARED, exec_=False)
overlap_window = plot_phoneme_overlap(**SHARED, exec_=False)

layout.addWidget(counts_window.centralWidget())
layout.addWidget(overlap_window.centralWidget())

container.show()
sys.exit(app.exec())
```

### Standalone interactive window

The default behaviour — opens a native Qt window and blocks until it is closed.

```python
from alignment_comparison_plots import plot_phoneme_counts

plot_phoneme_counts(**SHARED)  # exec_=True by default
```

To open multiple windows in one process, drive the event loop yourself:

```python
from PyQt6.QtWidgets import QApplication
from alignment_comparison_plots import plot_phoneme_counts, plot_phoneme_overlap
import sys

app = QApplication(sys.argv)

w1 = plot_phoneme_counts(**SHARED, exec_=False)
w2 = plot_phoneme_overlap(**SHARED, exec_=False)
w1.show()
w2.show()

sys.exit(app.exec())
```

## License

MIT
