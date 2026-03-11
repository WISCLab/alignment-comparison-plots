# Shared parameters

All four plot functions accept the same core parameters.


```python
import glob
from alignment_comparison_plots import plot_phoneme_counts  # or any other function

paths_a = glob.glob("/path/to/alignment_a/**/*.TextGrid", recursive=True)
paths_b = glob.glob("/path/to/alignment_b/**/*.TextGrid", recursive=True)

plot_phoneme_counts(
    paths_a=paths_a,
    paths_b=paths_b,
    label_a="W2TG Reference",
    label_b="MFA Hypothesis",
    aggregate_emphasis=True,
)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `paths_a` | `list[str]` | — | TextGrid file paths for the first alignment set |
| `paths_b` | `list[str]` | — | TextGrid file paths for the second alignment set |
| `label_a` | `str` | `"Set A"` | Human-readable name for set A, shown in titles and legends |
| `label_b` | `str` | `"Set B"` | Human-readable name for set B, shown in titles and legends |
| `tier_name` | `str` | `"phones"` | Name of the TextGrid interval tier to read |
| `aggregate_emphasis` | `bool` | `False` | Strip trailing stress digits — `AH0`, `AH1`, `AH2` → `AH` |
| `theme` | `tuple[str, str, str] \| None` | `None` | Override colours as `(color_a_or_low, color_b_or_high, background)` hex strings |
| `save_png` | `str \| None` | `None` | Save the chart to this file path instead of (or before) displaying it |
| `exec_` | `bool` | `True` | When `True`, starts the Qt event loop and blocks until the window is closed — the normal behaviour for standalone scripts. Set to `False` when embedding the returned `QMainWindow` inside an existing PyQt6 application or when only saving to PNG. |

