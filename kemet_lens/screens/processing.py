from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout

from ..theme import TITLE_FONT_STACK
from ..translations import text
from ..widgets import GlyphSpinner, GradientScreen, role_label


class ProcessingScreen(GradientScreen):
    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 40)
        layout.setSpacing(8)
        layout.addStretch(1)

        self.title = role_label("", "title")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet(f"font-family: {TITLE_FONT_STACK}; font-size: 20px; font-weight: 700; color: #ffe9ad;")
        layout.addWidget(self.title)

        spinner_row = QHBoxLayout()
        spinner_row.addStretch(1)
        spinner_row.addWidget(GlyphSpinner(158))
        spinner_row.addStretch(1)
        layout.addLayout(spinner_row)

        self.step = role_label("", "brand")
        self.step.setAlignment(Qt.AlignCenter)
        self.step.setStyleSheet(f"color: #e0ad3f; font-family: {TITLE_FONT_STACK}; font-size: 13px; letter-spacing: 1px;")
        layout.addWidget(self.step)

        self.subtitle = role_label("", "subtitle")
        self.subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.subtitle)

        dots = role_label("●  ●  ●", "section")
        self.dots = dots
        self.dots.setAlignment(Qt.AlignCenter)
        self.dots.setStyleSheet('color: #e0ad3f; font-size: 18px;')
        layout.addWidget(self.dots)
        layout.addStretch(1)
        self.dot_index = 0
        self.dot_timer = QTimer(self)
        self.dot_timer.timeout.connect(self._animate_dots)
        self.dot_timer.start(360)
        self.refresh()

    def start(self) -> None:
        QTimer.singleShot(2300, self.app.finish_processing)

    def refresh(self) -> None:
        language = self.app.language
        self.title.setText(text(language, "processing_title"))
        self.step.setText(text(language, "processing_step"))
        self.subtitle.setText(text(language, "processing_subtitle"))

    def _animate_dots(self) -> None:
        states = ["●  ·  ·", "●  ●  ·", "●  ●  ●", "·  ●  ●"]
        self.dots.setText(states[self.dot_index % len(states)])
        self.dot_index += 1
