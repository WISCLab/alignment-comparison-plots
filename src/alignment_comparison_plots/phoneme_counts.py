"""Aggregate phoneme counts across two sets of TextGrids and plot side-by-side bars."""

import sys
from collections import Counter

import textgrids
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QRectF


def count_phonemes(paths: list[str], tier_name: str = "phones", normalize: bool = False) -> Counter:
    counts: Counter = Counter()
    for path in paths:
        tg = textgrids.TextGrid(path)
        for interval in tg[tier_name]:
            label = interval.text.strip()
            if label:
                if normalize:
                    label = label.rstrip("0123456789")
                counts[label] += 1
    return counts


class BarChartWidget(QWidget):
    PAD_L = 60
    PAD_R = 20
    PAD_T = 16
    PAD_B = 60
    BAR_GAP = 2      # gap between the two bars of a group
    GROUP_GAP = 9    # gap between groups
    MAX_BAR_W = 32

    DEFAULT_COLOR_A = QColor("#89b4fa")
    DEFAULT_COLOR_B = QColor("#fab387")
    DEFAULT_BG = QColor("#1e1e2e")
    GRID = QColor("#313244")
    FG = QColor("#cdd6f4")

    def __init__(
        self,
        counts_a: Counter,
        counts_b: Counter,
        label_a: str,
        label_b: str,
        theme: tuple[str, str, str] | None = None,
    ):
        super().__init__()
        if theme is not None:
            self.COLOR_A = QColor(theme[0])
            self.COLOR_B = QColor(theme[1])
            self.BG = QColor(theme[2])
        else:
            self.COLOR_A = self.DEFAULT_COLOR_A
            self.COLOR_B = self.DEFAULT_COLOR_B
            self.BG = self.DEFAULT_BG
        # Union of phonemes present in either set, sorted
        all_phonemes = sorted(set(counts_a) | set(counts_b))
        # Drop phonemes with zero in both (shouldn't happen given union, but kept for clarity)
        self.phonemes = [p for p in all_phonemes if counts_a[p] > 0 or counts_b[p] > 0]
        self.counts_a = counts_a
        self.counts_b = counts_b
        self.label_a = label_a
        self.label_b = label_b
        self.setMinimumSize(max(400, len(self.phonemes) * 54 + self.PAD_L + self.PAD_R), 340)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        chart_w = w - self.PAD_L - self.PAD_R
        chart_h = h - self.PAD_T - self.PAD_B

        painter.fillRect(self.rect(), self.BG)

        if not self.phonemes:
            painter.setPen(self.FG)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No phonemes found.")
            painter.end()
            return

        n = len(self.phonemes)
        max_count = max(
            max((self.counts_a[p] for p in self.phonemes), default=0),
            max((self.counts_b[p] for p in self.phonemes), default=0),
        )

        # Y-axis grid lines + labels
        tick_font = QFont("monospace", 8)
        painter.setFont(tick_font)
        n_ticks = 5
        for i in range(n_ticks + 1):
            val = round(max_count * i / n_ticks)
            y = self.PAD_T + chart_h - (val / max_count) * chart_h if max_count else self.PAD_T
            painter.setPen(self.GRID)
            painter.drawLine(self.PAD_L, int(y), w - self.PAD_R, int(y))
            painter.setPen(self.FG)
            painter.drawText(QRectF(0, y - 10, self.PAD_L - 4, 20),
                             Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                             str(val))

        # Axis lines
        painter.setPen(self.FG)
        painter.drawLine(self.PAD_L, self.PAD_T, self.PAD_L, self.PAD_T + chart_h)
        painter.drawLine(self.PAD_L, self.PAD_T + chart_h, w - self.PAD_R, self.PAD_T + chart_h)

        # Bars
        group_w = chart_w / n
        bar_w = min(self.MAX_BAR_W, (group_w - self.GROUP_GAP * 2 - self.BAR_GAP) / 2)

        for i, phoneme in enumerate(self.phonemes):
            cx = self.PAD_L + (i + 0.5) * group_w
            base_y = self.PAD_T + chart_h

            for count, color, side in [
                (self.counts_a[phoneme], self.COLOR_A, -1),
                (self.counts_b[phoneme], self.COLOR_B, +1),
            ]:
                if count == 0:
                    continue
                bar_h = (count / max_count) * chart_h if max_count else 0
                x = cx + side * (bar_w / 2 + self.BAR_GAP / 2)
                rect = QRectF(x - bar_w / 2, base_y - bar_h, bar_w, bar_h)
                painter.fillRect(rect, color)

                # Count label on top of bar
                painter.setPen(self.FG)
                painter.setFont(QFont("monospace", 8))
                painter.drawText(
                    QRectF(x - bar_w / 2, base_y - bar_h - 16, bar_w, 16),
                    Qt.AlignmentFlag.AlignCenter,
                    str(count),
                )

            # Phoneme label below axis
            painter.setPen(self.FG)
            painter.setFont(QFont("monospace", 9, QFont.Weight.Bold))
            painter.drawText(
                QRectF(cx - group_w / 2, base_y + 4, group_w, 24),
                Qt.AlignmentFlag.AlignCenter,
                phoneme,
            )

        painter.end()


