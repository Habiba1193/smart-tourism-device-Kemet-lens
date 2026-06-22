from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..theme import GOLD, MUTED, TITLE_FONT_STACK
from ..translations import text
from ..widgets import GradientScreen, content_shell, make_button, role_label, transparent_scroll


class AboutScreen(GradientScreen):
    def __init__(self, app) -> None:
        super().__init__()

        self.app = app
        self.flow_items: list[tuple[QLabel, QLabel, str, str]] = []
        self.feature_items: list[tuple[QLabel, QLabel, str, str]] = []

        outer = content_shell((52, 62, 52, 38), 18)
        self.setLayout(outer)

        self.back = make_button("", "back", 32)
        self.back.clicked.connect(lambda: self.app.show_screen("home"))
        outer.addWidget(self.back)

        self.title = role_label("", "title")
        self.title.setStyleSheet(
            f"font-family: {TITLE_FONT_STACK}; "
            "font-size: 32px; "
            "font-weight: 900; "
            "color: #ffe9ad;"
        )
        outer.addWidget(self.title)

        self.intro = role_label("", "subtitle", True)
        self.intro.setStyleSheet(
            "font-size: 16px; "
            "font-weight: 650; "
            "color: #fff3cc;"
        )
        outer.addWidget(self.intro)

        host = QWidget()
        self.inner = QVBoxLayout(host)
        self.inner.setContentsMargins(0, 14, 0, 0)
        self.inner.setSpacing(18)

        self.inner.addWidget(self._how_it_works())

        self.section = QLabel("")
        self.section.setStyleSheet(
            f"color: {GOLD}; "
            f"font-family: {TITLE_FONT_STACK}; "
            "font-size: 24px; "
            "font-weight: 800;"
        )
        self.inner.addWidget(self.section)

        for icon, title_text, body in [
            ("OFF", "offline_title", "offline_body"),
            ("AI", "ai_title", "ai_body"),
            ("ASK", "bakkar_title", "bakkar_body"),
            ("PI", "pi_title", "pi_body"),
            ("UI", "touch_title", "touch_body"),
            ("EN", "multi_title", "multi_body"),
            ("M", "museum_title", "museum_body"),
        ]:
            self.inner.addWidget(self._feature(icon, title_text, body))

        self.inner.addStretch(1)
        outer.addWidget(transparent_scroll(host), 1)

        self.home = make_button("", "primary", 76)
        self.home.setStyleSheet(
            "font-size: 17px; "
            "font-weight: 800;"
        )
        self.home.clicked.connect(lambda: self.app.show_screen("home"))
        outer.addWidget(self.home)

        self.refresh()

    def _how_it_works(self) -> QFrame:
        card = QFrame()
        card.setProperty("card", "dark")
        card.setMinimumHeight(180)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(20)

        self.how_title = QLabel("")
        self.how_title.setStyleSheet(
            f"color: {GOLD}; "
            f"font-family: {TITLE_FONT_STACK}; "
            "font-size: 24px; "
            "font-weight: 800;"
        )
        layout.addWidget(self.how_title)

        row = QHBoxLayout()
        row.setSpacing(16)

        for icon, title_text, body in [
            ("CAM", "camera", "camera_body"),
            ("AI", "ai_detection", "ai_detection_body"),
            ("INFO", "artifact_info", "artifact_info_body"),
            ("ASK", "guide_flow", "guide_flow_body"),
            ("UI", "display", "display_body"),
        ]:
            col = QVBoxLayout()
            col.setSpacing(8)

            badge = QLabel(icon)
            badge.setAlignment(Qt.AlignCenter)
            badge.setFixedSize(62, 62)
            badge.setStyleSheet(
                f"background: rgba(224,173,63,45); "
                f"color: {GOLD}; "
                "border-radius: 31px; "
                "font-size: 13px; "
                "font-weight: 900;"
            )

            name = QLabel(title_text)
            name.setAlignment(Qt.AlignCenter)
            name.setWordWrap(True)
            name.setStyleSheet(
                "color: #ffe9ad; "
                "font-size: 13px; "
                "font-weight: 900;"
            )

            desc = QLabel(body)
            desc.setAlignment(Qt.AlignCenter)
            desc.setWordWrap(True)
            desc.setStyleSheet(
                f"color: {MUTED}; "
                "font-size: 12px; "
                "font-weight: 650;"
            )

            col.addWidget(badge, 0, Qt.AlignCenter)
            col.addWidget(name)
            col.addWidget(desc)

            row.addLayout(col, 1)

            self.flow_items.append((name, desc, title_text, body))

        layout.addLayout(row)

        return card

    def _feature(self, icon: str, title_text: str, body: str) -> QFrame:
        card = QFrame()
        card.setProperty("card", "dark")
        card.setMinimumHeight(105)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(22, 16, 22, 16)
        layout.setSpacing(20)

        badge = QLabel(icon)
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedSize(58, 58)
        badge.setStyleSheet(
            f"background: rgba(224,173,63,45); "
            f"color: {GOLD}; "
            "border-radius: 12px; "
            "font-size: 14px; "
            "font-weight: 900;"
        )
        layout.addWidget(badge)

        text_box = QVBoxLayout()
        text_box.setSpacing(7)

        title = QLabel(title_text)
        title.setStyleSheet(
            "color: #ffe9ad; "
            "font-size: 18px; "
            "font-weight: 900;"
        )

        desc = QLabel(body)
        desc.setWordWrap(True)
        desc.setStyleSheet(
            f"color: {MUTED}; "
            "font-size: 15px; "
            "font-weight: 650;"
        )

        text_box.addWidget(title)
        text_box.addWidget(desc)

        layout.addLayout(text_box, 1)

        self.feature_items.append((title, desc, title_text, body))

        return card

    def refresh(self) -> None:
        language = self.app.language

        self.back.setText(f"←  {text(language, 'back')}")
        self.title.setText(text(language, "about_title"))
        self.intro.setText(text(language, "about_intro"))
        self.how_title.setText(text(language, "how_it_works"))
        self.section.setText(text(language, "features"))
        self.home.setText(text(language, "return_home"))

        for title, desc, title_key, body_key in self.flow_items:
            title.setText(text(language, title_key))
            desc.setText(text(language, body_key))

        for title, desc, title_key, body_key in self.feature_items:
            title.setText(text(language, title_key))
            desc.setText(text(language, body_key))
