from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from ..theme import GOLD, MUTED, PAPYRUS_DARK_TEXT, TITLE_FONT_STACK
from ..translations import LANGUAGES, text
from ..widgets import GradientScreen, add_shadow, content_shell, make_button, repolish, role_label


class LanguageCard(QFrame):
    def __init__(self, language: dict, selected: bool, callback) -> None:
        super().__init__()

        self.language = language
        self.callback = callback

        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(104)
        self.setProperty("card", "papyrus" if selected else "glass")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 16, 22, 16)
        layout.setSpacing(22)

        icon = QLabel(language["icon"])
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(56, 56)

        if selected:
            icon.setStyleSheet(
                f"border: 2px solid {GOLD}; "
                "border-radius: 28px; "
                f"color: {GOLD}; "
                "background: rgba(224, 173, 63, 26); "
                "font-size: 17px; "
                "font-weight: 800;"
            )
        else:
            icon.setStyleSheet(
                "border-radius: 28px; "
                f"color: {GOLD}; "
                "background: #06080d; "
                "font-size: 17px; "
                "font-weight: 800;"
            )

        layout.addWidget(icon)

        text_box = QVBoxLayout()
        text_box.setSpacing(5)

        name = QLabel(language["native"])
        english = QLabel(language["english"])

        if selected:
            name.setStyleSheet(
                f"color: {PAPYRUS_DARK_TEXT}; "
                "font-weight: 900; "
                "font-size: 18px;"
            )
            english.setStyleSheet(
                "color: #735f38; "
                "font-size: 15px; "
                "font-weight: 650;"
            )
        else:
            name.setStyleSheet(
                "color: #fff1bd; "
                "font-weight: 900; "
                "font-size: 18px;"
            )
            english.setStyleSheet(
                f"color: {MUTED}; "
                "font-size: 15px; "
                "font-weight: 650;"
            )

        text_box.addWidget(name)
        text_box.addWidget(english)

        layout.addLayout(text_box, 1)

        mark = QLabel("•" if selected else "")
        mark.setAlignment(Qt.AlignCenter)
        mark.setFixedSize(34, 34)
        mark.setStyleSheet(
            f"border-radius: 17px; "
            f"background: {GOLD if selected else 'transparent'}; "
            f"color: {PAPYRUS_DARK_TEXT}; "
            "font-size: 18px; "
            "font-weight: 900;"
        )

        layout.addWidget(mark)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self.callback(self.language["code"])

        super().mousePressEvent(event)


class LanguageScreen(GradientScreen):
    def __init__(self, app) -> None:
        super().__init__()

        self.app = app

        self.layout = content_shell((52, 64, 52, 42), 18)
        self.setLayout(self.layout)

        self.cards: list[LanguageCard] = []

        self.refresh()

    def refresh(self) -> None:
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()

        back = make_button(f"←  {text(self.app.language, 'back')}", "back", 32)
        back.clicked.connect(self.app.cancel_language)
        self.layout.addWidget(back)

        title = role_label(text(self.app.language, "choose_language"), "title")
        title.setStyleSheet(
            f"font-family: {TITLE_FONT_STACK}; "
            "font-size: 34px; "
            "font-weight: 900; "
            "color: #ffe9ad;"
        )
        self.layout.addWidget(title)

        subtitle = role_label(text(self.app.language, "language_subtitle"), "subtitle", True)
        subtitle.setStyleSheet(
            "font-size: 17px; "
            "font-weight: 650; "
            "color: #fff3cc;"
        )
        self.layout.addWidget(subtitle)

        self.layout.addSpacing(12)

        self.cards.clear()

        for language in LANGUAGES:
            selected = language["code"] == self.app.language
            card = LanguageCard(language, selected, self.app.set_language)
            self.layout.addWidget(card)
            self.cards.append(card)

        self.layout.addStretch(1)

        cont = make_button(text(self.app.language, "continue"), "primary", 76)
        cont.setStyleSheet(
            "font-size: 17px; "
            "font-weight: 800;"
        )
        cont.clicked.connect(self.app.continue_from_language)
        add_shadow(cont, 24, 65)
        self.layout.addWidget(cont)

        for card in self.cards:
            repolish(card)
