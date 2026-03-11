# alignment-comparison-plots

[![PyPI](https://img.shields.io/pypi/v/alignment-comparison-plots)](https://pypi.org/project/alignment-comparison-plots/)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://WISCLab.github.io/alignment-comparison-plots/)
[![WiscLab](https://img.shields.io/badge/WiscLab-kidspeech.wisc.edu-c5050c)](https://kidspeech.wisc.edu/)
[![CI](https://github.com/WiscLab/alignment-comparison-plots/actions/workflows/ci.yml/badge.svg)](https://github.com/WiscLab/alignment-comparison-plots/actions/workflows/ci.yml) [![CD](https://github.com/WiscLab/alignment-comparison-plots/actions/workflows/cd.yml/badge.svg)](https://github.com/WiscLab/alignment-comparison-plots/actions/workflows/cd.yml)

When two forced aligners (e.g. MFA and Wav2TextGrid) produce different `.TextGrid` files for the same audio, it can be hard to know where and how they disagree. This package provides ready-made Qt charts that let you visually audit alignment quality and inter-aligner agreement across an entire corpus in seconds:

> [!NOTE]
> The analyses implemented here were originally developed in R by [@tjmahr](https://github.com/tjmahr). This package adapts his work for Python.

## Install

```bash
pip install alignment-comparison-plots
# or with uv
uv add alignment-comparison-plots
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

## Development

See the [Contributing guide](https://WISCLab.github.io/alignment-comparison-plots/devops/contributing/) for instructions on adding new plot functions.

```bash
make serve-docs   # local docs preview at http://127.0.0.1:8000
make build-docs   # build static site into ./site
make typecheck    # run mypy on the source
make test         # run protocol conformance tests
```

## License

MIT