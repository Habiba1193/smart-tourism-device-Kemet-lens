from __future__ import annotations

from PySide6.QtCore import QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..chatbot import OllamaGuideWorker
from ..paths import ASSET_DIR
from ..theme import CREAM, GOLD, MUTED, TITLE_FONT_STACK
from ..translations import text
from ..widgets import BottomNav, GradientScreen, content_shell, make_button, transparent_scroll


# ============================================================
# Built-in touchscreen keyboard
# ============================================================

class TouchKeyboard(QFrame):
    def __init__(self, target_input: QLineEdit, on_enter) -> None:
        super().__init__()

        self.target_input = target_input
        self.on_enter = on_enter
        self.shift_enabled = False

        self.setObjectName("touchKeyboard")
        self.setStyleSheet(
            "QFrame#touchKeyboard { "
            "background: rgba(5, 7, 12, 245); "
            "border: 1px solid rgba(224, 173, 63, 85); "
            "border-radius: 14px; "
            "} "
            "QPushButton { "
            "background: rgba(224, 173, 63, 45); "
            "border: 1px solid rgba(224, 173, 63, 90); "
            "border-radius: 8px; "
            "color: #ffe9ad; "
            "font-size: 13px; "
            "font-weight: 800; "
            "min-height: 30px; "
            "} "
            "QPushButton:pressed { "
            "background: rgba(224, 173, 63, 135); "
            "color: #100d08; "
            "} "
            "QPushButton[special='true'] { "
            "background: rgba(8, 10, 16, 235); "
            "color: #e7dfcf; "
            "} "
        )

        layout = QGridLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(5)

        rows = [
            list("1234567890"),
            list("qwertyuiop"),
            list("asdfghjkl"),
            list("zxcvbnm"),
        ]

        for row_index, keys in enumerate(rows):
            offset = 0

            if row_index == 2:
                offset = 1
            elif row_index == 3:
                offset = 2

            for col_index, key in enumerate(keys):
                button = self._make_key(key)
                layout.addWidget(button, row_index, col_index + offset)

        shift = self._make_special_key("Shift", self._toggle_shift)
        layout.addWidget(shift, 3, 0, 1, 2)

        backspace = self._make_special_key("⌫", self._backspace)
        layout.addWidget(backspace, 3, 9, 1, 1)

        clear = self._make_special_key("Clear", self._clear)
        layout.addWidget(clear, 4, 0, 1, 2)

        space = self._make_special_key("Space", self._space)
        layout.addWidget(space, 4, 2, 1, 4)

        question = self._make_special_key("?", lambda: self._insert_text("?"))
        layout.addWidget(question, 4, 6, 1, 1)

        dot = self._make_special_key(".", lambda: self._insert_text("."))
        layout.addWidget(dot, 4, 7, 1, 1)

        enter = self._make_special_key("Ask", self._enter)
        layout.addWidget(enter, 4, 8, 1, 2)

        self.hide()

    def _make_key(self, key: str) -> QPushButton:
        button = QPushButton(key)
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(lambda: self._insert_key(key))
        return button

    def _make_special_key(self, label: str, callback) -> QPushButton:
        button = QPushButton(label)
        button.setCursor(Qt.PointingHandCursor)
        button.setProperty("special", "true")
        button.clicked.connect(callback)
        return button

    def _insert_key(self, key: str) -> None:
        char = key.upper() if self.shift_enabled else key
        self.target_input.insert(char)

        if self.shift_enabled:
            self.shift_enabled = False

        self.target_input.setFocus()

    def _insert_text(self, value: str) -> None:
        self.target_input.insert(value)
        self.target_input.setFocus()

    def _toggle_shift(self) -> None:
        self.shift_enabled = not self.shift_enabled
        self.target_input.setFocus()

    def _backspace(self) -> None:
        text_value = self.target_input.text()
        cursor = self.target_input.cursorPosition()

        if cursor <= 0:
            self.target_input.setFocus()
            return

        new_text = text_value[:cursor - 1] + text_value[cursor:]
        self.target_input.setText(new_text)
        self.target_input.setCursorPosition(cursor - 1)
        self.target_input.setFocus()

    def _space(self) -> None:
        self.target_input.insert(" ")
        self.target_input.setFocus()

    def _clear(self) -> None:
        self.target_input.clear()
        self.target_input.setFocus()

    def _enter(self) -> None:
        self.hide()
        self.on_enter()


