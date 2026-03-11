"""Compare alignment overlap per phoneme between two paired sets of TextGrids."""

import sys
from collections import defaultdict
from pathlib import Path

import textgrids
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QRectF


_GITHUB_OVERLAP = (
    "https://github.com/WISCLab/alignment-comparison-plots"
    "/blob/main/src/alignment_comparison_plots/phoneme_overlap.py"
)


def _footer_label(description: str, url: str) -> QLabel:
    label = QLabel(
        f'{description} &nbsp;<a style="color:#6c7086;" href="{url}">[source]</a>'
    )
    label.setStyleSheet("color: #6c7086; font-family: monospace; font-size: 10px;")
    label.setOpenExternalLinks(True)
    label.setWordWrap(True)
    return label


def _iou(a_start: float, a_end: float, b_start: float, b_end: float) -> float:
    inter = max(0.0, min(a_end, b_end) - max(a_start, b_start))
    if inter == 0.0:
        return 0.0
    union = max(a_end, b_end) - min(a_start, b_start)
    return inter / union


def _collect_same_label_scores(
    paths_a: list[str],
    paths_b: list[str],
    tier_name: str,
    normalize: bool,
) -> dict[str, list[float]]:
    """
    For each reference interval find the best same-label hypothesis IoU.
    Returns raw per-interval scores grouped by phoneme label.
    """
    map_a = {Path(p).name: p for p in paths_a}
    map_b = {Path(p).name: p for p in paths_b}
    common = set(map_a) & set(map_b)

    scores: dict[str, list[float]] = defaultdict(list)

    def norm(s: str) -> str:
        return s.rstrip("0123456789") if normalize else s

    for name in common:
        tg_a = textgrids.TextGrid(map_a[name])
        tg_b = textgrids.TextGrid(map_b[name])

        ivs_b = [
            (float(iv.xmin), float(iv.xmax), norm(iv.text.strip()))
            for iv in tg_b[tier_name]
            if iv.text.strip()
        ]

        for iv in tg_a[tier_name]:
            label = norm(iv.text.strip())
            if not label:
                continue
            a_start, a_end = float(iv.xmin), float(iv.xmax)
            best = max(
                (_iou(a_start, a_end, bs, be) for bs, be, bl in ivs_b if bl == label),
                default=0.0,
            )
            scores[label].append(best)

    return dict(scores)


def compute_phoneme_overlap(
    paths_a: list[str],
    paths_b: list[str],
    tier_name: str = "phones",
    normalize: bool = False,
) -> dict[str, tuple[float, int]]:
    """Returns phoneme -> (mean_iou, count)."""
    raw = _collect_same_label_scores(paths_a, paths_b, tier_name, normalize)
    return {p: (sum(v) / len(v), len(v)) for p, v in raw.items()}


def compute_phoneme_overlap_rate(
    paths_a: list[str],
    paths_b: list[str],
    tier_name: str = "phones",
    normalize: bool = False,
    threshold: float = 0.5,
) -> dict[str, tuple[float, int]]:
    """Returns phoneme -> (fraction_meeting_threshold, count)."""
    raw = _collect_same_label_scores(paths_a, paths_b, tier_name, normalize)
    return {
        p: (sum(1 for s in v if s >= threshold) / len(v), len(v))
        for p, v in raw.items()
    }