_GITHUB_COUNTS = (
    "https://github.com/WISCLab/alignment-comparison-plots"
    "/blob/main/src/alignment_comparison_plots/phoneme_counts.py"
)


def _footer_label(description: str, url: str) -> QLabel:
    label = QLabel(
        f'{description} &nbsp;<a style="color:#6c7086;" href="{url}">[source]</a>'
    )
    label.setStyleSheet("color: #6c7086; font-family: monospace; font-size: 10px;")
    label.setOpenExternalLinks(True)
    label.setWordWrap(True)
    return label


class LegendWidget(QWidget):
    def __init__(self, entries: list[tuple[QColor, str]], bg: QColor):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(16)
        layout.addStretch()
        for color, label in entries:
            swatch = QLabel()
            swatch.setFixedSize(14, 14)
            swatch.setStyleSheet(
                f"background: {color.name()}; border-radius: 2px;"
            )
            text = QLabel(label)
            text.setStyleSheet("color: #cdd6f4; font-family: monospace; font-size: 11px;")
            layout.addWidget(swatch)
            layout.addWidget(text)
        layout.addStretch()
        self.setStyleSheet(f"background: {bg.name()};")


class PhonemeCountWindow(QMainWindow):
    def __init__(
        self,
        counts_a: Counter,
        counts_b: Counter,
        label_a: str = "Set A",
        label_b: str = "Set B",
        theme: tuple[str, str, str] | None = None,
    ):
        super().__init__()
        self.setWindowTitle("Phoneme Count Comparison")

        chart = BarChartWidget(counts_a, counts_b, label_a, label_b, theme=theme)
        self.setStyleSheet(f"background: {chart.BG.name()};")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)

        title = QLabel("Phoneme Counts per Set")
        title.setStyleSheet("color: #cdd6f4; font-size: 14px; font-weight: bold;")
        layout.addWidget(title)

        legend = LegendWidget(
            [(chart.COLOR_A, label_a), (chart.COLOR_B, label_b)],
            bg=chart.BG,
        )
        layout.addWidget(legend)
        layout.addWidget(chart)
        layout.addWidget(_footer_label(
            "Side-by-side bar chart of how many times each phoneme appears in each alignment set."
            " Use to check whether the two aligners produce similar phoneme distributions.",
            _GITHUB_COUNTS,
        ))

        self.setCentralWidget(container)
        self.resize(chart.minimumWidth() + 20, 420)


def _display_jupyter(path: str) -> None:
    try:
        from IPython import get_ipython
        if get_ipython() is not None:
            from IPython.display import Image, display
            display(Image(filename=path))
    except ImportError:
        pass


def plot_phoneme_counts(
    paths_a: list[str],
    paths_b: list[str],
    label_a: str = "Set A",
    label_b: str = "Set B",
    tier_name: str = "phones",
    aggregate_emphasis: bool = False,
    theme: tuple[str, str, str] | None = None,
    save_png: str | None = None,
    exec_: bool = True,
) -> "PhonemeCountWindow":
    """
    theme:    optional (color_a, color_b, background) hex strings, e.g.
              ("#ff6188", "#a9dc76", "#2d2a2e")
    save_png: optional file path (e.g. "counts.png").  The chart is rendered
              and saved; in Jupyter the image is also displayed inline.
    exec_:    when True (default) show the window and start the Qt event loop
              (standalone / script use).  Set to False when embedding inside a
              larger PyQt6 app — the window is returned without being shown so
              the caller can parent, lay out, or display it as needed.
    """
    counts_a = count_phonemes(paths_a, tier_name, normalize=aggregate_emphasis)
    counts_b = count_phonemes(paths_b, tier_name, normalize=aggregate_emphasis)

    if save_png is not None and exec_ and QApplication.instance() is None:
        import os
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    app = QApplication.instance() or QApplication(sys.argv)
    window = PhonemeCountWindow(counts_a, counts_b, label_a, label_b, theme=theme)

    if save_png is not None:
        window.show()
        app.processEvents()
        window.grab().save(save_png, "PNG")
        _display_jupyter(save_png)
        window.hide()

    if exec_:
        window.show()
        sys.exit(app.exec())

    return window