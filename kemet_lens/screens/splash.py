from PySide6.QtCore import Property, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsOpacityEffect, QVBoxLayout, QWidget

from ..theme import TITLE_FONT_STACK
from ..translations import text
from ..widgets import GradientScreen, role_label, spacer


class SplashEyeLogo(QWidget):
    def __init__(self) -> None:
        super().__init__()

        # Larger logo for the new fullscreen Raspberry Pi display.
        self.setFixedSize(210, 210)

        self._glow = 0.0

    def get_glow(self) -> float:
        return self._glow

    def set_glow(self, value: float) -> None:
        self._glow = value
        self.update()

    glow = Property(float, get_glow, set_glow)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        cx = self.width() / 2
        cy = self.height() / 2

        scale_x = self.width() / 132
        scale_y = self.height() / 132

        painter.save()
        painter.scale(scale_x, scale_y)

        base_cx = 66
        base_cy = 66
        gold = QColor("#e0ad3f")

        glow_alpha = 30 + int(self._glow * 60)

        painter.setBrush(QColor(224, 173, 63, glow_alpha))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(base_cx - 58, base_cy - 58, 116, 116))

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(224, 173, 63, 60), 1.7))
        painter.drawEllipse(QRectF(base_cx - 52, base_cy - 52, 104, 104))
        painter.drawEllipse(QRectF(base_cx - 39, base_cy - 39, 78, 78))

        painter.setPen(QPen(gold, 2.7))
        eye = QPainterPath()
        eye.moveTo(23, base_cy)
        eye.cubicTo(43, base_cy - 28, 89, base_cy - 28, 109, base_cy)
        eye.cubicTo(88, base_cy + 25, 43, base_cy + 25, 23, base_cy)
        painter.drawPath(eye)

        painter.setBrush(QColor(224, 173, 63, 52 + int(self._glow * 70)))
        painter.setPen(QPen(gold, 2.2))
        painter.drawEllipse(QRectF(base_cx - 15, base_cy - 15, 30, 30))

        painter.setBrush(gold)
        painter.drawEllipse(QRectF(base_cx - 5, base_cy - 5, 10, 10))

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(gold, 2.2))
        painter.drawLine(base_cx + 29, base_cy + 5, base_cx + 50, base_cy + 19)
        painter.drawLine(base_cx - 34, base_cy + 18, base_cx - 8, base_cy + 18)
        painter.drawLine(base_cx - 8, base_cy + 18, base_cx - 18, base_cy + 32)

        painter.restore()


class SplashScreen(GradientScreen):
    def __init__(self, app) -> None:
        super().__init__()

        self.app = app

        layout = QVBoxLayout(self)
        layout.setContentsMargins(52, 0, 52, 82)
        layout.setSpacing(18)

        layout.addStretch(1)

        self.logo = SplashEyeLogo()
        layout.addWidget(self.logo, 0, Qt.AlignHCenter)

        layout.addWidget(spacer(24))

        self.title = role_label("", "title")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet(
            f"font-family: {TITLE_FONT_STACK}; "
            "font-size: 54px; "
            "font-weight: 900; "
            "color: #ffe9ad;"
        )
        layout.addWidget(self.title)

        self.subtitle = role_label("", "brand")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setStyleSheet(
            "color: #b88925; "
            "font-size: 17px; "
            "font-weight: 800; "
            "letter-spacing: 7px;"
        )
        layout.addWidget(self.subtitle)

        layout.addStretch(1)

        self._setup_animation()
        self.refresh()

    def refresh(self) -> None:
        self.title.setText(text(self.app.language, "brand").upper())
        self.subtitle.setText(text(self.app.language, "splash_tagline"))

    def _setup_animation(self) -> None:
        from PySide6.QtCore import QEasingCurve, QPropertyAnimation

        self.logo_effect = QGraphicsOpacityEffect(self.logo)
        self.title_effect = QGraphicsOpacityEffect(self.title)
        self.subtitle_effect = QGraphicsOpacityEffect(self.subtitle)

        self.logo.setGraphicsEffect(self.logo_effect)
        self.title.setGraphicsEffect(self.title_effect)
        self.subtitle.setGraphicsEffect(self.subtitle_effect)

        for effect in (self.logo_effect, self.title_effect, self.subtitle_effect):
            effect.setOpacity(0.0)

        def fade(effect, duration: int) -> QPropertyAnimation:
            animation = QPropertyAnimation(effect, b"opacity", self)
            animation.setDuration(duration)
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            return animation

        self.logo_fade = fade(self.logo_effect, 760)
        self.title_fade = fade(self.title_effect, 900)
        self.subtitle_fade = fade(self.subtitle_effect, 850)

        self.glow_pulse = QPropertyAnimation(self.logo, b"glow", self)
        self.glow_pulse.setDuration(1300)
        self.glow_pulse.setStartValue(0.15)
        self.glow_pulse.setKeyValueAt(0.55, 1.0)
        self.glow_pulse.setEndValue(0.35)
        self.glow_pulse.setLoopCount(2)
        self.glow_pulse.setEasingCurve(QEasingCurve.InOutSine)

        QTimer.singleShot(150, self.logo_fade.start)
        QTimer.singleShot(260, self.glow_pulse.start)
        QTimer.singleShot(720, self.title_fade.start)
        QTimer.singleShot(1450, self.subtitle_fade.start)