def compute_phoneme_pair_overlap(
    paths_a: list[str],
    paths_b: list[str],
    tier_name: str = "phones",
    normalize: bool = False,
) -> dict[tuple[str, str], tuple[float, int]]:
    """
    Returns dict mapping (ref_phoneme, hyp_phoneme) -> (mean_iou, count).
    For each reference interval the hypothesis interval with the greatest
    temporal overlap is found (regardless of label) and the pair is recorded.
    """
    map_a = {Path(p).name: p for p in paths_a}
    map_b = {Path(p).name: p for p in paths_b}
    common = set(map_a) & set(map_b)

    scores: dict[tuple[str, str], list[float]] = defaultdict(list)

    def norm(s: str) -> str:
        return s.rstrip("0123456789") if normalize else s

    for name in common:
        tg_a = textgrids.TextGrid(map_a[name])
        tg_b = textgrids.TextGrid(map_b[name])

        ivs_b = [
            (float(iv.xmin), float(iv.xmax), norm(iv.text.strip()))
            for iv in tg_b[tier_name]
            if iv.text.strip()
        ]

        for iv in tg_a[tier_name]:
            ref_label = norm(iv.text.strip())
            if not ref_label:
                continue
            a_start, a_end = float(iv.xmin), float(iv.xmax)

            best_iou, best_hyp = 0.0, None
            for bs, be, bl in ivs_b:
                iou = _iou(a_start, a_end, bs, be)
                if iou > best_iou:
                    best_iou, best_hyp = iou, bl

            if best_hyp is not None:
                scores[(ref_label, best_hyp)].append(best_iou)

    return {pair: (sum(v) / len(v), len(v)) for pair, v in scores.items() if v}


def _lerp_color(c0: QColor, c1: QColor, t: float) -> QColor:
    t = max(0.0, min(1.0, t))
    return QColor(
        round(c0.red()   + (c1.red()   - c0.red())   * t),
        round(c0.green() + (c1.green() - c0.green()) * t),
        round(c0.blue()  + (c1.blue()  - c0.blue())  * t),
    )


class OverlapChartWidget(QWidget):
    PAD_L = 60
    PAD_R = 20
    PAD_T = 16
    PAD_B = 72    # extra room for "n=X" line below phoneme label
    GROUP_GAP = 12
    MAX_BAR_W = 36

    DEFAULT_LOW = QColor("#f38ba8")   # red  – poor overlap
    DEFAULT_HIGH = QColor("#a6e3a1")  # green – perfect overlap
    DEFAULT_BG = QColor("#1e1e2e")
    GRID = QColor("#313244")
    FG = QColor("#cdd6f4")

    def __init__(
        self,
        overlap: dict[str, tuple[float, int]],
        theme: tuple[str, str, str] | None = None,
    ):
        super().__init__()
        if theme is not None:
            self.LOW = QColor(theme[0])
            self.HIGH = QColor(theme[1])
            self.BG = QColor(theme[2])
        else:
            self.LOW = self.DEFAULT_LOW
            self.HIGH = self.DEFAULT_HIGH
            self.BG = self.DEFAULT_BG
        # Sort ascending so worst-overlapping phonemes appear on the left
        self.phonemes = sorted(overlap, key=lambda p: overlap[p][0])
        self.overlap = overlap
        self.setMinimumSize(max(400, len(self.phonemes) * 48 + self.PAD_L + self.PAD_R), 340)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        chart_w = w - self.PAD_L - self.PAD_R
        chart_h = h - self.PAD_T - self.PAD_B

        painter.fillRect(self.rect(), self.BG)

        if not self.phonemes:
            painter.setPen(self.FG)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No overlap data.")
            painter.end()
            return

        n = len(self.phonemes)

        # Y-axis grid lines + labels (0.0 → 1.0)
        painter.setFont(QFont("monospace", 8))
        for i in range(6):
            val = i / 5
            y = self.PAD_T + chart_h - val * chart_h
            painter.setPen(self.GRID)
            painter.drawLine(self.PAD_L, int(y), w - self.PAD_R, int(y))
            painter.setPen(self.FG)
            painter.drawText(
                QRectF(0, y - 10, self.PAD_L - 4, 20),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                f"{val:.1f}",
            )

        # Axis lines
        painter.setPen(self.FG)
        painter.drawLine(self.PAD_L, self.PAD_T, self.PAD_L, self.PAD_T + chart_h)
        painter.drawLine(self.PAD_L, self.PAD_T + chart_h, w - self.PAD_R, self.PAD_T + chart_h)

        group_w = chart_w / n
        bar_w = min(self.MAX_BAR_W, group_w - self.GROUP_GAP * 2)

        for i, phoneme in enumerate(self.phonemes):
            mean_iou, count = self.overlap[phoneme]
            cx = self.PAD_L + (i + 0.5) * group_w
            base_y = self.PAD_T + chart_h
            bar_h = mean_iou * chart_h

            painter.fillRect(
                QRectF(cx - bar_w / 2, base_y - bar_h, bar_w, bar_h),
                _lerp_color(self.LOW, self.HIGH, mean_iou),
            )

            # IoU value on top of bar
            painter.setPen(self.FG)
            painter.setFont(QFont("monospace", 8))
            painter.drawText(
                QRectF(cx - bar_w / 2, base_y - bar_h - 16, bar_w, 16),
                Qt.AlignmentFlag.AlignCenter,
                f"{mean_iou:.2f}",
            )

            # Phoneme label
            painter.setFont(QFont("monospace", 9, QFont.Weight.Bold))
            painter.drawText(
                QRectF(cx - group_w / 2, base_y + 4, group_w, 22),
                Qt.AlignmentFlag.AlignCenter,
                phoneme,
            )

            # Sample count
            painter.setFont(QFont("monospace", 7))
            painter.drawText(
                QRectF(cx - group_w / 2, base_y + 26, group_w, 18),
                Qt.AlignmentFlag.AlignCenter,
                f"n={count}",
            )

        painter.end()


