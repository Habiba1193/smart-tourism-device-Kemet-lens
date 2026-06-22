from __future__ import annotations

from pathlib import Path
from typing import Callable

from PySide6.QtCore import Property, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .paths import ASSET_DIR
from .theme import BORDER, CREAM, GOLD, GREEN, INK, INK_2, MUTED, PAPYRUS_DARK_TEXT
from .translations import text


def repolish(widget: QWidget) -> None:
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


def role_label(text: str, role: str, wrap: bool = False) -> QLabel:
    label = QLabel(text)
    label.setProperty("role", role)
    label.setWordWrap(wrap)
    label.setTextFormat(Qt.PlainText)
    return label


def make_button(text: str, variant: str, height: int = 64) -> QPushButton:
    button = QPushButton(text)
    button.setCursor(Qt.PointingHandCursor)
    button.setProperty("variant", variant)
    button.setFixedHeight(height)
    return button


class GradientScreen(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setAutoFillBackground(False)
        self.setObjectName("gradientScreen")

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, QColor("#070d18"))
        gradient.setColorAt(0.56, QColor("#10111a"))
        gradient.setColorAt(1.0, QColor("#1b100b"))
        painter.fillRect(rect, gradient)

        self._draw_background_glyphs(painter)

        painter.setPen(QPen(QColor(224, 173, 63, 28), 1))
        painter.drawLine(182, self.height() - 52, 213, self.height() - 52)
        painter.drawLine(217, self.height() - 52, 248, self.height() - 52)
        painter.setBrush(QColor(GOLD))
        painter.setPen(Qt.NoPen)
        painter.save()
        painter.translate(215, self.height() - 52)
        painter.rotate(45)
        painter.drawRect(-3, -3, 6, 6)
        painter.restore()

        super().paintEvent(event)

    def _draw_background_glyphs(self, painter: QPainter) -> None:
        h = self.height()
        glyphs = [
            (364, 82, 1.0, -7, self._draw_bg_ankh),
            (68, 190, 1.25, 10, self._draw_bg_eye),
            (326, max(500, h - 215), 1.45, -8, self._draw_bg_scarab),
            (55, max(450, h - 280), 1.2, 8, self._draw_bg_lotus),
            (362, 455, 1.25, -16, self._draw_bg_feather),
            (76, max(555, h - 82), 1.12, 6, self._draw_bg_djed),
        ]
        for x, y, scale, rotation, drawer in glyphs:
            painter.save()
            painter.translate(x, y)
            painter.rotate(rotation)
            painter.scale(scale, scale)
            painter.setPen(QPen(QColor(224, 173, 63, 18), 1.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.setBrush(Qt.NoBrush)
            drawer(painter)
            painter.restore()

    @staticmethod
    def _draw_bg_ankh(painter: QPainter) -> None:
        painter.drawEllipse(QRectF(-8, -26, 16, 18))
        painter.drawLine(0, -8, 0, 32)
        painter.drawLine(-18, 4, 18, 4)
        painter.drawLine(-10, 32, 10, 32)

    @staticmethod
    def _draw_bg_eye(painter: QPainter) -> None:
        eye = QPainterPath()
        eye.moveTo(-34, 0)
        eye.cubicTo(-17, -18, 17, -18, 34, 0)
        eye.cubicTo(17, 16, -17, 16, -34, 0)
        painter.drawPath(eye)
        painter.drawEllipse(QRectF(-7, -7, 14, 14))
        painter.drawLine(22, 9, 34, 18)
        painter.drawLine(-2, 17, -10, 27)

    @staticmethod
    def _draw_bg_scarab(painter: QPainter) -> None:
        body = QPainterPath()
        body.moveTo(0, -30)
        body.cubicTo(22, -26, 28, -2, 19, 22)
        body.cubicTo(10, 34, -10, 34, -19, 22)
        body.cubicTo(-28, -2, -22, -26, 0, -30)
        painter.drawPath(body)
        painter.drawLine(0, -26, 0, 30)
        painter.drawArc(QRectF(-19, -17, 38, 24), 205 * 16, 130 * 16)
        painter.drawLine(-19, -1, -36, -11)
        painter.drawLine(19, -1, 36, -11)
        painter.drawLine(-17, 15, -34, 25)
        painter.drawLine(17, 15, 34, 25)

    @staticmethod
    def _draw_bg_lotus(painter: QPainter) -> None:
        center = QPainterPath()
        center.moveTo(0, -34)
        center.cubicTo(13, -16, 11, 10, 0, 24)
        center.cubicTo(-11, 10, -13, -16, 0, -34)
        painter.drawPath(center)

        left = QPainterPath()
        left.moveTo(-4, -15)
        left.cubicTo(-29, -18, -36, 8, -8, 24)
        left.cubicTo(-15, 7, -12, -6, -4, -15)
        painter.drawPath(left)

        right = QPainterPath()
        right.moveTo(4, -15)
        right.cubicTo(29, -18, 36, 8, 8, 24)
        right.cubicTo(15, 7, 12, -6, 4, -15)
        painter.drawPath(right)

        painter.drawLine(-24, 27, 24, 27)
        painter.drawLine(-12, 34, 12, 34)
        painter.drawLine(0, 24, 0, 39)

    @staticmethod
    def _draw_bg_feather(painter: QPainter) -> None:
        painter.drawLine(-6, -36, 9, 36)
        for y, length in [(-26, 24), (-16, 28), (-6, 30), (5, 27), (16, 22)]:
            painter.drawLine(-4, y, -length, y + 12)
            painter.drawLine(-2, y + 1, length - 6, y + 10)
        painter.drawLine(9, 36, 20, 42)

    @staticmethod
    def _draw_bg_djed(painter: QPainter) -> None:
        painter.drawLine(-10, -28, -10, 30)
        painter.drawLine(10, -28, 10, 30)
        for y, width in [(-31, 32), (-20, 42), (-9, 38), (2, 34)]:
            painter.drawLine(-width / 2, y, width / 2, y)
            painter.drawLine(-width / 2 + 4, y + 6, width / 2 - 4, y + 6)
        painter.drawLine(-17, 31, 17, 31)
        painter.drawLine(-22, 39, 22, 39)


class RoundedImage(QWidget):
    def __init__(
        self,
        filename: str | None,
        radius: int = 14,
        placeholder: str = "Artifact Image",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.filename = filename
        self.radius = radius
        self.placeholder = placeholder
        self.badge_text = ""
        self._pixmap = self._load_pixmap(filename)
        self.setMinimumHeight(120)

    def set_image(self, filename: str | None) -> None:
        self.filename = filename
        self._pixmap = self._load_pixmap(filename)
        self.update()

    def set_badge_text(self, text: str) -> None:
        self.badge_text = text
        self.update()

    def _load_pixmap(self, filename: str | None) -> QPixmap:
        if not filename:
            return QPixmap()
        path = ASSET_DIR / filename
        if path.exists():
            return QPixmap(str(path))
        if Path(filename).exists():
            return QPixmap(str(filename))
        return QPixmap()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(rect, self.radius, self.radius)
        painter.setClipPath(path)

        if not self._pixmap.isNull():
            target = self.size()
            scaled = self._pixmap.scaled(
                target.width(),
                target.height(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation,
            )
            source = QRectF(
                (scaled.width() - target.width()) / 2,
                (scaled.height() - target.height()) / 2,
                target.width(),
                target.height(),
            )
            painter.drawPixmap(QRectF(0, 0, target.width(), target.height()), scaled, source)
        else:
            painter.fillRect(rect, QColor("#151821"))
            painter.setPen(QColor(MUTED))
            painter.setFont(QFont("Segoe UI", 11, QFont.Bold))
            painter.drawText(rect, Qt.AlignCenter, self.placeholder)

        painter.setClipping(False)
        if self.badge_text:
            badge_height = 28
            painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
            badge_width = min(
                max(88, painter.fontMetrics().horizontalAdvance(self.badge_text) + 24),
                max(88, int(rect.width()) - 24),
            )
            badge = QRectF(rect.right() - badge_width - 12, rect.top() + 12, badge_width, badge_height)
            painter.setPen(Qt.NoPen)
            badge_path = QPainterPath()
            badge_path.addRoundedRect(badge, 14, 14)
            painter.fillPath(badge_path, QColor(GOLD))
            painter.setPen(QColor("#16100a"))
            painter.drawText(badge, Qt.AlignCenter, self.badge_text)
        painter.setPen(QPen(QColor(255, 233, 173, 40), 1))
        painter.drawRoundedRect(rect, self.radius, self.radius)


class CircularImage(QWidget):
    def __init__(self, filename: str, diameter: int = 166) -> None:
        super().__init__()
        self.setFixedSize(diameter + 34, diameter + 34)
        self.diameter = diameter
        self.pixmap = QPixmap(str(ASSET_DIR / filename))

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        cx = self.width() / 2
        cy = self.height() / 2

        for offset, alpha in [(16, 18), (9, 28), (0, 42)]:
            painter.setPen(QPen(QColor(224, 173, 63, alpha), 1))
            painter.drawEllipse(QRectF(cx - self.diameter / 2 - offset, cy - self.diameter / 2 - offset,
                                       self.diameter + offset * 2, self.diameter + offset * 2))

        rect = QRectF(cx - self.diameter / 2, cy - self.diameter / 2, self.diameter, self.diameter)
        path = QPainterPath()
        path.addEllipse(rect)
        painter.setClipPath(path)
        if not self.pixmap.isNull():
            scaled = self.pixmap.scaled(rect.size().toSize(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            painter.drawPixmap(rect.topLeft(), scaled)
            painter.fillRect(rect, QColor(4, 8, 16, 112))
        else:
            painter.fillPath(path, QColor("#141720"))
        painter.setClipping(False)

        painter.setBrush(QColor(224, 173, 63, 38))
        painter.setPen(QPen(QColor(224, 173, 63, 75), 1))
        painter.drawEllipse(QRectF(cx - 31, cy - 31, 62, 62))
        painter.setPen(QPen(QColor(GOLD), 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        scale = 0.46
        eye = QPainterPath()
        eye.moveTo(cx - 43 * scale, cy)
        eye.cubicTo(cx - 23 * scale, cy - 28 * scale, cx + 23 * scale, cy - 28 * scale, cx + 43 * scale, cy)
        eye.cubicTo(cx + 22 * scale, cy + 25 * scale, cx - 23 * scale, cy + 25 * scale, cx - 43 * scale, cy)
        painter.drawPath(eye)

        painter.setBrush(QColor(224, 173, 63, 80))
        painter.setPen(QPen(QColor(GOLD), 1.6))
        iris_radius = 15 * scale
        painter.drawEllipse(QRectF(cx - iris_radius, cy - iris_radius, iris_radius * 2, iris_radius * 2))
        painter.setBrush(QColor(GOLD))
        pupil_radius = 5 * scale
        painter.drawEllipse(QRectF(cx - pupil_radius, cy - pupil_radius, pupil_radius * 2, pupil_radius * 2))

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(GOLD), 1.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(cx + 29 * scale, cy + 5 * scale, cx + 50 * scale, cy + 19 * scale)
        painter.drawLine(cx - 34 * scale, cy + 18 * scale, cx - 8 * scale, cy + 18 * scale)
        painter.drawLine(cx - 8 * scale, cy + 18 * scale, cx - 18 * scale, cy + 32 * scale)


class LogoMark(QWidget):
    def __init__(self, size: int = 108) -> None:
        super().__init__()
        self.setFixedSize(size, size)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        cx = self.width() / 2
        cy = self.height() / 2
        for radius, alpha, width in [(50, 35, 1), (37, 72, 2), (25, 100, 2), (12, 145, 2)]:
            painter.setPen(QPen(QColor(224, 173, 63, alpha), width))
            painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))
        painter.setBrush(QColor(GOLD))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(cx - 4, cy - 4, 8, 8))
        painter.setPen(QPen(QColor(GOLD), 2))
        painter.drawEllipse(QRectF(cx - 8, cy - 8, 16, 16))


class GlyphSpinner(QWidget):
    def __init__(self, size: int = 150) -> None:
        super().__init__()
        self.setFixedSize(size, size)
        self._angle = 0
        self._pulse = 0
        self._frame = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(32)

    def _tick(self) -> None:
        self._angle = (self._angle + 1.4) % 360
        self._pulse = (self._pulse + 1) % 80
        self._frame = (self._frame + 1) % 240
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        cx = self.width() / 2
        cy = self.height() / 2
        self._draw_fading_glyphs(painter)
        self._draw_scan_pulses(painter, cx, cy)
        self._draw_rotating_ring(painter, cx, cy)

        pulse = abs(40 - self._pulse) / 40
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(224, 173, 63, 28 + int(pulse * 34)))
        painter.drawEllipse(QRectF(cx - 26, cy - 26, 52, 52))

        eye = QPainterPath()
        eye.moveTo(cx - 34, cy)
        eye.cubicTo(cx - 20, cy - 17, cx + 20, cy - 17, cx + 34, cy)
        eye.cubicTo(cx + 20, cy + 16, cx - 20, cy + 16, cx - 34, cy)
        painter.setPen(QPen(QColor(255, 233, 173, 150), 1.4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(QColor(9, 10, 14, 120))
        painter.drawPath(eye)

        painter.setPen(QPen(QColor(GOLD), 1.2))
        painter.setBrush(QColor(224, 173, 63, 70 + int(pulse * 60)))
        painter.drawEllipse(QRectF(cx - 8, cy - 8, 16, 16))
        painter.setBrush(QColor(255, 233, 173, 180))
        painter.drawEllipse(QRectF(cx - 2.5, cy - 2.5, 5, 5))

        painter.setPen(QPen(QColor(224, 173, 63, 120), 1.1, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(cx - 16, cy + 24, cx + 18, cy + 24)
        painter.drawArc(QRectF(cx - 16, cy + 17, 32, 15), 180 * 16, 180 * 16)

    def _draw_rotating_ring(self, painter: QPainter, cx: float, cy: float) -> None:
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self._angle)
        painter.setPen(QPen(QColor(224, 173, 63, 95), 2.1, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(QRectF(-67, -67, 134, 134), 22 * 16, 104 * 16)
        painter.drawArc(QRectF(-67, -67, 134, 134), 205 * 16, 82 * 16)
        painter.setPen(QPen(QColor(255, 233, 173, 70), 1.1, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(QRectF(-55, -55, 110, 110), 320 * 16, 58 * 16)
        painter.restore()

    def _draw_scan_pulses(self, painter: QPainter, cx: float, cy: float) -> None:
        for offset in (0, 27, 54):
            life = (self._pulse + offset) % 80
            radius = 24 + life * 0.78
            alpha = max(0, 78 - life)
            painter.setPen(QPen(QColor(224, 173, 63, alpha), 1.2))
            painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))

    def _draw_fading_glyphs(self, painter: QPainter) -> None:
        marks = [
            (22, 35, 0, "ankh"),
            (118, 36, 48, "reed"),
            (20, 104, 96, "wave"),
            (130, 98, 144, "eye"),
        ]
        for x, y, phase, kind in marks:
            fade = abs(((self._frame + phase) % 160) - 80) / 80
            alpha = int(16 + (1 - fade) * 52)
            painter.setPen(QPen(QColor(224, 173, 63, alpha), 1.05))
            if kind == "ankh":
                painter.drawEllipse(QRectF(x - 4, y - 8, 8, 9))
                painter.drawLine(x, y + 1, x, y + 15)
                painter.drawLine(x - 7, y + 6, x + 7, y + 6)
            elif kind == "reed":
                painter.drawLine(x, y - 10, x, y + 13)
                painter.drawLine(x, y - 10, x + 7, y - 4)
                painter.drawLine(x + 4, y + 2, x + 10, y + 7)
            elif kind == "wave":
                painter.drawArc(QRectF(x - 9, y - 4, 10, 8), 0, 180 * 16)
                painter.drawArc(QRectF(x, y - 4, 10, 8), 180 * 16, 180 * 16)
                painter.drawArc(QRectF(x + 9, y - 4, 10, 8), 0, 180 * 16)
            else:
                eye = QPainterPath()
                eye.moveTo(x - 12, y)
                eye.cubicTo(x - 5, y - 8, x + 5, y - 8, x + 12, y)
                eye.cubicTo(x + 5, y + 7, x - 5, y + 7, x - 12, y)
                painter.drawPath(eye)
                painter.drawEllipse(QRectF(x - 3, y - 3, 6, 6))


class ScannerPreview(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setFixedHeight(430)
        self.status_text = text("en", "scanner_status")
        self.placeholder_text = text("en", "place_artifact_here")
        self.object_detected = False
        self.frame_pixmap = QPixmap()
        self._line = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(45)

    def _tick(self) -> None:
        self._line = (self._line + 3) % max(1, self.height())
        self.update()

    def set_status_text(self, value: str) -> None:
        self.status_text = value
        self.update()

    def set_placeholder_text(self, value: str) -> None:
        self.placeholder_text = value
        self.update()

    def set_object_detected(self, detected: bool) -> None:
        self.object_detected = detected
        self.update()

    def set_frame(self, image: QImage) -> None:
        self.frame_pixmap = QPixmap.fromImage(image)
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(rect, 16, 16)
        painter.setClipPath(path)

        camera_gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        camera_gradient.setColorAt(0.0, QColor("#111722"))
        camera_gradient.setColorAt(0.48, QColor("#070b12"))
        camera_gradient.setColorAt(1.0, QColor("#020407"))
        painter.fillRect(rect, camera_gradient)

        if self.frame_pixmap.isNull():
            painter.setPen(QPen(QColor(224, 173, 63, 16), 1))
            for x in (46, 84, 152, 218, 284, 350):
                painter.drawLine(x, 22, x - 32, self.height() - 28)
            painter.setPen(QPen(QColor(255, 233, 173, 10), 1))
            for y in (62, 118, 174, 230):
                painter.drawLine(22, y, self.width() - 22, y + 8)
        else:
            scaled = self.frame_pixmap.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            x = int((self.width() - scaled.width()) / 2)
            y = int((self.height() - scaled.height()) / 2)
            painter.drawPixmap(x, y, scaled)
            painter.fillRect(rect, QColor(2, 5, 10, 72))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(2, 3, 5, 92))
        painter.drawEllipse(QRectF(-60, -48, self.width() + 120, 132))
        painter.drawEllipse(QRectF(-95, self.height() - 118, self.width() + 190, 170))

        if self.frame_pixmap.isNull():
            painter.setFont(QFont("Segoe UI", 18, QFont.Bold))
            painter.setPen(QColor(255, 233, 173, 125))
            painter.drawText(QRectF(18, 90, self.width() - 36, 28), Qt.AlignCenter, self.placeholder_text)
        painter.setClipping(False)

        painter.setPen(QPen(QColor(GOLD), 2))
        corner = 34
        pad = 17
        points = [
            ((pad, pad + corner), (pad, pad), (pad + corner, pad)),
            ((self.width() - pad - corner, pad), (self.width() - pad, pad), (self.width() - pad, pad + corner)),
            ((pad, self.height() - pad - corner), (pad, self.height() - pad), (pad + corner, self.height() - pad)),
            ((self.width() - pad - corner, self.height() - pad), (self.width() - pad, self.height() - pad), (self.width() - pad, self.height() - pad - corner)),
        ]
        for a, b, c in points:
            painter.drawLine(*a, *b)
            painter.drawLine(*b, *c)

        cx = self.width() / 2
        cy = self.height() / 2
        self._draw_ai_lens_symbol(painter, cx, cy)

        y = self._line
        scan = QLinearGradient(18, y, self.width() - 18, y)
        scan.setColorAt(0.0, QColor(224, 173, 63, 0))
        scan.setColorAt(0.5, QColor(224, 173, 63, 118))
        scan.setColorAt(1.0, QColor(224, 173, 63, 0))
        painter.fillRect(QRectF(18, y, self.width() - 36, 2), scan)
        if self.object_detected:
            painter.setBrush(QColor(5, 8, 11, 232))
            painter.setPen(QPen(QColor("#20251d"), 1))
            badge = QRectF(66, self.height() - 48, self.width() - 132, 28)
            painter.drawRoundedRect(badge, 14, 14)
            painter.setBrush(QColor(GREEN))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QRectF(badge.left() + 14, badge.center().y() - 4, 8, 8))
            painter.setPen(QColor(CREAM))
            painter.setFont(QFont("Segoe UI", 13, QFont.Bold))
            painter.drawText(badge.adjusted(29, 0, -8, 0), Qt.AlignVCenter, self.status_text)

    def _draw_ai_lens_symbol(self, painter: QPainter, cx: float, cy: float) -> None:
        painter.save()
        painter.translate(cx, cy)
        painter.setBrush(Qt.NoBrush)

        painter.setPen(QPen(QColor(224, 173, 63, 86), 1.15, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        lens = QPainterPath()
        lens.moveTo(0, -24)
        lens.lineTo(24, 0)
        lens.lineTo(0, 24)
        lens.lineTo(-24, 0)
        lens.closeSubpath()
        painter.drawPath(lens)

        painter.setPen(QPen(QColor(255, 233, 173, 112), 1.05, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(QRectF(-13, -13, 26, 26), 30 * 16, 115 * 16)
        painter.drawArc(QRectF(-13, -13, 26, 26), 210 * 16, 115 * 16)

        painter.setPen(QPen(QColor(GOLD), 1.3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        for sx, sy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            painter.drawLine(sx * 34, sy * 24, sx * 24, sy * 24)
            painter.drawLine(sx * 24, sy * 34, sx * 24, sy * 24)

        painter.setBrush(QColor(224, 173, 63, 84))
        painter.setPen(QPen(QColor(255, 233, 173, 150), 1))
        painter.drawEllipse(QRectF(-5, -5, 10, 10))
        painter.setPen(QPen(QColor(255, 233, 173, 135), 1.1))
        painter.drawLine(-2, -13, 2, -13)
        painter.drawLine(0, -15, 0, -11)
        painter.restore()

class ClickableFrame(QFrame):
    clicked = Signal()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class IconGlyph(QWidget):
    def __init__(self, kind: str, size: int = 18, use_bakkar_image: bool = False) -> None:
        super().__init__()
        self.kind = kind
        self.setFixedSize(size, size)
        self.use_bakkar_image = use_bakkar_image
        bakkar_path = ASSET_DIR / "bakkar_icon.png"
        if not bakkar_path.exists():
            bakkar_path = ASSET_DIR / "bakkar_icon.jpeg"
        self.pixmap = QPixmap(str(bakkar_path)) if kind == "bakkar" and use_bakkar_image else QPixmap()
        if not self.pixmap.isNull():
            self.pixmap = self._gold_only_pixmap(self.pixmap)
        self.source_rect = self._gold_bounds(self.pixmap) if not self.pixmap.isNull() else QRectF()

    @staticmethod
    def _is_gold_pixel(color: QColor) -> bool:
        red = color.red()
        green = color.green()
        blue = color.blue()
        return red > 120 and green > 95 and blue < 215 and red - blue > 24 and green - blue > 8

    @classmethod
    def _gold_only_pixmap(cls, pixmap: QPixmap) -> QPixmap:
        image = pixmap.toImage()
        for y in range(image.height()):
            for x in range(image.width()):
                color = QColor(image.pixel(x, y))
                if cls._is_gold_pixel(color):
                    color.setAlpha(255)
                else:
                    color.setAlpha(0)
                image.setPixelColor(x, y, color)
        return QPixmap.fromImage(image)

    @classmethod
    def _gold_bounds(cls, pixmap: QPixmap) -> QRectF:
        image = pixmap.toImage()
        min_x = image.width()
        min_y = image.height()
        max_x = 0
        max_y = 0
        found = False
        step = max(1, min(image.width(), image.height()) // 260)
        for y in range(0, image.height(), step):
            for x in range(0, image.width(), step):
                color = QColor(image.pixel(x, y))
                if color.alpha() > 0 and cls._is_gold_pixel(color):
                    found = True
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
        if not found:
            return QRectF(0, 0, pixmap.width(), pixmap.height())

        pad = 28
        left = max(0, min_x - pad)
        top = max(0, min_y - pad)
        right = min(image.width(), max_x + pad)
        bottom = min(image.height(), max_y + pad)
        return QRectF(left, top, right - left, bottom - top)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.kind == "bakkar" and self.use_bakkar_image and not self.pixmap.isNull():
            source = self.source_rect if not self.source_rect.isNull() else QRectF(0, 0, self.pixmap.width(), self.pixmap.height())
            target = QRectF(self.rect()).adjusted(-1, -1, 1, 1)
            for dx, dy in ((0, 0), (0.45, 0), (0, 0.45), (-0.35, 0)):
                painter.drawPixmap(target.translated(dx, dy), self.pixmap, source)
            return
        if self.width() != 18 or self.height() != 18:
            painter.scale(self.width() / 18, self.height() / 18)
        painter.setPen(QPen(QColor(MUTED), 1.15))
        painter.setBrush(Qt.NoBrush)
        w = 18
        h = 18
        if self.kind == "discover":
            eye = QPainterPath()
            eye.moveTo(3, h / 2)
            eye.cubicTo(7, 3, w - 7, 3, w - 3, h / 2)
            eye.cubicTo(w - 7, h - 3, 7, h - 3, 3, h / 2)
            painter.drawPath(eye)
            painter.drawEllipse(QRectF(w / 2 - 4, h / 2 - 4, 8, 8))
            painter.setBrush(QColor(MUTED))
            painter.drawEllipse(QRectF(w / 2 - 1.8, h / 2 - 1.8, 3.6, 3.6))
            painter.setBrush(Qt.NoBrush)
            painter.drawLine(1, 1, 6, 1)
            painter.drawLine(1, 1, 1, 6)
            painter.drawLine(w - 1, h - 1, w - 6, h - 1)
            painter.drawLine(w - 1, h - 1, w - 1, h - 6)
        elif self.kind == "home":
            painter.drawLine(3, h - 4, w - 3, h - 4)
            painter.drawLine(5, h - 4, 5, h - 10)
            painter.drawLine(w - 5, h - 4, w - 5, h - 10)
            painter.drawLine(8, h - 4, 8, h - 12)
            painter.drawLine(w - 8, h - 4, w - 8, h - 12)
            painter.drawLine(w / 2, h - 4, w / 2, h - 12)
            painter.drawLine(3, h - 12, w - 3, h - 12)
            path = QPainterPath()
            path.moveTo(w / 2, 2)
            path.lineTo(3, h - 12)
            path.lineTo(w - 3, h - 12)
            path.closeSubpath()
            painter.drawPath(path)
        elif self.kind == "language":
            painter.drawEllipse(QRectF(3, 3, w - 6, h - 6))
            painter.drawLine(4, h / 2, w - 4, h / 2)
            painter.drawLine(w / 2, 3, w / 2, h - 3)
            painter.drawArc(QRectF(6, 3, w - 12, h - 6), 90 * 16, 180 * 16)
            painter.drawArc(QRectF(6, 3, w - 12, h - 6), -90 * 16, 180 * 16)
        elif self.kind == "recent":
            painter.drawEllipse(QRectF(3, 3, w - 6, h - 6))
            painter.drawArc(QRectF(1, 1, w - 2, h - 2), 130 * 16, 235 * 16)
            painter.drawLine(3, 5, 3, 10)
            painter.drawLine(3, 5, 8, 5)
            painter.drawLine(w / 2, h / 2, w / 2, 6)
            painter.drawLine(w / 2, h / 2, w - 5, h / 2 + 2)
        elif self.kind == "bakkar":
            bubble = QPainterPath()
            bubble.addRoundedRect(QRectF(3, 4, w - 6, h - 8), 5, 5)
            painter.drawPath(bubble)
            painter.drawLine(8, h - 5, 6, h - 1)
            painter.drawLine(8, h - 5, 12, h - 5)
            painter.drawEllipse(QRectF(w / 2 - 4, h / 2 - 4, 8, 8))
            painter.drawArc(QRectF(w / 2 - 7, h / 2 - 7, 14, 14), 30 * 16, 120 * 16)
            painter.drawArc(QRectF(w / 2 - 7, h / 2 - 7, 14, 14), 210 * 16, 120 * 16)


class BottomNav(QFrame):
    def __init__(
        self,
        on_discover: Callable[[], None],
        on_home: Callable[[], None],
        on_ask: Callable[[], None],
        on_language: Callable[[], None],
        on_recent: Callable[[], None],
        language: str = "en",
        use_bakkar_image: bool = False,
    ) -> None:
        super().__init__()

        self.setProperty("card", "nav")
        self.setFixedHeight(118)

        self.text_labels: list[tuple[QLabel, str]] = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(26, 12, 26, 12)
        layout.setSpacing(10)

        nav_items = [
            ("discover", "discover", on_discover),
            ("home", "home", on_home),
            ("bakkar", "ask_bakkar", on_ask),
            ("language", "change_language", on_language),
            ("recent", "recently_scanned", on_recent),
        ]

        for icon, label, callback in nav_items:
            item = ClickableFrame()
            item.setCursor(Qt.PointingHandCursor)
            item.clicked.connect(callback)
            item.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            item_layout = QVBoxLayout(item)
            item_layout.setContentsMargins(4, 2, 4, 2)
            item_layout.setSpacing(4)

            if icon == "bakkar" and use_bakkar_image:
                icon_size = 62
            else:
                icon_size = 44

            icon_label = IconGlyph(icon, icon_size, use_bakkar_image)

            text_label = QLabel(text(language, label))
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setWordWrap(True)
            text_label.setMinimumHeight(38)
            text_label.setStyleSheet(
                f"color: {MUTED}; "
                "font-size: 13px; "
                "font-weight: 700; "
                "line-height: 115%;"
            )

            self.text_labels.append((text_label, label))

            item_layout.addWidget(icon_label, 0, Qt.AlignCenter)
            item_layout.addWidget(text_label, 0, Qt.AlignCenter)

            layout.addWidget(item, 1)

    def set_language(self, language: str) -> None:
        for label, key in self.text_labels:
            label.setText(text(language, key))


def transparent_scroll(widget: QWidget, vertical: bool = True) -> QScrollArea:
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setAttribute(Qt.WA_TranslucentBackground)
    scroll.viewport().setAttribute(Qt.WA_TranslucentBackground)
    scroll.viewport().setAutoFillBackground(False)
    widget.setAttribute(Qt.WA_TranslucentBackground)
    widget.setAutoFillBackground(False)
    scroll.setStyleSheet(
        "QScrollArea { background: transparent; border: none; } "
        "QScrollArea > QWidget > QWidget { background: transparent; }"
    )
    scroll.setWidget(widget)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff if vertical else Qt.ScrollBarAsNeeded)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded if vertical else Qt.ScrollBarAlwaysOff)
    scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    return scroll


def content_shell(
    margins: tuple[int, int, int, int] = (44, 54, 44, 34),
    spacing: int = 22,
) -> QVBoxLayout:
    layout = QVBoxLayout()
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    return layout


def spacer(height: int) -> QWidget:
    widget = QWidget()
    widget.setFixedHeight(height)
    return widget


def add_shadow(widget: QWidget, blur: int = 24, alpha: int = 70) -> None:
    from PySide6.QtWidgets import QGraphicsDropShadowEffect

    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, 8)
    shadow.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(shadow)
