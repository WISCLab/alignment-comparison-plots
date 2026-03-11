from ._types import PlotFunction, PlotFunctionWithThreshold
from .phoneme_counts import plot_phoneme_counts as _plot_phoneme_counts
from .phoneme_overlap import (
    plot_phoneme_overlap as _plot_phoneme_overlap,
    plot_phoneme_overlap_rate as _plot_phoneme_overlap_rate,
    plot_phoneme_pair_scatter as _plot_phoneme_pair_scatter,
)

plot_phoneme_counts: PlotFunction = _plot_phoneme_counts
plot_phoneme_overlap: PlotFunction = _plot_phoneme_overlap
plot_phoneme_overlap_rate: PlotFunctionWithThreshold = _plot_phoneme_overlap_rate
plot_phoneme_pair_scatter: PlotFunction = _plot_phoneme_pair_scatter

__all__ = [
    "plot_phoneme_counts",
    "plot_phoneme_overlap",
    "plot_phoneme_overlap_rate",
    "plot_phoneme_pair_scatter",
    "PlotFunction",
]
