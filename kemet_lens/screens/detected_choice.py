from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..data import ARTIFACTS
from ..theme import GOLD, MUTED, TITLE_FONT_STACK
from ..translations import artifact_text, text
from ..widgets import (
    GradientScreen,
    RoundedImage,
    add_shadow,
    content_shell,
    make_button,
    role_label,
    transparent_scroll,
)


class DetectedChoiceScreen(GradientScreen):
    def __init__(self, app) -> None:
        super().__init__()

        self.app = app
        self.detections: list[tuple[str, int]] = []

        # Bigger margins and spacing for Raspberry Pi Touch Display 2 fullscreen.
        outer = content_shell((52, 62, 52, 38), 18)
        self.setLayout(outer)

        self.back = make_button("", "back", 40)
        self.back.clicked.connect(lambda: self.app.show_screen("scanner"))
        self.back.setStyleSheet(
            "font-size: 15px; "
            "font-weight: 800;"
        )
        outer.addWidget(self.back)

        self.title = role_label("", "title", True)
        self.title.setStyleSheet(
            f"font-family: {TITLE_FONT_STACK}; "
            "font-size: 32px; "
            "font-weight: 850; "
            "color: #ffe9ad;"
        )
        outer.addWidget(self.title)

        self.subtitle = role_label("", "subtitle", True)
        self.subtitle.setStyleSheet(
            "font-size: 16px; "
            "font-weight: 650; "
            "color: #fff3cc; "
            "line-height: 135%;"
        )
        outer.addWidget(self.subtitle)

        self.count = QLabel()
        self.count.setStyleSheet(
            f"color: {GOLD}; "
            "font-size: 15px; "
            "font-weight: 850;"
        )
        outer.addWidget(self.count)

        self.list_host = QWidget()
        self.list_layout = QVBoxLayout(self.list_host)
        self.list_layout.setContentsMargins(0, 12, 0, 0)
        self.list_layout.setSpacing(18)

        scroll = transparent_scroll(self.list_host)
        outer.addWidget(scroll, 1)

    def set_detections(self, detections: list[tuple[str, int]]) -> None:
        # Allow all 5 detected objects.
        self.detections = detections[:5]

    def refresh(self) -> None:
        self.back.setText(f"←  {text(self.app.language, 'back')}")
        self.title.setText(text(self.app.language, "detected_choice_title"))
        self.subtitle.setText(text(self.app.language, "detected_choice_subtitle"))
        self.count.setText(
            text(
                self.app.language,
                "detected_choice_count",
                count=len(self.detections),
            )
        )

        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()

        for key, confidence in self.detections:
            self.list_layout.addWidget(self._card(key, confidence))

        self.list_layout.addStretch(1)

    def _card(self, key: str, confidence: int) -> QFrame:
        artifact = ARTIFACTS[key]
        localized = artifact_text(self.app.language, artifact)

        card = QFrame()
        card.setCursor(Qt.PointingHandCursor)
        card.setMinimumHeight(126)
        card.setStyleSheet(
            "QFrame { "
            "background: rgba(8,10,16,218); "
            "border: 1px solid rgba(224,173,63,60); "
            "border-radius: 18px; "
            "} "
            "QFrame QLabel { "
            "background: transparent; "
            "border: none; "
            "}"
        )
        add_shadow(card, blur=18, alpha=55)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(18)

        image = RoundedImage(artifact.thumbnail, radius=12)
        image.setFixedSize(104, 104)
        layout.addWidget(image, 0, Qt.AlignVCenter)

        text_box = QVBoxLayout()
        text_box.setSpacing(8)

        top = QHBoxLayout()
        top.setSpacing(10)

        name = QLabel(localized["display_name"].upper())
        name.setWordWrap(True)
        name.setStyleSheet(
            f"color: #ffe9ad; "
            f"font-family: {TITLE_FONT_STACK}; "
            "font-size: 18px; "
            "font-weight: 850;"
        )

        confidence_badge = QLabel(
            text(
                self.app.language,
                "match_badge",
                confidence=confidence,
            )
        )
        confidence_badge.setAlignment(Qt.AlignCenter)
        confidence_badge.setMinimumHeight(32)
        confidence_badge.setStyleSheet(
            f"background: rgba(224,173,63,55); "
            f"color: {GOLD}; "
            "border-radius: 12px; "
            "font-size: 13px; "
            "font-weight: 850; "
            "padding: 5px 12px;"
        )

        top.addWidget(name, 1)
        top.addWidget(confidence_badge, 0, Qt.AlignTop)
        text_box.addLayout(top)

        desc = QLabel(localized["short_description"])
        desc.setWordWrap(True)
        desc.setStyleSheet(
            "color: #dbd4c5; "
            "font-size: 14px; "
            "font-weight: 600; "
            "line-height: 140%;"
        )
        text_box.addWidget(desc)

        select = QLabel(text(self.app.language, "detected_choice_select").upper())
        select.setStyleSheet(
            f"color: {MUTED}; "
            "font-size: 12px; "
            "font-weight: 900; "
            "letter-spacing: 1px;"
        )
        text_box.addWidget(select)

        layout.addLayout(text_box, 1)

        card.mousePressEvent = (
            lambda event, item=key, score=confidence: self.app.choose_detected_artifact(
                item,
                score,
            )
        )

        return card