class PhonemeOverlapWindow(QMainWindow):
    def __init__(
        self,
        overlap: dict[str, tuple[float, int]],
        label_a: str = "Set A",
        label_b: str = "Set B",
        theme: tuple[str, str, str] | None = None,
    ):
        super().__init__()
        self.setWindowTitle("Phoneme Overlap Comparison")

        chart = OverlapChartWidget(overlap, theme=theme)
        self.setStyleSheet(f"background: {chart.BG.name()};")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)

        title = QLabel(f"Phoneme Overlap (IoU): {label_a} vs {label_b}")
        title.setStyleSheet("color: #cdd6f4; font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        layout.addWidget(chart)
        layout.addWidget(_footer_label(
            "Mean IoU per phoneme across paired files. For each reference interval the best"
            " same-label hypothesis interval is scored. Sorted left→right by ascending overlap;"
            " colour interpolates red (poor) → green (perfect).",
            _GITHUB_OVERLAP,
        ))

        self.setCentralWidget(container)
        self.resize(chart.minimumWidth() + 20, 440)


def _display_jupyter(path: str) -> None:
    try:
        from IPython import get_ipython
        if get_ipython() is not None:
            from IPython.display import Image, display
            display(Image(filename=path))
    except ImportError:
        pass


def plot_phoneme_overlap(
    paths_a: list[str],
    paths_b: list[str],
    label_a: str = "Set A",
    label_b: str = "Set B",
    tier_name: str = "phones",
    aggregate_emphasis: bool = False,
    theme: tuple[str, str, str] | None = None,
    save_png: str | None = None,
    exec_: bool = True,
) -> "PhonemeOverlapWindow":
    """
    Plot mean IoU per phoneme between two paired sets of TextGrids.
    Files are matched by basename.

    theme:    optional (low_color, high_color, background) hex strings.
              Each bar's color interpolates from low (IoU=0) to high (IoU=1).
    save_png: optional file path (e.g. "overlap.png").  The chart is rendered
              and saved; in Jupyter the image is also displayed inline.
    exec_:    when True (default) show the window and start the Qt event loop
              (standalone / script use).  Set to False when embedding inside a
              larger PyQt6 app — the window is returned without being shown so
              the caller can parent, lay out, or display it as needed.
    """
    overlap = compute_phoneme_overlap(paths_a, paths_b, tier_name, normalize=aggregate_emphasis)

    if save_png is not None and QApplication.instance() is None:
        import os
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    app = QApplication.instance() or QApplication(sys.argv)
    window = PhonemeOverlapWindow(overlap, label_a, label_b, theme=theme)

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


class OverlapRateWidget(QWidget):
    PAD_L = 60
    PAD_R = 20
    PAD_T = 16
    PAD_B = 72
    GROUP_GAP = 12
    MAX_BAR_W = 36

    DEFAULT_LOW = QColor("#f38ba8")
    DEFAULT_HIGH = QColor("#a6e3a1")
    DEFAULT_BG = QColor("#1e1e2e")
    GRID = QColor("#313244")
    FG = QColor("#cdd6f4")

    def __init__(
        self,
        rates: dict[str, tuple[float, int]],
        threshold: float,
        theme: tuple[str, str, str] | None = None,
    ):
        super().__init__()
        if theme is not None:
            self.LOW = QColor(theme[0])
            self.HIGH = QColor(theme[1])
            self.BG = QColor(theme[2])
        else:
            self.LOW = self.DEFAULT_LOW
            self.HIGH = self.DEFAULT_HIGH
            self.BG = self.DEFAULT_BG
        self.threshold = threshold
        self.phonemes = sorted(rates, key=lambda p: rates[p][0])
        self.rates = rates
        self.setMinimumSize(max(400, len(self.phonemes) * 48 + self.PAD_L + self.PAD_R), 340)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        chart_w = w - self.PAD_L - self.PAD_R
        chart_h = h - self.PAD_T - self.PAD_B

        painter.fillRect(self.rect(), self.BG)

        if not self.phonemes:
            painter.setPen(self.FG)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No data.")
            painter.end()
            return

        n = len(self.phonemes)

        # Y-axis: 0% – 100%
        painter.setFont(QFont("monospace", 8))
        for i in range(6):
            val = i / 5
            y = self.PAD_T + chart_h - val * chart_h
            painter.setPen(self.GRID)
            painter.drawLine(self.PAD_L, int(y), w - self.PAD_R, int(y))
            painter.setPen(self.FG)
            painter.drawText(
                QRectF(0, y - 10, self.PAD_L - 4, 20),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                f"{round(val * 100)}%",
            )

        # Axis lines
        painter.setPen(self.FG)
        painter.drawLine(self.PAD_L, self.PAD_T, self.PAD_L, self.PAD_T + chart_h)
        painter.drawLine(self.PAD_L, self.PAD_T + chart_h, w - self.PAD_R, self.PAD_T + chart_h)

        group_w = chart_w / n
        bar_w = min(self.MAX_BAR_W, group_w - self.GROUP_GAP * 2)

        for i, phoneme in enumerate(self.phonemes):
            rate, count = self.rates[phoneme]
            cx = self.PAD_L + (i + 0.5) * group_w
            base_y = self.PAD_T + chart_h
            bar_h = rate * chart_h

            painter.fillRect(
                QRectF(cx - bar_w / 2, base_y - bar_h, bar_w, bar_h),
                _lerp_color(self.LOW, self.HIGH, rate),
            )

            # Percentage on top of bar
            painter.setPen(self.FG)
            painter.setFont(QFont("monospace", 8))
            painter.drawText(
                QRectF(cx - bar_w / 2, base_y - bar_h - 16, bar_w, 16),
                Qt.AlignmentFlag.AlignCenter,
                f"{round(rate * 100)}%",
            )

            # Phoneme label
            painter.setFont(QFont("monospace", 9, QFont.Weight.Bold))
            painter.drawText(
                QRectF(cx - group_w / 2, base_y + 4, group_w, 22),
                Qt.AlignmentFlag.AlignCenter,
                phoneme,
            )

            # Sample count
            painter.setFont(QFont("monospace", 7))
            painter.drawText(
                QRectF(cx - group_w / 2, base_y + 26, group_w, 18),
                Qt.AlignmentFlag.AlignCenter,
                f"n={count}",
            )

        painter.end()


class PhonemeOverlapRateWindow(QMainWindow):
    def __init__(
        self,
        rates: dict[str, tuple[float, int]],
        threshold: float,
        label_a: str = "Set A",
        label_b: str = "Set B",
        theme: tuple[str, str, str] | None = None,
    ):
        super().__init__()
        self.setWindowTitle("Phoneme Overlap Rate")

        chart = OverlapRateWidget(rates, threshold, theme=theme)
        self.setStyleSheet(f"background: {chart.BG.name()};")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)

        title = QLabel(
            f"% Intervals Meeting IoU ≥ {threshold:.2f}: {label_a} vs {label_b}"
        )
        title.setStyleSheet("color: #cdd6f4; font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        layout.addWidget(chart)
        layout.addWidget(_footer_label(
            f"Per-phoneme percentage of reference intervals whose best same-label hypothesis"
            f" match has IoU ≥ {threshold:.2f}. Sorted left→right by ascending rate;"
            f" colour interpolates red (0 %) → green (100 %).",
            _GITHUB_OVERLAP,
        ))

        self.setCentralWidget(container)
        self.resize(chart.minimumWidth() + 20, 440)


def plot_phoneme_overlap_rate(
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
) -> "PhonemeOverlapRateWindow":
    """
    Bar chart showing what percentage of each phoneme's intervals meet
    the given IoU threshold between two paired alignment sets.
    Files are matched by basename.

    threshold: minimum IoU to count as a successful match (default 0.5).
    theme:     optional (low_color, high_color, background) hex strings.
    save_png:  optional file path (e.g. "overlap_rate.png").  The chart is
               rendered and saved; in Jupyter the image is also displayed inline.
    exec_:     when True (default) show the window and start the Qt event loop
               (standalone / script use).  Set to False when embedding inside a
               larger PyQt6 app — the window is returned without being shown so
               the caller can parent, lay out, or display it as needed.
    """
    rates = compute_phoneme_overlap_rate(
        paths_a, paths_b, tier_name, normalize=aggregate_emphasis, threshold=threshold,
    )

    if save_png is not None and QApplication.instance() is None:
        import os
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    app = QApplication.instance() or QApplication(sys.argv)
    window = PhonemeOverlapRateWindow(rates, threshold, label_a, label_b, theme=theme)

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


class PairScatterWidget(QWidget):
    CELL = 22        # pixels per grid cell
    MAX_R = 9        # max bubble radius
    PAD_L = 64       # room for hyp labels on the left
    PAD_R = 20
    PAD_T = 20
    PAD_B = 64       # room for ref labels on the bottom

    DEFAULT_LOW = QColor("#f38ba8")
    DEFAULT_HIGH = QColor("#a6e3a1")
    DEFAULT_BG = QColor("#1e1e2e")
    GRID = QColor("#313244")
    FG = QColor("#cdd6f4")

    def __init__(
        self,
        pairs: dict[tuple[str, str], tuple[float, int]],
        label_a: str = "Set A",
        label_b: str = "Set B",
        theme: tuple[str, str, str] | None = None,
    ):
        super().__init__()
        if theme is not None:
            self.LOW = QColor(theme[0])
            self.HIGH = QColor(theme[1])
            self.BG = QColor(theme[2])
        else:
            self.LOW = self.DEFAULT_LOW
            self.HIGH = self.DEFAULT_HIGH
            self.BG = self.DEFAULT_BG

        self.label_a = label_a
        self.label_b = label_b
        self.pairs = pairs

        ref_phones = sorted({r for r, _ in pairs})
        hyp_phones = sorted({h for _, h in pairs})
        self.ref_phones = ref_phones
        self.hyp_phones = hyp_phones

        self.max_count = max((c for _, c in pairs.values()), default=1)

        w = self.PAD_L + len(ref_phones) * self.CELL + self.PAD_R
        h = self.PAD_T + len(hyp_phones) * self.CELL + self.PAD_B
        self.setMinimumSize(max(300, w), max(300, h))

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), self.BG)

        if not self.pairs:
            painter.setPen(self.FG)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No pair data.")
            painter.end()
            return

        n_ref = len(self.ref_phones)
        n_hyp = len(self.hyp_phones)

        # Grid lines
        for xi in range(n_ref + 1):
            x = self.PAD_L + xi * self.CELL
            painter.setPen(self.GRID)
            painter.drawLine(x, self.PAD_T, x, self.PAD_T + n_hyp * self.CELL)

        for yi in range(n_hyp + 1):
            y = self.PAD_T + yi * self.CELL
            painter.setPen(self.GRID)
            painter.drawLine(self.PAD_L, y, self.PAD_L + n_ref * self.CELL, y)

        # Ref phoneme labels (bottom)
        painter.setFont(QFont("monospace", 7, QFont.Weight.Bold))
        for xi, ref in enumerate(self.ref_phones):
            cx = self.PAD_L + (xi + 0.5) * self.CELL
            painter.setPen(self.FG)
            painter.save()
            painter.translate(cx, self.PAD_T + n_hyp * self.CELL + 6)
            painter.rotate(45)
            painter.drawText(0, 0, ref)
            painter.restore()

        # Hyp phoneme labels (left)
        painter.setFont(QFont("monospace", 7, QFont.Weight.Bold))
        for yi, hyp in enumerate(self.hyp_phones):
            cy = self.PAD_T + (yi + 0.5) * self.CELL
            painter.setPen(self.FG)
            painter.drawText(
                QRectF(0, cy - 8, self.PAD_L - 4, 16),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                hyp,
            )

        # Bubbles
        import math
        for (ref, hyp), (mean_iou, count) in self.pairs.items():
            xi = self.ref_phones.index(ref)
            yi = self.hyp_phones.index(hyp)
            cx = self.PAD_L + (xi + 0.5) * self.CELL
            cy = self.PAD_T + (yi + 0.5) * self.CELL
            r = self.MAX_R * math.sqrt(count / self.max_count)
            color = _lerp_color(self.LOW, self.HIGH, mean_iou)
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))

        painter.end()