class KeyboardLineEdit(QLineEdit):
    def __init__(self) -> None:
        super().__init__()
        self.keyboard: TouchKeyboard | None = None

    def focusInEvent(self, event) -> None:  # noqa: N802
        super().focusInEvent(event)

        if self.keyboard is not None:
            self.keyboard.show()
            self.keyboard.raise_()


# ============================================================
# Bakkar avatar widget
# ============================================================

class BakkarOutlineAvatar(QWidget):
    def __init__(self, size: int = 38) -> None:
        super().__init__()
        self.setFixedSize(size, size)

        icon_path = ASSET_DIR / "bakkar_icon.png"
        if not icon_path.exists():
            icon_path = ASSET_DIR / "bakkar_icon.jpeg"

        self.pixmap = self._gold_only_pixmap(QPixmap(str(icon_path)))
        self.source_rect = self._gold_bounds(self.pixmap) if not self.pixmap.isNull() else QRectF()

    @staticmethod
    def _is_gold_pixel(color: QColor) -> bool:
        return (
            color.alpha() > 0
            and color.red() > 120
            and color.green() > 95
            and color.blue() < 220
            and color.red() - color.blue() > 20
            and color.green() - color.blue() > 5
        )

    @classmethod
    def _gold_only_pixmap(cls, pixmap: QPixmap) -> QPixmap:
        if pixmap.isNull():
            return pixmap

        image = pixmap.toImage()

        for y in range(image.height()):
            for x in range(image.width()):
                color = image.pixelColor(x, y)
                color.setAlpha(255 if cls._is_gold_pixel(color) else 0)
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
                color = image.pixelColor(x, y)
                if color.alpha() > 0:
                    found = True
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)

        if not found:
            return QRectF(0, 0, pixmap.width(), pixmap.height())

        pad = 36
        left = max(0, min_x - pad)
        top = max(0, min_y - pad)
        right = min(image.width(), max_x + pad)
        bottom = min(image.height(), max_y + pad)

        return QRectF(left, top, right - left, bottom - top)

    def paintEvent(self, event) -> None:  # noqa: N802
        if self.pixmap.isNull():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        source = (
            self.source_rect
            if not self.source_rect.isNull()
            else QRectF(0, 0, self.pixmap.width(), self.pixmap.height())
        )

        painter.drawPixmap(QRectF(self.rect()), self.pixmap, source)


# ============================================================
# Ask Bakkar screen
# ============================================================

