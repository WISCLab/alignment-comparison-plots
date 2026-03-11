# Shared parameters

All plot functions implement one of the protocols defined in
[`src/alignment_comparison_plots/_types.py`](https://github.com/WiscLab/alignment-comparison-plots/blob/main/src/alignment_comparison_plots/_types.py) — the authoritative source for parameter names, types, and defaults.

---

## `PlotFunction`

Base interface.

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

---

## `PlotFunctionWithThreshold`

Extends `PlotFunction` with one additional parameter.

Includes all parameters from `PlotFunction`, plus:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `threshold` | `float` | `0.5` | Minimum IoU for a match to count as successful. Raise to tighten the criterion. |
