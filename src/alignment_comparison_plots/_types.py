from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QMainWindow


class PlotFunction(Protocol):
    """Shared interface that every plot function in this package must satisfy."""

    def __call__(
        self,
        paths_a: list[str],
        paths_b: list[str],
        label_a: str = "Set A",
        label_b: str = "Set B",
        tier_name: str = "phones",
        aggregate_emphasis: bool = False,
        theme: tuple[str, str, str] | None = None,
        save_png: str | None = None,
        exec_: bool = True,
    ) -> QMainWindow: ...


class PlotFunctionWithThreshold(PlotFunction, Protocol):
    """PlotFunction extended with a threshold parameter."""

    def __call__(  # type: ignore[override]
        self,
        paths_a: list[str],
        paths_b: list[str],
        label_a: str = "Set A",
        label_b: str = "Set B",
        tier_name: str = "phones",
        aggregate_emphasis: bool = False,
        threshold: float = 0.5,
        theme: tuple[str, str, str] | None = None,
        save_png: str | None = None,
        exec_: bool = True,
    ) -> QMainWindow: ...
