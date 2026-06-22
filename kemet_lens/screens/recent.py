from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..data import ARTIFACTS
from ..theme import GOLD, MUTED, TITLE_FONT_STACK
from ..translations import artifact_text, text
from ..widgets import GradientScreen, RoundedImage, content_shell, make_button, role_label, transparent_scroll


class RecentScreen(GradientScreen):
    def __init__(self, app) -> None:
        super().__init__()

        self.app = app

        outer = content_shell((52, 62, 52, 38), 18)
        self.setLayout(outer)

        self.back = make_button("", "back", 32)
        self.back.clicked.connect(lambda: self.app.show_screen("result"))
        outer.addWidget(self.back)

        self.title = role_label("", "title")
        self.title.setStyleSheet(
            f"font-family: {TITLE_FONT_STACK}; "
            "font-size: 32px; "
            "font-weight: 900; "
            "color: #ffe9ad;"
        )
        outer.addWidget(self.title)

        self.subtitle = role_label("", "subtitle", True)
        self.subtitle.setStyleSheet(
            "font-size: 16px; "
            "font-weight: 650; "
            "color: #fff3cc;"
        )
        outer.addWidget(self.subtitle)

        self.list_host = QWidget()
        self.list_layout = QVBoxLayout(self.list_host)
        self.list_layout.setContentsMargins(0, 18, 0, 0)
        self.list_layout.setSpacing(20)

        outer.addWidget(transparent_scroll(self.list_host), 1)

        self.home = make_button("", "secondary", 76)
        self.home.setStyleSheet(
            "font-size: 17px; "
            "font-weight: 800;"
        )
        self.home.clicked.connect(lambda: self.app.show_screen("home"))
        outer.addWidget(self.home)

    def refresh(self) -> None:
        self.back.setText(f"←  {text(self.app.language, 'back')}")
        self.title.setText(text(self.app.language, "recent_title"))
        self.subtitle.setText(text(self.app.language, "recent_subtitle"))
        self.home.setText(text(self.app.language, "home"))

        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()

        if self.app.recent_keys:
            for key in self.app.recent_keys:
                self.list_layout.addWidget(self._card(key))
        else:
            self.list_layout.addWidget(self._empty_state())

        self.list_layout.addStretch(1)

    def _empty_state(self) -> QFrame:
        card = QFrame()
        card.setObjectName("emptyRecentCard")
        card.setMinimumHeight(220)
        card.setStyleSheet(
            "QFrame#emptyRecentCard { "
            "background: rgba(8,10,16,190); "
            "border: 1px solid rgba(224,173,63,55); "
            "border-radius: 18px; "
            "} "
            "QFrame#emptyRecentCard QLabel { "
            "background: transparent; "
            "border: none; "
            "}"
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 28, 30, 28)
        layout.setSpacing(14)

        title = QLabel(text(self.app.language, "recent_empty_title"))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"color: #ffe9ad; "
            f"font-family: {TITLE_FONT_STACK}; "
            "font-size: 24px; "
            "font-weight: 900;"
        )
        layout.addWidget(title)

        body = QLabel(text(self.app.language, "recent_empty_body"))
        body.setAlignment(Qt.AlignCenter)
        body.setWordWrap(True)
        body.setStyleSheet(
            f"color: {MUTED}; "
            "font-size: 16px; "
            "font-weight: 650; "
            "line-height: 150%;"
        )
        layout.addWidget(body)

        return card

    def _card(self, key: str) -> QFrame:
        artifact = ARTIFACTS[key]
        localized = artifact_text(self.app.language, artifact)

        card = QFrame()
        card.setCursor(Qt.PointingHandCursor)
        card.setMinimumHeight(140)
        card.setStyleSheet(
            "QFrame { "
            "background: rgba(8,10,16,205); "
            "border: 1px solid rgba(224,173,63,45); "
            "border-radius: 18px; "
            "} "
            "QLabel { "
            "background: transparent; "
            "border: none; "
            "}"
        )

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(20)

        image = RoundedImage(artifact.thumbnail, radius=12)
        image.setFixedSize(106, 106)
        layout.addWidget(image)

        text_box = QVBoxLayout()
        text_box.setSpacing(8)

        top = QHBoxLayout()
        top.setSpacing(10)

        name = QLabel(localized["display_name"].upper())
        name.setWordWrap(True)
        name.setStyleSheet(
            f"color: #ffe9ad; "
            f"font-family: {TITLE_FONT_STACK}; "
            "font-size: 20px; "
            "font-weight: 900;"
        )

        confidence = QLabel(f"{artifact.default_confidence}%")
        confidence.setAlignment(Qt.AlignCenter)
        confidence.setMinimumHeight(34)
        confidence.setStyleSheet(
            f"background: rgba(224,173,63,55); "
            f"color: {GOLD}; "
            "border-radius: 17px; "
            "font-size: 14px; "
            "font-weight: 900; "
            "padding: 4px 12px;"
        )

        top.addWidget(name, 1)
        top.addWidget(confidence, 0, Qt.AlignTop)
        text_box.addLayout(top)

        short_description = localized["short_description"]

        if len(short_description) > 125:
            short_description = short_description[:125].rstrip() + "..."

        desc = QLabel(short_description)
        desc.setWordWrap(True)
        desc.setStyleSheet(
            "color: #dbd4c5; "
            "font-size: 15px; "
            "font-weight: 650; "
            "line-height: 145%;"
        )
        text_box.addWidget(desc)

        match = QLabel(text(self.app.language, "match").upper())
        match.setStyleSheet(
            f"color: {MUTED}; "
            "font-size: 12px; "
            "font-weight: 900; "
            "letter-spacing: 1px;"
        )
        text_box.addWidget(match)

        layout.addLayout(text_box, 1)

        card.mousePressEvent = lambda event, item=key: self.app.open_artifact(item)

        return card
