from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from ..theme import GOLD, TITLE_FONT_STACK
from ..translations import text
from ..widgets import GradientScreen, add_shadow, content_shell, make_button, role_label


class UnknownScreen(GradientScreen):
    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        layout = content_shell((30, 178, 30, 28), 14)
        self.setLayout(layout)
        layout.addStretch(1)

        icon = QLabel("?")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(98, 98)
        icon.setStyleSheet(
            f"color: {GOLD}; font-size: 46px; font-family: {TITLE_FONT_STACK}; "
            "background: rgba(224,173,63,22); border: 2px solid rgba(224,173,63,85); "
            "border-radius: 49px;"
        )
        layout.addWidget(icon, 0, Qt.AlignCenter)

        self.title = role_label("", "title")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet(f"font-family: {TITLE_FONT_STACK}; font-size: 21px; font-weight: 700; color: #ffe9ad;")
        layout.addWidget(self.title)

        self.subtitle = role_label("", "subtitle")
        self.subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.subtitle)

        tip = QFrame()
        tip.setProperty("card", "dark")
        tip_layout = QVBoxLayout(tip)
        tip_layout.setContentsMargins(20, 16, 20, 16)
        tip_layout.setSpacing(8)
        self.tip_label = QLabel("")
        self.tip_label.setStyleSheet(f"color: {GOLD}; font-size: 13px; font-weight: 800;")
        self.tip_body = QLabel("")
        self.tip_body.setAlignment(Qt.AlignCenter)
        self.tip_body.setStyleSheet("color: #e6deca; font-size: 12px; font-weight: 650;")
        tip_layout.addWidget(self.tip_label)
        tip_layout.addWidget(self.tip_body)
        layout.addSpacing(16)
        layout.addWidget(tip)

        self.retry = make_button("", "primary", 52)
        self.retry.clicked.connect(lambda: self.app.show_screen("scanner"))
        add_shadow(self.retry)
        layout.addWidget(self.retry)

        self.home = make_button("", "secondary", 48)
        self.home.clicked.connect(lambda: self.app.show_screen("home"))
        layout.addWidget(self.home)
        layout.addStretch(2)
        self.refresh()

    def refresh(self) -> None:
        language = self.app.language
        self.title.setText(text(language, "unknown_title"))
        self.subtitle.setText(text(language, "unknown_subtitle"))
        self.tip_label.setText(text(language, "tip"))
        self.tip_body.setText(text(language, "tip_body"))
        self.retry.setText(text(language, "discover"))
        self.home.setText(text(language, "return_home"))