class AskBakkarScreen(GradientScreen):
    def __init__(self, app) -> None:
        super().__init__()

        self.app = app
        self.guide_worker: OllamaGuideWorker | None = None
        self.guide_busy = False
        self.has_user_messages = False
        self.artifact_key = self.app.current_artifact.key
        self.language_code = self.app.language

        self.thinking_label: QLabel | None = None
        self.thinking_base_text = ""
        self.thinking_dot_step = 0

        self.thinking_timer = QTimer(self)
        self.thinking_timer.setInterval(420)
        self.thinking_timer.timeout.connect(self._animate_thinking_dots)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        content = QWidget()
        layout = content_shell((24, 44, 24, 18), 12)
        content.setLayout(layout)
        outer.addWidget(content, 1)

        self.back = make_button("", "back", 24)
        self.back.clicked.connect(lambda: self.app.show_screen("result"))
        layout.addWidget(self.back)

        self.title = QLabel()
        self.title.setStyleSheet(
            f"font-family: {TITLE_FONT_STACK}; "
            "font-size: 22px; "
            "font-weight: 800; "
            "color: #ffe9ad;"
        )
        layout.addWidget(self.title)

        self.subtitle = QLabel()
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(
            f"color: {MUTED}; "
            "font-size: 13px; "
            "font-weight: 650;"
        )
        layout.addWidget(self.subtitle)

        self.chat_host = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_host)
        self.chat_layout.setContentsMargins(0, 6, 0, 6)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setAlignment(Qt.AlignTop)

        self.chat_scroll = transparent_scroll(self.chat_host)
        layout.addWidget(self.chat_scroll, 1)

        composer = QFrame()
        composer.setObjectName("bakkarComposer")
        composer.setStyleSheet(
            "QFrame#bakkarComposer { "
            "background: rgba(8,10,16,225); "
            "border: 1px solid #2b2317; "
            "border-radius: 14px; "
            "} "
            f"QLineEdit {{ "
            "background: rgba(4, 6, 10, 230); "
            "border: 1px solid #2b2317; "
            "border-radius: 10px; "
            f"color: {CREAM}; "
            "padding: 0px 12px; "
            "font-size: 12px; "
            "} "
            f"QLineEdit:focus {{ "
            f"border: 1px solid {GOLD}; "
            "} "
            "QPushButton[guide='ask'] { "
            f"background: {GOLD}; "
            "color: #100d08; "
            "border-radius: 10px; "
            "font-size: 12px; "
            "font-weight: 800; "
            "padding: 0px 12px; "
            "} "
            "QPushButton:disabled { "
            "color: rgba(255, 233, 173, 95); "
            "background: rgba(80, 67, 36, 120); "
            "}"
        )

        composer_layout = QHBoxLayout(composer)
        composer_layout.setContentsMargins(12, 12, 12, 12)
        composer_layout.setSpacing(8)

        self.question_input = KeyboardLineEdit()
        self.question_input.setFixedHeight(40)
        self.question_input.returnPressed.connect(self._ask_bakkar)
        composer_layout.addWidget(self.question_input, 1)

        self.ask_button = QPushButton()
        self.ask_button.setCursor(Qt.PointingHandCursor)
        self.ask_button.setProperty("guide", "ask")
        self.ask_button.setFixedHeight(40)
        self.ask_button.setMinimumWidth(112)
        self.ask_button.clicked.connect(self._ask_bakkar)
        composer_layout.addWidget(self.ask_button)

        layout.addWidget(composer)

        self.touch_keyboard = TouchKeyboard(self.question_input, self._ask_bakkar)
        self.question_input.keyboard = self.touch_keyboard
        layout.addWidget(self.touch_keyboard)

        self.nav = BottomNav(
            lambda: self.app.show_screen("scanner"),
            lambda: self.app.show_screen("home"),
            lambda: self.app.show_screen("ask_bakkar"),
            lambda: self.app.open_language("ask_bakkar"),
            lambda: self.app.show_screen("recent"),
            self.app.language,
            use_bakkar_image=True,
        )
        outer.addWidget(self.nav)

        self.refresh()

    def refresh(self) -> None:
        current_key = self.app.current_artifact.key
        current_language = self.app.language

        if current_key != self.artifact_key or current_language != self.language_code:
            self.artifact_key = current_key
            self.language_code = current_language
            self._clear_chat()

        self.back.setText(f"←  {text(self.app.language, 'back')}")
        self.title.setText(text(self.app.language, "ask_bakkar"))
        self.subtitle.setText(text(self.app.language, "ask_bakkar_subtitle"))
        self.question_input.setPlaceholderText(text(self.app.language, "guide_input_placeholder"))
        self.ask_button.setText(text(self.app.language, "guide_ask"))
        self.nav.set_language(self.app.language)

        if self.chat_layout.count() == 0 or not self.has_user_messages:
            self._clear_chat()
            self._show_empty_message()

    def _clear_chat(self) -> None:
        self._stop_thinking_animation()

        while self.chat_layout.count():
            item = self.chat_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()

        self.has_user_messages = False

    def _show_empty_message(self) -> None:
        self.chat_layout.addStretch(1)

        row_host = QWidget()
        row_host.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        row = QHBoxLayout(row_host)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        row.addWidget(self._bakkar_avatar(), 0, Qt.AlignBottom)

        label = QLabel(text(self.app.language, "guide_empty_answer"))
        label.setWordWrap(True)
        label.setMaximumWidth(300)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setAlignment(Qt.AlignRight if self.app.language == "ar" else Qt.AlignLeft)
        label.setLayoutDirection(Qt.RightToLeft if self.app.language == "ar" else Qt.LeftToRight)
        label.setStyleSheet(
            "background: transparent; "
            "border: none; "
            "color: #ffe9ad; "
            "font-size: 12px; "
            "font-weight: 650; "
            "line-height: 150%;"
        )

        row.addWidget(label, 0)
        row.addStretch(1)

        self.chat_layout.addWidget(row_host)

    def _bakkar_avatar(self) -> BakkarOutlineAvatar:
        return BakkarOutlineAvatar(38)

    def _ask_bakkar(self) -> None:
        if self.guide_busy:
            return

        question = self.question_input.text().strip()

        if not question:
            return

        self.touch_keyboard.hide()
        self.question_input.clear()

        if not self.has_user_messages:
            self._clear_chat()
            self.has_user_messages = True

        self._add_message(question, "question")

        self.thinking_label = self._add_message(
            self._thinking_message_text(),
            "answer",
            object_name="thinkingMessage",
        )

        self._start_thinking_animation()

        self.guide_busy = True
        self._set_busy(True)

        worker = OllamaGuideWorker(
            self.app.language,
            self.app.current_artifact.key,
            question,
            self,
        )

        self.guide_worker = worker
        worker.answer_ready.connect(self._handle_answer)
        worker.finished.connect(worker.deleteLater)
        worker.start()

    def _handle_answer(self, answer: str, artifact_key: str) -> None:
        self._remove_thinking_message()

        self.guide_busy = False
        self.guide_worker = None
        self._set_busy(False)

        if artifact_key == self.app.current_artifact.key:
            self._add_message(answer, "answer")

    def _set_busy(self, busy: bool) -> None:
        self.question_input.setEnabled(not busy)
        self.ask_button.setEnabled(not busy)

        if busy:
            self.touch_keyboard.hide()

    def _remove_thinking_message(self) -> None:
        self._stop_thinking_animation()

        for index in range(self.chat_layout.count() - 1, -1, -1):
            item = self.chat_layout.itemAt(index)
            widget = item.widget()

            if widget and widget.objectName() == "thinkingMessage":
                self.chat_layout.takeAt(index)
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()
                return

    def _start_thinking_animation(self) -> None:
        self.thinking_base_text = text(self.app.language, "guide_thinking").rstrip(".…").strip()
        self.thinking_dot_step = 0
        self._animate_thinking_dots()
        self.thinking_timer.start()

    def _stop_thinking_animation(self) -> None:
        self.thinking_timer.stop()
        self.thinking_label = None
        self.thinking_base_text = ""
        self.thinking_dot_step = 0

    def _thinking_message_text(self) -> str:
        return f"{text(self.app.language, 'guide_thinking').rstrip('.…').strip()}..."

    def _animate_thinking_dots(self) -> None:
        if self.thinking_label is None:
            self.thinking_timer.stop()
            return

        self.thinking_dot_step = (self.thinking_dot_step % 3) + 1
        self.thinking_label.setText(f"{self.thinking_base_text}{'.' * self.thinking_dot_step}")

    def _add_message(self, value: str, kind: str, object_name: str = "") -> QLabel:
        row_host = QWidget()
        row_host.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        if object_name:
            row_host.setObjectName(object_name)

        row = QHBoxLayout(row_host)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        bubble = QFrame()
        bubble.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        is_question = kind == "question"

        bubble.setMaximumWidth(350)
        bubble.setStyleSheet(
            "QFrame { "
            f"background: {'rgba(224,173,63,45)' if is_question else 'rgba(8,10,16,235)'}; "
            f"border: 1px solid {'rgba(224,173,63,95)' if is_question else 'rgba(224,173,63,55)'}; "
            "border-radius: 14px; "
            "} "
            "QLabel { "
            "background: transparent; "
            "border: none; "
            "}"
        )

        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(16, 13, 16, 13)

        label = QLabel(value)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setAlignment(
            Qt.AlignRight
            if self.app.language == "ar" and not is_question
            else Qt.AlignLeft
        )
        label.setLayoutDirection(
            Qt.RightToLeft
            if self.app.language == "ar" and not is_question
            else Qt.LeftToRight
        )
        label.setStyleSheet(
            f"color: {'#fff0bf' if is_question else '#e7dfcf'}; "
            "font-size: 11px; "
            "font-weight: 520; "
            "line-height: 145%;"
        )

        bubble_layout.addWidget(label)

        if is_question:
            row.addStretch(1)
            row.addWidget(bubble, 0)
        else:
            row.addWidget(self._bakkar_avatar(), 0, Qt.AlignBottom)
            row.addWidget(bubble, 0)
            row.addStretch(1)

        self.chat_layout.addWidget(row_host)

        QTimer.singleShot(0, self._scroll_to_bottom)

        return label

    def _scroll_to_bottom(self) -> None:
        bar = self.chat_scroll.verticalScrollBar()
        bar.setValue(bar.maximum())
