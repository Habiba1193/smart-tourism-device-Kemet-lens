from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout

from ..theme import TITLE_FONT_STACK
from ..translations import text
from ..widgets import CircularImage, GradientScreen, add_shadow, content_shell, make_button, role_label, spacer


class HomeScreen(GradientScreen):
    def __init__(self, app) -> None:
        super().__init__()

        self.app = app

        layout = content_shell((52, 70, 52, 42), 18)
        self.setLayout(layout)

        layout.addStretch(1)

        self.brand = role_label("", "brand")
        self.brand.setAlignment(Qt.AlignCenter)
        self.brand.setStyleSheet(
            "color: #b88925; "
            "font-size: 16px; "
            "font-weight: 800; "
            "letter-spacing: 5px;"
        )
        layout.addWidget(self.brand)

        self.title = role_label("", "title")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setWordWrap(True)
        self.title.setStyleSheet(
            f"font-family: {TITLE_FONT_STACK}; "
            "font-size: 38px; "
            "font-weight: 900; "
            "color: #fff0bd;"
        )
        layout.addWidget(self.title)

        self.subtitle = role_label("", "subtitle", True)
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setStyleSheet(
            "color: #fff3cc; "
            "font-size: 17px; "
            "font-weight: 650; "
            "line-height: 145%;"
        )
        layout.addWidget(self.subtitle)

        layout.addStretch(2)

        image = CircularImage("gem.jpg", 230)
        layout.addWidget(image, 0, Qt.AlignCenter)

        layout.addStretch(2)

        self.begin = make_button("", "primary", 76)
        self.begin.setStyleSheet(
            "font-size: 18px; "
            "font-weight: 900;"
        )
        self.begin.clicked.connect(lambda: self.app.open_language("scanner"))
        add_shadow(self.begin, 26, 75)
        layout.addWidget(self.begin)

        layout.addWidget(spacer(8))

        self.about = make_button("", "secondary", 70)
        self.about.setStyleSheet(
            "font-size: 17px; "
            "font-weight: 800;"
        )
        self.about.clicked.connect(lambda: self.app.show_screen("about"))
        layout.addWidget(self.about)

        layout.addStretch(1)

        self.refresh()

    def refresh(self) -> None:
        language = self.app.language

        self.brand.setText(text(language, "brand").upper())
        self.title.setText(text(language, "home_title"))
        self.subtitle.setText(text(language, "home_subtitle"))
        self.begin.setText(text(language, "begin_journey"))
        self.about.setText(text(language, "about_kemet_lens"))