class PhonemeScatterWindow(QMainWindow):
    def __init__(
        self,
        pairs: dict[tuple[str, str], tuple[float, int]],
        label_a: str = "Set A",
        label_b: str = "Set B",
        theme: tuple[str, str, str] | None = None,
    ):
        super().__init__()
        self.setWindowTitle("Phoneme Pair Overlap Scatter")

        chart = PairScatterWidget(pairs, label_a, label_b, theme=theme)
        self.setStyleSheet(f"background: {chart.BG.name()};")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)

        title = QLabel(f"Phoneme Pair Overlap (IoU): {label_a} (x) vs {label_b} (y)")
        title.setStyleSheet("color: #cdd6f4; font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        layout.addWidget(chart)
        layout.addWidget(_footer_label(
            "Each bubble is a (reference, hypothesis) phoneme pair observed when the two aligners"
            " cover the same time region. Bubble size ∝ count; colour = mean IoU."
            " On-diagonal = label agreement; off-diagonal = substitutions.",
            _GITHUB_OVERLAP,
        ))

        self.setCentralWidget(container)
        self.resize(chart.minimumWidth() + 20, chart.minimumHeight() + 80)


def plot_phoneme_pair_scatter(
    paths_a: list[str],
    paths_b: list[str],
    label_a: str = "Set A",
    label_b: str = "Set B",
    tier_name: str = "phones",
    aggregate_emphasis: bool = False,
    theme: tuple[str, str, str] | None = None,
    save_png: str | None = None,
    exec_: bool = True,
) -> "PhonemeScatterWindow":
    """
    Scatter plot of phoneme pairs.  x = reference phoneme, y = hypothesis phoneme.
    Bubble size = observation count, colour = mean IoU (red → green).
    Files are matched by basename.

    theme:    optional (low_color, high_color, background) hex strings.
    save_png: optional file path (e.g. "pair_scatter.png").  The chart is
              rendered and saved; in Jupyter the image is also displayed inline.
    exec_:    when True (default) show the window and start the Qt event loop
              (standalone / script use).  Set to False when embedding inside a
              larger PyQt6 app — the window is returned without being shown so
              the caller can parent, lay out, or display it as needed.
    """
    pairs = compute_phoneme_pair_overlap(paths_a, paths_b, tier_name, normalize=aggregate_emphasis)

    if save_png is not None and QApplication.instance() is None:
        import os
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    app = QApplication.instance() or QApplication(sys.argv)
    window = PhonemeScatterWindow(pairs, label_a, label_b, theme=theme)

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