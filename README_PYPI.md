# alignment-comparison-plots

[![GitHub](https://img.shields.io/badge/GitHub-WiscLab/alignment--comparison--plots-181717?logo=github)](https://github.com/WiscLab/alignment-comparison-plots)

Qt-based forced-alignment comparision plot utils for Praat TextGrid corpora.

**[Full documentation →](https://WISCLab.github.io/alignment-comparison-plots/)**

## Install

```bash
pip install alignment-comparison-plots
```

Requires Python ≥ 3.11.

## Quickstart

```python
import glob
from alignment_comparison_plots import plot_phoneme_counts

paths_a = glob.glob("/path/to/alignment_a/**/*.TextGrid", recursive=True)
paths_b = glob.glob("/path/to/alignment_b/**/*.TextGrid", recursive=True)

plot_phoneme_counts(paths_a=paths_a, paths_b=paths_b, label_a="Ref", label_b="Hyp")
```

## License

MIT
